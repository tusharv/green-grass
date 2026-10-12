import copy
import json
import re

import pytest
from sqlalchemy import select

from app.models import Application, CV, CvConversation
from app.schemas import Profile
from app.services.cv_chat import CHAT, CvEdit, proposed_profile
from app.services.llm import ModelError
from app.services.prompts import REWRITE_CV, SCREEN, UPSKILL
from tests.samples import SAMPLE_PROFILE
from tests.test_api import ScriptedModel, _client, _csrf, _headers, _register, _upload


def block(prompt, name):
    return json.loads(re.search(rf'<{name}>\n(.*?)\n</{name}>', prompt, re.S)[1])


class ChatModel(ScriptedModel):
    def __init__(self):
        super().__init__({'required_skills': ['Python', 'SQL'], 'preferred_skills': ['Git']}, screen={})
        self.reply = None
        self.fail = None
        self.before_complete = None

    def complete(self, system, user):
        if self.fail == system:
            raise ModelError('The model service did not respond.')
        if system == CHAT:
            self.calls.append(system)
            self.last_prompt = user
            messages = block(user, 'conversation')
            human = [m for m in messages if m['role'] == 'user'][-1]
            response = self.reply(human, messages) if callable(self.reply) else self.reply
            return json.dumps(response or {'reply':'Which company was this, and did you use Git commands, branches or pull requests?', 'edits':[]})
        if system == REWRITE_CV:
            self.calls.append(system)
            if self.before_complete:
                hook, self.before_complete = self.before_complete, None
                hook()
            profile = block(user, 'profile')
            return json.dumps({key: profile[key] for key in ('summary', 'skills', 'experience')})
        if system == UPSKILL:
            self.calls.append(system)
            return json.dumps({'summary':'Practise the missing skills.', 'gaps': []})
        return super().complete(system, user)


def setup(tmp_path):
    model = ChatModel()
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    row = client.post('/api/applications',json={'cv_id':cv_id,'role_title':'Engineer',
        'job_description':'Python and SQL required. Git preferred.'},headers=_headers(_csrf(client))).json()
    return client, model, row, f"/api/applications/{row['id']}/chat"


def edits_reply(edits):
    def reply(human, messages):
        return {'reply':'Please review the proposed changes.', 'edits':[
            {**edit,'evidence':[{'message_id':human['id'],'quote':human['text']}]} for edit in edits]}
    return reply


def propose(client, model, url, text='At Analytical Engines I used Git branches and pull requests for 2 years.', revision=0):
    model.reply = edits_reply([
        {'kind':'add_skill','text':'Git'},
        {'kind':'add_bullet','role_index':0,'text':'Used Git branches and pull requests for 2 years.'},
    ])
    response = client.post(url,json={'message':text,'revision':revision},headers=_headers(_csrf(client)))
    assert response.status_code == 200, response.text
    return response.json()


def apply(client, url, state, **extra):
    return client.post(url+'/apply',json={'revision':state['revision'],'proposal_id':state['proposal']['id'],
        'confirmed':True,**extra},headers=_headers(_csrf(client)))


def test_clarification_is_private_and_leaves_cv_and_assessment_unchanged(tmp_path):
    client, model, row, url = setup(tmp_path)
    before = client.get(f"/api/cvs/{row['cv_id']}").json()['profile']
    response = client.post(url,json={'message':'I used GitHub for 2 years at my company and at college before that.', 'revision':0},headers=_headers(_csrf(client)))
    assert response.status_code == 200, response.text
    state = response.json()
    assert state['proposal'] is None
    assert 'Which company' in state['messages'][-1]['text']
    assert client.get(url).json() == state
    assert client.get(f"/api/cvs/{row['cv_id']}").json()['profile'] == before
    assert client.get(f"/api/applications/{row['id']}").json()['skill_board'] == row['skill_board']
    assert 'ada@example.com' not in model.last_prompt
    assert '<resume>' in model.last_prompt and '<job>' in model.last_prompt


