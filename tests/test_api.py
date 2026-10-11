import io
import json

from docx import Document
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import _name_slug, create_app
from app.services.prompts import EXTRACT_JOB, EXTRACT_RESUME, REWRITE_CV, SCREEN, UPSKILL
from tests.samples import SAMPLE_PROFILE, gap_job, suitable_job

EVIDENCE = "Translated a memoir on the analytical engine."


def evidenced(job: dict) -> dict:
    def rows(names: list[str]) -> list[dict]:
        return [{"skill": name, "quote": EVIDENCE} for name in names]

    return {
        "required": rows(job.get("required_skills") or []),
        "preferred": rows(job.get("preferred_skills") or []),
    }


class ScriptedModel:
    def __init__(
        self,
        job: dict,
        rewrite: dict | None = None,
        gap: dict | None = None,
        screen: dict | None | str = "auto",
    ):
        self.job = job
        self.rewrite = rewrite
        self.gap = gap
        self.screen = screen
        self.calls: list[str] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append(system)
        if system == EXTRACT_RESUME:
            return SAMPLE_PROFILE.model_dump_json()
        if system == EXTRACT_JOB:
            return json.dumps(self.job)
        if system == SCREEN:
            if self.screen == "auto":
                return json.dumps(evidenced(self.job))
            return json.dumps(self.screen or {"required": [], "preferred": []})
        if system == REWRITE_CV:
            return json.dumps(self.rewrite)
        if system == UPSKILL:
            return json.dumps(self.gap)
        raise AssertionError(system)


REWRITE = {
    "summary": "Programmer who translated a memoir on the analytical engine.",
    "skills": ["Python", "SQL"],
    "experience": [
        {
            "employer": "Analytical Engines",
            "title": "Programmer",
            "start": "1842",
            "end": "1843",
            "bullets": ["Translated a memoir on the analytical engine."],
        }
    ],
}

GAP = {
    "summary": "Two required skills are not on this CV.",
    "gaps": [
        {
            "skill": "Kubernetes",
            "why_it_matters": "The role runs services on it.",
            "practice": "Deploy one service to a local cluster.",
            "project": "Write down the steps you took.",
        },
        {
            "skill": "Rust",
            "why_it_matters": "The role builds tools in Rust.",
            "practice": "Write a small command line tool.",
            "project": "Describe the tool in your own words.",
        },
    ],
}


def _docx() -> bytes:
    buffer = io.BytesIO()
    document = Document()
    document.add_paragraph(
        "Ada Lovelace built analytical engines and wrote notes on the analytical engine."
    )
    document.save(buffer)
    return buffer.getvalue()


def _client(tmp_path, model: ScriptedModel) -> TestClient:
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        session_secret="test-secret",
        ollama_api_key="test-key",
        cookie_secure=False,
    )
    app = create_app(settings, model=model)
    return TestClient(app)


def _csrf(client: TestClient) -> str:
    response = client.get("/api/session")
    assert response.status_code == 200
    return response.json()["csrf"]


def _headers(token: str) -> dict[str, str]:
    return {"X-CSRF-Token": token}


def _register(client: TestClient, email: str = "ada@example.com") -> None:
    token = _csrf(client)
    response = client.post(
        "/api/register",
        json={"email": email, "password": "correct-horse"},
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text


def _upload(client: TestClient) -> int:
    token = _csrf(client)
    response = client.post(
        "/api/cvs",
        files={"file": ("ada.docx", _docx(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers=_headers(token),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_health(tmp_path):
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump()))
    assert client.get("/health").json() == {"ok": True}


def test_register_login_and_cv_isolation(tmp_path):
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE))
    _register(client)
    cv_id = _upload(client)
    mine = client.get(f"/api/cvs/{cv_id}")
    assert mine.status_code == 200
    assert mine.json()["profile"]["contact"]["name"] == "Ada Lovelace"

    client.post("/api/logout", headers=_headers(_csrf(client)))
    _register(client, "other@example.com")
    hidden = client.get(f"/api/cvs/{cv_id}")
    assert hidden.status_code == 404


def test_login_rejects_a_wrong_password(tmp_path):
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump()))
    _register(client)
    client.post("/api/logout", headers=_headers(_csrf(client)))
    response = client.post(
        "/api/login",
        json={"email": "ada@example.com", "password": "wrong-password"},
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 400
    assert "does not match" in response.json()["detail"]


def test_upload_rejects_the_wrong_type_and_oversize_files(tmp_path):
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump()))
    _register(client)
    token = _csrf(client)
    wrong = client.post(
        "/api/cvs",
        files={"file": ("notes.txt", b"not a resume but long enough to read maybe", "text/plain")},
        headers=_headers(token),
    )
    assert wrong.status_code == 400
    assert "PDF or DOCX" in wrong.json()["detail"]

    huge = client.post(
        "/api/cvs",
        files={"file": ("ada.pdf", b"x" * (5 * 1024 * 1024 + 1), "application/pdf")},
        headers=_headers(_csrf(client)),
    )
    assert huge.status_code == 400
    assert "5 MB" in huge.json()["detail"]
    assert client.get("/api/cvs").json() == []


