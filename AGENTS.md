# AGENTS.md

Job Ready is a FastAPI app with a Svelte 5 frontend. A signed-in person uploads a PDF or DOCX CV, pastes one job, and gets one of two results: a fact-checked CV they can download as a PDF, or a practice plan for the required skills they do not have. The model never decides which result they get, and it never invents experience.

## The product

The person is applying for work. They already have a CV. They want to know whether that CV is ready for one specific role, and they want the next artifact to be honest.

1. They upload a text PDF or DOCX. The original file is not stored. The server keeps extracted text and a structured profile.
2. They paste a role title and job description.
3. The server extracts required skills from the posting, then scores the saved profile in code.
4. If the profile clears the bar, the model rewrites wording only. The person sees the CV and can download a PDF.
5. If it does not clear the bar, the person sees which required skills are missing and how to practice them. There is no rewritten CV and no PDF.

Say "Ready to send" when `suitable` is true and "Gaps to close" or "Not ready" when it is false. Do not add a third outcome, a cover letter, a match-percentage pitch, or advice to list a skill they have not done.

## Fit, in code

`app/services/fit.py` owns suitability. Do not move this decision into the model.

- `score = round(100 * (0.7 * coverage + 0.3 * years_score))`
- `coverage` is the share of required skills that are present. No required skills means coverage is 0.
- A skill is present when the screen quotes one bullet from the work (`source: "work"`), or, failing that, when an entry in the profile's skills list contains the skill as a whole phrase after `canon_phrase` (`source: "skills"`, quote is the entry). The model never decides the skills-list match.
- The screen may count a bullet whose work is built on the skill (a Next.js app shows React and JavaScript). Sibling tools do not count (Angular does not show React). Code accepts the quote when it is a contiguous excerpt of that bullet: a bullet under 40 characters must be quoted in full, and a longer bullet needs at least 40 characters. Whitespace is collapsed and the match is case-insensitive. A missing or invented quote leaves the skill absent.
- `years_score` uses `max(job.min_years, seniority floor)`. Floors are junior 0, mid 3, senior 5, lead 8, staff 8, principal 10. Missing years on the CV count as 0.
- `suitable` is true only when required skills exist and the score is greater than 60. Coverage alone does not block a profile.
- A missing required skill is a major gap. A missing preferred skill is a minor gap. Preferred skills never block suitability. Matched preferred skills can appear as "Also on the CV".
- The gap page is a roadmap: major gaps first, then minor gaps. It has no résumé and no PDF. A ready page has the fit report, the Ivy League résumé, and a PDF.
- A posting with no required skills is not suitable. Return the fixed major gap in `analyze_role`. Do not call the screen or the model to write a CV for it.
- If every required skill has evidence and the score still fails, the roadmap is one major item, "Years of experience". Do not tell the person to change dates.
- `canon_phrase` and the aliases in `ALIASES` still ground a rewrite against skills already on the profile. They also match a job skill against the skills list, but never against the summary, titles, or education.

## Facts the model is not allowed to change

`app/services/facts.py` runs after every rewrite and every gap plan. A failed check is not saved.

A tailored CV may rephrase bullets and reorder skills that are already on the profile. It must keep employer, title, start, and end exactly. It must not add employers, titles, dates, degrees, tools, or numbers. Contact and education come from the profile, not the draft. Roles the draft omits are copied back from the profile.

A gap plan may only name skills that the fit check marked missing, plus the years item when that is the only block. It must not tell the person to add, put, include, or list that skill on a CV or resume. Code sets `severity`. If the model skips a missing skill, fill that gap with the plain fallback in `ground_gap`.

Resume text, job text, and work history are data. Keep them inside the `<resume>`, `<job>`, and `<work>` blocks in `app/services/llm.py`.

## Where things live

