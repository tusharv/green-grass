import re

from app.schemas import FitResult, JobExtract, Profile, SkillMark

SENIORITY_YEARS = {
    "junior": 0,
    "mid": 3,
    "senior": 5,
    "lead": 8,
    "principal": 10,
    "staff": 8,
}

# Phrase aliases so "React.js" and "Postgres" meet the words people actually write.
ALIASES = {
    "react js": "react",
    "reactjs": "react",
    "node js": "node",
    "nodejs": "node",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "golang": "go",
}


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9+#]+", text.lower())


def canon_phrase(text: str) -> str:
    phrase = " ".join(tokens(text))
    return ALIASES.get(phrase, phrase)


def phrase_in(phrase: str, haystack: str) -> bool:
    if not phrase:
        return False
    return f" {phrase} " in f" {haystack} "


def profile_haystack(profile: Profile) -> str:
    chunks: list[str] = [profile.summary, *profile.skills]
    for role in profile.experience:
        chunks.extend([role.employer, role.title, *role.bullets])
    for school in profile.education:
        chunks.extend([school.school, school.credential, school.year])
    phrases = [canon_phrase(chunk) for chunk in chunks if chunk and chunk.strip()]
    return " ".join(phrase for phrase in phrases if phrase)


def skill_present(required: str, haystack: str) -> bool:
    return phrase_in(canon_phrase(required), haystack)


def required_years(job: JobExtract) -> float:
    seniority = SENIORITY_YEARS.get((job.seniority or "").strip().lower(), 0)
    return max(float(job.min_years or 0), float(seniority))


def collapse(text: str) -> str:
    return " ".join((text or "").split()).casefold()


def work_bullets(profile: Profile) -> list[str]:
    bullets: list[str] = []
    for role in profile.experience:
        bullets.extend(bullet for bullet in role.bullets if bullet and bullet.strip())
    return bullets


def quote_accepted(quote: str, bullets: list[str]) -> bool:
    excerpt = collapse(quote)
    if not excerpt:
        return False
    for bullet in bullets:
        body = collapse(bullet)
        if not body or excerpt not in body:
            continue
        if len(body) < 40:
            if excerpt == body:
                return True
            continue
        if len(excerpt) >= 40:
            return True
    return False


def _marks_for(names: list[str], quotes: list, bullets: list[str]) -> list[SkillMark]:
    by_key: dict[str, str] = {}
    for item in quotes:
        key = canon_phrase(item.skill)
        if key and key not in by_key:
            by_key[key] = item.quote or ""
    marks: list[SkillMark] = []
    for name in names:
        quote = by_key.get(canon_phrase(name), "")
        accepted = quote_accepted(quote, bullets)
        marks.append(SkillMark(name=name, present=accepted, quote=quote if accepted else ""))
    return marks


def accept_screen(profile: Profile, job: JobExtract, screen) -> tuple[list[SkillMark], list[SkillMark]]:
    bullets = work_bullets(profile)
    required = _marks_for(job.required_skills, screen.required, bullets)
    preferred = _marks_for(job.preferred_skills, screen.preferred, bullets)
    return required, preferred


def score_fit(
    profile: Profile,
    job: JobExtract,
    required: list[SkillMark],
    preferred: list[SkillMark],
) -> FitResult:
    if not job.required_skills:
        coverage = 0.0
    else:
        coverage = sum(int(mark.present) for mark in required) / len(job.required_skills)

    years_needed = required_years(job)
    if years_needed <= 0:
        years_score = 1.0
    else:
        years_score = min(1.0, float(profile.years_experience or 0) / years_needed)

    score = round(100 * (0.7 * coverage + 0.3 * years_score))
    suitable = bool(job.required_skills) and score > 60
    return FitResult(
        score=score,
        coverage=coverage,
        suitable=suitable,
        required=list(required),
        preferred=list(preferred),
        matched_preferred=[mark.name for mark in preferred if mark.present],
    )