def test_suitable_role_saves_a_polished_cv(tmp_path):
    model = ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE)
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    response = client.post(
        "/api/applications",
        json={
            "cv_id": cv_id,
            "role_title": "Programmer",
            "job_description": "Required: Python and SQL. Preferred: writing.",
        },
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["suitable"] is True
    assert body["fit_score"] == 100
    assert body["result"]["kind"] == "cv"
    assert body["result"]["document"]["skills"][:2] == ["Python", "SQL"]
    assert EXTRACT_JOB in model.calls
    assert SCREEN in model.calls
    assert REWRITE_CV in model.calls
    assert UPSKILL not in model.calls
    quote = body["skill_board"]["required"][0]["quote"]
    assert quote == EVIDENCE
    saved = client.get(f"/api/applications/{body['id']}").json()["skill_board"]
    assert saved["required"][0]["quote"] == EVIDENCE
    assert saved["years_shown"] == 5
    assert saved["years_needed"] == 3
    assert saved["years_score"] == 1


def test_gap_role_saves_upskilling_and_no_pdf(tmp_path):
    model = ScriptedModel(gap_job().model_dump(), gap=GAP, screen=None)
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    response = client.post(
        "/api/applications",
        json={
            "cv_id": cv_id,
            "role_title": "Platform engineer",
            "job_description": "Required: Kubernetes and Rust.",
        },
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["suitable"] is False
    assert body["result"]["kind"] == "gap"
    skills = [(gap["skill"], gap["severity"]) for gap in body["result"]["report"]["gaps"]]
    assert skills == [("Kubernetes", "major"), ("Rust", "major")]
    present = {mark["name"]: mark["present"] for mark in body["skill_board"]["required"]}
    assert present == {"Kubernetes": False, "Rust": False}
    pdf = client.get(f"/api/applications/{body['id']}/pdf")
    assert pdf.status_code == 404
    assert "document" not in body["result"]


def test_invented_employer_is_not_saved(tmp_path):
    bad = {
        **REWRITE,
        "experience": [
            {
                "employer": "OpenAI",
                "title": "Researcher",
                "start": "2020",
                "end": "2024",
                "bullets": ["Led a team of 12."],
            }
        ],
    }
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump(), rewrite=bad))
    _register(client)
    cv_id = _upload(client)
    response = client.post(
        "/api/applications",
        json={"cv_id": cv_id, "role_title": "Programmer", "job_description": "Python and SQL required."},
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 422
    assert "Nothing was saved" in response.json()["detail"]
    assert client.get("/api/applications").json() == []


def test_cv_detail_lists_only_its_own_versions(tmp_path):
    model = ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE)
    client = _client(tmp_path, model)
    _register(client)
    first = _upload(client)
    second = _upload(client)
    created = client.post(
        "/api/applications",
        json={"cv_id": first, "role_title": "Programmer", "job_description": "Python and SQL required."},
        headers=_headers(_csrf(client)),
    )
    assert created.status_code == 201, created.text
    detail = client.get(f"/api/cvs/{first}").json()
    assert [item["role_title"] for item in detail["versions"]] == ["Programmer"]
    assert detail["versions"][0]["suitable"] is True
    assert client.get(f"/api/cvs/{second}").json()["versions"] == []
    listed = client.get("/api/cvs").json()
    assert "versions" not in listed[0]

    client.post("/api/logout", headers=_headers(_csrf(client)))
    _register(client, "other@example.com")
    assert client.get(f"/api/cvs/{first}").status_code == 404


