# AGENTS.md

Job Ready is a FastAPI app with a Svelte 5 frontend. A signed-in person uploads a PDF or DOCX CV, pastes one job, and gets one of two results: a fact-checked CV they can download as a PDF, or a practice plan for the required skills they do not have. The model never decides which result they get, and it never invents experience.

## The product

The person is applying for work. They already have a CV. They want to know whether that CV is ready for one specific role, and they want the next artifact to be honest.

1. They upload a text PDF or DOCX. The original file is not stored. The server keeps extracted text and a structured profile.
2. They paste a role title and job description.
3. The server extracts required skills from the posting, then scores the saved profile in code.
4. If the profile clears the bar, the model rewrites wording only. The person sees the CV and can download a PDF.
5. If it does not clear the bar, the person sees which required skills are missing and how to practice them. There is no rewritten CV and no PDF.

Say "Ready to send" when `suitable` is true and "Gaps to close" or "Not ready" when it is false. Do not add a third outcome, a match-percentage pitch, or advice to list a skill they have not done.

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

## User-confirmed CV chat updates

The application page can propose source-CV edits through private chat. `app/services/cv_chat.py` restricts edits to summary, skills and existing work bullets. Every edit cites exact human-message text; added skills must be stated in that evidence, and new numbers need source support. Work edits require the employer to be named. GitHub alone is not Git evidence; study is not professional work. Identity fields, education and total years are not editable through this flow.

`app/cv_chat_routes.py` stores private conversations in `cv_conversations`, keyed by CV. POST chat only proposes edits. Explicit accuracy confirmation and `POST /api/applications/{id}/chat/apply` apply a server-stored proposal and run the existing pipeline. Keep source CV, assessment and optional shared snapshot changes atomic. Reject stale/replayed proposals using conversation revisions and source fingerprints; preserve saved design. Other applications keep previous assessments. Never expose chat through public profiles, and only refresh a shared snapshot when the user selects that option. Original extracted upload text remains unchanged.

## Manual CV editor

The dedicated `/applications/{id}/edit` page's **Design and edit your CV** editor allows direct human edits to contact details, summary, skills, experience, education, years and additional sections. This is separate from the narrower chat proposal flow; do not loosen chat evidence rules.

- `app/cv_editor_routes.py` owns `/api/applications/{id}/editor` (GET/POST), `/editor/preview` and `/editor/logo`. Previews and logo uploads remain unsaved until the owner saves the editor.
- Factual saves require explicit accuracy confirmation, rerun the existing role pipeline, preserve the human's wording, and atomically update the source CV and this assessment. Original extracted upload text and other assessments stay unchanged. Existing shared CV snapshots refresh only when selected.
- Editor versions cover source, job and saved result. The shared conversation revision serializes manual and chat edits; manual factual saves invalidate pending chat proposals. Rejected or failed reassessments save nothing.
- `Profile.custom_sections` are human-authored, copied unchanged into `CvDocument`, and never treated as work/skills-list evidence. Custom entries must survive every renderer, including the default PDF.
- `ResumeDesign.sections` is an ordered subset of built-in/custom section IDs. Hiding a section preserves its source data and never changes fit. `company_logos` is keyed by normalized employer name, with metadata-free 256px PNG data URLs or an empty string to suppress automatic lookup. No remote logo URLs or uploaded originals are saved.
- The role review links to the standalone editor; it does not embed it. Content and Design tabs stay fixed above a scrolling controls panel, beside an independently scrolling CV. Mobile switches between full-width tools and canvas.
- Unsaved editor drafts are private in-memory state, scoped to the signed-in user. Never expose them in shared profiles or persist them in browser storage. Disable stale canvas edits during preview refresh so indexed fields cannot modify a different entry after reordering.

## Where things live

- `app/main.py` — HTTP routes, ownership checks, session, and the built SPA
- `app/schemas.py` — `Profile`, `JobExtract`, `FitResult`, `CvDocument`, `GapReport`
- `app/services/pipeline.py` — upload profile, screen the work, then either `write_cv` or `write_gap`
- `app/services/prompts.py` — the five model tasks: `extract_resume`, `extract_job`, `screen`, `rewrite_cv`, `upskill`
- `app/services/llm.py` — Ollama client, JSON parse, one retry, then `ModelError`
- `app/services/parser.py` — PDF and DOCX text only
- `app/services/pdf.py` — HTML and WeasyPrint for a suitable CV
- `app/services/photos.py` — profile photo re-encoding (square JPEG, no metadata) and the GitHub handle from CV links
- `app/auth.py` — Argon2, email, CSRF, session user, admin flag, view-as-user
- `app/admin_routes.py` — ops console APIs for listing/editing any user's CVs and role checks
- `frontend/src/pages/` — Login, Register, Dashboard, Upload, CvDetail, Apply, Result, Profile, Admin
- `frontend/src/lib/routes.js` — the only client routes
- `tests/` — pytest. API tests use `ScriptedModel` and do not call Ollama

