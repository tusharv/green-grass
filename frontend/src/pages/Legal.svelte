<script>
  let { page = 'privacy' } = $props();
</script>

<article class="legal">
  {#if page === 'terms'}
    <h1>Terms and conditions</h1>
    <p class="meta">12 October 2026</p>
    <p class="lede">These terms cover use of Job Ready at jobready.tech. The <a href="/privacy">privacy page</a> explains what is stored and who receives it.</p>

    <h2>The service</h2>
    <p>Job Ready compares one CV with one job. If the saved profile clears a fixed bar, you get a fact-checked CV and can download a PDF. If it does not, you get a practice plan for the required skills the work does not show. Wording can change. Employers, titles, dates, degrees, and numbers on the CV stay as they were. The model does not invent experience, and it does not decide which result you get.</p>

    <h2>An account</h2>
    <p>You need an account to upload a CV or run a check. You are responsible for the email and password, and for signing out on a shared computer. Passwords are at least 8 characters.</p>

    <h2>Your material</h2>
    <p>You confirm you have the right to upload the CV and any photo. You keep that right. Job Ready needs permission to store the extracted text, run the check, and, if you publish a link, show that snapshot to anyone who opens it.</p>

    <h2>What a result is</h2>
    <p>A result is a reading of one posting against one profile. It is not a job offer, a promise of an interview, or a reason to list a skill you have not done. A practice plan is for learning. It is not text to paste onto a CV as if the work were already done.</p>

    <h2>Sharing</h2>
    <p>A published profile is public to anyone with the link. It shows your name, the role title, the CV, and the current photo. It does not show the score or the practice plan. Do not publish a link if the CV contains details you do not want someone else to see. You can remove the link later. Deleting the role check removes the link too.</p>

    <h2>Acceptable use</h2>
    <p>Do not use Job Ready to break the law, to probe or disrupt the service, to upload a file you do not have the right to use, or to overload the site. A file that is not a text PDF or DOCX, including a scan, is rejected.</p>

    <h2>The service can change</h2>
    <p>Job Ready can change, pause, or stop. Saved CVs and checks stay available while the service is running and the account is open. These pages can change. The date at the top is the date of the current version. Using the site after that date means you accept the current version.</p>

    <h2>Responsibility</h2>
    <p>Job Ready is offered as it runs today. The check is built to stay honest about the CV you uploaded. It does not promise that an employer will read the CV the same way, or that the site will be available without interruption. To the extent the law allows, Job Ready is not liable for a hiring decision made from a result.</p>
  {:else}
    <h1>Privacy</h1>
    <p class="meta">12 October 2026</p>
    <p class="lede">Job Ready checks one CV against one job. This page says what the site keeps, what it sends on, and what you can remove. Use of the site is also covered by the <a href="/terms">terms and conditions</a>.</p>

    <h2>The account</h2>
    <p>We keep the email you register with and a hash of the password. The password itself is not stored. A session cookie named gg_session keeps you signed in for 14 days. Signing out clears that session. A CSRF token, returned with the session, stops another site from submitting a change as you.</p>

    <h2>The CV</h2>
    <p>The original PDF or DOCX is not stored. We keep the text extracted from it, the file name, and a structured profile: contact details, summary, skills, work history, education, and years of experience. A CV must be a text PDF or DOCX of at most 5 MB, with between 40 and 40,000 characters of text. Scanned pages are rejected.</p>

    <h2>A photo</h2>
    <p>You can upload a JPEG, PNG, or WebP of up to 3 MB. We keep only a 640 pixel square JPEG. The original file and its metadata, including location data, are not kept. If the CV has a GitHub profile link and you have not turned the photo off, the page loads that avatar from GitHub. We do not store the GitHub image. Choosing no photo does not fall back to GitHub. LinkedIn photos are not fetched.</p>

    <h2>The role</h2>
    <p>A role check keeps the title, the job description (at most 20,000 characters), the score, whether the CV cleared the bar, the skill evidence, and the result. A ready result is a rewritten CV. A gap result is a practice plan.</p>

    <h2>Who else receives it</h2>
    <p>To read the CV and the job, the server sends that text to <a href="https://ollama.com/" target="_blank" rel="noopener noreferrer">Ollama</a>, which runs Gemma 4. Job Ready does not use your CV or job text to train a model.</p>
    <p>Employer logos are looked up from the employer name only, through Wikidata and Wikimedia Commons. CV text and contact details are not sent for that lookup. A successful lookup stays in memory on the server for up to 24 hours.</p>
    <p>The site is hosted on <a href="https://render.com/" target="_blank" rel="noopener noreferrer">Render</a>. In production the database is Postgres there. The typefaces on the page are loaded from Google Fonts, so your browser requests those font files from Google.</p>

    <h2>A published profile</h2>
    <p>If you publish an employer link, anyone with that link can see your name, the role title, the CV, and the current photo. A ready result shows the fact-checked CV. A gap result shows the saved profile. The public page has no score, no practice plan, and no PDF. Removing the link, or deleting the role check, takes the page down.</p>

    <h2>Cookies</h2>
    <p>Job Ready uses one session cookie to keep you signed in. There are no advertising or analytics cookies.</p>

    <h2>What you can remove</h2>
    <p>Deleting a CV deletes its role checks, its published links, and its photo. Deleting a role check leaves the CV and removes that check’s published link. Deleting a photo means no photo. The account email remains. Job Ready does not yet offer a control that deletes the account in one step.</p>

    <h2>Changes</h2>
    <p>If this page changes, the date at the top changes with it.</p>
  {/if}
</article>

<style>
  .legal { max-width: 40rem; }
  .legal h1, .legal h2 { font-family: var(--serif); font-weight: 500; letter-spacing: -0.03em; }
  .legal h2 { font-size: 1.45rem; margin: 2rem 0 0.45rem; }
  .legal p { margin: 0.7rem 0 0; color: var(--muted); line-height: 1.7; }
  .legal .lede { margin-top: 0.8rem; }
  .meta { margin-top: 0.35rem; font-size: 0.85rem; }
  .legal a { font-weight: 600; }
</style>
