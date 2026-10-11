import re

from app.schemas import CvDocument, Experience, FitResult, GapItem, GapReport, Profile, TailoredDraft
from app.services.fit import canon_phrase, profile_haystack, skill_present

CLAIM_ON_CV = re.compile(
    r"\b(?:add|put|include|list)\b.{0,40}\b(?:on|to)\b.{0,24}\b(?:cv|resume)\b",
    re.IGNORECASE,
)
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


class FactError(Exception):
    pass


def norm_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def numbers_in(text: str) -> set[str]:
    return set(NUMBER.findall(text or ""))


def profile_corpus(profile: Profile) -> str:
    parts = [
        profile.summary,
        profile.contact.name,
        profile.contact.email,
        profile.contact.phone,
        profile.contact.location,
        *profile.contact.links,
        *profile.skills,
    ]
    for role in profile.experience:
        parts.extend([role.employer, role.title, role.start, role.end, *role.bullets])
    for school in profile.education:
        parts.extend([school.school, school.credential, school.year])
    return "\n".join(part for part in parts if part)


def canonical_skill(profile: Profile, requested: str) -> str:
    wanted = canon_phrase(requested)
    for skill in profile.skills:
        if canon_phrase(skill) == wanted:
            return skill
    return requested.strip()


def ground_tailored(profile: Profile, draft: TailoredDraft, fit: FitResult) -> CvDocument:
    source_numbers = numbers_in(profile_corpus(profile))
    summary = (draft.summary or "").strip() or profile.summary
    extra = numbers_in(summary) - source_numbers
    if extra:
        raise FactError(f"New metrics: {', '.join(sorted(extra))}")

    haystack = profile_haystack(profile)
    skills: list[str] = []
    seen: set[str] = set()
    for skill in draft.skills:
        if not skill_present(skill, haystack):
            raise FactError(f"Skill not on CV: {skill}")
        key = canon_phrase(skill)
        if key in seen:
            continue
        seen.add(key)
        skills.append(canonical_skill(profile, skill))

    roles = {
        (norm_label(role.employer), norm_label(role.title)): role for role in profile.experience
    }
    used: set[tuple[str, str]] = set()
    experience: list[Experience] = []
    for role in draft.experience:
        key = (norm_label(role.employer), norm_label(role.title))
        if key not in roles:
            raise FactError(f"Unknown role: {role.employer} / {role.title}")
        source = roles[key]
        if norm_label(role.start) != norm_label(source.start) or norm_label(role.end) != norm_label(source.end):
            raise FactError("Dates were changed")
        bullets = [bullet.strip() for bullet in role.bullets if bullet and bullet.strip()] or list(source.bullets)
        bullet_numbers = numbers_in("\n".join(bullets)) - source_numbers
        if bullet_numbers:
            raise FactError(f"New metrics: {', '.join(sorted(bullet_numbers))}")
        used.add(key)
        experience.append(
            Experience(
                employer=source.employer,
                title=source.title,
                start=source.start,
                end=source.end,
                bullets=bullets,
            )
        )

    for role in profile.experience:
        key = (norm_label(role.employer), norm_label(role.title))
        if key not in used:
            experience.append(role)

    if not skills:
        skills = list(profile.skills)

    ordered: list[str] = []
    ordered_keys: set[str] = set()

    def add(name: str) -> None:
        key = canon_phrase(name)
        if not key or key in ordered_keys:
            return
        ordered_keys.add(key)
        ordered.append(name)

    for mark in fit.required:
        if mark.present:
            add(canonical_skill(profile, mark.name))
    for skill in skills:
        add(skill)

    return CvDocument(
        contact=profile.contact,
        summary=summary,
        skills=ordered,
        experience=experience,
        education=list(profile.education),
    )


def claims_skill_on_cv(text: str) -> bool:
    for match in CLAIM_ON_CV.finditer(text or ""):
        window = text[max(0, match.start() - 16) : match.start()].lower()
        if "not " in window or "n't" in window:
            continue
        return True
    return False


def _fallback_gap(skill: str, severity: str) -> GapItem:
    if severity == "minor":
        why = f"The role lists {skill} as preferred, and the work does not show it."
    else:
        why = f"The role lists {skill} as required, and the work does not show it."
    return GapItem(
        skill=skill,
        severity=severity,  # type: ignore[arg-type]
        why_it_matters=why,
        practice=f"Practice {skill} until you can explain a small example without notes.",
        project=f"Build a short project that uses {skill}, then describe what you did in your own words.",
    )


def years_gap(shown: float, needed: float) -> GapReport:
    shown_label = f"{shown:g}"
    needed_label = f"{needed:g}"
    return GapReport(
        summary=f"This CV shows {shown_label} years. This role needs {needed_label}.",
        gaps=[
            GapItem(
                skill="Years of experience",
                severity="major",
                why_it_matters=f"This CV shows {shown_label} years. The role needs {needed_label}.",
                practice="Keep the dates already written on the CV.",
                project="Describe the work those dates already cover.",
            )
        ],
    )


def ground_gap(major: list[str], minor: list[str], report: GapReport) -> GapReport:
    ordered: list[tuple[str, str, str]] = []
    seen_keys: set[str] = set()
    for severity, names in (("major", major), ("minor", minor)):
        for skill in names:
            key = canon_phrase(skill)
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)
            ordered.append((key, skill, severity))

    allowed = {key for key, _, _ in ordered}
    found: dict[str, GapItem] = {}
    for gap in report.gaps:
        key = canon_phrase(gap.skill)
        if key not in allowed:
            raise FactError(f"Gap skill is not missing: {gap.skill}")
        text = " ".join([gap.why_it_matters, gap.practice, gap.project])
        if claims_skill_on_cv(text):
            raise FactError("Advice tells them to claim a skill on the CV")
        if key in found:
            continue
        found[key] = gap

    cleaned: list[GapItem] = []
    for key, skill, severity in ordered:
        gap = found.get(key)
        if gap is None:
            cleaned.append(_fallback_gap(skill, severity))
            continue
        cleaned.append(gap.model_copy(update={"skill": skill, "severity": severity}))

    summary = (report.summary or "").strip() or "This CV is missing required skills for the role."
    if claims_skill_on_cv(summary):
        raise FactError("Advice tells them to claim a skill on the CV")
    return GapReport(summary=summary, gaps=cleaned)
