from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    cvs: Mapped[list["CV"]] = relationship(back_populates="owner")
    applications: Mapped[list["Application"]] = relationship(back_populates="owner")


class CV(Base):
    __tablename__ = "cvs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    label: Mapped[str] = mapped_column(String(200))
    source_filename: Mapped[str] = mapped_column(String(255))
    extracted_text: Mapped[str] = mapped_column(Text)
    profile_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped[User] = relationship(back_populates="cvs")
    applications: Mapped[list["Application"]] = relationship(back_populates="cv")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    cv_id: Mapped[int] = mapped_column(ForeignKey("cvs.id"), index=True)
    role_title: Mapped[str] = mapped_column(String(200))
    job_description: Mapped[str] = mapped_column(Text)
    fit_score: Mapped[int] = mapped_column(Integer)
    suitable: Mapped[bool] = mapped_column(Boolean)
    skill_board_json: Mapped[dict] = mapped_column(JSON)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped[User] = relationship(back_populates="applications")
    cv: Mapped[CV] = relationship(back_populates="applications")
    share: Mapped["ProfileShare | None"] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ProfileShare(Base):
    """Public snapshot of one role check. The private review is not included."""

    __tablename__ = "profile_shares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    role_title: Mapped[str] = mapped_column(String(200))
    document_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    application: Mapped[Application] = relationship(back_populates="share")
