# Presentation Expansion (9 Slides) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Green Grass presentation deck in `/presentation/` to 9 cohesive, narrative slides adding "What's Green Grass", "What Problem It's Solving", "Why a Job-Specific CV Matters", "Deterministic Code Engine", "Actionable Practice Roadmap", and "Verified Public Snapshots".

**Architecture:** Multi-page static HTML slides (`index.html` through `honest.html`) connected by bi-directional arrow key navigation (`data-prev` / `data-next` in `deck.js`), unified pagination (`X of 9`), responsive CSS grid layouts (`.cards-3`, `.step`, `.sheet`), and botanical typography (`Literata` + `Atkinson Hyperlegible`). Automated integrity tests in `tests/test_presentation.py` verify link chains, content assertions, and keyboard bindings.

**Tech Stack:** Semantic HTML5, Vanilla CSS3 (Custom properties, grid, flexbox), Vanilla JavaScript (Keyboard navigation), Python pytest (Deck verification suite).

---

## File Structure

- **Create**: `tests/test_presentation.py` — Automated verification suite for the presentation deck (slide existence, unbroken navigation chain, content checks, footer counters).
- **Modify**: `presentation/deck.css` — Styling for 3-column card grid (`.cards-3`, `.card`), formula badges (`.formula`), and responsive layout.
- **Modify**: `presentation/deck.js` — Keyboard navigation (`Home` to `index.html`, `End` to `honest.html`, `ArrowLeft`/`ArrowRight`).
- **Modify**: `presentation/index.html` — Slide 1: "What is Green Grass", link to `problem.html`, `1 of 9` footer.
- **Create**: `presentation/problem.html` — Slide 2: "The Problem It Solves" (spray-and-pray, AI hallucinations, silent rejections), `2 of 9` footer.
- **Create**: `presentation/why-specific.html` — Slide 3: "Why a Job-Specific CV Matters" (6–7 second scans, evidence over buzzwords, honest alignment), `3 of 9` footer.
- **Modify**: `presentation/who.html` — Slide 4: Update links (`data-prev="why-specific.html" data-next="check.html"`), `4 of 9` footer.
- **Modify**: `presentation/check.html` — Slide 5: Update links (`data-prev="who.html" data-next="engine.html"`), `5 of 9` footer.
- **Create**: `presentation/engine.html` — Slide 6: "Deterministic Code Engine" (formula, 40-char quote rule, seniority floors), `6 of 9` footer.
- **Modify**: `presentation/outcomes.html` — Slide 7: Update links (`data-prev="engine.html" data-next="roadmap.html"`), `7 of 9` footer.
- **Create**: `presentation/roadmap.html` — Slide 8: "Actionable Practice Roadmap" (major/minor gaps, context, hands-on projects), `8 of 9` footer.
- **Modify**: `presentation/honest.html` — Slide 9: "Stand Behind What You Send & Public Snapshots", `9 of 9` footer, restart link.

---

### Task 1: Add Automated Verification Suite for Presentation Deck

**Files:**
- Create: `tests/test_presentation.py`

- [ ] **Step 1: Write the failing presentation test**

Create `tests/test_presentation.py` with complete integrity and navigation assertions:

```python
from pathlib import Path
import re

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
            assert f'href="{expected_next}">Next</a>' in content or f'href="{expected_next}">The Problem It Solves</a>' in content or f'href="{expected_next}"' in content, f"{filename} missing Next link to {expected_next}"
        else:
            assert "data-next=" not in content


def test_presentation_key_content():
    # Slide 1: What is Green Grass
    slide1 = (PRESENTATION_DIR / "index.html").read_text(encoding="utf-8")
    assert "What is Green Grass" in slide1

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_presentation.py -v`
Expected: FAIL because `problem.html`, `why-specific.html`, `engine.html`, and `roadmap.html` do not exist yet.

- [ ] **Step 3: Commit the test**

```bash
git add tests/test_presentation.py
git commit -m "test: add automated integrity test for presentation deck"
```

---

### Task 2: Update CSS Styles in `presentation/deck.css`

**Files:**
- Modify: `presentation/deck.css`

- [ ] **Step 1: Add `.cards-3`, `.card`, and `.formula` styles to `deck.css`**

Add the 3-column card grid, card styling, and formula badge rules to `presentation/deck.css`:

