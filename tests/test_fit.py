from app.schemas import Experience, JobExtract, Profile, ScreenResult, SkillMark, SkillQuote
from app.services.fit import accept_screen, profile_haystack, quote_accepted, score_fit, skill_present
from tests.samples import SAMPLE_PROFILE, gap_job, suitable_job

LONG_BULLET = "Ran the production cluster for the payments API and restored it after a failed release."
SHORT_BULLET = "Used Rust daily."


def _profile(*bullets: str, skills: list[str] | None = None) -> Profile:
    return Profile(
        skills=skills or [],
        experience=[
            Experience(
                employer="Analytical Engines",
                title="Programmer",
                start="1842",
                end="1843",
                bullets=list(bullets),
            )
        ],
        years_experience=5,
    )


def _screen(required: list[tuple[str, str]], preferred: list[tuple[str, str]] | None = None) -> ScreenResult:
    return ScreenResult(
        required=[SkillQuote(skill=skill, quote=quote) for skill, quote in required],
        preferred=[SkillQuote(skill=skill, quote=quote) for skill, quote in preferred or []],
    )


def test_react_alias_and_word_boundary():
    haystack = profile_haystack(Profile(skills=["React", "Postgres", "JavaScript"]))
    assert skill_present("React.js", haystack)
    assert skill_present("PostgreSQL", haystack)
    assert skill_present("Java", haystack) is False


def test_real_bullet_quote_marks_a_skill_present_without_naming_it():
    profile = _profile(LONG_BULLET)
    job = JobExtract(required_skills=["Kubernetes"], min_years=0, seniority="junior")
    required, preferred = accept_screen(profile, job, _screen([("Kubernetes", LONG_BULLET)]))
    assert required[0].present is True
    assert required[0].quote == LONG_BULLET
    fit = score_fit(profile, job, required, preferred)
    assert fit.suitable is True
    assert fit.coverage == 1


def test_one_bullet_can_support_two_skills():
    profile = _profile(LONG_BULLET)
    job = JobExtract(required_skills=["Kubernetes", "Payments"], seniority="junior")
    required, _ = accept_screen(
        profile,
        job,
        _screen([("Kubernetes", LONG_BULLET), ("Payments", LONG_BULLET)]),
    )
    assert [mark.present for mark in required] == [True, True]


def test_quote_missing_from_every_bullet_is_absent():
    profile = _profile(LONG_BULLET)
    job = JobExtract(required_skills=["Rust"], seniority="junior")
    invented = "Invented a compiler that never appears in this work history at all."
    required, _ = accept_screen(profile, job, _screen([("Rust", invented)]))
    assert required[0].present is False
    assert required[0].quote == ""


def test_skills_list_entry_marks_a_skill_present():
    profile = _profile(LONG_BULLET, skills=["React", "JavaScript (ES2022+)", "Tailwind CSS"])
    job = JobExtract(required_skills=["React", "JavaScript", "CSS", "PowerApps"], seniority="junior")
    required, _ = accept_screen(profile, job, _screen([("React", "React")]))
    assert [mark.present for mark in required] == [True, True, True, False]
    assert [mark.source for mark in required] == ["skills", "skills", "skills", ""]
    assert required[1].quote == "JavaScript (ES2022+)"
    fit = score_fit(profile, job, required, [])
    assert fit.coverage == 0.75
    assert fit.suitable is True


def test_work_quote_wins_over_skills_list():
    profile = _profile(LONG_BULLET, skills=["Kubernetes"])
    job = JobExtract(required_skills=["Kubernetes"], seniority="junior")
    required, _ = accept_screen(profile, job, _screen([("Kubernetes", LONG_BULLET)]))
    assert required[0].source == "work"
    assert required[0].quote == LONG_BULLET


def test_skills_list_match_respects_word_boundaries():
    profile = _profile(LONG_BULLET, skills=["JavaScript", "NoSQL", "React.js"])
    job = JobExtract(required_skills=["Java", "SQL", "React"], seniority="junior")
    required, _ = accept_screen(profile, job, ScreenResult())
    assert [mark.present for mark in required] == [False, False, True]


def test_short_excerpt_of_a_long_bullet_is_absent():
    profile = _profile(LONG_BULLET)
    job = JobExtract(required_skills=["Kubernetes"], seniority="junior")
    required, _ = accept_screen(profile, job, _screen([("Kubernetes", "Ran the production")]))
    assert required[0].present is False
    assert quote_accepted("Ran the production", [LONG_BULLET]) is False


