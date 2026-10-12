# Presentation Expansion Design Spec: What Job Ready Is, Problems Solved, Job-Specific CV Value, and Trust Architecture

## Overview

Expand the standalone HTML slide deck in `/presentation/` from 5 slides to 9 cohesive, narrative slides. This update incorporates:
1. **What is Job Ready**: The core value proposition—an honest CV evaluator and practice generator that verifies genuine experience in code and refuses to fabricate skills.
2. **The Problem It Solves**: The broken hiring pipeline—generic mass-application spam, hallucinating AI resume builders that lie, and uninformative automated rejections.
3. **Why a Job-Specific CV Matters**: The 6-second recruiter reality, proof-driven relevance over keyword stuffing, and honest alignment with role context.
4. **Deep-Dive Mechanics ("More")**:
   - **Deterministic Code Engine**: Python scoring formula (`app/services/fit.py`), >= 40-character contiguous bullet quoting, and strict seniority floors.
   - **Actionable Practice Roadmap**: Major vs. minor gaps, plain-English justifications, and concrete hands-on projects instead of empty rejections.
   - **Verified Public Snapshots**: Live employer-verifiable profile links (`/profiles/{token}`) and strict fact-checking guarantees (`facts.py`).

---

## Slide Architecture & Navigation Map

The presentation follows a 9-slide sequence with bi-directional navigation, keyboard shortcuts, and consistent footer pagination (`X of 9`).

| # | File Name | Title & Eyebrow | Prev Slide | Next Slide | Key Concept & Purpose |
|---|---|---|---|---|---|
| 1 | `index.html` | What is Job Ready | *(Home)* | `problem.html` | Core thesis: Ready to send or what to practice. Refuses to invent skills. |
| 2 | `problem.html` | The Problem It Solves | `index.html` | `why-specific.html` | The spray-and-pray trap, lying AI tools, and silent rejections. |
| 3 | `why-specific.html` | Why a Job-Specific CV Matters | `problem.html` | `who.html` | 6–7 second recruiter scans, relevance vs. volume, authentic alignment. |
| 4 | `who.html` | Who It Helps | `why-specific.html` | `check.html` | Three candidate mindsets: applying this week, close to role, not close yet. |
| 5 | `check.html` | Upload the CV. Paste the Job | `who.html` | `engine.html` | Fast 2-step process: text PDF/DOCX + job description. Privacy first. |
| 6 | `engine.html` | Deterministic Code Engine | `check.html` | `outcomes.html` | Under the hood: Python fit scoring, >=40-character quote checks, seniority floors. |
| 7 | `outcomes.html` | One of Two Answers | `engine.html` | `roadmap.html` | Binary result: Ready to send (Ivy League PDF) vs. Not ready (Practice plan). |
| 8 | `roadmap.html` | Actionable Practice Roadmap | `outcomes.html` | `honest.html` | Major/minor gap prioritization, why it matters, hands-on practice projects. |
| 9 | `honest.html` | Stand Behind What You Send | `roadmap.html` | `index.html` *(restart)* | Zero hallucination rules (`facts.py`) and public verified snapshots. |

---

## Detailed Slide Specifications

### Slide 1: `index.html` — What is Job Ready
- **File**: `presentation/index.html`
- **Body Attributes**: `data-next="problem.html"`
- **Eyebrow (`.say`)**: `What is Job Ready`
- **Headline (`h1.pitch`)**: `Your CV is either ready to send, or you get what to practice.`
- **Lede (`.lede`)**: `Job Ready is an honest CV evaluation platform. It verifies your real experience against one specific job posting in code—polishing your wording if you clear the bar, or providing a targeted practice plan if you have gaps. It never invents experience.`
- **Side Card**: Example fit check showing Python (Have), SQL (Have), Kubernetes (Gap).
- **CTA Button**: `<a class="button" href="problem.html">The Problem It Solves</a>`
- **Footer**: `1 of 9` | Next: `problem.html`

### Slide 2: `problem.html` — The Problem It Solves
- **File**: `presentation/problem.html` (New file)
- **Body Attributes**: `data-prev="index.html" data-next="why-specific.html"`
- **Eyebrow (`.say`)**: `The Problem`
- **Headline (`h1`)**: `The Hiring Dilemma: Generic Spam & AI Hallucinations.`
- **Lede (`.lede`)**: `Job seekers face a broken hiring pipeline, and existing tools make the problem worse:`
- **Content Grid (`.cards-3`)**:
  1. **The Spray-and-Pray Trap**: Sending 200 generic CVs into applicant tracking systems (ATS) yields near-zero callbacks, recruiter fatigue, and applicant burnout.
  2. **AI Builders That Lie**: Generative AI tools freely fabricate tools, inflated metrics, and fake responsibilities to "beat the ATS"—leading to immediate disaster in technical interviews.
  3. **Rejection Without Signal**: Standard rejection emails provide zero insight. Candidates never learn which specific requirements they lacked or what to learn next.
