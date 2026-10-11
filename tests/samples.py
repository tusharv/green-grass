from app.schemas import Contact, Education, Experience, FitResult, JobExtract, Profile, SkillMark

SAMPLE_PROFILE = Profile(
    contact=Contact(name="Ada Lovelace", email="ada@example.com", location="London"),
    summary="Built analytical engines and wrote notes on computation.",
    skills=["Python", "SQL", "Writing"],
    experience=[
        Experience(
            employer="Analytical Engines",
            title="Programmer",
            start="1842",
            end="1843",
            bullets=["Translated a memoir on the analytical engine."],
        )
    ],
    education=[Education(school="Home study", credential="Mathematics", year="1835")],
    years_experience=5,
)

SAMPLE_FIT = FitResult(
    score=100,
    coverage=1,
    suitable=True,
    required=[SkillMark(name="Python", present=True), SkillMark(name="SQL", present=True)],
    matched_preferred=["Writing"],
)


def suitable_job() -> JobExtract:
    return JobExtract(
        required_skills=["Python", "SQL"],
        preferred_skills=["Writing"],
        min_years=2,
        seniority="mid",
    )


def gap_job() -> JobExtract:
    return JobExtract(
        required_skills=["Kubernetes", "Rust"],
        preferred_skills=[],
        min_years=0,
        seniority="",
    )
