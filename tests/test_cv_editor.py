import base64
import copy
import io

import pytest
from PIL import Image

from app.models import CV
from app.schemas import CvDocument, ResumeDesign
from app.services.design import designed_html
from tests.test_api import _csrf, _headers, _register, REWRITE
from tests.test_learning_plan import ready_review


def editor(client, row):
    base = f"/api/applications/{row['id']}"
    response = client.get(base + '/editor')
    assert response.status_code == 200
    state = response.json()
    return base, {**state, 'confirmed': True, 'update_shared_profile': False}


def test_editor_saves_confirmed_source_and_preserves_other_assessments(tmp_path):
    client, model, row = ready_review(tmp_path)
    base = f"/api/applications/{row['id']}"
    shared = client.post(base + '/profile', headers=_headers(_csrf(client))).json()['share_path']
    original_public = client.get('/api' + shared).json()['document']
    other = client.post('/api/applications', json={'cv_id': row['cv_id'], 'role_title': 'Another role',
        'job_description': 'Python and SQL'}, headers=_headers(_csrf(client))).json()
    with client.app.state.Session() as db:
        original_text = db.get(CV, row['cv_id']).extracted_text
    base, body = editor(client, row)
    body['profile']['summary'] = 'My own carefully chosen wording.'
    body['profile']['contact']['location'] = 'London'
    body['profile']['custom_sections'] = [{'id': 'custom-projects', 'title': 'Projects', 'items': ['Built a parser.']}]
    body['design']['sections'] = ['skills', 'custom-projects', 'experience', 'summary']
    response = client.post(base + '/editor', json=body, headers=_headers(_csrf(client)))
    assert response.status_code == 200, response.text
    updated = response.json()['application']
    assert updated['result']['document']['summary'] == body['profile']['summary']
    assert updated['design']['sections'] == body['design']['sections']
    assert 'Built a parser.' in updated['design_html']
    source = client.get(f"/api/cvs/{row['cv_id']}").json()['profile']
    assert source == body['profile']
    assert client.get(f"/api/applications/{other['id']}").json()['result'] == other['result']
    assert client.get('/api' + shared).json()['document'] == original_public
    with client.app.state.Session() as db:
        assert db.get(CV, row['cv_id']).extracted_text == original_text
    assert client.post(base + '/editor', json=body, headers=_headers(_csrf(client))).status_code == 409


def test_editor_design_only_does_not_call_model_and_preview_does_not_save(tmp_path):
    client, model, row = ready_review(tmp_path)
    base, body = editor(client, row)
    count = len(model.calls)
    body['design']['sections'] = ['skills', 'summary']
    body['confirmed'] = False
    preview = client.post(base + '/editor/preview', json={'profile': body['profile'], 'design': body['design']}, headers=_headers(_csrf(client)))
    assert preview.status_code == 200
    assert '<section class="section experience"' not in preview.text
    assert client.get(base).json()['design'] == row['design']
    saved = client.post(base + '/editor', json=body, headers=_headers(_csrf(client)))
    assert saved.status_code == 200, saved.text
    assert len(model.calls) == count
    assert saved.json()['application']['result']['document'] == row['result']['document']


def test_editor_requires_confirmation_csrf_and_owner(tmp_path):
    client, _, row = ready_review(tmp_path)
    base, body = editor(client, row)
    body['profile']['summary'] = 'Updated by hand'
    body['confirmed'] = False
    assert client.post(base + '/editor', json=body, headers=_headers(_csrf(client))).status_code == 422
    assert client.post(base + '/editor', json=body).status_code == 403
    client.post('/api/logout', headers=_headers(_csrf(client)))
    _register(client, 'other@example.com')
    assert client.get(base + '/editor').status_code == 404
    assert client.post(base + '/editor/preview', json={'profile': body['profile'], 'design': body['design']}, headers=_headers(_csrf(client))).status_code == 404


def test_failed_reassessment_saves_nothing(tmp_path):
    client, model, row = ready_review(tmp_path)
    base, body = editor(client, row)
    before = copy.deepcopy(body)
    body['profile']['summary'] = 'New wording'
    body['design']['template'] = 'minimal'
    model.rewrite = {**REWRITE, 'summary': 'Invented 987654 clients'}
    response = client.post(base + '/editor', json=body, headers=_headers(_csrf(client)))
    assert response.status_code == 422
    assert client.get(base + '/editor').json()['profile'] == before['profile']
    assert client.get(base).json()['result'] == row['result']


def test_editor_reassessment_can_remove_pdf_and_refresh_shared_snapshot(tmp_path):
    client, model, row = ready_review(tmp_path)
    base = f"/api/applications/{row['id']}"
    shared = client.post(base + '/profile', headers=_headers(_csrf(client))).json()['share_path']
    base, body = editor(client, row)
    body['profile']['skills'] = []
    body['profile']['experience'] = []
    body['update_shared_profile'] = True
    model.gap = {'summary': '', 'gaps': []}
    response = client.post(base + '/editor', json=body, headers=_headers(_csrf(client)))
    assert response.status_code == 200, response.text
    assert response.json()['application']['result']['kind'] == 'gap'
    assert response.json()['application']['suitable'] is False
    assert client.get(base + '/pdf').status_code == 404
    assert client.get('/api' + shared).json()['document']['experience'] == []


