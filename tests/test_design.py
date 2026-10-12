import pytest
from app.schemas import ResumeDesign
from pydantic import ValidationError
from tests.test_learning_plan import ready_review
from tests.test_api import _csrf, _headers, _register


def test_design_saved_without_changing_facts_or_shared_link(tmp_path):
    client, _, row = ready_review(tmp_path)
    base = f"/api/applications/{row['id']}"
    shared = client.post(base+'/profile', headers=_headers(_csrf(client))).json()['share_path']
    design = ResumeDesign(template='creative', accent='#654321', sections=['skills','summary','experience','education']).model_dump()
    response = client.post(base+'/design', json=design, headers=_headers(_csrf(client)))
    assert response.status_code == 200
    assert response.json()['design'] == design
    assert response.json()['share_path'] == shared
    assert response.json()['result']['document'] == row['result']['document']
    public = client.get('/api'+shared).json()
    assert public['design'] == design
    assert 'creative' in public['design_html']
    assert 'learning_plan' not in public
    preview = client.post(base+'/design-preview', json=design, headers=_headers(_csrf(client)))
    assert preview.status_code == 200
    assert 'Ada Lovelace' in preview.text
    assert 'text/html' in preview.headers['content-type']
    assert client.post(base+'/design',json=design).status_code == 403
    client.post('/api/logout',headers=_headers(_csrf(client)))
    _register(client,'other@example.com')
    assert client.post(base+'/design',json=design,headers=_headers(_csrf(client))).status_code == 404


@pytest.mark.parametrize('bad', [{'accent':'red;display:none'}, {'template':'unknown'}, {'sections':['skills']}, {'sections':['summary']*4}])
def test_design_rejects_invalid_settings(bad):
    with pytest.raises(ValidationError):
        ResumeDesign(**bad)


@pytest.mark.parametrize('template', ['classic','modern','creative','minimal'])
def test_templates_escape_content_and_keep_every_fact(template):
    from app.schemas import CvDocument
    from app.services.design import designed_html
    from tests.samples import SAMPLE_PROFILE
    document = CvDocument.model_validate(SAMPLE_PROFILE.model_dump())
    document.summary = '<script>alert(1)</script>'
    html = designed_html(document, ResumeDesign(template=template))
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    for fact in ['Ada Lovelace','Analytical Engines','1842','1843','Mathematics','Python']:
        assert fact in html


def test_saved_design_reaches_pdf_renderer(tmp_path, monkeypatch):
    client, _, row = ready_review(tmp_path)
    base = f"/api/applications/{row['id']}"
    design = ResumeDesign(template='modern',text_size='large').model_dump()
    client.post(base+'/design', json=design, headers=_headers(_csrf(client)))
    calls = []
    def render(document, settings, photo):
        calls.append((document,settings,photo))
        return b'%PDF-test'
    monkeypatch.setattr('app.main.render_pdf',render)
    assert client.get(base+'/pdf').status_code == 200
    assert calls[0][1].model_dump() == design
    assert calls[0][0].contact.name == 'Ada Lovelace'


def test_contact_actions_and_light_accent_stay_readable():
    from app.schemas import CvDocument
    from app.services.design import designed_html
    from tests.samples import SAMPLE_PROFILE
    document = CvDocument.model_validate(SAMPLE_PROFILE.model_dump())
    document.contact.links = ['https://example.com/portfolio', 'https://user:password@example.com']
    html = designed_html(document,ResumeDesign(template='creative',accent='#ffffff'))
    assert 'href="mailto:ada@example.com"' in html
    assert 'href="https://example.com/portfolio"' in html
    assert 'href="https://user:password' not in html
    assert 'background:#ffffff; color:#111111' in html
    assert 'color:#20252b; font-size:11pt' in html


def test_design_does_not_unlock_gap_pdf(tmp_path):
    from tests.test_api import ScriptedModel, GAP, _client, _upload
    from tests.samples import gap_job
    client = _client(tmp_path,ScriptedModel(gap_job().model_dump(),gap=GAP,screen={}))
    _register(client)
    cv = _upload(client)
    row = client.post('/api/applications',json={'cv_id':cv,'role_title':'Engineer','job_description':'Rust and Kubernetes required.'},headers=_headers(_csrf(client))).json()
    base = f"/api/applications/{row['id']}"
    response=client.post(base+'/design',json=ResumeDesign(template='modern').model_dump(),headers=_headers(_csrf(client)))
    assert response.status_code == 200
    assert response.json()['suitable'] is False
    assert response.json()['result']['kind'] == 'gap'
    assert client.get(base+'/pdf').status_code == 404


def test_design_photo_preferences_and_browser_github_source():
    from types import SimpleNamespace
    from app.main import _design_photo
    from app.schemas import CvDocument
    from app.services.design import designed_html
    from tests.samples import SAMPLE_PROFILE
    doc = CvDocument.model_validate(SAMPLE_PROFILE.model_dump())
    doc.contact.links = ['https://github.com/ada-l']
    cv = SimpleNamespace(photo=None, profile_json=doc.model_dump())
    url = _design_photo(cv, web=True)
    assert url == 'https://github.com/ada-l.png?size=640'
    assert _design_photo(cv) == ''
    assert '<img class="portrait"' in designed_html(doc, ResumeDesign(show_photo=True), url)
    assert '<img class="portrait"' not in designed_html(doc, ResumeDesign(show_photo=False), url)
    cv.photo = SimpleNamespace(source='none')
    assert _design_photo(cv, web=True) == ''
    cv.photo = SimpleNamespace(source='upload', data=b'jpeg')
    assert _design_photo(cv, web=True).startswith('data:image/jpeg;base64,')
    assert '<img class="portrait"' not in designed_html(doc, ResumeDesign(), 'https://untrusted.example/photo.png')


@pytest.mark.parametrize('font', ['serif','sans','editorial','humanist','book','geometric','mono'])
def test_extended_design_controls_render(font):
    from app.schemas import CvDocument
    from app.services.design import designed_html
    from tests.samples import SAMPLE_PROFILE
    design = ResumeDesign(font=font,palette='navy',photo_size='large',photo_shape='rounded')
    html = designed_html(CvDocument.model_validate(SAMPLE_PROFILE.model_dump()),design,'data:image/jpeg;base64,eA==')
    assert '--page-color:#f0f4fa' in html
    assert '--design-accent:#203c64' in html
    assert '--photo-size:152px' in html
    assert '--photo-radius:18%' in html
    assert '<img class="portrait"' in html
