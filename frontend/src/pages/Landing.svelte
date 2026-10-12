<script>
  import meadow from '../assets/landing-meadow.jpg';
  import workspace from '../assets/landing-workspace.jpg';
  import Icon from '../lib/Icon.svelte';

  const steps = [
    { title: 'Start with your experience.', text: 'Upload your existing CV as a text PDF or DOCX. Job Ready reads your skills, work history, and education.' },
    { title: 'Bring one role into focus.', text: 'Paste the role title and job description. We check the requirements against the experience already on your CV.' },
    { title: 'Know your next step.', text: 'Get a fact-checked CV when you meet the bar, or a focused practice plan when there are gaps to close.' },
  ];
</script>

<div class="landing">
  <section class="landing-hero" aria-labelledby="landing-title">
    <div class="hero-copy">
      <p class="landing-eyebrow">A little clarity for your next chapter</p>
      <h1 id="landing-title">Your next role.<br /><span>An honest next step.</span></h1>
      <p class="hero-description">Turn your CV and one job description into a clearer application or a focused plan to grow.</p>
      <div class="hero-actions">
        <a class="button" href="/register">Create account <Icon name="arrow" size={18} /></a>
        <a class="learn-link" href="#how-it-works">See how it works <span aria-hidden="true">↓</span></a>
      </div>
    </div>
    <figure class="hero-image">
      <img src={meadow} width="1440" height="960" alt="A winding path through a sunlit green meadow toward a lone tree." fetchpriority="high" />
    </figure>
  </section>

  <section class="landing-intro" aria-labelledby="intro-title">
    <h2 id="intro-title">A better application starts<br />with the experience you have.</h2>
    <p>Job Ready helps you see how your CV fits a specific job. It brings your relevant experience forward and makes the missing skills clear, so you can choose your next step with confidence.</p>
  </section>

  <section id="how-it-works" class="landing-process" aria-labelledby="process-title">
    <div class="process-image">
      <img src={workspace} width="1000" height="667" alt="An open notebook, green pen, and coffee on a sunlit desk beside a window." loading="lazy" decoding="async" />
    </div>
    <div class="process-copy">
      <h2 id="process-title">One CV. One role.<br />A clearer way forward.</h2>
      <ol class="process-steps">
        {#each steps as step, index}
          <li>
            <span class="step-number" aria-hidden="true">0{index + 1}</span>
            <div><h3>{step.title}</h3><p>{step.text}</p></div>
          </li>
        {/each}
      </ol>
    </div>
  </section>

  <section class="landing-outcomes" aria-labelledby="outcomes-title">
    <div class="outcomes-heading">
      <h2 id="outcomes-title">Two outcomes. Both move you forward.</h2>
      <p>Useful whether you’re ready to apply or still building the experience.</p>
    </div>
    <div class="outcome-grid">
      <article class="landing-outcome outcome-ready">
        <span class="outcome-icon"><Icon name="ready" size={28} /></span>
        <h3>Ready to send</h3>
        <p>When your CV meets the bar, get a tailored version that puts your relevant experience into clearer words.</p>
        <ul>
          <li>A fit report grounded in your CV</li>
          <li>Your facts preserved, your wording refined</li>
          <li>A clean, professional PDF to download</li>
        </ul>
        <p class="outcome-note">Your experience, presented with purpose.</p>
      </article>
      <article class="landing-outcome outcome-grow">
        <span class="outcome-icon"><Icon name="skills" size={28} /></span>
        <h3>Gaps to close</h3>
        <p>When your CV doesn’t meet the bar yet, get a practical roadmap for the skills or experience you need to build.</p>
        <ul>
          <li>Missing requirements made clear</li>
          <li>The most important gaps first</li>
          <li>Focused ways to practice and improve</li>
        </ul>
        <p class="outcome-note">A practice plan, with no rewritten CV or PDF.</p>
      </article>
    </div>
  </section>

  <section class="landing-principle" aria-labelledby="principle-title">
    <span class="principle-mark" aria-hidden="true"><Icon name="cv" size={30} /></span>
    <h2 id="principle-title">Better wording.<br />Always your real story.</h2>
    <p>Your employers, titles, dates, and qualifications stay yours. Every rewrite is checked against your saved profile. Job Ready won’t invent experience to make a role look like a fit.</p>
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
        <summary>Can I share my CV with an employer?</summary>
        <p>Yes. You can choose to publish an employer link from a role check and remove it later. It shows your CV without your score or practice plan. Ready results also include a downloadable PDF.</p>
      </details>
    </div>
  </section>

  <footer class="landing-footer">
    <p>Job Ready <span>jobready.tech</span></p>
    <a href="/login">Already have an account? Sign in <span aria-hidden="true">↗</span></a>
  </footer>
</div>

<style>
  .landing { --landing-space: clamp(4rem, 8vw, 7rem); }
  .landing h1, .landing h2 { font-family: var(--serif); }
  .landing h2 { font-size: clamp(1.8rem, 3.4vw, 2.65rem); line-height: 1.15; font-weight: 500; letter-spacing: -0.035em; }
  .landing p { color: var(--muted); }
  .landing-hero { padding-top: 1.2rem; }
  .hero-copy { padding: 0.5rem 0 2.6rem; }
  .landing-eyebrow { margin: 0 0 1.3rem; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; }
  .landing h1 { margin: 0; max-width: 100%; font-size: clamp(2.5rem, 5.9vw, 4.6rem); font-weight: 500; line-height: 1.08; letter-spacing: -0.045em; }
  .landing h1 span { color: var(--accent-deep); }
  .hero-description { max-width: 32rem; margin: 1.4rem 0 1.6rem; font-size: 1.12rem; line-height: 1.5; }
  .hero-actions { display: flex; align-items: center; gap: 1.6rem; flex-wrap: wrap; }
  .hero-actions .button { padding: 0.8rem 1.3rem; gap: 1rem; white-space: nowrap; }
  .learn-link { font-weight: 600; font-size: 0.94rem; text-decoration: none; }
  .learn-link:hover { text-decoration: underline; }
  .learn-link span { margin-left: 0.55rem; }
  .hero-image { margin: 0; overflow: hidden; border-radius: var(--radius-surface); }
  .hero-image img { display: block; width: 100%; height: clamp(16rem, 32vw, 27rem); object-fit: cover; object-position: center 35%; }
  .landing-intro { max-width: 42rem; margin: var(--landing-space) auto; text-align: center; }
  .landing-intro h2 { margin: 0 0 1.3rem; }
  .landing-intro p { max-width: 36rem; margin: 0 auto; line-height: 1.75; }
  .landing-process { display: grid; grid-template-columns: 0.95fr 1fr; align-items: center; gap: clamp(2rem, 6vw, 5rem); scroll-margin-top: 2rem; }
  .process-image { align-self: stretch; border-radius: var(--radius-surface); overflow: hidden; }
  .process-image img { display: block; width: 100%; height: 100%; max-height: 36rem; object-fit: cover; }
  .process-copy h2 { margin: 0 0 2.2rem; }
  .process-steps { list-style: none; padding: 0; margin: 0; display: grid; gap: 1.7rem; }
  .process-steps li { display: grid; grid-template-columns: 2rem 1fr; gap: 1rem; }
  .step-number { font-family: var(--serif); font-size: 1.1rem; color: var(--accent); padding-top: 0.05rem; }
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
  .outcome-icon { display: inline-flex; color: var(--accent-deep); margin-bottom: 1.3rem; }
  .landing-outcome h3 { font-family: var(--serif); font-weight: 500; font-size: 1.8rem; letter-spacing: -0.025em; }
  .landing-outcome > p { line-height: 1.65; font-size: 0.98rem; }
  .landing-outcome ul { padding-left: 1.15rem; color: var(--muted); font-size: 0.94rem; line-height: 1.65; display: grid; gap: 0.45rem; margin: 1.5rem 0 1.8rem; }
  .landing-outcome li::marker { color: var(--accent); }
  .landing-outcome .outcome-note { margin: 0; padding-top: 1rem; border-top: 1px solid #cad6cc; font-size: 0.88rem; }
  .landing-principle { padding: var(--landing-space) 0; max-width: 39rem; text-align: center; margin: auto; }
  .principle-mark { display: inline-flex; margin-bottom: 1rem; color: var(--accent); }
  .landing-principle h2 { margin: 0 0 1.3rem; }
  .landing-principle p { margin: 0; line-height: 1.75; }
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
  @media (min-width: 1000px) {
    .hero-copy { position: relative; }
    .hero-description { position: absolute; right: 0; bottom: 3rem; max-width: 18rem; margin: 0; }
    .hero-actions { margin-top: 1.8rem; }
  }
  @media (max-width: 760px) {
    .landing-hero { padding-top: 0.5rem; }
    .hero-copy { padding-bottom: 2rem; }
    .landing-eyebrow { font-size: 0.65rem; letter-spacing: 0.09em; }
    .landing h1 { font-size: clamp(1.75rem, 8.5vw, 3.6rem); }
    .hero-description { font-size: 1.02rem; }
    .hero-actions { gap: 1.1rem; }
    .hero-image img { height: 18rem; }
    .landing-process, .landing-faq { grid-template-columns: 1fr; gap: 2rem; }
    .process-image img { height: 19rem; }
    .outcome-grid { grid-template-columns: 1fr; }
    .landing-footer { align-items: flex-start; flex-direction: column; gap: 1rem; }
    .landing-footer p span { display: block; margin: 0.35rem 0 0; }
  }
  @media (prefers-reduced-motion: no-preference) {
    .hero-copy { animation: arrive 550ms ease-out both; }
    @keyframes arrive { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
  }
</style>