## Routes

Client: `/` desk, `/login`, `/register`, `/admin` (admins only), `/cvs/new`, `/cvs/{id}`, `/apply?cv={id}`, `/applications/{id}`, `/applications/{id}/edit`, `/profiles/{first}-{last}-{hash}` (no sign-in). The hash is 16 hex characters. A single name, or a name with no ASCII letters, uses that one word or `profile` before the hash.

API, all under the signed-in user except session, register, login, and the public profile:

- `GET /health`
- `GET /api/session` returns `{ csrf, user, impersonating }`. `user` includes `is_admin`. `ADMIN_EMAILS` (comma-separated) sets `is_admin` on register/login.
- `POST /api/register`, `/api/login`, `/api/logout`
- Admin ops (`is_admin` required; uses the real admin account even while viewing as a user): `GET /api/admin/users`, `GET /api/admin/users/{id}`, `GET|PATCH|DELETE /api/admin/cvs/{id}`, `GET|PATCH|DELETE /api/admin/applications/{id}`, `POST /api/admin/impersonate/{user_id}`, `POST /api/admin/stop-impersonation`. Admin patches are support overrides; fit math remains code-owned for normal role checks.
- `GET|POST /api/cvs`, `GET|DELETE /api/cvs/{id}`. Deleting a CV deletes its role checks and its photo.
- `GET|POST|DELETE /api/cvs/{id}/photo`, `POST /api/cvs/{id}/photo/github`. A photo is JPEG, PNG, or WebP up to 3 MB, stored only as a 640px square JPEG. With no choice saved, a GitHub link on the CV supplies the photo. DELETE means no photo, not "fall back to GitHub". LinkedIn photos cannot be fetched; people upload instead.
- `POST /api/job-description` imports readable text from a public HTTP(S) job link for user review; it does not run the model or create an application. Fetches validate and pin public IPs, revalidate redirects, and limit time and response size.
- `GET|POST /api/applications`, `GET|DELETE /api/applications/{id}`. Deleting a role check leaves the CV. Role checks may store an optional `job_url`; it is visible to the owner and excluded from public snapshots.
- `POST /api/applications/{id}/learning-plan` generates and saves a grounded AI learning plan using the saved profile, job description, and missing skills. Complete plans are reused; incomplete plans can be retried. It never changes fit, CV, or PDF eligibility.
- `POST /api/applications/{id}/design` saves validated template settings per role check; `POST /api/applications/{id}/design-preview` previews without saving. Saved settings style the existing employer link and eligible PDF without changing CV facts.
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

## Ollama-generated personalized content

Use Ollama for all personalized narrative content: honest reviews, cover letters, CV rewrites, learning plans and other candidate-specific advice or pitches. Do not substitute hard-coded paragraphs, canned assessments, preset advice, or string-assembled narrative templates for model output. Prompts may define tone, structure and constraints, but the final personalized prose must come from Ollama.

Ground generation in the saved CV, job description and code-owned assessment. Validate model output before saving it. If Ollama is unavailable or validation fails, show a clear error with a retry option; never silently fall back to fixed prose or label a template as AI-generated. Cached output is allowed only when it was model-generated, validated, and still matches its source inputs. Keep scripted model responses in tests only.

This rule concerns generated content, not product mechanics: UI labels, help text, schemas, authentication, ownership, limits, deterministic fit scoring, evidence checks and PDF eligibility stay in code. Preserve the explicitly required fixed safety outcomes (such as a posting with no required skills); Ollama must never decide suitability or invent missing experience.

## Private review and cover letter

The role page includes an Ollama-written candid review and positive cover letter (explicitly requested product additions). `POST /api/applications/{id}/insights` (also available through `/cover-letter`) requires ownership and CSRF. Both drafts use the saved CV, job description and code-owned assessment. A separate Ollama verification checks support and tone; code rejects nonexistent evidence IDs and new numerals. Failed drafts are never saved and no fixed prose fallback is used. Source fingerprints, including job description, invalidate old drafts and reject changes made during generation. Both artifacts are private and excluded from public profiles. They never change suitability or PDF eligibility. Do not claim to predict an employer’s next-round decision.

### Independent insight drafts

Honest Review and Cover Letter generate automatically and independently on first opening a role page. Each has separate POST generation and PATCH manual-save endpoints (`/honest-review`, `/cover-letter`), private text, busy/error state, and source-aware revision. Regeneration writes only the selected section and must preserve the other section, including user edits. Failed generation preserves the prior draft. Manual edits require a matching revision, are explicitly labeled user-edited, do not retain AI-verification claims, and never change source CV or fit. Subsequent visits reuse saved drafts. Warn before replacing saved text and before leaving unsaved edits.
