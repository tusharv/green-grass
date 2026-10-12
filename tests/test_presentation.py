from pathlib import Path

PRESENTATION_DIR = Path(__file__).resolve().parent.parent / "presentation"

EXPECTED_SLIDES = [
    ("index.html", None, "problem.html", "1 of 9"),
    ("problem.html", "index.html", "why-specific.html", "2 of 9"),
    ("why-specific.html", "problem.html", "who.html", "3 of 9"),
    ("who.html", "why-specific.html", "check.html", "4 of 9"),
    ("check.html", "who.html", "engine.html", "5 of 9"),
    ("engine.html", "check.html", "outcomes.html", "6 of 9"),
    ("outcomes.html", "engine.html", "roadmap.html", "7 of 9"),
    ("roadmap.html", "outcomes.html", "honest.html", "8 of 9"),
    ("honest.html", "roadmap.html", None, "9 of 9"),
]


def test_presentation_files_exist_and_chain_correctly():
    for filename, expected_prev, expected_next, expected_counter in EXPECTED_SLIDES:
        filepath = PRESENTATION_DIR / filename
        assert filepath.exists(), f"Slide {filename} does not exist in {PRESENTATION_DIR}"

        content = filepath.read_text(encoding="utf-8")

        # Verify HTML basics
        assert "<!doctype html>" in content
        assert "deck.css" in content
        assert "deck.js" in content
        assert f"<p>{expected_counter}</p>" in content

        # Verify data-prev and data-next
        if expected_prev:
            assert f'data-prev="{expected_prev}"' in content, f"{filename} missing data-prev='{expected_prev}'"
            assert f'href="{expected_prev}">Back</a>' in content, f"{filename} missing Back link to {expected_prev}"
        else:
            assert "data-prev=" not in content

        if expected_next:
            assert f'data-next="{expected_next}"' in content, f"{filename} missing data-next='{expected_next}'"
            assert (
                f'href="{expected_next}">Next</a>' in content
                or f'href="{expected_next}">The Problem It Solves</a>' in content
                or f'href="{expected_next}"' in content
            ), f"{filename} missing Next link to {expected_next}"
        else:
            assert "data-next=" not in content


def test_presentation_key_content():
    # Slide 1: What is Job Ready
    slide1 = (PRESENTATION_DIR / "index.html").read_text(encoding="utf-8")
    assert "What is Job Ready" in slide1

    # Slide 2: Problem
    slide2 = (PRESENTATION_DIR / "problem.html").read_text(encoding="utf-8")
    assert "The Problem" in slide2
    assert "Spray-and-Pray" in slide2 or "spray-and-pray" in slide2.lower()
    assert "Hallucination" in slide2 or "hallucinat" in slide2.lower()

    # Slide 3: Why Job-Specific CV
    slide3 = (PRESENTATION_DIR / "why-specific.html").read_text(encoding="utf-8")
    assert "Job-Specific CV" in slide3
    assert "6 to 7 seconds" in slide3 or "7 seconds" in slide3

    # Slide 6: Deterministic Code Engine
    slide6 = (PRESENTATION_DIR / "engine.html").read_text(encoding="utf-8")
    assert "Code Decides Fit" in slide6 or "fit.py" in slide6
    assert "0.7 * coverage + 0.3 * years_score" in slide6
    assert "40" in slide6

    # Slide 8: Practice Roadmap
    slide8 = (PRESENTATION_DIR / "roadmap.html").read_text(encoding="utf-8")
    assert "Roadmap" in slide8 or "Practice Plan" in slide8
    assert "Major" in slide8

    # Slide 9: Honesty & Public Snapshots
    slide9 = (PRESENTATION_DIR / "honest.html").read_text(encoding="utf-8")
    assert "profiles" in slide9 or "Stand behind" in slide9.lower() or "stand behind" in slide9.lower()


def test_deck_js_key_bindings():
    deck_js = (PRESENTATION_DIR / "deck.js").read_text(encoding="utf-8")
    assert 'location.href = "index.html"' in deck_js
    assert 'location.href = "honest.html"' in deck_js


def test_presentation_routes_served_by_api():
    from app.main import create_app
    from starlette.testclient import TestClient

    app = create_app()
    client = TestClient(app)

    # /presentation redirects to /presentation/ so relative links resolve correctly
    res = client.get("/presentation", follow_redirects=False)
    assert res.status_code in (307, 308, 301, 302)
    assert res.headers["location"] == "/presentation/"

    # /presentation/ returns index.html
    res = client.get("/presentation/")
    assert res.status_code == 200
    assert "What is Job Ready" in res.text

    # /presentation/problem.html returns problem.html
    res = client.get("/presentation/problem.html")
    assert res.status_code == 200
    assert "The Problem" in res.text

    # /presentation/deck.css returns CSS
    res = client.get("/presentation/deck.css")
    assert res.status_code == 200
    assert "--grass" in res.text
