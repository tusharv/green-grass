"""Owner-only conversation and atomic source-CV reassessment endpoints."""
import secrets
from typing import Literal

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import update, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_csrf, require_user
from app.models import Application, CV, CvConversation, utcnow
from app.schemas import CvDocument, Profile
from app.services.cv_chat import CvEdit, chat_reply, fingerprint, proposed_profile
from app.services.llm import ModelError, write_gap
from app.services.pipeline import analyze_role


class MessageBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    message: str = Field(min_length=1, max_length=3000)
    revision: int = Field(ge=0)


class ApplyChatBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    proposal_id: str = Field(min_length=1, max_length=64)
    revision: int = Field(ge=0)
    confirmed: Literal[True]
    update_shared_profile: bool = False


class DismissBody(BaseModel):
    model_config = ConfigDict(extra='forbid')
    revision: int = Field(ge=0)


def job_fingerprint(row):
    return fingerprint([row.id, row.role_title, row.job_description])


def current_conversation(db, cv_id):
    return db.get(CvConversation, cv_id)


def expect_revision(conversation, revision):
    if revision != (conversation.revision if conversation else 0):
        raise HTTPException(409, 'This conversation changed in another tab. Refresh it before continuing.')


def claim(db, cv_id, revision, messages, pending):
    """Compare-and-swap serializes edits to the same CV across application pages."""
    values = dict(revision=revision + 1, messages=messages[-40:], pending=pending, updated_at=utcnow())
    if revision == 0:
        db.add(CvConversation(cv_id=cv_id, **values))
        try:
            db.flush()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(409, 'Another conversation update finished first. Refresh and try again.') from exc
    else:
        result = db.execute(update(CvConversation).where(
            CvConversation.cv_id == cv_id, CvConversation.revision == revision,
        ).values(**values).execution_options(synchronize_session=False))
        if result.rowcount != 1:
            db.rollback()
            raise HTTPException(409, 'This conversation changed while the request was running. Refresh and try again.')


def state_for(db, row):
    convo = current_conversation(db, row.cv_id)
    pending = convo.pending if convo else None
    stale = bool(pending and (pending['profile_hash'] != fingerprint(row.cv.profile_json)
                            or (pending['application_id'] == row.id and pending['job_hash'] != job_fingerprint(row))))
    visible = pending if pending and pending['application_id'] == row.id and not stale else None
    return {
        'revision': convo.revision if convo else 0,
        'messages': convo.messages if convo else [],
        'proposal': ({'id': visible['id'], 'changes': visible['changes']} if visible else None),
        'notice': ('The CV changed. Send a message to prepare a fresh proposal.' if stale else
                   'A proposal is waiting on another role check for this CV.' if pending and not visible else ''),
    }


