"""Manual, owner-confirmed source edits and private, unsaved design previews."""
import json
import math
import secrets

from fastapi import Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_csrf, require_user
from app.cv_chat_routes import claim, current_conversation, expect_revision, job_fingerprint
from app.models import Application, CV
from app.schemas import CvDocument, Profile, ResumeDesign
from app.services.cv_chat import fingerprint
from app.services.design import designed_html
from app.services.editor_images import MAX_LOGO_BYTES, logo_image
from app.services.llm import ModelError
from app.services.pipeline import analyze_role


class EditorPreview(BaseModel):
    model_config = ConfigDict(extra='forbid')
    profile: Profile
    design: ResumeDesign

    @model_validator(mode='after')
    def bounded_profile(self):
        p = self.profile
        if not math.isfinite(p.years_experience) or not 0 <= p.years_experience <= 100:
            raise ValueError('Years of experience must be between 0 and 100.')
        if len(json.dumps(p.model_dump(), ensure_ascii=False)) > 60_000:
            raise ValueError('Keep the CV under 60,000 characters.')
        if len(p.summary) > 10_000 or len(p.skills) > 300 or len(p.experience) > 50 or len(p.education) > 50:
            raise ValueError('This CV contains too much content.')
        if any(len(r.bullets) > 100 for r in p.experience) or len(p.contact.links) > 20:
            raise ValueError('Use fewer entries in this CV.')
        ids = [section.id for section in p.custom_sections]
        if len(ids) != len(set(ids)):
            raise ValueError('Each custom section needs its own identifier.')
        if any(name.startswith('custom-') and name not in ids for name in self.design.sections):
            raise ValueError('That custom section is no longer in the CV.')
        return self


class EditorSave(EditorPreview):
    version: str = Field(min_length=64, max_length=64)
    revision: int = Field(ge=0)
    confirmed: bool = False
    update_shared_profile: bool = False


def editor_version(row):
    # Include presentation and assessment so a stale editor cannot overwrite a newer save.
    return fingerprint([row.cv.profile_json, job_fingerprint(row), row.result_json])


def editor_state(db, row):
    conversation = current_conversation(db, row.cv_id)
    return {'profile': Profile.model_validate(row.cv.profile_json).model_dump(),
            'design': ResumeDesign.model_validate(row.result_json.get('design') or {}).model_dump(),
            'version': editor_version(row), 'revision': conversation.revision if conversation else 0}


def register_cv_editor(app, get_db, owned_application, model_client, application_detail, design_photo):
    @app.get('/api/applications/{application_id}/editor')
    def get_editor(application_id: int, request: Request, db: Session = Depends(get_db)):
        row = owned_application(db, require_user(request, db), application_id)
        return editor_state(db, row)

    @app.post('/api/applications/{application_id}/editor/preview')
    def preview(application_id: int, body: EditorPreview, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        row = owned_application(db, require_user(request, db), application_id)
        html = designed_html(CvDocument.model_validate(body.profile.model_dump()), body.design,
                             design_photo(row.cv, web=True))
        return Response(html, media_type='text/html')

    @app.post('/api/applications/{application_id}/editor/logo')
    async def upload_logo(application_id: int, request: Request, file: UploadFile = File(...),
                          crop: bool = Form(False), db: Session = Depends(get_db)):
        require_csrf(request)
        owned_application(db, require_user(request, db), application_id)
        raw = await file.read(MAX_LOGO_BYTES + 1)
        try:
            return {'url': logo_image(raw, crop)}
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        finally:
            await file.close()

    @app.post('/api/applications/{application_id}/editor')
    def save_editor(application_id: int, body: EditorSave, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        row = owned_application(db, require_user(request, db), application_id)
        convo = current_conversation(db, row.cv_id)
        expect_revision(convo, body.revision)
        if editor_version(row) != body.version:
            raise HTTPException(409, 'The CV or role check changed. Reload the editor before saving.')
        changed = body.profile != Profile.model_validate(row.cv.profile_json)
        if changed and not body.confirmed:
            raise HTTPException(422, 'Confirm that your CV edits are accurate before saving.')
        payload = dict(row.result_json)
        if changed:
            try:
                fit, result = analyze_role(model_client(), body.profile, row.role_title, row.job_description)
            except ModelError as exc:
                raise HTTPException(422, 'Nothing was changed. ' + str(exc)) from exc
            # The user deliberately wrote this text. Keep it verbatim rather than replacing
            # it with model wording. The existing pipeline still checks every model result.
            payload = ({'kind': 'cv', 'document': CvDocument.model_validate(body.profile.model_dump()).model_dump()}
                       if isinstance(result, CvDocument) else {'kind': 'gap', 'report': result.model_dump()})
        messages = list(convo.messages if convo else [])
        if changed:
            messages.append({'id': secrets.token_hex(12), 'role': 'assistant',
                'text': 'Your manually confirmed CV edits were saved and this role was reassessed.',
                'application_id': row.id, 'role_title': row.role_title})
        # All source edits (including chat) serialize on the same revision.
        claim(db, row.cv_id, body.revision, messages, None if changed else (convo.pending if convo else None))
        db.expire_all()
        row = db.scalar(select(Application).where(Application.id == application_id).with_for_update())
        if row is None:
            db.rollback()
            raise HTTPException(409, 'This role check was deleted. Nothing was changed.')
        cv = db.scalar(select(CV).where(CV.id == row.cv_id).with_for_update())
        if editor_version(row) != body.version:
            db.rollback()
            raise HTTPException(409, 'The CV or role changed while saving. Nothing was changed; reload the editor.')
        payload['design'] = body.design.model_dump()
        if changed:
            cv.profile_json = body.profile.model_dump()
            row.fit_score, row.suitable = fit.score, fit.suitable
            row.skill_board_json = fit.model_dump()
        row.result_json = payload
        shared_updated = bool(changed and body.update_shared_profile and row.share)
        if shared_updated:
            row.share.document_json = CvDocument.model_validate(body.profile.model_dump()).model_dump()
        db.commit()
        db.expire_all()
        return {'application': application_detail(row), 'editor': editor_state(db, row),
                'shared_updated': shared_updated}
