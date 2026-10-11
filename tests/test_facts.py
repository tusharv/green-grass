import json

from app.schemas import Experience, FitResult, GapItem, GapReport, JobExtract, Profile, SkillMark, TailoredDraft
from app.services.facts import FactError, claims_skill_on_cv, ground_gap, ground_tailored, years_gap
from app.services.pipeline import report_when_blocked
from tests.samples import SAMPLE_FIT, SAMPLE_PROFILE


def test_rejects_invented_employer():
    profile = SAMPLE_PROFILE
    draft = TailoredDraft(
        summary=profile.summary,
        skills=["Python"],
        experience=[
            Experience(
                employer="OpenAI",
                title="Programmer",
                start="1842",
                end="1843",
                bullets=["Translated a memoir on the analytical engine."],
            )
        ],
    )
    try:
        ground_tailored(profile, draft, SAMPLE_FIT)
    except FactError as exc:
        assert "Unknown role" in str(exc)
    else:
        raise AssertionError("invented employer was accepted")


def test_rejects_invented_metric():
    profile = SAMPLE_PROFILE
    draft = TailoredDraft(
        summary=profile.summary,
        skills=["Python"],
        experience=[
            Experience(
                employer="Analytical Engines",
                title="Programmer",
                start="1842",
                end="1843",
                bullets=["Improved throughput by 40%."],
            )
        ],
    )
    try:
        ground_tailored(profile, draft, SAMPLE_FIT)
    except FactError as exc:
        assert "40" in str(exc)
    else:
        raise AssertionError("invented metric was accepted")


def test_accepts_rephrased_bullet_without_new_facts():
    profile = SAMPLE_PROFILE
    draft = TailoredDraft(
        summary="Programmer who translated a memoir on the analytical engine.",
        skills=["SQL", "Python"],
        experience=[
            Experience(
                employer="Analytical Engines",
                title="Programmer",
                start="1842",
                end="1843",
                bullets=["Translated a memoir on the analytical engine."],
            )
        ],
    )
    document = ground_tailored(profile, draft, SAMPLE_FIT)
    assert document.experience[0].employer == "Analytical Engines"
    assert document.skills[0] == "Python"
    assert document.skills[1] == "SQL"
    assert document.education[0].school == "Home study"


def test_gap_rejects_skill_that_is_not_missing():
    report = GapReport(
        summary="One skill is missing.",
        gaps=[
            GapItem(
                skill="Python",
                why_it_matters="Already on the CV.",
                practice="Skip this.",
                project="Do not invent a project.",
            )
        ],
    )
    try:
        ground_gap(["Kubernetes"], [], report)
    except FactError as exc:
        assert "not missing" in str(exc)
    else:
        raise AssertionError("present skill was accepted as a gap")


def test_gap_rejects_advice_to_claim_the_skill():
    report = GapReport(
        summary="Learn the missing skill first.",
        gaps=[
            GapItem(
                skill="Kubernetes",
                why_it_matters="The role uses it.",
                practice="Add Kubernetes to your CV after reading a blog.",
                project="None.",
            )
        ],
    )
    try:
        ground_gap(["Kubernetes"], [], report)
    except FactError as exc:
        assert "claim" in str(exc)
    else:
        raise AssertionError("claim-on-CV advice was accepted")


def test_negated_claim_is_allowed():
    assert claims_skill_on_cv("Do not add Rust to your CV yet.") is False


def test_gap_fills_a_missing_skill_the_model_skipped():
    report = GapReport(
        summary="Rust is missing.",
        gaps=[
            GapItem(
                skill="Rust",
                why_it_matters="The role builds tools in Rust.",
                practice="Write a small command line tool.",
                project="Describe the tool in your own words.",
            )
        ],
    )
    grounded = ground_gap(["Rust", "Kubernetes"], [], report)
    names = [gap.skill for gap in grounded.gaps]
    assert names == ["Rust", "Kubernetes"]
    assert "CV" not in grounded.gaps[1].practice
    assert grounded.gaps[1].severity == "major"


def test_gap_orders_major_before_minor_and_sets_severity():
    report = GapReport(
        summary="Two kinds of gap.",
        gaps=[
            GapItem(
                skill="GraphQL",
                severity="major",
                why_it_matters="Nice to have.",
                practice="Read one query.",
                project="Ask for one field.",
            )
        ],
    )
    grounded = ground_gap(["Rust"], ["GraphQL", "Writing"], report)
    assert [(gap.skill, gap.severity) for gap in grounded.gaps] == [
        ("Rust", "major"),
        ("GraphQL", "minor"),
        ("Writing", "minor"),
    ]
    assert "required" in grounded.gaps[0].why_it_matters
    assert grounded.gaps[1].why_it_matters == "Nice to have."
    assert "preferred" in grounded.gaps[2].why_it_matters


def test_years_only_failure_returns_the_years_item():
    fit = FitResult(
        score=50,
        coverage=1,
        suitable=False,
        required=[SkillMark(name="Python", present=True, quote="Translated a memoir on the analytical engine.")],
        preferred=[SkillMark(name="GraphQL", present=False)],
    )
    job = JobExtract(required_skills=["Python"], min_years=10, seniority="principal")
    report = report_when_blocked(None, SAMPLE_PROFILE, job, "Analyst", fit)  # type: ignore[arg-type]
    assert report.gaps[0].skill == "Years of experience"
    assert report.gaps[0].severity == "major"
    assert "5" in report.summary
    assert "10" in report.summary
    assert len(report.gaps) == 1
    direct = years_gap(5, 10)
    assert direct.gaps[0].skill == "Years of experience"


def test_round_trip_json():
    raw = json.dumps(SAMPLE_PROFILE.model_dump())
    assert Profile.model_validate_json(raw).contact.name == "Ada Lovelace"
