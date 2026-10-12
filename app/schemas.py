from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Contact(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[str] = Field(default_factory=list)


class Experience(BaseModel):
    employer: str = ""
    title: str = ""
    start: str = ""
    end: str = ""
    bullets: list[str] = Field(default_factory=list)


class Education(BaseModel):
    school: str = ""
    credential: str = ""
    year: str = ""


class Profile(BaseModel):
    contact: Contact = Field(default_factory=Contact)
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    years_experience: float = 0


class JobExtract(BaseModel):
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_years: float = 0
    seniority: str = ""


class SkillMark(BaseModel):
    name: str
    present: bool
    quote: str = ""
    source: Literal["", "work", "skills"] = ""


class FitResult(BaseModel):
    score: int
    coverage: float
    suitable: bool
    required: list[SkillMark]
    preferred: list[SkillMark] = Field(default_factory=list)
    matched_preferred: list[str] = Field(default_factory=list)
    years_shown: float | None = None
    years_needed: float | None = None
    years_score: float | None = None


class SkillQuote(BaseModel):
    skill: str = ""
    quote: str = ""


class ScreenResult(BaseModel):
    required: list[SkillQuote] = Field(default_factory=list)
    preferred: list[SkillQuote] = Field(default_factory=list)


class TailoredDraft(BaseModel):
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)


class CvDocument(BaseModel):
    contact: Contact
    summary: str
    skills: list[str]
    experience: list[Experience]
    education: list[Education]


class LearningResource(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    url: str

    @field_validator("url")
    @classmethod
    def safe_url(cls, value: str) -> str:
        parsed = HttpUrl(value)
        if parsed.scheme != "https" or parsed.username or parsed.password:
            raise ValueError("Learning links must use HTTPS without embedded credentials.")
        return str(parsed)


class GapItem(BaseModel):
    skill: str
    severity: Literal["major", "minor"] = "major"
    why_it_matters: str
    practice: str
    project: str
    learn: list[str] = Field(default_factory=list, max_length=6)
    verify: str = ""
    resources: list[LearningResource] = Field(default_factory=list, max_length=4)


class GapReport(BaseModel):
    summary: str = ""
    gaps: list[GapItem] = Field(default_factory=list)
