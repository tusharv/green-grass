import re
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def normalize_email(email: str) -> str:
    cleaned = (email or "").strip().lower()
    if not EMAIL_RE.match(cleaned):
        raise HTTPException(status_code=400, detail="Enter a valid email address.")
    return cleaned


def check_password(password: str) -> str:
    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail="Use a password of at least 8 characters.")
    return password


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        import secrets

        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def require_csrf(request: Request) -> None:
    expected = request.session.get("csrf")
    sent = request.headers.get("x-csrf-token", "")
    if not expected or sent != expected:
        raise HTTPException(status_code=403, detail="The form expired. Refresh the page and try again.")


def current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def require_user(request: Request, db: Session) -> User:
    user = current_user(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Sign in to continue.")
    return user


def user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def label_from_filename(filename: str) -> str:
    stem = Path(filename or "CV").stem.strip() or "CV"
    return stem[:200]