def test_posting_without_required_skills_skips_screening(tmp_path):
    model = ScriptedModel({"required_skills": [], "preferred_skills": [], "min_years": 0, "seniority": ""})
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    response = client.post(
        "/api/applications",
        json={"cv_id": cv_id, "role_title": "Analyst", "job_description": "A general role."},
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["suitable"] is False
    assert body["result"]["kind"] == "gap"
    assert body["result"]["report"]["gaps"][0]["skill"] == "Required skills"
    assert body["result"]["report"]["gaps"][0]["severity"] == "major"
    assert SCREEN not in model.calls


def test_owner_can_delete_a_role_and_a_cv(tmp_path):
    model = ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE)
    client = _client(tmp_path, model)
    _register(client)
    cv_id = _upload(client)
    created = client.post(
        "/api/applications",
        json={"cv_id": cv_id, "role_title": "Programmer", "job_description": "Required: Python and SQL."},
        headers=_headers(_csrf(client)),
    )
    assert created.status_code == 201, created.text
    application_id = created.json()["id"]

    client.post("/api/logout", headers=_headers(_csrf(client)))
    _register(client, "other@example.com")
    denied_role = client.delete(f"/api/applications/{application_id}", headers=_headers(_csrf(client)))
    denied_cv = client.delete(f"/api/cvs/{cv_id}", headers=_headers(_csrf(client)))
    assert denied_role.status_code == 404
    assert denied_cv.status_code == 404

    client.post("/api/logout", headers=_headers(_csrf(client)))
    client.post(
        "/api/login",
        json={"email": "ada@example.com", "password": "correct-horse"},
        headers=_headers(_csrf(client)),
    )
    missing_token = client.delete(f"/api/applications/{application_id}")
    assert missing_token.status_code == 403
    assert client.get(f"/api/applications/{application_id}").status_code == 200

    removed_role = client.delete(f"/api/applications/{application_id}", headers=_headers(_csrf(client)))
    assert removed_role.status_code == 204
    assert client.get(f"/api/applications/{application_id}").status_code == 404
    assert client.get(f"/api/cvs/{cv_id}").status_code == 200

    again = client.post(
        "/api/applications",
        json={"cv_id": cv_id, "role_title": "Analyst", "job_description": "Required: Python and SQL."},
        headers=_headers(_csrf(client)),
    )
    assert again.status_code == 201, again.text
    removed_cv = client.delete(f"/api/cvs/{cv_id}", headers=_headers(_csrf(client)))
    assert removed_cv.status_code == 204
    assert client.get(f"/api/cvs/{cv_id}").status_code == 404
    assert client.get(f"/api/applications/{again.json()['id']}").status_code == 404
    assert client.get("/api/cvs").json() == []
    assert client.get("/api/applications").json() == []


