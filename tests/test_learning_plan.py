import copy

import pytest
from pydantic import ValidationError

from app.schemas import GapReport
from app.services.facts import FactError, ground_gap
from app.services.prompts import UPSKILL
from tests.test_api import ScriptedModel, REWRITE, _client, _csrf, _headers, _register, _upload

PLAN = {
    'summary': 'Practise Rust for the role.',
    'gaps': [{
        'skill': 'Rust', 'why_it_matters': 'The role builds a parser.',
        'learn': ['Learn ownership through a small parser.'],
        'practice': 'Parse a line of sample input.', 'project': 'Build a parser for sample records.',
        'verify': 'Check a valid record and a malformed record.',
        'resources': [{'title': 'The Rust Book', 'url': 'https://doc.rust-lang.org/book/'}],
    }],
}

class ContextModel(ScriptedModel):
    def complete(self, system, user):
        if system == UPSKILL:
            self.learning_context = user
        return super().complete(system, user)


def ready_review(tmp_path, plan=None):
    model = ContextModel({'required_skills': ['Python', 'SQL', 'Rust']}, rewrite=REWRITE, gap=plan or copy.deepcopy(PLAN), screen={})
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    response = client.post('/api/applications', json={'cv_id': cv_id, 'role_title': 'Parser engineer', 'job_description': 'Build parsers using Rust, Python and SQL.'}, headers=_headers(_csrf(client)))
    assert response.status_code == 201
    row = response.json()
    assert row['suitable']
    return client, model, row


def test_saved_ready_review_gets_contextual_ai_plan_without_changing_cv_or_fit(tmp_path):
    client, model, before = ready_review(tmp_path)
    url = f"/api/applications/{before['id']}/learning-plan"
    response = client.post(url, headers=_headers(_csrf(client)))
    assert response.status_code == 200, response.text
    after = response.json()
    assert after['result']['learning_plan']['gaps'][0]['resources'] == PLAN['gaps'][0]['resources']
    for field in ['suitable', 'fit_score', 'skill_board']:
        assert after[field] == before[field]
    assert after['result']['document'] == before['result']['document']
    assert '<resume>' in model.learning_context and '</resume>' in model.learning_context
    assert '<job>' in model.learning_context and 'Build parsers using Rust' in model.learning_context
    assert 'Translated a memoir' in model.learning_context
    assert 'ada@example.com' not in model.learning_context
    assert client.get(f"/api/applications/{before['id']}").json()['result'] == after['result']
    count = len(model.calls)
    assert client.post(url, headers=_headers(_csrf(client))).json()['result'] == after['result']
    assert len(model.calls) == count


def test_learning_plan_requires_csrf_and_ownership(tmp_path):
    client, model, row = ready_review(tmp_path)
    url = f"/api/applications/{row['id']}/learning-plan"
    assert client.post(url).status_code == 403
    client.post('/api/logout', headers=_headers(_csrf(client)))
    _register(client, 'someoneelse@example.com')
    assert client.post(url, headers=_headers(_csrf(client))).status_code == 404
    assert UPSKILL not in model.calls


def test_invalid_ai_plan_is_not_saved(tmp_path):
    plan = copy.deepcopy(PLAN)
    plan['gaps'][0]['skill'] = 'Python'
    client, model, row = ready_review(tmp_path, plan)
    response = client.post(f"/api/applications/{row['id']}/learning-plan", headers=_headers(_csrf(client)))
    assert response.status_code == 422
    assert client.get(f"/api/applications/{row['id']}").json()['result'] == row['result']


@pytest.mark.parametrize('field', ['learn', 'verify', 'resources'])
def test_new_learning_fields_reject_claiming_unearned_skills(field):
    plan = copy.deepcopy(PLAN)
    bad = 'Add Rust to your CV.'
    plan['gaps'][0][field] = [bad] if field == 'learn' else [{'title': bad, 'url': 'https://example.com/'}] if field == 'resources' else bad
    with pytest.raises(FactError):
        ground_gap(['Rust'], [], GapReport.model_validate(plan))


@pytest.mark.parametrize('url', ['javascript:alert(1)', 'http://example.com/course', 'https://user:pass@example.com/course'])
def test_resources_reject_unsafe_links(url):
    plan = copy.deepcopy(PLAN)
    plan['gaps'][0]['resources'][0]['url'] = url
    with pytest.raises(ValidationError):
        GapReport.model_validate(plan)

@pytest.mark.parametrize('job', [
    {'required_skills': [], 'preferred_skills': ['Rust']},
    {'required_skills': ['Python'], 'preferred_skills': ['Rust'], 'min_years': 100},
])
def test_special_outcomes_do_not_call_ai_or_create_skill_courses(tmp_path, job):
    model = ScriptedModel(job, rewrite=REWRITE, screen={})
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    row = client.post('/api/applications', json={'cv_id': cv_id, 'role_title': 'Engineer', 'job_description': 'A role description.'}, headers=_headers(_csrf(client))).json()
    if job.get('min_years'):
        # Historical years-only reviews remain readable even though full coverage
        # clears the current score threshold.
        from app.models import Application
        from app.services.facts import years_gap
        with client.app.state.Session() as db:
            saved = db.get(Application, row['id'])
            saved.suitable = False
            saved.result_json = {'kind': 'gap', 'report': years_gap(5, 100).model_dump()}
            db.commit()
        row = client.get(f"/api/applications/{row['id']}").json()
    count = len(model.calls)
    after = client.post(f"/api/applications/{row['id']}/learning-plan", headers=_headers(_csrf(client)))
    assert after.status_code == 200
    assert after.json()['result'] == row['result']
    assert len(model.calls) == count
    assert client.get(f"/api/applications/{row['id']}/pdf").status_code == 404


def test_gap_plan_enrichment_does_not_unlock_pdf(tmp_path):
    model = ScriptedModel({'required_skills': ['Rust']}, gap=copy.deepcopy(PLAN), screen={})
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    row = client.post('/api/applications', json={'cv_id': cv_id, 'role_title': 'Parser engineer', 'job_description': 'Build parsers with Rust.'}, headers=_headers(_csrf(client))).json()
    assert row['suitable'] is False
    response = client.post(f"/api/applications/{row['id']}/learning-plan", headers=_headers(_csrf(client)))
    assert response.status_code == 200
    assert response.json()['result']['kind'] == 'gap'
    assert 'document' not in response.json()['result']
    assert client.get(f"/api/applications/{row['id']}/pdf").status_code == 404


def test_incomplete_grounded_plan_can_be_regenerated(tmp_path):
    client, model, row = ready_review(tmp_path, {'summary': 'Try the missing skill.', 'gaps': []})
    url = f"/api/applications/{row['id']}/learning-plan"
    first = client.post(url, headers=_headers(_csrf(client)))
    assert first.status_code == 200
    assert first.json()['result']['learning_plan']['gaps'][0]['resources'] == []
    model.gap = copy.deepcopy(PLAN)
    second = client.post(url, headers=_headers(_csrf(client)))
    assert second.status_code == 200
    assert second.json()['result']['learning_plan']['gaps'][0]['resources'] == PLAN['gaps'][0]['resources']