def test_confirmed_edits_update_source_and_reassess_without_publishing(tmp_path):
    client, model, row, url = setup(tmp_path)
    base = f"/api/applications/{row['id']}"
    path = client.post(base+'/profile',headers=_headers(_csrf(client))).json()['share_path']
    public_before = client.get('/api'+path).json()
    profile_before = client.get(f"/api/cvs/{row['cv_id']}").json()['profile']
    state = propose(client, model, url)
    assert len(state['proposal']['changes']) == 2
    assert client.get(f"/api/cvs/{row['cv_id']}").json()['profile'] == profile_before
    response = apply(client, url, state)
    assert response.status_code == 200, response.text
    after = response.json()
    assert after['application']['skill_board']['preferred'][0]['present']
    assert after['application']['skill_board']['preferred'][0]['source'] == 'skills'
    assert after['application']['fit_score'] == row['fit_score']  # Preferred skills never change fit.
    profile_after = client.get(f"/api/cvs/{row['cv_id']}").json()['profile']
    assert 'Git' in profile_after['skills']
    assert profile_after['experience'][0]['bullets'][-1] == 'Used Git branches and pull requests for 2 years.'
    assert profile_after['years_experience'] == profile_before['years_experience']
    for key in ['contact','education']:
        assert profile_after[key] == profile_before[key]
    for key in ['employer','title','start','end']:
        assert profile_after['experience'][0][key] == profile_before['experience'][0][key]
    assert client.get('/api'+path).json() == public_before
    assert after['chat']['proposal'] is None
    assert apply(client, url, state).status_code == 409
    assert 'chat' not in client.get('/api'+path).json()


def test_apply_option_updates_shared_snapshot_and_preserves_design(tmp_path):
    from app.schemas import ResumeDesign
    client, model, row, url = setup(tmp_path)
    base = f"/api/applications/{row['id']}"
    path = client.post(base+'/profile',headers=_headers(_csrf(client))).json()['share_path']
    state = propose(client, model, url)
    design = ResumeDesign(template='creative',palette='plum').model_dump()
    client.post(base+'/design',json=design,headers=_headers(_csrf(client)))
    response = apply(client, url, state, update_shared_profile=True)
    assert response.status_code == 200, response.text
    assert response.json()['shared_updated'] is True
    assert response.json()['application']['design'] == design
    public = client.get('/api'+path).json()
    assert 'Git' in public['document']['skills']
    assert public['design'] == design
    assert 'conversation' not in json.dumps(public)


def test_failure_during_reassessment_changes_nothing_and_can_retry(tmp_path):
    client, model, row, url = setup(tmp_path)
    state = propose(client, model, url)
    before = client.get(f"/api/cvs/{row['cv_id']}").json()
    model.fail = SCREEN
    response = apply(client, url, state)
    assert response.status_code == 422
    assert 'Nothing was changed' in response.json()['detail']
    assert client.get(f"/api/cvs/{row['cv_id']}").json() == before
    assert client.get(f"/api/applications/{row['id']}").json() == row
    assert client.get(url).json() == state
    model.fail = None
    assert apply(client, url, state).status_code == 200


def test_stale_proposals_and_conflicting_conversation_are_rejected(tmp_path):
    client, model, row, url = setup(tmp_path)
    state = propose(client, model, url)
    assert client.post(url,json={'message':'another tab','revision':0},headers=_headers(_csrf(client))).status_code == 409
    with client.app.state.Session() as db:
        cv = db.get(CV, row['cv_id'])
        cv.profile_json = {**cv.profile_json,'summary':'Changed in another conversation.'}
        db.commit()
    assert apply(client, url, state).status_code == 409
    assert client.get(url).json()['proposal'] is None
    assert 'CV changed' in client.get(url).json()['notice']


def test_confirmation_csrf_and_ownership_required(tmp_path):
    client, model, row, url = setup(tmp_path)
    assert client.post(url,json={'message':'test','revision':0}).status_code == 403
    state = propose(client, model, url)
    assert client.post(url+'/apply',json={'revision':1,'proposal_id':state['proposal']['id'],'confirmed':False},headers=_headers(_csrf(client))).status_code == 422
    assert client.post(url+'/apply',json={'revision':1,'proposal_id':state['proposal']['id'],'confirmed':True}).status_code == 403
    client.post('/api/logout',headers=_headers(_csrf(client)))
    _register(client,'other@example.com')
    assert client.get(url).status_code == 404
    assert client.post(url,json={'message':'hello','revision':1},headers=_headers(_csrf(client))).status_code == 404
    assert apply(client,url,state).status_code == 404
    assert client.request('DELETE',url+'/proposal',json={'revision':1},headers=_headers(_csrf(client))).status_code == 404