- `app/main.py` — HTTP routes, ownership checks, session, and the built SPA
- `app/schemas.py` — `Profile`, `JobExtract`, `FitResult`, `CvDocument`, `GapReport`
- `app/services/pipeline.py` — upload profile, screen the work, then either `write_cv` or `write_gap`
- `app/services/prompts.py` — the five model tasks: `extract_resume`, `extract_job`, `screen`, `rewrite_cv`, `upskill`
- `app/services/llm.py` — Ollama client, JSON parse, one retry, then `ModelError`
- `app/services/parser.py` — PDF and DOCX text only
- `app/services/pdf.py` — HTML and WeasyPrint for a suitable CV
- `app/services/photos.py` — profile photo re-encoding (square JPEG, no metadata) and the GitHub handle from CV links
- `app/auth.py` — Argon2, email, CSRF, session user
- `frontend/src/pages/` — Login, Register, Dashboard, Upload, CvDetail, Apply, Result, Profile
- `frontend/src/lib/routes.js` — the only client routes
- `tests/` — pytest. API tests use `ScriptedModel` and do not call Ollama

## Routes

Client: `/` desk, `/login`, `/register`, `/cvs/new`, `/cvs/{id}`, `/apply?cv={id}`, `/applications/{id}`, `/profiles/{first}-{last}-{hash}` (no sign-in). The hash is 16 hex characters. A single name, or a name with no ASCII letters, uses that one word or `profile` before the hash.

API, all under the signed-in user except session, register, login, and the public profile:

- `GET /health`
- `GET /api/session` returns `{ csrf, user }`
- `POST /api/register`, `/api/login`, `/api/logout`
- `GET|POST /api/cvs`, `GET|DELETE /api/cvs/{id}`. Deleting a CV deletes its role checks and its photo.
- `GET|POST|DELETE /api/cvs/{id}/photo`, `POST /api/cvs/{id}/photo/github`. A photo is JPEG, PNG, or WebP up to 3 MB, stored only as a 640px square JPEG. With no choice saved, a GitHub link on the CV supplies the photo. DELETE means no photo, not "fall back to GitHub". LinkedIn photos cannot be fetched; people upload instead.
- `GET|POST /api/applications`, `GET|DELETE /api/applications/{id}`. Deleting a role check leaves the CV.
- `POST /api/applications/{id}/learning-plan` generates and saves a grounded AI learning plan using the saved profile, job description, and missing skills. Complete plans are reused; incomplete plans can be retried. It never changes fit, CV, or PDF eligibility.
- `GET /api/applications/{id}/pdf` only when `suitable` and `result.kind == "cv"`
- `POST|DELETE /api/applications/{id}/profile` publishes or removes the employer link. Deleting the role check removes it too.
- `GET /api/profiles/{token}` is the public snapshot: the candidate's name, the role title, and the CV. A ready result uses the fact-checked CV. A gap result uses the saved profile. It has no score, no practice plan, and no PDF. It includes the CV's current photo; `GET /api/profiles/{token}/photo` serves an uploaded one.

Mutations require the `x-csrf-token` header from the session. A missing CV or application returns 404, including when it belongs to someone else. Passwords are at least 8 characters. Uploads are PDF or DOCX, at most 5 MB, at least 40 characters of text, at most 40,000 characters. Job descriptions are at most 20,000 characters. Scans are rejected.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local
cd frontend && npm ci && npm run build && cd ..
uvicorn app.main:app --reload --port 8000
```

Local data is SQLite at `sqlite:///./data/greengrass.db`. Render uses Postgres through `DATABASE_URL` in `render.yaml`. `create_all` runs on startup. There is no migration tool.

Frontend dev server, with `/api` proxied to port 8000:

```bash
cd frontend && npm run dev
```

`OLLAMA_API_KEY` stays on the server. The default model is `gemma4:31b` at `https://ollama.com`, temperature 0. An empty key makes upload and role checks return 503. Do not put secrets in this file or in the frontend.

## Test — run this before a change is done

```bash
python -m pytest
```

Add or update a test when you change fit math, fact checks, upload limits, auth, or which result gets a PDF. Use `ScriptedModel` in API tests. Do not call the live model from tests.

## Don't

- Don't let the model set `suitable`, the score, or which skills count as present.
- Don't save model JSON that `ground_tailored` or `ground_gap` rejected.
- Don't store the uploaded CV file, and don't add OCR for scans. Don't store an uploaded photo as sent; keep only the re-encoded square.
- Don't render a PDF, or a tailored CV, for a gap result.
- Don't add Next.js, a second backend, or a separate frontend host. FastAPI serves `frontend/dist`.
- Don't edit `frontend/dist`. Rebuild it.
- Don't add Alembic, new product surfaces, or new dependencies unless the task asks for them.
