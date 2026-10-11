# Profile, job versions, and deep screening

## Decisions

After a CV upload, the person sees one Ivy League résumé of the saved profile. Each job checked against that CV is a version of it. The jobs already stored as applications are those versions. There is no new table.

A job page has two states, and only these two:

- Ready to send: the fit report, the Ivy League résumé rewritten for that role, and a PDF of that same sheet.
- Gaps to close: the fit report and a roadmap. No résumé and no PDF.

A required skill counts only when the screen quotes a bullet that is already on the profile. The model chooses that bullet because the work shows the skill. Code checks that the quote is a real excerpt, then computes coverage, the score, and `suitable`. The model does not set those. A skills list is not evidence.

A missing required skill is a major gap. A missing preferred skill is a minor gap. Preferred skills never block Ready to send. The roadmap takes major gaps first, then minor ones. It does not tell the person to put a skill on the CV.

## Profile page

`GET /api/cvs/{id}` keeps the current profile and adds `versions`: the applications for that CV, newest first. Each version has `id`, `cv_id`, `role_title`, `fit_score`, `suitable`, and `created_at`. The list endpoint stays a summary and does not include versions.

`/cvs/{id}` renders the profile as an Ivy League sheet and lists the versions under it. Each version links to `/applications/{id}` and is labeled Ready to send or Gaps to close. The page offers Check a role. An empty version list says "No roles checked yet."

The sheet shows only fields already on the profile: name, contact, summary, experience, skills, and education. It does not show a photo, a skill meter, or a section the profile does not have.

## Ivy League sheet

One sheet component draws both the saved profile and a ready résumé. The PDF uses the same structure.

- The name is a serif heading. Contact sits on one line under it.
- A full-width hairline sits under the contact line.
- Section labels are small, uppercase, and followed by a lighter hairline.
- A role has the title and dates on one line, the employer in italic, then the bullets.
- Skills are one line separated by middots.
- Education is credential, school, and year.

The paper is `#fbfaf6`, the ink is `#1a1a1a`, the strong rule is `#1a1a1a`, and the section rule is `#d9d2c5`. The PDF uses Liberation Serif and Liberation Sans, which WeasyPrint already has. The page uses the serif and sans already loaded by the app.

## Job page

`/applications/{id}` stays the only result route.

When `suitable` is true and `result.kind` is `cv`, the page shows the fit report, then the Ivy League sheet of `result.document`, and a link to the existing PDF route. The PDF route stays 404 unless both of those are true.

When `suitable` is false, the page shows the fit report and the roadmap. It does not render a sheet and does not offer a PDF.

The fit report says Ready to send or Gaps to close. It shows the score, each required skill as present or Major, and matched preferred skills as "Also on the CV". On a gap page, a missing preferred skill is labeled Minor. On a ready page, unmatched preferred skills are omitted.

## Screening

`analyze_role` still extracts the job first. If the posting has no required skills, it does not call screening or the CV writer. It returns the current fixed gap, and that item is major.

Otherwise it asks the model to screen the work. The user message contains the role title, the required skills, the preferred skills, and the experience records. Experience goes in a `<work>` block and is data. The skills list, summary, and education are not included.

The model returns JSON only:

```json
{"required":[{"skill":"Kubernetes","quote":""}],"preferred":[{"skill":"GraphQL","quote":""}]}
```

`skill` must be copied from the list it was given. `quote` is empty when the work does not show the skill. A present skill quotes one bullet.

Code accepts a quote only when all of these hold:

- Whitespace is collapsed, and the comparison is case-insensitive.
- The quote is a contiguous excerpt of a single bullet.
- A bullet shorter than 40 characters must be quoted in full.
- A longer bullet must be quoted with at least 40 characters.
- The quote is not taken from a skills list, a summary, a title, an employer, or education.