- **Footer**: `2 of 9` | Back: `index.html` | Next: `why-specific.html`

### Slide 3: `why-specific.html` — Why a Job-Specific CV Matters
- **File**: `presentation/why-specific.html` (New file)
- **Body Attributes**: `data-prev="problem.html" data-next="who.html"`
- **Eyebrow (`.say`)**: `Why It Matters`
- **Headline (`h1`)**: `Why a Job-Specific CV is Non-Negotiable.`
- **Lede (`.lede`)**: `Recruiters spend an average of 6 to 7 seconds on an initial scan. Specific relevance always beats generic volume:`
- **Content Grid (`.cards-3`)**:
  1. **High Signal in 7 Seconds**: Hiring managers look for proof of 3–5 role-critical skills. A tailored CV surfaces real evidence upfront instead of burying it under unrelated accomplishments.
  2. **Context Over Buzzwords**: Real engineering teams evaluate evidence depth—how tools were applied in production—not just a disconnected keyword list.
  3. **Honest Alignment, Not Embellishment**: True tailoring re-contextualizes genuine work into the role's language while preserving employers, dates, and numbers with 100% fidelity.
- **Footer**: `3 of 9` | Back: `problem.html` | Next: `who.html`

### Slide 4: `who.html` — Who It Helps
- **File**: `presentation/who.html`
- **Body Attributes**: `data-prev="why-specific.html" data-next="check.html"`
- **Eyebrow (`.say`)**: `Target Audience`
- **Headline (`h1`)**: `For people who already have real experience.`
- **Lede (`.lede`)**: `A posting is open. They want to know if their genuine track record stands up to this specific role before putting their reputation on the line:`
- **Situations List (`.situations`)**:
  1. **Applying this week**: Needs an instant, honest sanity check before hitting send.
  2. **Close to the role**: Has the required competencies; wants bullets cleanly sharpened for this specific job without inventing a single fact.
  3. **Not close yet**: Wants an actionable, honest practice plan rather than a false-confidence CV that gets screened out.
- **Footer**: `4 of 9` | Back: `why-specific.html` | Next: `check.html`

### Slide 5: `check.html` — Upload the CV. Paste the Job.
- **File**: `presentation/check.html`
- **Body Attributes**: `data-prev="who.html" data-next="engine.html"`
- **Eyebrow (`.say`)**: `How It Works`
- **Headline (`h1`)**: `Upload the CV. Paste the job.`
- **Steps Grid (`.steps`)**:
  - **Upload**: Text PDF or DOCX up to 5 MB. Scans are rejected. Original files are discarded immediately after text extraction.
  - **Paste**: Role title and job description (up to 20,000 chars). Required skills, preferred skills, and seniority expectations are parsed instantly.
- **Note (`.note`)**: `Required skills are marked on the CV. The fit score is calculated from those skills and the years already on the profile.`
- **Footer**: `5 of 9` | Back: `who.html` | Next: `engine.html`

### Slide 6: `engine.html` — Deterministic Code Engine
- **File**: `presentation/engine.html` (New file)
- **Body Attributes**: `data-prev="check.html" data-next="outcomes.html"`
- **Eyebrow (`.say`)**: `Under the Hood`
- **Headline (`h1`)**: `Code Decides Fit, Not an LLM Guess.`
- **Lede (`.lede`)**: `Suitability is calculated by a deterministic Python engine (`app/services/fit.py`), never delegated to model hallucinations:`
- **Content Grid (`.cards-3`)**:
  1. **Deterministic Fit Formula**: `score = round(100 * (0.7 * coverage + 0.3 * years_score))`. Suitable *only* if required skills exist and the calculated score exceeds 60.
  2. **Contiguous Bullet Proofs**: A skill only counts as present if the engine can quote a contiguous excerpt of at least 40 characters directly from the candidate's actual work history. Sibling tools don't count (Angular never proves React).
  3. **Strict Seniority Floors**: Experience years are measured against explicit industry floors (Junior: 0, Mid: 3, Senior: 5, Lead: 8, Principal: 10). Missing dates count as 0.
- **Footer**: `6 of 9` | Back: `check.html` | Next: `outcomes.html`

### Slide 7: `outcomes.html` — One of Two Answers
- **File**: `presentation/outcomes.html`
- **Body Attributes**: `data-prev="engine.html" data-next="roadmap.html"`
- **Eyebrow (`.say`)**: `Binary Decision`
- **Headline (`h1`)**: `One of two answers. Never a false promise.`
- **Outcomes Grid (`.outcomes`)**:
  - **Ready to Send**: Score > 60 and required skills verified. Bullet wording is polished to match the role context; download a clean, distraction-free Ivy League PDF.
  - **Not Ready**: Gaps exist. You get a concrete breakdown of missing required skills and what to practice. **No rewritten CV and no PDF.**