```css
/* 3-Column Card Layout for Pitch & Detail Slides */
.cards-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-top: 1.6rem;
}

.card {
  background: var(--strip);
  color: var(--strip-ink);
  border-radius: 2px;
  padding: 1.3rem 1.35rem 1.45rem;
  display: flex;
  flex-direction: column;
}

.card.light {
  background: var(--sheet);
  color: var(--ink);
  border: 1px solid var(--line);
}

.card h2 {
  font-family: var(--serif);
  font-weight: 560;
  font-size: 1.55rem;
  line-height: 1.2;
  margin: 0 0 0.6rem;
}

.card p {
  margin: 0;
  color: #d5e6db;
  font-size: 1.02rem;
  line-height: 1.45;
}

.card.light p {
  color: var(--muted);
}

.card .tag {
  display: inline-block;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-weight: 700;
  color: #92dfb3;
  margin-bottom: 0.5rem;
}

.card.light .tag {
  color: var(--grass-deep);
}

.formula {
  background: rgba(27, 107, 69, 0.15);
  border: 1px solid rgba(27, 107, 69, 0.35);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  padding: 0.4rem 0.65rem;
  border-radius: 3px;
  font-size: 0.95rem;
  display: inline-block;
  margin: 0.5rem 0;
  color: var(--strip-ink);
}

.card.light .formula {
  background: #f0f7f3;
  color: var(--grass-deep);
}

@media (max-width: 860px) {
  .cards-3 {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Commit CSS updates**

```bash
git add presentation/deck.css
git commit -m "style: add cards-3, card, and formula styles to deck.css"
```

---

### Task 3: Update Slide 1 (`index.html`) & Create Slide 2 (`problem.html`)

**Files:**
- Modify: `presentation/index.html`
- Create: `presentation/problem.html`

- [ ] **Step 1: Update `presentation/index.html`**

Update `presentation/index.html` with:
- `data-next="problem.html"`
- Eyebrow: `What is Green Grass`
- Pitch: `Your CV is either ready to send, or you get what to practice.`
- Lede: `Green Grass is an honest CV evaluation platform. It verifies your real experience against one specific job posting in code—polishing your wording if you clear the bar, or providing a targeted practice plan if you have gaps. It never invents experience.`
- CTA: `<a class="button" href="problem.html">The Problem It Solves</a>`
- Footer: `1 of 9`, Next: `problem.html`

- [ ] **Step 2: Create `presentation/problem.html`**

Create `presentation/problem.html` with:
- `data-prev="index.html" data-next="why-specific.html"`
- Eyebrow: `The Problem`
- Title: `The Hiring Dilemma: Generic Spam & AI Hallucinations.`
- Lede: `Job seekers face a broken hiring pipeline, and existing automated tools only make it worse:`
- Three cards in `.cards-3`:
  1. `Spray-and-Pray Trap`: Sending 200 generic CVs into applicant tracking systems (ATS) yields near-zero callbacks, recruiter fatigue, and applicant burnout.
  2. `AI Builders That Lie`: Generative AI tools freely fabricate tools, inflated metrics, and fake responsibilities to "beat the ATS"—leading to immediate disaster in technical interviews.
  3. `Rejection Without Signal`: Standard rejection emails provide zero insight. Candidates never learn which specific requirements they lacked or what to learn next.
- Footer: `2 of 9`, Back: `index.html`, Next: `why-specific.html`.

- [ ] **Step 3: Commit Slides 1 and 2**

```bash
git add presentation/index.html presentation/problem.html
git commit -m "feat: update Slide 1 and create Slide 2 (The Problem)"
```

---

### Task 4: Create Slide 3 (`why-specific.html`) & Update Slide 4 (`who.html`) and Slide 5 (`check.html`)

**Files:**
- Create: `presentation/why-specific.html`
- Modify: `presentation/who.html`
- Modify: `presentation/check.html`

- [ ] **Step 1: Create `presentation/why-specific.html`**

Create `presentation/why-specific.html` with:
- `data-prev="problem.html" data-next="who.html"`
- Eyebrow: `Why It Matters`
- Title: `Why a Job-Specific CV is Non-Negotiable.`
- Lede: `Recruiters spend an average of 6 to 7 seconds on an initial scan. Specific relevance always beats generic volume:`
- Three cards in `.cards-3`:
  1. `High Signal in 7 Seconds`: Hiring managers look for proof of 3–5 role-critical competencies. A targeted CV surfaces real evidence upfront instead of burying it under unrelated accomplishments.
  2. `Context Over Buzzwords`: High-performing engineering teams evaluate evidence depth—how tools were applied in production—not just a disconnected keyword list.
  3. `Honest Alignment, Not Embellishment`: True tailoring re-contextualizes your genuine track record into the role's language while preserving employers, dates, and numbers with 100% fidelity.
- Footer: `3 of 9`, Back: `problem.html`, Next: `who.html`.

- [ ] **Step 2: Update `presentation/who.html`**

Update `presentation/who.html` with:
- `data-prev="why-specific.html" data-next="check.html"`
- Footer: `4 of 9`, Back: `why-specific.html`, Next: `check.html`.

- [ ] **Step 3: Update `presentation/check.html`**

Update `presentation/check.html` with:
- `data-prev="who.html" data-next="engine.html"`
- Footer: `5 of 9`, Back: `who.html`, Next: `engine.html`.

- [ ] **Step 4: Commit Slides 3, 4, and 5**

```bash
git add presentation/why-specific.html presentation/who.html presentation/check.html
git commit -m "feat: add Slide 3 (Why Job-Specific CV) and update navigation in Slides 4 & 5"
```

---

### Task 5: Create Slide 6 (`engine.html`) & Update Slide 7 (`outcomes.html`)

**Files:**
- Create: `presentation/engine.html`
- Modify: `presentation/outcomes.html`

- [ ] **Step 1: Create `presentation/engine.html`**

Create `presentation/engine.html` with:
- `data-prev="check.html" data-next="outcomes.html"`
- Eyebrow: `Under the Hood`
- Title: `Code Decides Fit, Not an LLM Guess.`
- Lede: `Suitability is calculated by a deterministic Python engine (`app/services/fit.py`), never delegated to model hallucinations:`
- Three cards in `.cards-3`:
  1. `Deterministic Fit Formula`:
     `<span class="formula">score = round(100 * (0.7 * coverage + 0.3 * years_score))</span>`
     Suitable *only* when required skills exist and the calculated score exceeds 60. Coverage alone does not guarantee a pass.
  2. `Contiguous Bullet Proofs`:
     A skill only counts as "Have" if the screener can quote a contiguous excerpt of at least 40 characters directly from the candidate's actual work history. Sibling tools never count (Angular never proves React).
  3. `Strict Seniority Floors`:
     Experience years are cross-checked against explicit industry floors: Junior 0, Mid 3, Senior 5, Lead/Staff 8, Principal 10. Missing CV dates count as 0.
- Footer: `6 of 9`, Back: `check.html`, Next: `outcomes.html`.

- [ ] **Step 2: Update `presentation/outcomes.html`**

Update `presentation/outcomes.html` with:
- `data-prev="engine.html" data-next="roadmap.html"`
- Footer: `7 of 9`, Back: `engine.html`, Next: `roadmap.html`.

- [ ] **Step 3: Commit Slides 6 and 7**

```bash
git add presentation/engine.html presentation/outcomes.html
git commit -m "feat: add Slide 6 (Deterministic Code Engine) and update Slide 7 navigation"
```

---

### Task 6: Create Slide 8 (`roadmap.html`) & Update Slide 9 (`honest.html`)

**Files:**
- Create: `presentation/roadmap.html`
- Modify: `presentation/honest.html`

- [ ] **Step 1: Create `presentation/roadmap.html`**

Create `presentation/roadmap.html` with:
- `data-prev="outcomes.html" data-next="honest.html"`
- Eyebrow: `Practice Plan`
- Title: `An Actionable Roadmap Over an Empty Rejection.`
- Lede: `Traditional applications end in silence or generic automated rejections. Green Grass turns a gap into a clear path forward:`
- Three cards in `.cards-3`:
  1. `Major vs. Minor Gaps`: Missing required skills are prioritized as Major Gaps; missing preferred skills as Minor Gaps. Candidates know exactly what is blocking suitability.
  2. `Clear Context on Why It Matters`: Plain-English explanation of why the role specifically demands the skill and how it connects to day-to-day engineering duties.
  3. `Concrete Hands-on Projects`: Recommends a specific, self-contained project or exercise to build authentic proof before applying again.
- Footer: `8 of 9`, Back: `outcomes.html`, Next: `honest.html`.

- [ ] **Step 2: Update `presentation/honest.html`**

Update `presentation/honest.html` with:
- `data-prev="roadmap.html"`
- Eyebrow: `Integrity & Proof`
- Title: `You can stand behind what you send.`
- Three rules in `.rules`:
  1. `Zero Invented Experience (facts.py)`: A rewrite can sharpen phrasing and reorder existing skills. It cannot add employers, titles, dates, degrees, tools, or numbers.
  2. `No Sham Advice`: A gap plan will never tell you to "add", "put", or "list" a skill on your CV that you haven't actually practiced.
  3. `Verified Public Snapshots (/profiles/{token})`: Candidates can share a live, tamper-proof employer link featuring candidate photo and the fact-checked CV—no inflated claims.
- CTA: `<a class="button" href="index.html">Start from beginning</a>`
- Footer: `9 of 9`, Back: `roadmap.html`.

- [ ] **Step 3: Commit Slides 8 and 9**

```bash
git add presentation/roadmap.html presentation/honest.html
git commit -m "feat: add Slide 8 (Practice Roadmap) and update Slide 9 (Honesty & Snapshots)"
```

---

### Task 7: Full Verification Suite Run & Visual Polish

**Files:**
- Test: `tests/test_presentation.py`
- Verify: Full pytest test suite

- [ ] **Step 1: Run the presentation test suite**

Run: `.venv/bin/python -m pytest tests/test_presentation.py -v`
Expected: 3 passed in < 1 second.

- [ ] **Step 2: Run the full test suite**

Run: `.venv/bin/python -m pytest`
Expected: 72 passed, 0 failures.

- [ ] **Step 3: Verification commit**

```bash
git status
```
Ensure working tree is clean.