def test_discard_and_cv_deletion(tmp_path):
    client, model, row, url = setup(tmp_path)
    state = propose(client, model, url)
    response = client.request('DELETE',url+'/proposal',json={'revision':1},headers=_headers(_csrf(client)))
    assert response.status_code == 200
    assert response.json()['proposal'] is None
    assert apply(client,url,state).status_code == 409
    assert client.delete(f"/api/cvs/{row['cv_id']}",headers=_headers(_csrf(client))).status_code == 204
    with client.app.state.Session() as db:
        assert db.get(CvConversation,row['cv_id']) is None


@pytest.mark.parametrize('edit,quote', [
    ({'kind':'add_skill','text':'Git'}, 'I used GitHub at college.'),
    ({'kind':'add_bullet','role_index':99,'text':'Used Git.'}, 'I used Git.'),
    ({'kind':'add_bullet','role_index':0,'text':'Improved speed by 99%.'}, 'I improved speed.'),
])
def test_invalid_edits_rejected(edit, quote):
    edit['evidence'] = [{'message_id':'user1','quote':quote}]
    with pytest.raises(ModelError):
        proposed_profile(SAMPLE_PROFILE,[CvEdit(**edit)],[{'id':'user1','role':'user','text':quote}])


def test_fabricated_or_assistant_evidence_is_rejected():
    edit = CvEdit(kind='add_skill',text='Git',evidence=[{'message_id':'a','quote':'I used Git.'}])
    with pytest.raises(ModelError):
        proposed_profile(SAMPLE_PROFILE,[edit],[{'id':'a','role':'assistant','text':'I used Git.'}])
    with pytest.raises(ModelError):
        proposed_profile(SAMPLE_PROFILE,[edit],[{'id':'a','role':'user','text':'I used GitHub.'}])


def test_ready_can_become_gap_and_pdf_is_removed(tmp_path):
    client, model, row, url = setup(tmp_path)
    model.reply = edits_reply([{'kind':'remove_skill','text':'Python'},{'kind':'remove_skill','text':'SQL'}])
    state = client.post(url,json={'message':'Remove Python and SQL. They were extracted incorrectly.', 'revision':0},headers=_headers(_csrf(client))).json()
    response = apply(client,url,state)
    assert response.status_code == 200, response.text
    assert response.json()['application']['suitable'] is False
    assert response.json()['application']['result']['kind'] == 'gap'
    assert 'document' not in response.json()['application']['result']
    assert client.get(f"/api/applications/{row['id']}/pdf").status_code == 404


def test_gap_can_become_ready_from_confirmed_experience(tmp_path):
    model = ChatModel()
    model.job = {'required_skills':['Rust']}
    client = _client(tmp_path,model)
    _register(client)
    cv_id = _upload(client)
    row = client.post('/api/applications',json={'cv_id':cv_id,'role_title':'Rust engineer','job_description':'Rust required'},headers=_headers(_csrf(client))).json()
    assert not row['suitable']
    url = f"/api/applications/{row['id']}/chat"
    model.reply = edits_reply([{'kind':'add_skill','text':'Rust'}])
    state = client.post(url,json={'message':'I have used Rust to build a parser at college.', 'revision':0},headers=_headers(_csrf(client))).json()
    response = apply(client,url,state)
    assert response.status_code == 200, response.text
    assert response.json()['application']['suitable']
    assert response.json()['application']['result']['kind'] == 'cv'
    profile = client.get(f'/api/cvs/{cv_id}').json()['profile']
    assert profile['experience'] == SAMPLE_PROFILE.model_dump()['experience']
    assert profile['years_experience'] == SAMPLE_PROFILE.years_experience


