import re
import secrets
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app import __version__
from app.auth import (
    check_password,
    csrf_token,
    current_user,
    hash_password,
    label_from_filename,
    normalize_email,
    require_csrf,
    require_user,
    user_by_email,
    verify_password,
)
from app.config import MAX_JOB_CHARS, Settings, ensure_sqlite_parent, load_settings
from app.database import Base, make_engine, make_session_factory
from app.models import Application, CV, CvPhoto, ProfileShare, User, utcnow
from app.schemas import CvDocument, GapReport, Profile
from app.services.llm import ModelError, OllamaCloudClient
from app.services.logos import CompanyLogos
from app.services.parser import UploadError, extract_text
from app.services.pdf import render_pdf
from app.services.photos import MAX_PHOTO_BYTES, PhotoError, github_avatar, github_handle, square_jpeg
from app.services.pipeline import analyze_role, build_profile

DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
PRESENTATION = Path(__file__).resolve().parent.parent / "presentation"


class Credentials(BaseModel):
    email: str
    password: str


class ApplyBody(BaseModel):
    cv_id: int
    role_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=1)


def create_app(settings: Settings | None = None, model=None) -> FastAPI:
    settings = settings or load_settings()
    ensure_sqlite_parent(settings.database_url)
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
    session_factory = make_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(engine)
        yield

    app = FastAPI(title="Job Ready", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.Session = session_factory
    app.state.model = model
    app.state.logos = CompanyLogos()

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.session_secret,
        session_cookie="gg_session",
        max_age=60 * 60 * 24 * 14,
        same_site="lax",
        https_only=settings.cookie_secure,
    )

    def get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    def model_client():
        if app.state.model is not None:
            return app.state.model
        if not settings.ollama_api_key:
            raise HTTPException(
                status_code=503,
                detail="Add OLLAMA_API_KEY before checking a role.",
            )
        return OllamaCloudClient(
            api_key=settings.ollama_api_key,
            model=settings.ollama_model,
            host=settings.ollama_host,
        )

    def owned_cv(db: Session, user: User, cv_id: int) -> CV:
        cv = db.get(CV, cv_id)
        if cv is None or cv.user_id != user.id:
            raise HTTPException(status_code=404, detail="That CV was not found.")
        return cv

    def owned_application(db: Session, user: User, application_id: int) -> Application:
        row = db.get(Application, application_id)
        if row is None or row.user_id != user.id:
            raise HTTPException(status_code=404, detail="That check was not found.")
        return row

    @app.get("/health")
    def health():
        return {"ok": True, "version": __version__}

    @app.get("/api/session")
    def session(request: Request, db: Session = Depends(get_db)):
        user = current_user(request, db)
        return {
            "csrf": csrf_token(request),
            "user": None if user is None else {"id": user.id, "email": user.email},
        }

    @app.post("/api/register", status_code=201)
    def register(body: Credentials, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        email = normalize_email(body.email)
        password = check_password(body.password)
        if user_by_email(db, email) is not None:
            raise HTTPException(status_code=409, detail="That email is already registered.")
        user = User(email=email, password_hash=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
        request.session["user_id"] = user.id
        return {"id": user.id, "email": user.email}

    @app.post("/api/login")
    def login(body: Credentials, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        email = normalize_email(body.email)
        user = user_by_email(db, email)
        if user is None or not verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Email or password does not match.")
        request.session["user_id"] = user.id
        return {"id": user.id, "email": user.email}

    @app.post("/api/logout")
    def logout(request: Request):
        require_csrf(request)
        request.session.clear()
        csrf_token(request)
        return {"ok": True}

    @app.get("/api/cvs")
    def list_cvs(request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        rows = (
            db.query(CV)
            .filter(CV.user_id == user.id)
            .order_by(CV.created_at.desc())
            .all()
        )
        return [_cv_summary(row) for row in rows]

    @app.post("/api/cvs", status_code=201)
    async def upload_cv(
        request: Request,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
    ):
        require_csrf(request)
        user = require_user(request, db)
        data = await _read_upload(file, settings.max_upload_bytes, "This file is larger than 5 MB.")
        try:
            text = extract_text(file.filename or "", data, settings.max_upload_bytes)
            profile = build_profile(model_client(), text)
        except UploadError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ModelError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        if not profile.contact.name:
            profile.contact.name = label_from_filename(file.filename or "CV")
        row = CV(
            user_id=user.id,
            label=label_from_filename(file.filename or "CV"),
            source_filename=(file.filename or "cv")[:255],
            extracted_text=text,
            profile_json=profile.model_dump(),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _cv_detail(row)

    @app.get("/api/cvs/{cv_id}")
    def get_cv(cv_id: int, request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        return _cv_detail(owned_cv(db, user, cv_id))

    @app.delete("/api/cvs/{cv_id}", status_code=204)
    def delete_cv(cv_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        cv = owned_cv(db, user, cv_id)
        for row in list(cv.applications):
            db.delete(row)
        db.delete(cv)
        db.commit()
        return Response(status_code=204)

    def set_photo(db: Session, cv: CV, source: str, data: bytes | None = None) -> None:
        if cv.photo is None:
            cv.photo = CvPhoto(source=source, data=data)
        else:
            cv.photo.source = source
            cv.photo.data = data
            cv.photo.updated_at = utcnow()
        db.commit()
        db.refresh(cv)

    @app.post("/api/cvs/{cv_id}/photo")
    async def upload_photo(
        cv_id: int,
        request: Request,
        file: UploadFile = File(...),
        db: Session = Depends(get_db),
    ):
        require_csrf(request)
        user = require_user(request, db)
        cv = owned_cv(db, user, cv_id)
        data = await _read_upload(file, MAX_PHOTO_BYTES, "This photo is larger than 3 MB.")
        try:
            jpeg = square_jpeg(data)
        except PhotoError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        set_photo(db, cv, "upload", jpeg)
        return {"photo": _photo(cv, cv.profile_json, f"/api/cvs/{cv.id}/photo")}

    @app.post("/api/cvs/{cv_id}/photo/github")
    def use_github_photo(cv_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        cv = owned_cv(db, user, cv_id)
        if not _github_for(cv.profile_json):
            raise HTTPException(status_code=400, detail="This CV has no GitHub link to take a photo from.")
        set_photo(db, cv, "github")
        return {"photo": _photo(cv, cv.profile_json, f"/api/cvs/{cv.id}/photo")}

    @app.delete("/api/cvs/{cv_id}/photo", status_code=204)
    def remove_photo(cv_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        set_photo(db, owned_cv(db, user, cv_id), "none")
        return Response(status_code=204)

    @app.get("/api/cvs/{cv_id}/photo")
    def cv_photo(cv_id: int, request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        return _photo_bytes(owned_cv(db, user, cv_id))

    @app.get("/api/applications")
    def list_applications(request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        rows = (
            db.query(Application)
            .filter(Application.user_id == user.id)
            .order_by(Application.created_at.desc())
            .all()
        )
        return [_application_summary(row) for row in rows]

    @app.post("/api/applications", status_code=201)
    def create_application(body: ApplyBody, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        role = body.role_title.strip()
        description = body.job_description.strip()
        if not role:
            raise HTTPException(status_code=400, detail="Enter the role title.")
        if not description:
            raise HTTPException(status_code=400, detail="Paste the job description.")
        if len(description) > MAX_JOB_CHARS:
            raise HTTPException(status_code=400, detail="That job description is too long. Shorten it and try again.")
        cv = owned_cv(db, user, body.cv_id)
        profile = Profile.model_validate(cv.profile_json)
        try:
            fit, result = analyze_role(model_client(), profile, role, description)
        except ModelError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        if isinstance(result, CvDocument):
            payload = {"kind": "cv", "document": result.model_dump()}
        elif isinstance(result, GapReport):
            payload = {"kind": "gap", "report": result.model_dump()}
        else:
            raise HTTPException(status_code=500, detail="The check did not finish.")
        row = Application(
            user_id=user.id,
            cv_id=cv.id,
            role_title=role,
            job_description=description,
            fit_score=fit.score,
            suitable=fit.suitable,
            skill_board_json=fit.model_dump(),
            result_json=payload,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _application_detail(row)

    @app.get("/api/applications/{application_id}")
    def get_application(application_id: int, request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        return _application_detail(owned_application(db, user, application_id))

    @app.delete("/api/applications/{application_id}", status_code=204)
    def delete_application(application_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        row = owned_application(db, user, application_id)
        db.delete(row)
        db.commit()
        return Response(status_code=204)

    @app.get("/api/applications/{application_id}/pdf")
    def application_pdf(application_id: int, request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        row = owned_application(db, user, application_id)
        if not row.suitable or row.result_json.get("kind") != "cv":
            raise HTTPException(status_code=404, detail="A PDF is available when the CV is ready to send.")
        document = CvDocument.model_validate(row.result_json["document"])
        try:
            pdf = render_pdf(document)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        filename = _pdf_filename(row.role_title)
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.post("/api/applications/{application_id}/profile")
    def publish_profile(application_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        row = owned_application(db, user, application_id)
        share = _publish_profile(db, row)
        return {"share_path": f"/profiles/{share.token}"}

    @app.delete("/api/applications/{application_id}/profile", status_code=204)
    def unpublish_profile(application_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        user = require_user(request, db)
        row = owned_application(db, user, application_id)
        if row.share is not None:
            row.share = None
            db.commit()
        return Response(status_code=204)

    @app.get("/api/profiles/{token}")
    def public_profile(token: str, request: Request, db: Session = Depends(get_db)):
        share = db.query(ProfileShare).filter(ProfileShare.token == token).one_or_none()
        if share is None:
            raise HTTPException(status_code=404, detail="That profile was not found.")
        document = share.document_json or {}
        contact = document.get("contact") or {}
        body = {
            "name": contact.get("name") or "Candidate",
            "role_title": share.role_title,
            "document": document,
            "photo": None,
        }
        if share.application is not None:
            body["photo"] = _photo(share.application.cv, document, f"/api/profiles/{token}/photo")
        user = current_user(request, db)
        if user is not None and share.application is not None and share.application.user_id == user.id:
            body["cv_id"] = share.application.cv_id
            body["application_id"] = share.application.id
        return body

    def company_logo(document: dict, index: int):
        roles = document.get("experience") or []
        if index < 0 or index >= len(roles):
            raise HTTPException(status_code=404, detail="That employer was not found.")
        logo = app.state.logos.lookup(roles[index].get("employer") or "")
        return JSONResponse(logo or {"url": None, "source": None}, headers={"Cache-Control": "private, no-store"})

    @app.get("/api/cvs/{cv_id}/logos/{index}")
    def cv_logo(cv_id: int, index: int, request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        return company_logo(owned_cv(db, user, cv_id).profile_json, index)

    @app.get("/api/applications/{application_id}/logos/{index}")
    def application_logo(application_id: int, index: int, request: Request, db: Session = Depends(get_db)):
        user = require_user(request, db)
        row = owned_application(db, user, application_id)
        return company_logo(_employer_document(row), index)

    @app.get("/api/profiles/{token}/logos/{index}")
    def profile_logo(token: str, index: int, db: Session = Depends(get_db)):
        share = db.query(ProfileShare).filter(ProfileShare.token == token).one_or_none()
        if share is None:
            raise HTTPException(status_code=404, detail="That profile was not found.")
        return company_logo(share.document_json or {}, index)

    @app.get("/api/profiles/{token}/photo")
    def profile_photo(token: str, db: Session = Depends(get_db)):
        share = db.query(ProfileShare).filter(ProfileShare.token == token).one_or_none()
        if share is None or share.application is None:
            raise HTTPException(status_code=404, detail="That profile was not found.")
        return _photo_bytes(share.application.cv)

    @app.get("/presentation")
    def presentation_root():
        return RedirectResponse("/presentation/", status_code=307)

    @app.get("/presentation/{file_path:path}")
    def presentation_file(file_path: str = ""):
        if not file_path:
            index = PRESENTATION / "index.html"
            if index.is_file():
                return FileResponse(index)
        candidate = (PRESENTATION / file_path).resolve()
        if PRESENTATION.resolve() in candidate.parents and candidate.is_file():
            return FileResponse(candidate)
        if candidate.is_dir() and (candidate / "index.html").is_file():
            return FileResponse(candidate / "index.html")
        index = PRESENTATION / "index.html"
        if index.is_file():
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Presentation file not found.")

    @app.get("/")
    @app.get("/{full_path:path}")
    def spa(full_path: str = ""):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not found.")
        if full_path:
            candidate = (DIST / full_path).resolve()
            if DIST.resolve() in candidate.parents and candidate.is_file():
                return FileResponse(candidate)
        index = DIST / "index.html"
        if index.is_file():
            return FileResponse(index)
        return JSONResponse(
            {"detail": "The Svelte app is not built yet. From frontend/, run npm install and npm run build."},
            status_code=503,
        )

    return app


def _candidate_name(row: Application) -> str:
    contact = (row.cv.profile_json or {}).get("contact") or {}
    return contact.get("name") or row.cv.label


def _employer_document(row: Application) -> dict:
    """Facts an employer can read. A gap result keeps the saved profile, not a rewrite."""
    raw = row.cv.profile_json or {}
    if row.suitable and (row.result_json or {}).get("kind") == "cv":
        raw = row.result_json.get("document") or raw
    profile = Profile.model_validate(raw)
    return CvDocument(
        contact=profile.contact,
        summary=profile.summary,
        skills=profile.skills,
        experience=profile.experience,
        education=profile.education,
    ).model_dump()


def _publish_profile(db: Session, row: Application) -> ProfileShare:
    if row.share is not None:
        row.share = None
        db.flush()
    document = _employer_document(row)
    share = ProfileShare(
        application_id=row.id,
        token=_fresh_profile_token(db, (document.get("contact") or {}).get("name") or ""),
        role_title=row.role_title,
        document_json=document,
    )
    row.share = share
    db.commit()
    db.refresh(row)
    return row.share


def _cv_summary(row: CV) -> dict:
    profile = row.profile_json or {}
    contact = profile.get("contact") or {}
    return {
        "id": row.id,
        "label": row.label,
        "name": contact.get("name") or row.label,
        "created_at": row.created_at.isoformat(),
    }


def _cv_detail(row: CV) -> dict:
    versions = sorted(row.applications, key=lambda item: item.created_at, reverse=True)
    return {
        **_cv_summary(row),
        "profile": row.profile_json,
        "photo": _photo(row, row.profile_json, f"/api/cvs/{row.id}/photo"),
        "github": _github_for(row.profile_json) or None,
        "versions": [_version_summary(item) for item in versions],
    }


def _github_for(document: dict | None) -> str:
    contact = (document or {}).get("contact") or {}
    return github_handle(contact.get("links"))


def _photo(cv: CV, document: dict | None, upload_url: str) -> dict | None:
    """Which photo an employer sees. With no choice saved, a GitHub link on the CV supplies one."""
    choice = cv.photo.source if cv.photo is not None else "github"
    if choice == "upload" and cv.photo is not None and cv.photo.data:
        version = int(cv.photo.updated_at.timestamp())
        return {"url": f"{upload_url}?v={version}", "source": "upload"}
    if choice == "github":
        handle = _github_for(document)
        if handle:
            return {"url": github_avatar(handle), "source": "github"}
    return None


def _photo_bytes(cv: CV) -> Response:
    if cv.photo is None or cv.photo.source != "upload" or not cv.photo.data:
        raise HTTPException(status_code=404, detail="No photo was uploaded for this CV.")
    return Response(
        content=cv.photo.data,
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=300"},
    )


def _application_summary(row: Application) -> dict:
    return {
        "id": row.id,
        "cv_id": row.cv_id,
        "role_title": row.role_title,
        "fit_score": row.fit_score,
        "suitable": row.suitable,
        "created_at": row.created_at.isoformat(),
    }


def _version_summary(row: Application) -> dict:
    summary = _application_summary(row)
    if row.share is not None:
        summary["share_path"] = f"/profiles/{row.share.token}"
    return summary


def _application_detail(row: Application) -> dict:
    return {
        **_version_summary(row),
        "candidate_name": _candidate_name(row),
        "skill_board": row.skill_board_json,
        "result": row.result_json,
    }


async def _read_upload(file: UploadFile, max_bytes: int, too_large: str) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        size += len(chunk)
        if size > max_bytes:
            raise HTTPException(status_code=400, detail=too_large)
        chunks.append(chunk)
    return b"".join(chunks)


def _name_slug(name: str) -> str:
    """First and last name, ASCII, for a public profile path."""
    folded = unicodedata.normalize("NFKD", name or "")
    ascii_name = folded.encode("ascii", "ignore").decode("ascii")
    parts = [part for part in re.split(r"\s+", ascii_name.strip()) if part]
    if len(parts) >= 2:
        chosen = f"{parts[0]} {parts[-1]}"
    elif parts:
        chosen = parts[0]
    else:
        chosen = "profile"
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in chosen)
    slug = "-".join(part for part in slug.split("-") if part) or "profile"
    return slug[:47].strip("-") or "profile"


def _profile_token(name: str) -> str:
    return f"{_name_slug(name)}-{secrets.token_hex(8)}"


def _fresh_profile_token(db: Session, name: str) -> str:
    for _ in range(5):
        token = _profile_token(name)
        taken = db.query(ProfileShare.id).filter(ProfileShare.token == token).first()
        if taken is None:
            return token
    raise RuntimeError("Could not allocate a profile link.")


def _pdf_filename(role_title: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in role_title).strip("-")
    slug = "-".join(part for part in slug.split("-") if part) or "cv"
    return f"{slug}.pdf"


app = create_app()
