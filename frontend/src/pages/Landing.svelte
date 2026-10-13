<script>
  import focusedCv from '../assets/landing-focused-cv.jpg';
  import nextStep from '../assets/landing-build-your-next-step.jpg';
  import chatImage from '../assets/landing-feature-chat.webp';
  import profileImage from '../assets/landing-feature-profile.webp';
  import themesImage from '../assets/landing-feature-themes.webp';
  import pdfImage from '../assets/landing-feature-pdf.webp';
  import Icon from '../lib/Icon.svelte';

  const features = [
    { title: 'Resume review', image: focusedCv, width: 1200, height: 1200, alt: 'Scattered applications become one focused CV beside a role on green steps.', text: 'See which job requirements your experience supports and which skills are missing. Get a clear next step for this role.' },
    { title: 'Themes that feel like you', image: themesImage, width: 1200, height: 800, alt: 'Three paper CV layouts with a fan of green and grey colour swatches.', text: 'Choose from four templates, then adjust colours, fonts and layout. Your saved design carries through to your public profile and eligible PDF.' },
    { title: 'Download as PDF', image: pdfImage, width: 1200, height: 800, alt: 'A finished paper CV in a green document tray beside a download arrow.', text: 'When your result is Ready to send, download a fact-checked CV as a polished PDF, styled with your chosen theme.' },
    { title: 'A plan to close the gaps', image: nextStep, width: 1200, height: 1200, alt: 'A practice workbook and learning blocks build the next step on a green staircase.', text: 'Missing a required skill? Get a focused learning plan, with the most important gaps first and practical ways to build experience.' },
  ];

  const steps = [
    { icon: 'cv', title: 'Bring the work you’ve actually done.', text: 'Upload your existing CV as a text PDF or DOCX. Job Ready reads your skills, work history, and education.' },
    { icon: 'role', title: 'See what this role needs.', text: 'Paste the role title and job description. We check the requirements against the experience already on your CV.' },
    { icon: 'skills', title: 'Apply with clarity. Or build toward it.', text: 'Get a fact-checked CV when you meet the bar, or a focused practice plan when there are gaps to close.' },
  ];
</script>

