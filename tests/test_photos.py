import io

from fastapi.testclient import TestClient
from PIL import Image

from app.services.photos import PhotoError, github_handle, square_jpeg
from tests.samples import SAMPLE_PROFILE, gap_job
from tests.test_api import GAP, ScriptedModel, _client, _csrf, _headers, _register, _upload


def _png(width: int = 300, height: int = 200, mode: str = "RGBA") -> bytes:
    buffer = io.BytesIO()
    Image.new(mode, (width, height), (20, 120, 80, 200) if mode == "RGBA" else (20, 120, 80)).save(buffer, format="PNG")
    return buffer.getvalue()


def _with_github(model: ScriptedModel, link: str = "https://github.com/ada-l") -> ScriptedModel:
    profile = SAMPLE_PROFILE.model_copy(deep=True)
    profile.contact.links = ["linkedin.com/in/ada", link]
    original = model.complete

    def complete(system: str, user: str) -> str:
        from app.services.prompts import EXTRACT_RESUME

        if system == EXTRACT_RESUME:
            model.calls.append(system)
            return profile.model_dump_json()
        return original(system, user)

    model.complete = complete
    return model


def _share(client: TestClient, cv_id: int) -> str:
    created = client.post(
        "/api/applications",
        json={"cv_id": cv_id, "role_title": "Platform engineer", "job_description": "Required: Kubernetes and Rust."},
        headers=_headers(_csrf(client)),
    )
    assert created.status_code == 201, created.text
    published = client.post(f"/api/applications/{created.json()['id']}/profile", headers=_headers(_csrf(client)))
    return published.json()["share_path"].rsplit("/", 1)[-1]


def test_square_jpeg_crops_and_strips_the_original():
    out = Image.open(io.BytesIO(square_jpeg(_png())))
    assert out.format == "JPEG"
    assert out.size == (640, 640)


def test_square_jpeg_rejects_non_images_and_tiny_images():
    for data in (b"not an image", b"%PDF-1.4 fake", _png(40, 40)):
        try:
            square_jpeg(data)
        except PhotoError:
            continue
        raise AssertionError("expected PhotoError")


def test_github_handle_reads_profile_links_only():
    assert github_handle(["linkedin.com/in/ada", "github.com/androizer"]) == "androizer"
    assert github_handle(["https://www.github.com/Ada-L/"]) == "Ada-L"
    assert github_handle(["github.com/ada/repo", "github.com/orgs", "gist.github.com/ada"]) == ""


def test_github_photo_is_the_default_and_can_be_removed(tmp_path):
    client = _client(tmp_path, _with_github(ScriptedModel(gap_job().model_dump(), gap=GAP, screen=None)))
    guest = TestClient(client.app)
    _register(client)
    cv_id = _upload(client)
    detail = client.get(f"/api/cvs/{cv_id}").json()
    assert detail["github"] == "ada-l"
    assert detail["photo"] == {"url": "https://github.com/ada-l.png?size=640", "source": "github"}

    token = _share(client, cv_id)
    assert guest.get(f"/api/profiles/{token}").json()["photo"]["source"] == "github"

    removed = client.delete(f"/api/cvs/{cv_id}/photo", headers=_headers(_csrf(client)))
    assert removed.status_code == 204
    assert client.get(f"/api/cvs/{cv_id}").json()["photo"] is None
    assert guest.get(f"/api/profiles/{token}").json()["photo"] is None

    restored = client.post(f"/api/cvs/{cv_id}/photo/github", headers=_headers(_csrf(client)))
    assert restored.json()["photo"]["source"] == "github"


def test_uploaded_photo_is_owner_only_until_shared(tmp_path):
    client = _client(tmp_path, ScriptedModel(gap_job().model_dump(), gap=GAP, screen=None))
    guest = TestClient(client.app)
    _register(client)
    cv_id = _upload(client)
    assert client.get(f"/api/cvs/{cv_id}").json()["photo"] is None
    assert client.post(f"/api/cvs/{cv_id}/photo/github", headers=_headers(_csrf(client))).status_code == 400

    files = {"file": ("me.png", _png(), "image/png")}
    assert client.post(f"/api/cvs/{cv_id}/photo", files=files).status_code == 403
    bad = client.post(
        f"/api/cvs/{cv_id}/photo",
        files={"file": ("me.png", b"nope", "image/png")},
        headers=_headers(_csrf(client)),
    )
    assert bad.status_code == 400
    uploaded = client.post(f"/api/cvs/{cv_id}/photo", files=files, headers=_headers(_csrf(client)))
    assert uploaded.status_code == 200, uploaded.text
    photo = uploaded.json()["photo"]
    assert photo["source"] == "upload"
    assert photo["url"].startswith(f"/api/cvs/{cv_id}/photo?v=")
    own = client.get(f"/api/cvs/{cv_id}/photo")
    assert own.status_code == 200
    assert own.headers["content-type"] == "image/jpeg"
    assert guest.get(f"/api/cvs/{cv_id}/photo").status_code == 401

    token = _share(client, cv_id)
    public = guest.get(f"/api/profiles/{token}").json()["photo"]
    assert public["url"].startswith(f"/api/profiles/{token}/photo?v=")
    assert guest.get(f"/api/profiles/{token}/photo").content == own.content

    client.post("/api/logout", headers=_headers(_csrf(client)))
    _register(client, "other@example.com")
    assert client.get(f"/api/cvs/{cv_id}/photo").status_code == 404
    assert client.post(f"/api/cvs/{cv_id}/photo", files=files, headers=_headers(_csrf(client))).status_code == 404


def test_deleting_the_cv_deletes_its_photo(tmp_path):
    client = _client(tmp_path, ScriptedModel(gap_job().model_dump(), gap=GAP, screen=None))
    _register(client)
    cv_id = _upload(client)
    client.post(
        f"/api/cvs/{cv_id}/photo",
        files={"file": ("me.png", _png(), "image/png")},
        headers=_headers(_csrf(client)),
    )
    assert client.delete(f"/api/cvs/{cv_id}", headers=_headers(_csrf(client))).status_code == 204
    from app.models import CvPhoto

    with client.app.state.Session() as db:
        assert db.query(CvPhoto).count() == 0