def test_concurrent_design_update_survives_slow_reassessment(tmp_path):
    from app.schemas import ResumeDesign
    client, model, row, url = setup(tmp_path)
    state = propose(client,model,url)
    design = ResumeDesign(template='modern',palette='teal').model_dump()
    def save_design():
        with client.app.state.Session() as db:
            app = db.get(Application,row['id'])
            app.result_json = {**app.result_json,'design':design}
            db.commit()
    model.before_complete = save_design
    response = apply(client,url,state)
    assert response.status_code == 200, response.text
    assert response.json()['application']['design'] == design


def test_model_failure_when_sending_preserves_previous_proposal(tmp_path):
    client, model, row, url = setup(tmp_path)
    state = propose(client,model,url)
    model.fail = CHAT
    response = client.post(url,json={'message':'Please revise that.', 'revision':1},headers=_headers(_csrf(client)))
    assert response.status_code == 422
    assert client.get(url).json() == state


def test_other_applications_keep_their_assessments(tmp_path):
    client, model, row, url = setup(tmp_path)
    second = client.post('/api/applications',json={'cv_id':row['cv_id'],'role_title':'Another engineer',
        'job_description':'Python and SQL required. Git preferred.'},headers=_headers(_csrf(client))).json()
    state = propose(client,model,url)
    assert apply(client,url,state).status_code == 200
    assert client.get(f"/api/applications/{second['id']}").json() == second
    shared_chat = client.get(f"/api/applications/{second['id']}/chat").json()
    assert shared_chat['messages'][-1]['application_id'] == row['id']


def test_profile_changed_during_model_work_is_not_overwritten(tmp_path):
    client, model, row, url = setup(tmp_path)
    state = propose(client,model,url)
    def change_cv():
        with client.app.state.Session() as db:
            cv = db.get(CV,row['cv_id'])
            cv.profile_json = {**cv.profile_json,'summary':'A concurrent, saved correction.'}
            db.commit()
    model.before_complete = change_cv
    response = apply(client,url,state)
    assert response.status_code == 409
    assert client.get(f"/api/cvs/{row['cv_id']}").json()['profile']['summary'] == 'A concurrent, saved correction.'
    assert client.get(f"/api/applications/{row['id']}").json() == row
    assert client.get(url).json()['revision'] == 1


def test_rewrite_fact_rejection_rolls_back_source_update(tmp_path):
    client, model, row, url = setup(tmp_path)
    state = propose(client,model,url)
    original = model.complete
    def complete(system, user):
        if system == REWRITE_CV:
            return json.dumps({'summary':'Saved $999999 every year.','skills':['Git'],'experience':[]})
        return original(system,user)
    model.complete = complete
    response = apply(client,url,state)
    assert response.status_code == 422
    assert 'Git' not in client.get(f"/api/cvs/{row['cv_id']}").json()['profile']['skills']
    assert client.get(f"/api/applications/{row['id']}").json() == row


def test_chat_message_bounds_and_blank_input(tmp_path):
    client, model, row, url = setup(tmp_path)
    for message, status in [('   ',400), ('a'*3001,422)]:
        assert client.post(url,json={'message':message,'revision':0},headers=_headers(_csrf(client))).status_code == status
    assert client.get(url).json()['revision'] == 0


def test_work_update_requires_named_employer():
    text = 'I used Git at college for 2 years.'
    edit = CvEdit(kind='add_bullet',role_index=0,text='Used Git for 2 years.',evidence=[{'message_id':'u','quote':text}])
    with pytest.raises(ModelError,match='name the employer'):
        proposed_profile(SAMPLE_PROFILE,[edit],[{'id':'u','role':'user','text':text}])


def test_replacements_and_removals_use_original_bullet_indices():
    profile = SAMPLE_PROFILE.model_copy(deep=True)
    profile.experience[0].bullets = ['First bullet.', 'Second bullet.', 'Third bullet.']
    message = 'At Analytical Engines, remove the first bullet and replace the third with Wrote notes.'
    evidence = [{'message_id':'u','quote':message}]
    result, changes = proposed_profile(profile,[
        CvEdit(kind='remove_bullet',role_index=0,bullet_index=0,evidence=evidence),
        CvEdit(kind='replace_bullet',role_index=0,bullet_index=2,text='Wrote notes.',evidence=evidence),
    ],[{'id':'u','role':'user','text':message}])
    assert result.experience[0].bullets == ['Second bullet.','Wrote notes.']
    assert len(changes) == 2