def register_cv_chat(app, get_db, owned_application, model_client, application_detail):
    @app.get('/api/applications/{application_id}/chat')
    def get_chat(application_id: int, request: Request, db: Session = Depends(get_db)):
        row = owned_application(db, require_user(request, db), application_id)
        return state_for(db, row)

    @app.post('/api/applications/{application_id}/chat')
    def send_chat(application_id: int, body: MessageBody, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        row = owned_application(db, require_user(request, db), application_id)
        convo = current_conversation(db, row.cv_id)
        expect_revision(convo, body.revision)
        text = body.message.strip()
        if not text:
            raise HTTPException(400, 'Enter a message about your experience.')
        profile = Profile.model_validate(row.cv.profile_json)
        source_hash, job_hash = fingerprint(row.cv.profile_json), job_fingerprint(row)
        message = {'id': secrets.token_hex(12), 'role': 'user', 'text': text,
                   'application_id': row.id, 'role_title': row.role_title}
        messages = [*(convo.messages if convo else [])[-38:], message]
        try:
            reply, changes = chat_reply(model_client(), profile, row.role_title, row.job_description, messages)
        except ModelError as exc:
            raise HTTPException(422, str(exc)) from exc
        messages.append({'id': secrets.token_hex(12), 'role': 'assistant', 'text': reply.reply,
                         'application_id': row.id, 'role_title': row.role_title})
        pending = None
        if changes:
            pending = {'id': secrets.token_hex(16), 'application_id': row.id,
                       'profile_hash': source_hash, 'job_hash': job_hash,
                       'edits': [e.model_dump() for e in reply.edits], 'changes': changes}
        claim(db, row.cv_id, body.revision, messages, pending)
        db.refresh(row.cv)
        db.refresh(row)
        if fingerprint(row.cv.profile_json) != source_hash or job_fingerprint(row) != job_hash:
            db.rollback()
            raise HTTPException(409, 'The CV or role changed. Refresh and resend your message.')
        db.commit()
        db.expire_all()
        return state_for(db, row)

    @app.delete('/api/applications/{application_id}/chat/proposal')
    def dismiss_chat(application_id: int, body: DismissBody, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        row = owned_application(db, require_user(request, db), application_id)
        convo = current_conversation(db, row.cv_id)
        expect_revision(convo, body.revision)
        if convo and convo.pending and convo.pending['application_id'] == row.id:
            messages = [*convo.messages, {'id': secrets.token_hex(12), 'role': 'assistant',
                        'text': 'Proposal discarded. Your saved CV has not changed.',
                        'application_id': row.id, 'role_title': row.role_title}]
            claim(db, row.cv_id, body.revision, messages, None)
            db.commit()
            db.expire_all()
        return state_for(db, row)

    @app.post('/api/applications/{application_id}/chat/apply')
    def apply_chat(application_id: int, body: ApplyChatBody, request: Request, db: Session = Depends(get_db)):
        require_csrf(request)
        row = owned_application(db, require_user(request, db), application_id)
        convo = current_conversation(db, row.cv_id)
        expect_revision(convo, body.revision)
        pending = convo.pending if convo else None
        if not pending or pending['id'] != body.proposal_id or pending['application_id'] != row.id:
            raise HTTPException(409, 'This proposal is no longer available. Send a message to prepare another.')
        if fingerprint(row.cv.profile_json) != pending['profile_hash'] or job_fingerprint(row) != pending['job_hash']:
            raise HTTPException(409, 'The CV or role changed. Prepare a new proposal before applying.')
        try:
            candidate, changes = proposed_profile(Profile.model_validate(row.cv.profile_json),
                [CvEdit.model_validate(e) for e in pending['edits']], convo.messages)
            client = model_client()
            fit, result = analyze_role(client, candidate, row.role_title, row.job_description)
            payload = ({'kind': 'cv', 'document': result.model_dump()} if isinstance(result, CvDocument)
                       else {'kind': 'gap', 'report': result.model_dump()})
            major = [mark.name for mark in fit.required if not mark.present]
            minor = [mark.name for mark in fit.preferred if not mark.present]
            if fit.suitable and (major or minor):
                payload['learning_plan'] = write_gap(client, row.role_title, major, minor,
                                                     candidate, row.job_description).model_dump()
        except ModelError as exc:
            raise HTTPException(422, 'Nothing was changed. ' + str(exc)) from exc
        messages = [*convo.messages, {'id': secrets.token_hex(12), 'role': 'assistant',
                    'text': 'Your main CV was updated and this role was reassessed. Other role checks keep their previous assessments.',
                    'application_id': row.id, 'role_title': row.role_title, 'applied_changes': changes}]
        claim(db, row.cv_id, body.revision, messages, None)
        # Re-read after the claim. Preserve designs saved while the model was working.
        db.expire_all()
        row = db.scalar(select(Application).where(Application.id == application_id).with_for_update())
        if row is None:
            db.rollback()
            raise HTTPException(409, 'This role check was deleted while reassessing.')
        cv = db.scalar(select(CV).where(CV.id == row.cv_id).with_for_update())
        if fingerprint(cv.profile_json) != pending['profile_hash'] or job_fingerprint(row) != pending['job_hash']:
            db.rollback()
            raise HTTPException(409, 'The CV or role changed while reassessing. Nothing was changed; refresh and try again.')
        if row.result_json.get('design'):
            payload['design'] = row.result_json['design']
        cv.profile_json = candidate.model_dump()
        row.fit_score, row.suitable = fit.score, fit.suitable
        row.skill_board_json, row.result_json = fit.model_dump(), payload
        shared_updated = bool(body.update_shared_profile and row.share)
        if shared_updated:
            row.share.document_json = (result.model_dump() if isinstance(result, CvDocument)
                else CvDocument.model_validate(candidate.model_dump()).model_dump())
        db.commit()
        db.expire_all()
        return {'application': application_detail(row), 'chat': state_for(db, row),
                'shared_updated': shared_updated}
