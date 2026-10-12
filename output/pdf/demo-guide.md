# Job Ready demo

All people, employers, schools, and vacancies in this pack are fictional.

1. Upload `demo-cv-alex-morgan.pdf` once.
2. Apply with the same saved CV using the title **Backend Developer** and the description in `role-1-ready-to-send.txt` (omit its first Role title line).
3. Expected: **Ready to send**, a tailored CV, and a PDF download. Four required skills have direct work-bullet evidence. pytest and Git are supported preferred skills.
4. Apply again with the same saved CV using the title **Senior Cloud Platform Engineer** and the description in `role-2-gaps-to-close.txt` (omit its first Role title line).
5. Expected: **Gaps to close**, a practice roadmap, and no tailored CV or PDF. Major gaps: AWS, Kubernetes, Terraform, Prometheus. Minor gaps: Helm and Argo CD.

## Validation and limits

The CV states 4 years of experience, with consistent July 2022-June 2026 dates. Against the intended extracted requirements and full-bullet evidence, the app's scoring function gives the first role 100 and suitable=true; the second role 24 and suitable=false. These are internal validation values, not a demo match-percentage pitch.

Live extraction, screening, and writing still depend on the configured model and server API key. The fixtures do not bypass those steps. The second role is deliberately distinct from the CV to make the gap branch robust. The experience shortfall is not a separate years-only roadmap item because required skills are also missing.
