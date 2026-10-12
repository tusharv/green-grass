from app.schemas import CvDocument, FitResult, GapItem, GapReport, Profile
from app.services.facts import years_gap
from app.services.fit import accept_screen, required_years, score_fit
from app.services.llm import ModelClient, extract_job, extract_profile, screen_work, write_cv, write_gap


def build_profile(client: ModelClient, resume_text: str) -> Profile:
    return extract_profile(client, resume_text)


def empty_requirements_gap() -> GapReport:
    return GapReport(
        summary="This job description did not list required skills, so the CV was not marked ready to send.",
        gaps=[
            GapItem(
                skill="Required skills",
                severity="major",
                why_it_matters="A match needs skills the posting treats as required.",
                practice="Paste a description that names the skills the role needs.",
                project="List those skills from one posting, then check this CV again.",
            )
        ],
    )


def report_when_blocked(client: ModelClient, profile: Profile, job, role_title: str, fit: FitResult, job_description: str = "") -> GapReport:
    major = [mark.name for mark in fit.required if not mark.present]
    minor = [mark.name for mark in fit.preferred if not mark.present]
    if not major:
        return years_gap(float(profile.years_experience or 0), required_years(job))
    return write_gap(client, role_title, major, minor, profile, job_description)


def analyze_role(
    client: ModelClient, profile: Profile, role_title: str, job_description: str
) -> tuple[FitResult, CvDocument | GapReport]:
    job = extract_job(client, role_title, job_description)
    if not job.required_skills:
        return score_fit(profile, job, [], []), empty_requirements_gap()
    screen = screen_work(client, profile, role_title, job)
    required, preferred = accept_screen(profile, job, screen)
    fit = score_fit(profile, job, required, preferred)
    if fit.suitable:
        return fit, write_cv(client, profile, role_title, fit)
    return fit, report_when_blocked(client, profile, job, role_title, fit, job_description)