A skill with no accepted quote is absent. A skill the model skips is absent. A skill outside the job lists is ignored. One bullet may support more than one skill. A failed screen is retried once, then `ModelError`, and nothing is saved.

`score_fit` then uses those marks. The formula is unchanged: `score = round(100 * (0.7 * coverage + 0.3 * years_score))`. Coverage is the share of required skills with an accepted quote. No required skills means coverage is 0. Years still use `max(job.min_years, seniority floor)` and treat missing CV years as 0. `suitable` is true only when required skills exist, coverage is at least 0.60, and score is at least 60.

Phrase aliases stay available for grounding a rewrite against skills already on the profile. They do not mark a job skill present.

Each required and preferred mark stores `name`, `present`, and `quote`. The quote is kept on the skill board. Existing rows without a quote read as an empty quote.

## Roadmap

A gap item gains `severity`, either `major` or `minor`. Code sets it. The model does not.

Missing required skills are major, in the posting's order. Missing preferred skills are minor, in the posting's order. The roadmap is that single ordered list. The page groups it under Major gaps and Minor gaps and numbers the steps. It does not store a second plan.

Each step has the skill, why it matters, what to practice, and one small project. `ground_gap` still rejects a skill that is not in the missing lists, rejects duplicate skills, and rejects advice that tells the person to add, put, include, or list the skill on a CV or résumé. A skipped skill is filled with a plain fallback. The major fallback says the role lists the skill as required and it is not shown by the work. The minor fallback says the role lists it as preferred. The fallback practice and project stay plain and do not mention the CV.

If the score fails only because of years, and every required skill has evidence, the roadmap is one major item, "Years of experience". It states the years on the profile and the years bar, which is `max(min_years, seniority floor)`. It does not tell the person to change dates. This replaces the current message that claims the posting listed no required skills.

When the person is ready to send, missing preferred skills do not create a roadmap.

## What stays

Upload limits, auth, CSRF, ownership, and the 404 for someone else's CV or application stay as they are. The original file is still not stored. The rewrite may still rephrase bullets and reorder skills that are already on the profile. Employer, title, start, and end stay exact. Contact and education still come from the profile. Omitted roles are still copied back. A failed fact check is still not saved.

The desk still lists CVs and past checks. No new routes, no new dependency, and no migration tool.

## Tests

API tests keep using `ScriptedModel` and gain a scripted screen response. They do not call Ollama.

- A quote of a real bullet marks that required skill present even when the bullet never names the skill.
- A quote that is not in any bullet, a quote of the skills list, and a too-short excerpt of a long bullet all leave the skill absent.
- The score and `suitable` follow the existing bar once the marks are known.
- A missing preferred skill is minor and does not block Ready to send.
- A gap result has no document. Its PDF is 404. A ready result has a document and a PDF.
- `ground_gap` orders major skills before minor skills and fills a skill the model skipped.
- A CV detail response includes that CV's versions and no one else's.
- The years-only failure returns the years item, not the empty-requirements item.

## Files

- `app/schemas.py` — quote on a skill mark, preferred marks, gap severity
- `app/services/fit.py` — accept quotes, then score the marks
- `app/services/prompts.py` and `app/services/llm.py` — the screen task, one retry
- `app/services/pipeline.py` — screen, then rewrite or roadmap
- `app/services/facts.py` — severity, order, and the years item
- `app/services/pdf.py` — Ivy League PDF
- `app/main.py` — versions on the CV detail
- `frontend/src/pages/CvDetail.svelte`, `Result.svelte`, `frontend/src/lib/CvSheet.svelte`, `frontend/src/lib/FitStrip.svelte`
- `tests/test_fit.py`, `tests/test_facts.py`, `tests/test_api.py`, `tests/test_pdf.py`
- `AGENTS.md` — say that presence comes from an accepted bullet quote, and that a gap page has major gaps, minor gaps, and a roadmap

Rebuild `frontend/dist` after the page changes. Do not edit `frontend/dist` by hand.
