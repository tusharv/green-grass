import json
from copy import deepcopy
import pytest
from app.services.llm import write_application_insights, ModelError
from app.services.prompts import APPLICATION_INSIGHTS, VERIFY_APPLICATION_INSIGHTS
from tests.samples import SAMPLE_PROFILE, suitable_job
from tests.test_api import _client, _register, _csrf, _headers, _docx, ScriptedModel, REWRITE

DRAFT = {'letter':[
    {'text':'Dear Hiring Team,','evidence_ids':[]},
    {'text':'I bring Python skills and would welcome the opportunity to contribute to your team.','evidence_ids':['s0']},
    {'text':'Kind regards,\nAda Lovelace','evidence_ids':[]}],
    'verdict':'Your Python and SQL skills support this application.',
    'risks':['A listed skill is not proof of using it in a work project.'],
    'next_round':'The employer’s decision cannot be predicted; relevant work examples will matter in screening.'}

class PitchModel(ScriptedModel):
    def __init__(self, draft=None, verified=True):
        super().__init__(suitable_job().model_dump(),rewrite=REWRITE)
        self.draft = deepcopy(draft or DRAFT)
        self.verified = verified
        self.contexts=[]
    def complete(self, system, user):
        if system.startswith(APPLICATION_INSIGHTS) or system == VERIFY_APPLICATION_INSIGHTS:
            self.calls.append(system)
            self.contexts.append(user)
            if system.startswith(APPLICATION_INSIGHTS):
                return json.dumps(self.draft)
            return json.dumps({'supported':self.verified,'positive_letter':self.verified,'honest_review':self.verified,'reasons':[] if self.verified else ['Unsupported expertise claim.']})
        return super().complete(system,user)


def test_both_sections_come_from_model_with_private_contact_minimized():
    model=PitchModel()
    result=write_application_insights(model,'Engineer','Python services',suitable_job().model_dump(),SAMPLE_PROFILE.model_dump())
    assert result['cover_letter']['text']=='\n\n'.join(p['text'] for p in DRAFT['letter'])
    assert result['honest_review']['verdict']==DRAFT['verdict']
    assert model.calls==[APPLICATION_INSIGHTS,VERIFY_APPLICATION_INSIGHTS]
    assert '<resume>' in model.contexts[0] and '<job>' in model.contexts[0]
    assert SAMPLE_PROFILE.contact.email not in model.contexts[0]


@pytest.mark.parametrize('change',[{'text':'I saved $999999 million.','evidence_ids':['s0']},{'text':'I built Python tools.','evidence_ids':['invented']}])
def test_bad_citations_and_new_metrics_never_pass(change):
    draft=deepcopy(DRAFT);draft['letter'][1]=change
    model=PitchModel(draft)
    with pytest.raises(ModelError):
        write_application_insights(model,'Engineer','Python',{},SAMPLE_PROFILE.model_dump())
    assert model.calls.count(APPLICATION_INSIGHTS)==2
    assert VERIFY_APPLICATION_INSIGHTS not in model.calls


def test_semantic_verification_failure_is_not_saved_or_replaced_by_template():
    model=PitchModel(verified=False)
    with pytest.raises(ModelError,match='Nothing was saved'):
        write_application_insights(model,'Engineer','Python',{},SAMPLE_PROFILE.model_dump())
    assert model.calls.count(VERIFY_APPLICATION_INSIGHTS)==2


def setup_role(client):
    _register(client)
    headers=_headers(_csrf(client))
    cv=client.post('/api/cvs',headers=headers,files={'file':('cv.docx',_docx())}).json()
    row=client.post('/api/applications',headers=headers,json={'cv_id':cv['id'],'role_title':'Engineer','job_description':'Python and SQL required'}).json()
    return headers,row


def test_insights_cache_private_and_invalidated_after_source_change(tmp_path):
    from app.models import Application
    model=PitchModel()
    with _client(tmp_path,model) as client:
        headers,row=setup_role(client)
        url=f"/api/applications/{row['id']}/insights"
        assert row['honest_review'] is None and row['cover_letter'] is None
        assert client.post(url).status_code==403
        response=client.post(url,headers=headers)
        assert response.status_code==200,response.text
        assert response.json()['honest_review']['verdict']==DRAFT['verdict']
        count=len(model.calls)
        assert client.post(url,headers=headers).status_code==200
        assert len(model.calls)==count
        shared=client.post(f"/api/applications/{row['id']}/profile",headers=headers).json()
        public=client.get('/api'+shared['share_path']).json()
        assert 'cover_letter' not in public and 'honest_review' not in public
        with client.app.state.Session() as db:
            saved=db.get(Application,row['id'])
            saved.job_description='A changed job description'
            db.commit()
        updated=client.get(f"/api/applications/{row['id']}").json()
        assert updated['cover_letter'] is None and updated['honest_review'] is None
        assert 'application_insights' not in updated['result']
        client.post('/api/logout',headers=headers)
        _register(client,'other@example.com')
        assert client.post(url,headers=_headers(_csrf(client))).status_code==404