def test_csrf_is_required(tmp_path):
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump()))
    response = client.post(
        "/api/register",
        json={"email": "ada@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 403


def test_profile_slug_uses_first_and_last_name():
    assert _name_slug("Ada Lovelace") == "ada-lovelace"
    assert _name_slug("Ada Augusta King Lovelace") == "ada-lovelace"
    assert _name_slug("Ada") == "ada"
    assert _name_slug("José García") == "jose-garcia"
    assert _name_slug("Mary-Jane O'Connor") == "mary-jane-o-connor"
    assert _name_slug("   ") == "profile"
    assert len(_name_slug("A" * 80 + " " + "B" * 80)) <= 47


def test_employer_profile_is_the_saved_cv_without_the_practice_plan(tmp_path):
    model = ScriptedModel(gap_job().model_dump(), gap=GAP, screen=None)
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / 'test.db'}",
        session_secret="test-secret",
        ollama_api_key="test-key",
        cookie_secure=False,
    )
    app = create_app(settings, model=model)
    owner = TestClient(app)
    guest = TestClient(app)
    _register(owner)
    cv_id = _upload(owner)
    created = owner.post(
        "/api/applications",
        json={
            "cv_id": cv_id,
            "role_title": "Platform engineer",
            "job_description": "Required: Kubernetes and Rust.",
        },
        headers=_headers(_csrf(owner)),
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["candidate_name"] == "Ada Lovelace"
    assert body["cv_id"] == cv_id
    assert "share_path" not in body
    application_id = body["id"]

    assert guest.get("/api/profiles/not-a-real-token").status_code == 404
    assert owner.post(f"/api/applications/{application_id}/profile").status_code == 403
    assert owner.get(f"/api/applications/{application_id}").json().get("share_path") is None

    published = owner.post(
        f"/api/applications/{application_id}/profile",
        headers=_headers(_csrf(owner)),
    )
    assert published.status_code == 200, published.text
    share_path = published.json()["share_path"]
    token = share_path.rsplit("/", 1)[-1]
    assert share_path.startswith("/profiles/ada-lovelace-")
    assert len(token.removeprefix("ada-lovelace-")) == 16
    assert all(ch in "0123456789abcdef" for ch in token.removeprefix("ada-lovelace-"))
    detail = owner.get(f"/api/applications/{application_id}").json()
    assert detail["candidate_name"] == "Ada Lovelace"
    assert detail["share_path"] == share_path
    versions = owner.get(f"/api/cvs/{cv_id}").json()["versions"]
    assert versions[0]["share_path"] == share_path

    public = guest.get(f"/api/profiles/{token}")
    assert public.status_code == 200, public.text
    snapshot = public.json()
    assert snapshot["name"] == "Ada Lovelace"
    assert snapshot["role_title"] == "Platform engineer"
    assert snapshot["document"]["summary"] == SAMPLE_PROFILE.summary
    assert snapshot["document"]["contact"]["email"] == "ada@example.com"
    assert "years_experience" not in snapshot["document"]
    assert "application_id" not in snapshot
    assert "skill_board" not in snapshot
    assert "Kubernetes" not in json.dumps(snapshot)
    assert guest.get(f"/api/applications/{application_id}").status_code == 401

    owned = owner.get(f"/api/profiles/{token}").json()
    assert owned["cv_id"] == cv_id
    assert owned["application_id"] == application_id

    owner.post("/api/logout", headers=_headers(_csrf(owner)))
    _register(owner, "other@example.com")
    assert owner.post(
        f"/api/applications/{application_id}/profile",
        headers=_headers(_csrf(owner)),
    ).status_code == 404
    assert guest.get(f"/api/profiles/{token}").status_code == 200

    owner.post("/api/logout", headers=_headers(_csrf(owner)))
    owner.post(
        "/api/login",
        json={"email": "ada@example.com", "password": "correct-horse"},
        headers=_headers(_csrf(owner)),
    )
    stopped = owner.delete(
        f"/api/applications/{application_id}/profile",
        headers=_headers(_csrf(owner)),
    )
    assert stopped.status_code == 204
    assert guest.get(f"/api/profiles/{token}").status_code == 404

    again = owner.post(
        f"/api/applications/{application_id}/profile",
        headers=_headers(_csrf(owner)),
    )
    assert again.status_code == 200, again.text
    new_token = again.json()["share_path"].rsplit("/", 1)[-1]
    assert new_token != token
    assert guest.get(f"/api/profiles/{token}").status_code == 404
    assert guest.get(f"/api/profiles/{new_token}").status_code == 200

    removed = owner.delete(
        f"/api/applications/{application_id}",
        headers=_headers(_csrf(owner)),
    )
    assert removed.status_code == 204
    assert guest.get(f"/api/profiles/{new_token}").status_code == 404
    assert owner.get(f"/api/cvs/{cv_id}").status_code == 200


def test_ready_profile_uses_the_fact_checked_cv(tmp_path):
    model = ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE)
    client = _client(tmp_path, model)
    guest = TestClient(client.app)
    _register(client)
    cv_id = _upload(client)
    created = client.post(
        "/api/applications",
        json={"cv_id": cv_id, "role_title": "Programmer", "job_description": "Required: Python and SQL."},
        headers=_headers(_csrf(client)),
    )
    assert created.status_code == 201, created.text
    published = client.post(
        f"/api/applications/{created.json()['id']}/profile",
        headers=_headers(_csrf(client)),
    )
    assert published.status_code == 200, published.text
    token = published.json()["share_path"].rsplit("/", 1)[-1]
    snapshot = guest.get(f"/api/profiles/{token}").json()
    assert snapshot["name"] == "Ada Lovelace"
    assert snapshot["role_title"] == "Programmer"
    assert snapshot["document"]["summary"] == REWRITE["summary"]
    assert snapshot["document"]["experience"][0]["employer"] == "Analytical Engines"
    assert "fit_score" not in snapshot
    removed = client.delete(f"/api/cvs/{cv_id}", headers=_headers(_csrf(client)))
    assert removed.status_code == 204
    assert guest.get(f"/api/profiles/{token}").status_code == 404


