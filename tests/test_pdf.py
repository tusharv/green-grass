from app.schemas import CvDocument
from app.services.pdf import document_html
from tests.samples import SAMPLE_PROFILE


def test_cv_html_uses_source_facts_only():
    document = CvDocument(
        contact=SAMPLE_PROFILE.contact,
        summary=SAMPLE_PROFILE.summary,
        skills=["Python", "SQL"],
        experience=SAMPLE_PROFILE.experience,
        education=SAMPLE_PROFILE.education,
    )
    html = document_html(document)
    assert "Ada Lovelace" in html
    assert "Analytical Engines" in html
    assert "Python · SQL" in html
    assert "border-top: 1px solid #1a1a1a" in html
    assert "#fbfaf6" in html
    assert "<script" not in html.lower()
