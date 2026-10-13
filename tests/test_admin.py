import io

from docx import Document
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.services.prompts import EXTRACT_RESUME
from tests.samples import SAMPLE_PROFILE
from tests.test_api import ScriptedModel, _csrf, _headers, suitable_job


def _docx() -> bytes:
    buffer = io.BytesIO()
    document = Document()
    document.add_paragraph(
        "Ada Lovelace built analytical engines and wrote notes on the analytical engine."
    )
    document.save(buffer)
    return buffer.getvalue()


class ExtractOnly(ScriptedModel):
    def complete(self, system: str, user: str) -> str:
        if system == EXTRACT_RESUME:
            return SAMPLE_PROFILE.model_dump_json()
        raise AssertionError(system)


def _app(tmp_path, name: str, admin_emails: frozenset[str]):
    settings = Settings(
        database_url=f"sqlite:///{tmp_path / name}",
        session_secret="test-secret",
        ollama_api_key="test-key",
        cookie_secure=False,
        admin_emails=admin_emails,
    )
    return create_app(settings, model=ExtractOnly(suitable_job().model_dump()))


def _register(client: TestClient, email: str, password: str = "correct-horse") -> dict:
    response = client.post(
        "/api/register",
        json={"email": email, "password": password},
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _login(client: TestClient, email: str, password: str = "correct-horse") -> dict:
    response = client.post(
        "/api/login",
        json={"email": email, "password": password},
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 200, response.text
    return response.json()


def _upload(client: TestClient) -> int:
    response = client.post(
        "/api/cvs",
        files={
            "file": (
                "ada.docx",
                _docx(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        headers=_headers(_csrf(client)),
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_non_admin_cannot_list_users(tmp_path):
    client = TestClient(_app(tmp_path, "nope.db", frozenset()))
    _register(client, "ada@example.com")
    assert client.get("/api/admin/users").status_code == 403


def test_admin_emails_promotes_on_login_and_session_includes_flag(tmp_path):
    app = _app(tmp_path, "promote.db", frozenset({"admin@example.com"}))
    member = TestClient(app)
    admin = TestClient(app)

    plain = _register(member, "plain@example.com")
    assert plain["is_admin"] is False
    session = member.get("/api/session").json()
    assert session["user"]["is_admin"] is False
    assert session["impersonating"] is None

    created = _register(admin, "admin@example.com")
    assert created["is_admin"] is True
    logged = _login(admin, "admin@example.com")
    assert logged["is_admin"] is True
    session = admin.get("/api/session").json()
    assert session["user"] == {
        "id": logged["id"],
        "email": "admin@example.com",
        "is_admin": True,
    }
    assert session["impersonating"] is None


def test_admin_lists_users_and_can_patch_other_cv(tmp_path):
    app = _app(tmp_path, "ops.db", frozenset({"admin@example.com"}))
    member = TestClient(app)
    admin = TestClient(app)

    _register(member, "ada@example.com")
    cv_id = _upload(member)
    _register(admin, "admin@example.com")

    users = admin.get("/api/admin/users").json()
    assert {row["email"] for row in users} == {"ada@example.com", "admin@example.com"}
    ada = next(row for row in users if row["email"] == "ada@example.com")
    assert ada["cv_count"] == 1
    assert ada["application_count"] == 0

    detail = admin.get(f"/api/admin/users/{ada['id']}").json()
    assert detail["cvs"][0]["id"] == cv_id

    cv = admin.get(f"/api/admin/cvs/{cv_id}").json()
    assert cv["user_id"] == ada["id"]
    profile = dict(cv["profile_json"])
    profile["summary"] = "Corrected by admin."
    patched = admin.patch(
        f"/api/admin/cvs/{cv_id}",
        json={"label": "Ada CV", "profile_json": profile},
        headers=_headers(_csrf(admin)),
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["label"] == "Ada CV"
    assert patched.json()["profile_json"]["summary"] == "Corrected by admin."


def test_impersonation_switches_owned_cvs_and_stop_restores_admin(tmp_path):
    app = _app(tmp_path, "view.db", frozenset({"admin@example.com"}))
    member = TestClient(app)
    admin = TestClient(app)

    _register(member, "ada@example.com")
    cv_id = _upload(member)
    ada_id = member.get("/api/session").json()["user"]["id"]

    _register(admin, "admin@example.com")
    assert admin.get("/api/cvs").json() == []

    started = admin.post(
        f"/api/admin/impersonate/{ada_id}",
        headers=_headers(_csrf(admin)),
    )
    assert started.status_code == 200, started.text
    assert started.json()["impersonating"]["email"] == "ada@example.com"
    session = admin.get("/api/session").json()
    assert session["user"]["email"] == "ada@example.com"
    assert session["impersonating"]["email"] == "ada@example.com"
    assert [row["id"] for row in admin.get("/api/cvs").json()] == [cv_id]

    stopped = admin.post("/api/admin/stop-impersonation", headers=_headers(_csrf(admin)))
    assert stopped.status_code == 200, stopped.text
    assert stopped.json()["user"]["email"] == "admin@example.com"
    assert stopped.json()["impersonating"] is None
    assert admin.get("/api/cvs").json() == []
    assert admin.get("/api/session").json()["impersonating"] is None


def test_cannot_impersonate_another_admin(tmp_path):
    app = _app(tmp_path, "admins.db", frozenset({"one@example.com", "two@example.com"}))
    one = TestClient(app)
    two = TestClient(app)
    _register(one, "one@example.com")
    _register(two, "two@example.com")
    two_id = two.get("/api/session").json()["user"]["id"]
    denied = one.post(
        f"/api/admin/impersonate/{two_id}",
        headers=_headers(_csrf(one)),
    )
    assert denied.status_code == 400


def test_admin_can_patch_and_delete_another_users_application(tmp_path):
    from app.database import make_engine, make_session_factory
    from app.models import Application

    app = _app(tmp_path, "apps.db", frozenset({"admin@example.com"}))
    member = TestClient(app)
    admin = TestClient(app)
    _register(member, "ada@example.com")
    cv_id = _upload(member)
    ada_id = member.get("/api/session").json()["user"]["id"]

    engine = make_engine(f"sqlite:///{tmp_path / 'apps.db'}")
    db = make_session_factory(engine)()
    row = Application(
        user_id=ada_id,
        cv_id=cv_id,
        role_title="Engineer",
        job_description="Build things with Python and care.",
        fit_score=40,
        suitable=False,
        skill_board_json={
            "score": 40,
            "coverage": 0.5,
            "suitable": False,
            "required": [{"name": "Python", "present": True, "quote": "x", "source": "work"}],
            "preferred": [],
            "matched_preferred": [],
        },
        result_json={
            "kind": "gap",
            "report": {
                "summary": "Missing practice.",
                "gaps": [
                    {
                        "skill": "Rust",
                        "severity": "major",
                        "why_it_matters": "Role uses it.",
                        "practice": "Write a tool.",
                        "project": "Describe it.",
                    }
                ],
            },
        },
    )
    db.add(row)
    db.commit()
    application_id = row.id
    db.close()

    _register(admin, "admin@example.com")
    detail = admin.get(f"/api/admin/applications/{application_id}").json()
    assert detail["role_title"] == "Engineer"
    patched = admin.patch(
        f"/api/admin/applications/{application_id}",
        json={"role_title": "Staff Engineer", "fit_score": 55},
        headers=_headers(_csrf(admin)),
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["role_title"] == "Staff Engineer"
    assert patched.json()["fit_score"] == 55

    removed = admin.delete(
        f"/api/admin/applications/{application_id}",
        headers=_headers(_csrf(admin)),
    )
    assert removed.status_code == 204
    assert admin.get(f"/api/admin/applications/{application_id}").status_code == 404

    cv_removed = admin.delete(f"/api/admin/cvs/{cv_id}", headers=_headers(_csrf(admin)))
    assert cv_removed.status_code == 204
    assert admin.get(f"/api/admin/cvs/{cv_id}").status_code == 404