def test_company_logos_follow_cv_and_share_access(tmp_path):
    owner = _client(tmp_path, ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE))
    guest = TestClient(owner.app)
    _register(owner)
    cv_id = _upload(owner)
    logo = {'url': 'https://upload.wikimedia.org/acme.png', 'source': 'https://commons.wikimedia.org/wiki/File:Acme.svg'}

    class Logos:
        def lookup(self, employer):
            assert employer == 'Analytical Engines'
            return logo

    owner.app.state.logos = Logos()
    cv_url = f'/api/cvs/{cv_id}/logos/0'
    assert owner.get(cv_url).json() == logo
    assert guest.get(cv_url).status_code == 401
    assert owner.get(f'/api/cvs/{cv_id}/logos/-1').status_code == 404
    assert owner.get(f'/api/cvs/{cv_id}/logos/1').status_code == 404
    created = owner.post('/api/applications', json={'cv_id': cv_id, 'role_title': 'Programmer', 'job_description': 'Python and SQL required'}, headers=_headers(_csrf(owner)))
    assert created.status_code == 201
    app_id = created.json()['id']
    app_url = f'/api/applications/{app_id}/logos/0'
    assert owner.get(app_url).json() == logo
    assert guest.get(app_url).status_code == 401
    published = owner.post(f'/api/applications/{app_id}/profile', headers=_headers(_csrf(owner)))
    token = published.json()['share_path'].rsplit('/', 1)[-1]
    public_url = f'/api/profiles/{token}/logos/0'
    assert guest.get(public_url).json() == logo
    _register(guest, 'other@example.com')
    assert guest.get(cv_url).status_code == 404
    assert guest.get(app_url).status_code == 404
    owner.delete(f'/api/applications/{app_id}/profile', headers=_headers(_csrf(owner)))
    assert guest.get(public_url).status_code == 404


def test_preexisting_profiles_get_logos_without_reupload_or_republish(tmp_path):
    """Old records contain no logo metadata; resolve from their saved employers."""
    from copy import deepcopy

    from app.models import CV, ProfileShare
    from app.services.logos import CompanyLogos
    import httpx

    original = _client(tmp_path, ScriptedModel(suitable_job().model_dump(), rewrite=REWRITE))
    _register(original)
    cv_id = _upload(original)
    created = original.post(
        '/api/applications',
        json={'cv_id': cv_id, 'role_title': 'Programmer', 'job_description': 'Python and SQL required'},
        headers=_headers(_csrf(original)),
    )
    assert created.status_code == 201
    app_id = created.json()['id']
    published = original.post(f'/api/applications/{app_id}/profile', headers=_headers(_csrf(original)))
    token = published.json()['share_path'].rsplit('/', 1)[-1]
    with original.app.state.Session() as db:
        old_cv = deepcopy(db.get(CV, cv_id).profile_json)
        old_share = deepcopy(db.query(ProfileShare).filter_by(token=token).one().document_json)

    # A fresh app opens the existing database. No upload/publish/model call occurs.
    restarted = create_app(original.app.state.settings, model=ScriptedModel({}))

    def provider(request):
        action = request.url.params['action']
        if action == 'wbsearchentities':
            assert request.url.params['search'] == 'Analytical Engines'
            return httpx.Response(200, json={'search': [{'id': 'Q1', 'label': 'Analytical Engines'}]})
        if action == 'wbgetentities':
            return httpx.Response(200, json={'entities': {'Q1': {'claims': {
                'P856': [{'mainsnak': {'datavalue': {'value': 'https://example.com'}}}],
                'P154': [{'mainsnak': {'datavalue': {'value': 'Engines.svg'}}}],
            }}}})
        return httpx.Response(200, json={'query': {'pages': {'1': {'imageinfo': [{
            'thumburl': 'https://upload.wikimedia.org/engines.png',
            'descriptionurl': 'https://commons.wikimedia.org/wiki/File:Engines.svg',
        }]}}}})

    with httpx.Client(transport=httpx.MockTransport(provider)) as provider_client:
        restarted.state.logos = CompanyLogos(client=provider_client)
        guest = TestClient(restarted)
        logo = guest.get(f'/api/profiles/{token}/logos/0')
        assert logo.status_code == 200
        assert logo.json()['url'] == 'https://upload.wikimedia.org/engines.png'
        owner = TestClient(restarted)
        login = owner.post('/api/login', json={'email': 'ada@example.com', 'password': 'correct-horse'}, headers=_headers(_csrf(owner)))
        assert login.status_code == 200
        assert owner.get(f'/api/cvs/{cv_id}/logos/0').json() == logo.json()
        assert owner.get(f'/api/applications/{app_id}/logos/0').json() == logo.json()
        assert guest.get(f'/api/profiles/{token}').json()['document'] == old_share
        assert owner.get(f'/api/cvs/{cv_id}').json()['profile'] == old_cv
        assert restarted.state.model.calls == []
