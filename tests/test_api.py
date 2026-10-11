import io
import json

from docx import Document
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
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


def test_csrf_is_required(tmp_path):
    client = _client(tmp_path, ScriptedModel(suitable_job().model_dump()))
    response = client.post(
        "/api/register",
        json={"email": "ada@example.com", "password": "correct-horse"},
    )
    assert response.status_code == 403