<div class="landing">
  <section class="landing-hero" aria-labelledby="landing-title">
    <div class="hero-copy">
      <p class="landing-eyebrow">Applying, but hearing nothing?</p>
      <h1 id="landing-title">Show why you fit.<br /><span>One role at a time.</span></h1>
      <p class="hero-description">Your experience matters. Compare it with one role, then get a fact-checked CV that shows your fit or a plan to build what’s missing.</p>
      <div class="hero-actions">
        <a class="button" href="/register">Check your CV <Icon name="arrow" size={18} /></a>
        <a class="learn-link" href="#how-it-works">See how it works <span aria-hidden="true">↓</span></a>
      </div>
    </div>
    <figure class="hero-image">
      <svg class="hero-steps" viewBox="0 0 160 160" fill="none" aria-hidden="true"><path d="M10 150V80H80V10H150" stroke="currentColor" stroke-width="14" stroke-linejoin="round" stroke-linecap="round" /></svg>
      <img src={focusedCv} width="1200" height="1200" alt="Job Ready’s steps logo on a green staircase, carrying scattered applications toward one focused CV and role." fetchpriority="high" />
    </figure>
  </section>

  <section id="features" class="landing-features" aria-labelledby="features-title">
    <div class="features-heading">
      <h2 id="features-title">Review it. Refine it. Make it yours.</h2>
      <p>From understanding your fit to sharing your experience, keep your next application in one place.</p>
    </div>
    <div class="feature-spotlights">
      <article class="feature-spotlight">
        <img src={chatImage} width="1200" height="800" alt="Paper conversation bubbles beside a CV with an approval seal." loading="lazy" decoding="async" />
        <div class="spotlight-copy">
          <h3>AI updates through chat</h3>
          <p>Tell Job Ready about work your CV is missing. Get proposed edits to your summary, skills and work bullets, then confirm they’re accurate before applying them.</p>
          <span class="feature-detail">Private chat. You approve every update.</span>
        </div>
      </article>
      <article class="feature-spotlight">
        <img src={profileImage} width="1200" height="800" alt="An upright paper profile with interlocking links for sharing." loading="lazy" decoding="async" />
        <div class="spotlight-copy">
          <h3>A public profile, ready to share</h3>
          <p>Give employers a link to your CV, with your chosen design and photo. They see your experience; your assessment, practice plan and chat stay private.</p>
          <span class="feature-detail">Publish when you choose. Remove the link anytime.</span>
        </div>
      </article>
    </div>
    <div class="feature-grid">
      {#each features as feature}
        <article class="feature-item">
          <div class="feature-image"><img src={feature.image} width={feature.width} height={feature.height} alt={feature.alt} loading="lazy" decoding="async" /></div>
          <h3>{feature.title}</h3>
          <p>{feature.text}</p>
        </article>
      {/each}
    </div>
  </section>

  <section class="landing-intro" aria-labelledby="intro-title">
    <div class="journey" aria-label="Your CV and a role lead to a clearer next step">
      <span><Icon name="cv" size={24} /> Your CV</span>
      <span class="journey-join" aria-hidden="true">+</span>
      <span><Icon name="role" size={24} /> One role</span>
      <span class="journey-line" aria-hidden="true"></span>
      <span class="journey-result"><Icon name="skills" size={24} /> Your next step</span>
    </div>
    <h2 id="intro-title">Silence isn’t a verdict<br />on your experience.</h2>
    <p>A generic CV can make relevant work easy to miss. Sending more applications may not fix that. Start with one role and make the experience that matters easier to see.</p>
  </section>

  <section id="how-it-works" class="landing-process" aria-labelledby="process-title">
    <div class="process-image">
      <img src={nextStep} width="1200" height="1200" alt="A practice workbook and learning blocks on a staircase branded with the Job Ready steps logo, with a new step ready to build." loading="lazy" decoding="async" />
    </div>
    <div class="process-copy">
      <h2 id="process-title">Before you apply,<br />make the connection.</h2>
      <ol class="process-steps">
        {#each steps as step}
          <li>
            <span class="step-number"><Icon name={step.icon} size={22} /></span>
            <div><h3>{step.title}</h3><p>{step.text}</p></div>
          </li>
        {/each}
      </ol>
    </div>
  </section>

  <section class="landing-outcomes" aria-labelledby="outcomes-title">
    <div class="outcomes-heading">
      <h2 id="outcomes-title">Two outcomes. Both move you forward.</h2>
      <p>Leave with something you can use: a CV to send or a plan to work on.</p>
    </div>
    <div class="outcome-grid">
      <article class="landing-outcome outcome-ready">
        <div class="outcome-art" aria-hidden="true">
          <svg viewBox="0 0 280 120" fill="none">
            <rect x="64" y="8" width="148" height="104" rx="8" fill="var(--paper)" stroke="currentColor" stroke-width="1.5" />
            <g transform="translate(176 21) scale(.6)"><rect width="32" height="32" rx="7" fill="var(--accent)" /><path d="M9 23V16H16V9H23" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" /></g>
            <path d="M84 30H154M84 42H126" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
            <path d="M84 62H184M84 74H172M84 86H184" stroke="currentColor" stroke-opacity=".3" stroke-width="3" stroke-linecap="round" />
            <circle cx="212" cy="82" r="26" fill="var(--accent)" />
            <path d="M200 82L208 90L225 73" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        <h3>Ready to send</h3>
        <p>When your CV meets the bar, make your relevant work easier to spot. Get a tailored CV grounded in the experience you already have.</p>
        <ul>
          <li>A fit report grounded in your CV</li>
          <li>Your facts preserved, your wording refined</li>
          <li>A clean, professional PDF to download</li>
        </ul>
        <p class="outcome-note">Same experience. A clearer story for this role.</p>
      </article>
      <article class="landing-outcome outcome-grow">
        <div class="outcome-art" aria-hidden="true">
          <svg viewBox="0 0 280 120" fill="none">
            <path d="M44 108V76H108V44H172V12H236" stroke="currentColor" stroke-opacity=".18" stroke-width="16" stroke-linejoin="round" />
            <circle cx="76" cy="76" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5" />
            <circle cx="140" cy="44" r="15" fill="var(--paper)" stroke="currentColor" stroke-width="1.5" />
            <g transform="translate(190 0) scale(.85)"><rect width="32" height="32" rx="7" fill="var(--accent)" /><path d="M9 23V16H16V9H23" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" /></g>
            <path d="M70 76H82M76 70V82M134 44H146M140 38V50" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </div>
        <h3>Gaps to close</h3>
        <p>You don’t have to fit every role. When there are gaps, see what matters most and get practical ways to build toward the job.</p>
        <ul>
          <li>Missing requirements made clear</li>
          <li>The most important gaps first</li>
          <li>Focused ways to practice and improve</li>
        </ul>
        <p class="outcome-note">Build the missing skills, one practical step at a time.</p>
      </article>
    </div>
  </section>

  <section id="samples" class="landing-samples" aria-labelledby="samples-title">
    <div class="outcomes-heading">
      <h2 id="samples-title">See a sample profile and review.</h2>
      <p>Explore two fictional applications, from shared profile to the evidence behind the result.</p>
    </div>
    <div class="sample-grid">
      <article class="sample-card sample-ready">
        <div><span class="sample-kicker">FICTIONAL SAMPLE</span><h3>Frontend Developer</h3><p>See how relevant experience supports a Ready to send result.</p></div>
        <div class="sample-links"><a href="/samples/ready/profile">View sample profile <Icon name="arrow" size={16} /></a><a href="/samples/ready/evaluation">View sample evaluation <Icon name="arrow" size={16} /></a></div>
      </article>
      <article class="sample-card sample-gaps">
        <div><span class="sample-kicker">FICTIONAL SAMPLE</span><h3>Data Analyst</h3><p>See how missing requirements and experience lead to Gaps to close.</p></div>
        <div class="sample-links"><a href="/samples/gaps/profile">View sample profile <Icon name="arrow" size={16} /></a><a href="/samples/gaps/evaluation">View sample evaluation <Icon name="arrow" size={16} /></a></div>
      </article>
    </div>
  </section>

  <section class="landing-principle" aria-labelledby="principle-title">
    <span class="principle-mark" aria-hidden="true"><Icon name="cv" size={30} /></span>
    <h2 id="principle-title">Make your relevance clear.<br />Keep your story true.</h2>
    <p>Tailoring means helping an employer see the connection between your work and their role. Your employers, titles, dates, and qualifications stay yours. Every rewrite is checked against your saved profile. No invented skills, projects, or numbers.</p>
    <a class="article-link" href="https://peerlist.io/tusharv/articles/applying-everywhere-but-not-getting-replies">Read why we built Job Ready <Icon name="arrow" size={16} /></a>
  </section>

  <section class="landing-faq" aria-labelledby="faq-title">
    <h2 id="faq-title">A few things to know.</h2>
    <div class="faq-items">
      <details>
        <summary>What kind of CV can I upload?</summary>
        <p>A text PDF or DOCX up to 5 MB. Your CV needs selectable text; scanned documents and image-only PDFs aren’t supported.</p>
      </details>
      <details>
        <summary>What happens to my original file?</summary>
        <p>The original upload isn’t stored. Job Ready saves the extracted text and a structured profile so you can check your experience against different roles.</p>
      </details>
      <details>
        <summary>Does AI decide whether I’m ready?</summary>
        <p>No. Fixed rules check your skills and experience against the job requirements. AI helps read the documents and write the result, but it doesn’t decide which outcome you get.</p>
      </details>
      <details>
        <summary>Can I update my CV through chat?</summary>
        <p>Yes. Use the private chat on a role check to describe your experience. AI proposes changes to your summary, skills and existing work bullets. Nothing is applied until you confirm the edits are accurate. Applying them updates your saved CV and reassesses that role.</p>
      </details>
      <details>
        <summary>Can I change how my CV looks?</summary>
        <p>Choose Classic, Modern, Creative or Minimal, then customise colours, fonts, spacing and your photo. Save the design for that role check to update its public profile and any eligible PDF download. A PDF is available only for a Ready to send result.</p>
      </details>
      <details>
        <summary>Can I share my CV with an employer?</summary>
        <p>Yes. You can choose to publish an employer link from a role check and remove it later. It shows your CV without your score or practice plan. Ready results also include a downloadable PDF.</p>
      </details>
    </div>
  </section>

  <footer class="landing-footer">
    <p>Job Ready <span>One step ahead in your job search.</span></p>
    <a href="/login">Already have an account? Sign in <span aria-hidden="true">↗</span></a>
  </footer>
</div>

<style>
  .landing { --landing-space: clamp(4rem, 8vw, 7rem); }
  .landing h1, .landing h2 { font-family: var(--serif); }
  .landing h2 { font-size: clamp(1.8rem, 3.4vw, 2.65rem); line-height: 1.15; font-weight: 500; letter-spacing: -0.035em; }
  .landing p { color: var(--muted); }
  .landing-hero { padding: 2.8rem 0 1rem; display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; }
  .hero-copy { padding: 1rem 0; }
  .landing-eyebrow { margin: 0 0 1.3rem; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; }
  .landing h1 { margin: 0; max-width: 100%; font-size: clamp(2.3rem, 4.2vw, 3.6rem); font-weight: 500; line-height: 1.08; letter-spacing: -0.045em; }
  .landing h1 span { color: var(--accent-deep); }
  .hero-description { max-width: 32rem; margin: 1.4rem 0 1.6rem; font-size: 1.12rem; line-height: 1.5; }
  .hero-actions { display: flex; align-items: center; gap: 1.6rem; flex-wrap: wrap; }
  .hero-actions .button { padding: 0.8rem 1.3rem; gap: 1rem; white-space: nowrap; }
  .learn-link { font-weight: 600; font-size: 0.94rem; text-decoration: none; }
  .learn-link:hover { text-decoration: underline; }
  .learn-link span { margin-left: 0.55rem; }
  .hero-image { margin: 0; position: relative; padding: 0 0 1.5rem 1.5rem; }
  .hero-steps { position: absolute; width: 8rem; height: 8rem; left: -0.6rem; bottom: 0; color: #c5dbce; }
  .hero-image img { position: relative; display: block; width: 100%; height: auto; aspect-ratio: 1; object-fit: contain; border-radius: var(--radius-surface); }
  .landing-features { margin-top: var(--landing-space); scroll-margin-top: 2rem; }
  .features-heading { max-width: 42rem; margin-bottom: 2.2rem; }
  .features-heading h2 { margin: 0 0 1rem; }
  .features-heading p { margin: 0; max-width: 35rem; line-height: 1.65; }
  .feature-spotlights { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1.5rem; }
  .feature-spotlight { min-width: 0; overflow: hidden; border: 1px solid var(--line); border-radius: var(--radius-surface); background: var(--paper); }
  .feature-spotlight > img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 2; object-fit: contain; }
  .spotlight-copy { padding: clamp(1.3rem, 3vw, 2rem); }
  .spotlight-copy h3 { font-family: var(--serif); font-size: clamp(1.5rem, 2.5vw, 1.9rem); font-weight: 500; letter-spacing: -0.025em; margin: 0 0 0.8rem; line-height: 1.2; }
  .spotlight-copy p { font-size: 0.98rem; line-height: 1.7; margin: 0 0 1.3rem; }
  .feature-detail { display: block; color: var(--accent-deep); font-size: 0.82rem; line-height: 1.6; font-weight: 600; }
  .feature-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1.5rem; margin-top: 2.5rem; }
  .feature-item { min-width: 0; }
  .feature-image { background: #f6f7f6; border-radius: var(--radius-surface); overflow: hidden; aspect-ratio: 1; }
  .feature-image img { display: block; width: 100%; height: 100%; object-fit: contain; }
  .feature-item h3 { font-size: 1.06rem; line-height: 1.4; margin: 1.2rem 0 0.6rem; font-weight: 600; }
  .feature-item p { font-size: 0.9rem; line-height: 1.7; margin: 0; }
  @media (max-width: 1000px) { .feature-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 2rem 1.5rem; } }
  @media (max-width: 600px) {
    .feature-spotlights, .feature-grid { grid-template-columns: minmax(0, 1fr); }
    .feature-grid { gap: 2rem; }
    .feature-image { aspect-ratio: 3 / 2; }
  }
  .landing-intro { max-width: 48rem; margin: var(--landing-space) auto; text-align: center; }
  .landing-intro h2 { margin: 0 0 1.3rem; }
  .landing-intro p { max-width: 36rem; margin: 0 auto; line-height: 1.75; }
  .landing-process { display: grid; grid-template-columns: 0.95fr 1fr; align-items: center; gap: clamp(2rem, 6vw, 5rem); scroll-margin-top: 2rem; }
  .process-image { align-self: center; border-radius: var(--radius-surface); overflow: hidden; }
  .process-image img { display: block; width: 100%; height: auto; aspect-ratio: 1; object-fit: contain; }
  .process-copy h2 { margin: 0 0 2.2rem; }
  .process-steps { list-style: none; padding: 0; margin: 0; display: grid; gap: 1.7rem; }
  .process-steps li { position: relative; display: grid; grid-template-columns: 2.8rem 1fr; gap: 1rem; }
  .process-steps li:not(:last-child)::after { content: ""; position: absolute; top: 2.8rem; bottom: -1.7rem; left: 1.35rem; border-left: 1px solid var(--line); }
  .step-number { display: grid; place-items: center; width: 2.8rem; height: 2.8rem; border: 1px solid var(--line); border-radius: 50%; color: var(--accent); background: var(--canvas); }
  .process-steps h3 { font-family: var(--sans); font-size: 1.08rem; font-weight: 600; margin: 0 0 0.4rem; }
  .process-steps p { margin: 0; font-size: 0.96rem; line-height: 1.65; }
  .landing-outcomes { margin-top: var(--landing-space); }
  .outcomes-heading { max-width: 42rem; margin-bottom: 2rem; }
  .outcomes-heading h2 { margin: 0 0 0.8rem; }
  .outcomes-heading p { margin: 0; }
  .outcome-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
  .landing-outcome { border-radius: var(--radius-surface); padding: clamp(1.5rem, 3.5vw, 2.8rem); }
  .outcome-ready { background: #e6eee7; }
  .outcome-grow { background: #edf0ec; }
  .landing-samples { margin-top: var(--landing-space); }
  .sample-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:1.2rem; }
  .sample-card { display:flex; flex-direction:column; justify-content:space-between; gap:1.5rem; padding:clamp(1.5rem,3.5vw,2.4rem); border:1px solid var(--line); border-radius:var(--radius-surface); background:#f4f7f4; }
  .sample-gaps { background:#f7f3f0; }
  .sample-kicker { color:var(--accent-deep); font-size:.7rem; font-weight:700; letter-spacing:.09em; }
  .sample-card h3 { margin:.8rem 0 .5rem; font:500 1.8rem/1.2 var(--serif); }
  .sample-card p { margin:0; max-width:30rem; line-height:1.65; }
  .sample-links { display:flex; gap:.8rem 1.5rem; flex-wrap:wrap; padding-top:1rem; border-top:1px solid var(--line); }
  .sample-links a { display:inline-flex; align-items:center; gap:.45rem; font-weight:600; font-size:.9rem; }
  .outcome-art { color: var(--accent-deep); height: 8rem; margin: 0 0 1.6rem; }
  .outcome-art svg { display: block; width: 100%; height: 100%; }
  .landing-outcome h3 { font-family: var(--serif); font-weight: 500; font-size: 1.8rem; letter-spacing: -0.025em; }
  .landing-outcome > p { line-height: 1.65; font-size: 0.98rem; }
  .landing-outcome ul { padding-left: 1.15rem; color: var(--muted); font-size: 0.94rem; line-height: 1.65; display: grid; gap: 0.45rem; margin: 1.5rem 0 1.8rem; }
  .landing-outcome li::marker { color: var(--accent); }
  .landing-outcome .outcome-note { margin: 0; padding-top: 1rem; border-top: 1px solid #cad6cc; font-size: 0.88rem; }
  .landing-principle { padding: var(--landing-space) 0; max-width: 39rem; text-align: center; margin: auto; }
  .principle-mark { display: inline-flex; margin-bottom: 1rem; color: var(--accent); }
  .landing-principle h2 { margin: 0 0 1.3rem; }
  .landing-principle p { margin: 0; line-height: 1.75; }
  .article-link { display: inline-flex; align-items: center; gap: 0.5rem; margin-top: 1.5rem; font-size: 0.95rem; font-weight: 600; }
  .landing-faq { display: grid; grid-template-columns: 0.8fr 1.2fr; gap: 3rem; padding-top: 2.6rem; border-top: 1px solid var(--line); }
  .landing-faq h2 { margin: 0; font-size: 2rem; }
  .faq-items details { border-bottom: 1px solid var(--line); }
  .faq-items summary { padding: 1.15rem 1.5rem 1.15rem 0; cursor: pointer; font-weight: 600; list-style: none; position: relative; }
  .faq-items details:first-child summary { padding-top: 0.2rem; }
  .faq-items summary::-webkit-details-marker { display: none; }
  .faq-items summary::after { content: '+'; position: absolute; right: 0; color: var(--accent); font-size: 1.25rem; font-weight: 400; line-height: 1.2; }
  .faq-items details[open] summary::after { content: '−'; }
  .faq-items p { margin: 0 1.5rem 1.2rem 0; font-size: 0.94rem; line-height: 1.7; }
  .landing-footer { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; padding-top: 2rem; margin-top: var(--landing-space); border-top: 1px solid var(--line); font-size: 0.85rem; }
  .landing-footer p { margin: 0; color: var(--ink); font-weight: 600; }
  .landing-footer p span { margin-left: 1rem; font-weight: 400; color: var(--muted); }
  .landing-footer a { text-decoration: none; }
  .landing-footer a:hover { text-decoration: underline; }
  .journey { display: flex; align-items: center; justify-content: center; gap: 1rem; margin: 0 auto 3rem; }
  .journey > span:not(.journey-join):not(.journey-line) { display: inline-flex; align-items: center; gap: 0.6rem; font-size: 0.95rem; font-weight: 600; white-space: nowrap; }
  .journey-result { padding: 0.8rem 1rem; border-radius: var(--radius-control); background: #e6eee7; color: var(--accent-deep); }
  .journey-join { color: var(--muted); font-size: 1.3rem; }
  .journey-line { width: 3rem; border-top: 1px solid var(--accent); }
  .landing-principle { position: relative; }
  .principle-mark { padding: 1rem; border: 1px solid var(--line); border-radius: var(--radius-surface); background: #e6eee7; }
  @media (min-width: 761px) and (max-width: 1100px) {
    .landing-hero { gap: 1.3rem; }
    .landing h1 { font-size: 3.5vw; }
    .hero-actions { gap: 1rem; }
  }
  @media (max-width: 760px) {
    .landing-hero { padding-top: 0.5rem; grid-template-columns: 1fr; gap: 0.5rem; }
    .hero-copy { padding-bottom: 2rem; }
    .landing-eyebrow { font-size: 0.65rem; letter-spacing: 0.09em; }
    .landing h1 { font-size: clamp(1.75rem, 8.5vw, 3.6rem); }
    .hero-description { font-size: 1.02rem; }
    .hero-actions { gap: 1.1rem; }
    .hero-image img { height: auto; aspect-ratio: 1; }
    .hero-image { padding-left: 1rem; padding-bottom: 1rem; }
    .hero-steps { width: 6rem; height: 6rem; left: 0; }
    .journey { display: grid; grid-template-columns: auto auto auto; gap: 0.55rem 1rem; max-width: 23rem; margin-bottom: 2rem; }
    .journey-line { grid-column: 2; grid-row: 2; justify-self: center; height: 1.2rem; width: 0; border-top: 0; border-left: 1px solid var(--accent); }
    .journey-result { grid-column: 1 / -1; grid-row: 3; justify-self: center; }
    .journey > span:not(.journey-join):not(.journey-line) { font-size: 0.85rem; }
    .landing-process, .landing-faq { grid-template-columns: 1fr; gap: 2rem; }
    .process-image img { height: auto; min-height: 0; aspect-ratio: 1; }
    .outcome-grid, .sample-grid { grid-template-columns: 1fr; }
    .landing-footer { align-items: flex-start; flex-direction: column; gap: 1rem; }
    .landing-footer p span { display: block; margin: 0.35rem 0 0; }
  }
  @media (prefers-reduced-motion: no-preference) {
    .hero-copy { animation: arrive 550ms ease-out both; }
    @keyframes arrive { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  }
</style>