def test_short_bullet_must_be_quoted_in_full():
    profile = _profile(SHORT_BULLET)
    job = JobExtract(required_skills=["Rust"], seniority="junior")
    partial, _ = accept_screen(profile, job, _screen([("Rust", "Used Rust")]))
    full, _ = accept_screen(profile, job, _screen([("Rust", SHORT_BULLET)]))
    assert partial[0].present is False
    assert full[0].present is True


def test_skipped_skill_is_absent():
    profile = _profile(LONG_BULLET)
    job = JobExtract(required_skills=["Kubernetes", "Rust"], seniority="junior")
    required, _ = accept_screen(profile, job, _screen([("Kubernetes", LONG_BULLET)]))
    assert [mark.present for mark in required] == [True, False]


def test_missing_preferred_skill_does_not_block():
    profile = _profile(LONG_BULLET)
    job = JobExtract(required_skills=["Kubernetes"], preferred_skills=["GraphQL"], seniority="junior")
    required, preferred = accept_screen(profile, job, _screen([("Kubernetes", LONG_BULLET)], [("GraphQL", "")]))
    fit = score_fit(profile, job, required, preferred)
    assert fit.suitable is True
    assert preferred[0].present is False
    assert fit.matched_preferred == []


def test_score_above_60_generates_a_profile_even_with_low_coverage():
    job = JobExtract(required_skills=["Python", "Kubernetes"], min_years=1, seniority="junior")
    required = [
        SkillMark(name="Python", present=True, quote=LONG_BULLET),
        SkillMark(name="Kubernetes", present=False),
    ]
    fit = score_fit(SAMPLE_PROFILE, job, required, [])
    assert fit.coverage == 0.5
    assert fit.score == 65
    assert fit.suitable is True


def test_score_of_60_does_not_generate_a_profile():
    job = JobExtract(required_skills=["Python", "Kubernetes"], min_years=6, seniority="junior")
    required = [
        SkillMark(name="Python", present=True, quote=LONG_BULLET),
        SkillMark(name="Kubernetes", present=False),
    ]
    fit = score_fit(SAMPLE_PROFILE, job, required, [])
    assert fit.score == 60
    assert fit.suitable is False


def test_coverage_without_years_is_a_gap():
    job = JobExtract(
        required_skills=["Python", "SQL", "Writing", "Editing", "Research"],
        min_years=10,
        seniority="senior",
    )
    thin = SAMPLE_PROFILE.model_copy(update={"years_experience": 1})
    required = [
        SkillMark(name=name, present=name in {"Python", "SQL", "Writing"}, quote=LONG_BULLET)
        for name in job.required_skills
    ]
    fit = score_fit(thin, job, required, [])
    assert fit.coverage == 0.6
    assert fit.score < 60
    assert fit.suitable is False


def test_no_required_skills_is_not_suitable():
    fit = score_fit(SAMPLE_PROFILE, JobExtract(), [], [])
    assert fit.suitable is False
    assert fit.required == []


def test_review_explains_experience_against_seniority_floor():
    job = JobExtract(required_skills=["Python"], min_years=2, seniority="senior")
    profile = SAMPLE_PROFILE.model_copy(update={"years_experience": 3})
    fit = score_fit(profile, job, [SkillMark(name="Python", present=True)], [])
    review = fit.model_dump()
    assert review["years_shown"] == 3
    assert review["years_needed"] == 5
    assert review["years_score"] == 0.6
    assert fit.score == 88


def test_review_does_not_invent_missing_experience():
    fit = score_fit(Profile(), JobExtract(required_skills=["Python"], seniority="mid"), [], [])
    review = fit.model_dump()
    assert review["years_shown"] == 0
    assert review["years_needed"] == 3
    assert review["years_score"] == 0


def test_empty_profile_matches_nothing():
    required, preferred = accept_screen(Profile(), suitable_job(), _screen([("Python", LONG_BULLET), ("SQL", LONG_BULLET)]))
    fit = score_fit(Profile(), suitable_job(), required, preferred)
    assert fit.coverage == 0
    assert fit.suitable is False


def test_gap_job_quotes_are_absent_when_the_screen_is_empty():
    required, _ = accept_screen(SAMPLE_PROFILE, gap_job(), ScreenResult())
    assert [mark.name for mark in required if not mark.present] == ["Kubernetes", "Rust"]
