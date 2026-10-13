from fastapi import Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import require_admin, require_csrf, user_payload
from app.config import MAX_CV_CHARS, MAX_JOB_CHARS
from app.models import Application, CV, User
from app.schemas import CvDocument, FitResult, GapReport, Profile


class AdminCvPatch(BaseModel):
    label: str | None = None
    profile_json: dict | None = None
    extracted_text: str | None = None


class AdminApplicationPatch(BaseModel):
    role_title: str | None = None
    job_description: str | None = None
    fit_score: int | None = None
    suitable: bool | None = None
    skill_board_json: dict | None = None
    result_json: dict | None = None


def register_admin_routes(app, get_db) -> None:
    @app.get("/api/admin/users")
    def list_users(request: Request, db: Session = Depends(get_db)):
        require_admin(request, db)
        cv_counts = dict(
            db.execute(select(CV.user_id, func.count()).group_by(CV.user_id)).all()
        )
        app_counts = dict(
            db.execute(select(Application.user_id, func.count()).group_by(Application.user_id)).all()
        )
        rows = db.scalars(select(User).order_by(User.created_at.desc())).all()
        return [
            {
                **user_payload(user),
                "created_at": user.created_at.isoformat(),
                "cv_count": int(cv_counts.get(user.id, 0)),
                "application_count": int(app_counts.get(user.id, 0)),
            }
            for user in rows
        ]

    @app.get("/api/admin/users/{user_id}")
    def get_user(user_id: int, request: Request, db: Session = Depends(get_db)):
        require_admin(request, db)
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="That user was not found.")
        cvs = (
            db.query(CV)
            .filter(CV.user_id == user.id)
            .order_by(CV.created_at.desc())
            .all()
        )
        applications = (
            db.query(Application)
            .filter(Application.user_id == user.id)
            .order_by(Application.created_at.desc())
            .all()
        )
        return {
            **user_payload(user),
            "created_at": user.created_at.isoformat(),
            "cvs": [_admin_cv_summary(row) for row in cvs],
            "applications": [_admin_application_summary(row) for row in applications],
        }

    @app.get("/api/admin/cvs/{cv_id}")
    def get_cv(cv_id: int, request: Request, db: Session = Depends(get_db)):
        require_admin(request, db)
        cv = _admin_cv(db, cv_id)
        return {
            **_admin_cv_summary(cv),
            "source_filename": cv.source_filename,
            "extracted_text": cv.extracted_text,
            "profile_json": cv.profile_json,
            "photo_source": cv.photo.source if cv.photo is not None else None,
        }

    @app.patch("/api/admin/cvs/{cv_id}")
    def patch_cv(cv_id: int, body: AdminCvPatch, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        require_admin(request, db)
        cv = _admin_cv(db, cv_id)
        if body.label is not None:
            label = body.label.strip()
            if not label:
                raise HTTPException(status_code=400, detail="Enter a CV label.")
            cv.label = label[:200]
        if body.extracted_text is not None:
            text = body.extracted_text.strip()
            if len(text) < 40:
                raise HTTPException(status_code=400, detail="Extracted text must be at least 40 characters.")
            if len(text) > MAX_CV_CHARS:
                raise HTTPException(status_code=400, detail="Extracted text is too long.")
            cv.extracted_text = text
        if body.profile_json is not None:
            try:
                profile = Profile.model_validate(body.profile_json)
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail="That profile JSON is not valid.") from exc
            cv.profile_json = profile.model_dump()
        db.commit()
        db.refresh(cv)
        return {
            **_admin_cv_summary(cv),
            "source_filename": cv.source_filename,
            "extracted_text": cv.extracted_text,
            "profile_json": cv.profile_json,
            "photo_source": cv.photo.source if cv.photo is not None else None,
        }

    @app.delete("/api/admin/cvs/{cv_id}", status_code=204)
    def delete_cv(cv_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        require_admin(request, db)
        cv = _admin_cv(db, cv_id)
        for row in list(cv.applications):
            db.delete(row)
        db.delete(cv)
        db.commit()
        return Response(status_code=204)

    @app.get("/api/admin/applications/{application_id}")
    def get_application(application_id: int, request: Request, db: Session = Depends(get_db)):
        require_admin(request, db)
        row = _admin_application(db, application_id)
        return {
            **_admin_application_summary(row),
            "job_description": row.job_description,
            "skill_board_json": row.skill_board_json,
            "result_json": row.result_json,
        }

    @app.patch("/api/admin/applications/{application_id}")
    def patch_application(
        application_id: int,
        body: AdminApplicationPatch,
        request: Request,
        db: Session = Depends(get_db),
    ):
        require_csrf(request)
        require_admin(request, db)
        row = _admin_application(db, application_id)
        if body.role_title is not None:
            role = body.role_title.strip()
            if not role:
                raise HTTPException(status_code=400, detail="Enter the role title.")
            row.role_title = role[:200]
        if body.job_description is not None:
            description = body.job_description.strip()
            if not description:
                raise HTTPException(status_code=400, detail="Paste the job description.")
            if len(description) > MAX_JOB_CHARS:
                raise HTTPException(status_code=400, detail="That job description is too long.")
            row.job_description = description
        if body.fit_score is not None:
            if body.fit_score < 0 or body.fit_score > 100:
                raise HTTPException(status_code=400, detail="Fit score must be between 0 and 100.")
            row.fit_score = body.fit_score
        if body.suitable is not None:
            row.suitable = body.suitable
        if body.skill_board_json is not None:
            try:
                board = FitResult.model_validate(body.skill_board_json)
            except ValidationError as exc:
                raise HTTPException(status_code=400, detail="That skill board JSON is not valid.") from exc
            row.skill_board_json = board.model_dump()
        if body.result_json is not None:
            row.result_json = _validated_result(body.result_json)
        db.commit()
        db.refresh(row)
        return {
            **_admin_application_summary(row),
            "job_description": row.job_description,
            "skill_board_json": row.skill_board_json,
            "result_json": row.result_json,
        }

    @app.delete("/api/admin/applications/{application_id}", status_code=204)
    def delete_application(application_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        require_admin(request, db)
        row = _admin_application(db, application_id)
        db.delete(row)
        db.commit()
        return Response(status_code=204)

    @app.post("/api/admin/impersonate/{user_id}")
    def impersonate(user_id: int, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        admin = require_admin(request, db)
        if request.session.get("impersonator_id"):
            raise HTTPException(status_code=400, detail="Stop viewing as the current user first.")
        target = db.get(User, user_id)
        if target is None:
            raise HTTPException(status_code=404, detail="That user was not found.")
        if target.is_admin:
            raise HTTPException(status_code=400, detail="Cannot view the app as another admin.")
        if target.id == admin.id:
            raise HTTPException(status_code=400, detail="Already signed in as that user.")
        request.session["impersonator_id"] = admin.id
        request.session["user_id"] = target.id
        return {
            "user": user_payload(target),
            "impersonating": {"id": target.id, "email": target.email},
        }

    @app.post("/api/admin/stop-impersonation")
    def stop_impersonation(request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        admin = require_admin(request, db)
        if not request.session.get("impersonator_id"):
            raise HTTPException(status_code=400, detail="Not viewing as another user.")
        request.session["user_id"] = admin.id
        request.session.pop("impersonator_id", None)
        return {"user": user_payload(admin), "impersonating": None}


def _admin_cv(db: Session, cv_id: int) -> CV:
    cv = db.get(CV, cv_id)
    if cv is None:
        raise HTTPException(status_code=404, detail="That CV was not found.")
    return cv


def _admin_application(db: Session, application_id: int) -> Application:
    row = db.get(Application, application_id)
    if row is None:
        raise HTTPException(status_code=404, detail="That check was not found.")
    return row


def _admin_cv_summary(row: CV) -> dict:
    profile = row.profile_json or {}
    contact = profile.get("contact") or {}
    return {
        "id": row.id,
        "user_id": row.user_id,
        "label": row.label,
        "name": contact.get("name") or row.label,
        "created_at": row.created_at.isoformat(),
    }


def _admin_application_summary(row: Application) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "cv_id": row.cv_id,
        "role_title": row.role_title,
        "fit_score": row.fit_score,
        "suitable": row.suitable,
        "created_at": row.created_at.isoformat(),
    }


def _validated_result(payload: dict) -> dict:
    kind = payload.get("kind")
    try:
        if kind == "cv":
            document = CvDocument.model_validate(payload.get("document") or {})
            result = {"kind": "cv", "document": document.model_dump()}
        elif kind == "gap":
            report = GapReport.model_validate(payload.get("report") or {})
            result = {"kind": "gap", "report": report.model_dump()}
        else:
            raise HTTPException(status_code=400, detail="Result kind must be cv or gap.")
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="That result JSON is not valid.") from exc
    for key in ("design", "learning_plan"):
        if key in payload:
            result[key] = payload[key]
    return result