def test_uploaded_logo_is_reencoded_and_saved_in_preview_and_pdf_design(tmp_path):
    client, _, row = ready_review(tmp_path)
    base, body = editor(client, row)
    out = io.BytesIO()
    Image.new('RGB', (300, 100), 'red').save(out, format='PNG')
    response = client.post(base + '/editor/logo', files={'file': ('logo.png', out.getvalue(), 'image/png')}, headers=_headers(_csrf(client)))
    assert response.status_code == 200
    url = response.json()['url']
    image = Image.open(io.BytesIO(base64.b64decode(url.split(',')[1])))
    assert image.size == (256, 256)
    assert not image.info
    body['design']['company_logos'] = {'analytical engines': url}
    response = client.post(base + '/editor', json=body, headers=_headers(_csrf(client)))
    assert response.status_code == 200
    assert url in response.json()['application']['design_html']
    assert client.get(base + '/logos/0').json()['url'] == url
    assert client.post(base + '/editor/logo', files={'file': ('bad.svg', b'<svg onload="evil()"/>', 'image/svg+xml')}, headers=_headers(_csrf(client))).status_code == 400
    assert client.post(base + '/editor/logo', files={'file': ('huge.png', b'x' * (3 * 1024 * 1024 + 1), 'image/png')}, headers=_headers(_csrf(client))).status_code == 400


def test_custom_sections_are_copied_from_source_not_model():
    from app.services.facts import ground_tailored
    from app.schemas import TailoredDraft
    from app.services.fit import score_fit
    from tests.samples import SAMPLE_PROFILE, suitable_job
    profile = SAMPLE_PROFILE.model_copy(deep=True)
    profile = type(profile).model_validate({**profile.model_dump(), 'custom_sections': [{'id': 'custom-projects', 'title': '<Projects>', 'items': ['<script>bad</script>']}]})
    result = ground_tailored(profile, TailoredDraft.model_validate(REWRITE), score_fit(profile, suitable_job(), [], []))
    assert result.custom_sections == profile.custom_sections
    html = designed_html(result, ResumeDesign(sections=['custom-projects']))
    assert '&lt;Projects&gt;' in html and '<script>bad</script>' not in html


@pytest.mark.parametrize('change', [{'years_experience': -1}, {'summary': 'a' * 40001}, {'skills': ['a'] * 301}])
def test_editor_rejects_unbounded_or_invalid_profile(tmp_path, change):
    client, _, row = ready_review(tmp_path)
    base, body = editor(client, row)
    body['profile'].update(change)
    assert client.post(base + '/editor', json=body, headers=_headers(_csrf(client))).status_code == 422


def test_stale_editor_cannot_overwrite_another_design_save(tmp_path):
    client, _, row = ready_review(tmp_path)
    base, body = editor(client, row)
    newer = ResumeDesign(template='minimal').model_dump()
    client.post(base + '/design', json=newer, headers=_headers(_csrf(client)))
    body['profile']['summary'] = 'Stale draft'
    assert client.post(base + '/editor', json=body, headers=_headers(_csrf(client))).status_code == 409
    assert client.get(base).json()['design']['template'] == 'minimal'


def test_manual_save_invalidates_pending_chat_proposal(tmp_path):
    from app.models import CvConversation
    client, _, row = ready_review(tmp_path)
    with client.app.state.Session() as db:
        db.add(CvConversation(cv_id=row['cv_id'], revision=1, messages=[], pending={'id':'old','application_id':row['id']}))
        db.commit()
    base, body = editor(client, row)
    body['profile']['summary'] = 'Confirmed manual edit'
    response = client.post(base + '/editor', json=body, headers=_headers(_csrf(client)))
    assert response.status_code == 200
    chat = client.get(base + '/chat').json()
    assert chat['proposal'] is None
    assert chat['revision'] == 2
    assert client.post(base + '/chat/apply',json={'proposal_id':'old','revision':1,'confirmed':True},headers=_headers(_csrf(client))).status_code == 409


def test_concurrent_source_edit_during_model_work_rolls_back_editor(tmp_path, monkeypatch):
    client, model, row = ready_review(tmp_path)
    base, body = editor(client, row)
    body['profile']['summary'] = 'Editor text'
    original = model.complete
    changed = False
    def complete(system, user):
        nonlocal changed
        if not changed:
            changed = True
            with client.app.state.Session() as db:
                cv = db.get(CV, row['cv_id'])
                cv.profile_json = {**cv.profile_json, 'summary':'A concurrent support correction'}
                db.commit()
        return original(system,user)
    monkeypatch.setattr(model,'complete',complete)
    response = client.post(base + '/editor',json=body,headers=_headers(_csrf(client)))
    assert response.status_code == 409
    assert client.get(base).json()['result'] == row['result']
    assert client.get(f"/api/cvs/{row['cv_id']}").json()['profile']['summary'] == 'A concurrent support correction'
    assert client.get(base + '/chat').json()['revision'] == 0


def test_custom_content_survives_default_pdf_and_is_escaped():
    from app.services.pdf import document_html
    from tests.samples import SAMPLE_PROFILE
    document = CvDocument.model_validate({**SAMPLE_PROFILE.model_dump(), 'custom_sections': [
        {'id':'custom-projects','title':'<Projects>','items':['A <script>bad</script> project']} ]})
    rendered = document_html(document)
    assert '&lt;Projects&gt;' in rendered
    assert 'A &lt;script&gt;bad&lt;/script&gt; project' in rendered
    assert '<script>' not in rendered


def test_logo_preview_follows_employer_after_reorder_and_rejects_unknown_names(tmp_path):
    client, _, row = ready_review(tmp_path)
    seen = []
    client.app.state.logos.lookup = lambda name: seen.append(name) or {'url':None,'source':None}
    url = f"/api/cvs/{row['cv_id']}/logos/5"
    assert client.get(url,params={'employer':'Analytical Engines'}).status_code == 200
    assert seen == ['Analytical Engines']
    assert client.get(url,params={'employer':'Unconfirmed company'}).json()['url'] is None
    assert seen == ['Analytical Engines']