def test_failed_generation_leaves_assessment_and_pdf_eligibility_unchanged(tmp_path):
    with _client(tmp_path,PitchModel(verified=False)) as client:
        headers,row=setup_role(client)
        assert client.post(f"/api/applications/{row['id']}/insights",headers=headers).status_code==422
        current=client.get(f"/api/applications/{row['id']}").json()
        assert current['result']==row['result']
        assert current['suitable']==row['suitable']
        assert current['cover_letter'] is None


def test_source_change_during_generation_rejected(tmp_path):
    from app.models import Application
    model=PitchModel()
    with _client(tmp_path,model) as client:
        headers,row=setup_role(client)
        original=model.complete
        def complete(system,user):
            result=original(system,user)
            if system==VERIFY_APPLICATION_INSIGHTS:
                with client.app.state.Session() as db:
                    saved=db.get(Application,row['id']);saved.job_description='Changed while generating';db.commit()
            return result
        model.complete=complete
        assert client.post(f"/api/applications/{row['id']}/insights",headers=headers).status_code==409
        assert client.get(f"/api/applications/{row['id']}").json()['cover_letter'] is None


def test_assessed_years_are_available_as_evidence():
    draft=deepcopy(DRAFT)
    draft['letter'][1]={'text':'I bring 8 years of experience.','evidence_ids':['years_shown']}
    result=write_application_insights(PitchModel(draft),'Engineer','Python',{'years_shown':8,'years_needed':10},SAMPLE_PROFILE.model_dump())
    assert '8 years' in result['cover_letter']['text']


def test_missing_requirement_cannot_be_claimed_even_if_verifier_accepts():
    draft=deepcopy(DRAFT)
    draft['letter'][1]={'text':'I have Kubernetes skills.','evidence_ids':['s0']}
    with pytest.raises(ModelError):
        write_application_insights(PitchModel(draft),'Engineer','Kubernetes',{'required':[{'name':'Kubernetes','present':False}]},SAMPLE_PROFILE.model_dump())


def test_inline_citation_digits_are_not_treated_as_metrics():
    draft=deepcopy(DRAFT)
    draft['letter'][1]={'text':'I bring Python skills [s0].','evidence_ids':['s0']}
    result=write_application_insights(PitchModel(draft),'Engineer','Python',{},SAMPLE_PROFILE.model_dump())
    assert 'I bring Python skills.' in result['cover_letter']['text']
    assert '[s0]' not in result['cover_letter']['text']
    assert result['cover_letter']['sources'][0]['id']=='s0'


def test_bracketed_metrics_and_uncited_ids_are_not_removed():
    for text in ('I saved [999999] dollars.', 'I bring Python skills [w99b12].'):
        draft=deepcopy(DRAFT)
        draft['letter'][1]={'text':text,'evidence_ids':['s0']}
        with pytest.raises(ModelError):
            write_application_insights(PitchModel(draft),'Engineer','Python',{},SAMPLE_PROFILE.model_dump())


def test_independent_generation_edit_and_regeneration(tmp_path):
    model=PitchModel()
    with _client(tmp_path,model) as client:
        headers,row=setup_role(client)
        root=f"/api/applications/{row['id']}"
        first=client.post(root+'/honest-review',headers=headers)
        assert first.status_code==200,first.text
        first=first.json()
        assert first['honest_review'] and first['cover_letter'] is None
        review=first['honest_review']
        assert 'ONLY the honest review' in model.calls[-2]
        second=client.post(root+'/cover-letter',headers=headers).json()
        assert second['honest_review']==review
        letter=second['cover_letter']
        assert 'ONLY the cover letter' in model.calls[-2]
        edited=client.patch(root+'/cover-letter',headers=headers,json={'text':'My own positive pitch.','expected_revision':letter['revision']})
        assert edited.status_code==200,edited.text
        assert edited.json()['cover_letter']['edited_by_user']
        assert edited.json()['honest_review']==review
        assert client.patch(root+'/cover-letter',headers=headers,json={'text':'Stale edit','expected_revision':letter['revision']}).status_code==409
        regenerated=client.post(root+'/honest-review',headers=headers).json()
        assert regenerated['cover_letter']['text']=='My own positive pitch.'
        count=len(model.calls)
        final=client.post(root+'/cover-letter',headers=headers).json()
        assert len(model.calls)>count
        assert not final['cover_letter'].get('edited_by_user')
        assert final['honest_review']==regenerated['honest_review']