- **Footer**: `7 of 9` | Back: `engine.html` | Next: `roadmap.html`

### Slide 8: `roadmap.html` — Actionable Practice Roadmap
- **File**: `presentation/roadmap.html` (New file)
- **Body Attributes**: `data-prev="outcomes.html" data-next="honest.html"`
- **Eyebrow (`.say`)**: `Practice Plan`
- **Headline (`h1`)**: `An Actionable Roadmap Over an Empty Rejection.`
- **Lede (`.lede`)**: `Traditional applications end in silence or automated rejections. Job Ready turns a gap into a clear path forward:`
- **Content Grid (`.cards-3`)**:
  1. **Major vs. Minor Prioritization**: Missing required skills are prioritized as Major Gaps; missing preferred skills as Minor Gaps. Candidates know what blocks suitability.
  2. **Clear Context on Why It Matters**: Breaks down why the role specifically demands the skill and how it connects to day-to-day engineering duties.
  3. **Concrete Hands-on Projects**: Recommends a specific, self-contained project or exercise to build authentic proof before applying again.
- **Footer**: `8 of 9` | Back: `outcomes.html` | Next: `honest.html`

### Slide 9: `honest.html` — Stand Behind What You Send & Public Snapshots
- **File**: `presentation/honest.html`
- **Body Attributes**: `data-prev="roadmap.html"`
- **Eyebrow (`.say`)**: `Integrity & Proof`
- **Headline (`h1`)**: `You can stand behind what you send.`
- **Rules List (`.rules`)**:
  1. **Zero Invented Experience (`facts.py`)**: Rewrites can polish phrasing, but cannot add employers, titles, dates, degrees, tools, or numbers.
  2. **No Sham Advice**: Gap plans will never advise a candidate to "list" or "put" a skill on their CV that they haven't actually practiced.
  3. **Verified Public Snapshots (`/profiles/{token}`)**: Candidates can share a live, tamper-proof employer link featuring candidate photo and the fact-checked CV—no inflated claims.
- **Lede (`.lede`)**: `Leave with a CV you can send, or with the next piece of work.`
- **CTA Button**: `<a class="button" href="index.html">Start from beginning</a>`
- **Footer**: `9 of 9` | Back: `roadmap.html`

---

## Styling & Layout System (`presentation/deck.css`)

1. **Card Grid (`.cards-3`)**:
   - Layout: `display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; margin-top: 1.6rem;`
   - Responsive: `@media (max-width: 860px) { grid-template-columns: 1fr; }`
2. **Card Component (`.card`)**:
   - Background: `var(--strip)` with `color: var(--strip-ink)` or `var(--sheet)` with `border: 1px solid var(--line)`.
   - Typography: `h2` styled with `var(--serif)` (approx 1.5–1.75rem), `p` styled with `var(--sans)` in muted green/gray.
   - Icon integration: Standard `.icon` or `.icon.big` at the top of each card.
3. **Code & Formula Badges (`.formula`)**:
   - Background: `rgba(27, 107, 69, 0.15)` with monospace font, subtle border, and padding.
4. **Deck Navigation (`.deck-nav`)**:
   - Updated max-width and layout consistency across all slides.

---

## Scripting (`presentation/deck.js`)

- `End` key handler navigates to `honest.html`.
- `Home` key handler navigates to `index.html`.
- `ArrowRight` and `ArrowLeft` follow `data-next` and `data-prev` on `<body>`.

---

## Verification & Acceptance Criteria

1. **Navigation Flow**:
   - Cycling through `ArrowRight` starts at `index.html` (1 of 9) and progresses through `problem.html`, `why-specific.html`, `who.html`, `check.html`, `engine.html`, `outcomes.html`, `roadmap.html`, to `honest.html` (9 of 9).
   - `ArrowLeft` reverses all steps back to `index.html`.
   - `Home` always loads `index.html`; `End` always loads `honest.html`.
2. **Content Coverage**:
   - What is Job Ready is clearly articulated on Slide 1.
   - The problems of spray-and-pray, AI hallucinations, and silent rejections are articulated on Slide 2.
   - The rationale for job-specific CVs is articulated on Slide 3.
   - The deterministic engine (formula, quote rule, seniority floors) is articulated on Slide 6.
   - The actionable practice roadmap is articulated on Slide 8.
   - Verified public snapshots and fact-checking guarantees are articulated on Slide 9.
3. **Visual Quality & Responsive Design**:
   - Consistent typography (`Literata` + `Atkinson Hyperlegible`).
   - Cards scale cleanly across desktop (>1024px), tablet (768px–1024px), and mobile (<768px).
   - Valid HTML5 semantics (`<main>`, `<header>`, `<footer>`, `<nav>`, `<article>`).
