<script>
  let { sample } = $props();
  const review = $derived(sample.review);
  const score = $derived(Math.round(100 * (0.7 * review.coverage + 0.3 * review.yearsScore)));
  const requiredPresent = $derived(review.required.filter((mark) => mark.present).length);
  const gaps = $derived(review.required.filter((mark) => !mark.present));
</script>

<section class="sample-evaluation stack">
  <p class="sample-banner"><strong>Fictional sample evaluation</strong><span>The profile, role and review below are examples created to show how the assessment works.</span></p>
  <header class="sample-head">
    <div>
      <p class="eyebrow">Sample role check · {sample.job.company}</p>
      <h1>{sample.person}</h1>
      <p class="lede">{sample.job.title}</p>
      <p class="job-description">{sample.job.description}</p>
    </div>
    <a class="button secondary" href="/samples/{sample.key}/profile">View sample profile</a>
  </header>

  <div class="sample-result" class:sample-ready={review.suitable}>
    <div class="sample-verdict"><span aria-hidden="true">{review.suitable ? '✓' : '↗'}</span><div><h2>{review.suitable ? 'Ready to send' : 'Gaps to close'}</h2><p>{review.suitable ? 'Required skills are evidenced and the score clears the bar.' : 'The score is below the readiness bar. Missing required skills are major gaps.'}</p></div></div>
    <div class="sample-score"><strong>{score}</strong><span>/ 100</span><small>Readiness score</small></div>
  </div>

  <section class="sample-card" aria-labelledby="sample-how-title">
    <h2 id="sample-how-title">How this score is calculated</h2>
    <p>Required skill evidence contributes 70 points. Experience contributes 30 points. Ready to send requires at least one required skill and a score above 60. Preferred skills never block readiness.</p>
    <dl class="sample-math"><div><dt>Required skills evidenced</dt><dd>{requiredPresent} / {review.required.length}</dd></div><div><dt>Skill evidence</dt><dd>{(review.coverage * 70).toFixed(1)} / 70</dd></div><div><dt>Experience shown</dt><dd>{review.yearsShown} {review.yearsShown === 1 ? 'year' : 'years'}</dd></div><div><dt>Experience for this role</dt><dd>{review.yearsNeeded} {review.yearsNeeded === 1 ? 'year' : 'years'}</dd></div><div><dt>Experience score</dt><dd>{(review.yearsScore * 30).toFixed(1)} / 30</dd></div></dl>
  </section>

  <section class="sample-card" aria-labelledby="sample-requirements-title">
    <p class="eyebrow">The evidence behind the review</p>
    <h2 id="sample-requirements-title">Job requirement comparison</h2>
    <p class="hint">A skill counts when a work bullet contains a valid quote, or when it appears in the CV skills list. “Not evidenced” describes this sample CV, not a person’s ability.</p>
    <div class="sample-table-wrap"><table class="sample-table"><thead><tr><th scope="col">Requirement</th><th scope="col">Review</th><th scope="col">CV evidence</th></tr></thead><tbody>
      {#each review.required as mark}
        <tr><th scope="row">{mark.name}<small>Required</small></th><td><span class:present={mark.present} class="sample-status">{mark.present ? 'Evidenced' : 'Major gap'}</span></td><td>{#if mark.present && mark.source === 'work'}<blockquote>“{mark.quote}”</blockquote>{:else if mark.present}<p>Listed in CV skills: <strong>{mark.quote}</strong></p>{:else}<p>Not evidenced in this sample CV.</p>{/if}</td></tr>
      {/each}
      {#each review.preferred as mark}
        <tr><th scope="row">{mark.name}<small>Preferred</small></th><td><span class:present={mark.present} class="sample-status">{mark.present ? 'Evidenced' : 'Minor gap'}</span></td><td>{#if mark.present}<blockquote>“{mark.quote}”</blockquote>{:else}<p>Not evidenced in this sample CV.</p>{/if}</td></tr>
      {/each}
    </tbody></table></div>
  </section>

  {#if gaps.length}
    <section class="sample-card sample-next" aria-labelledby="sample-next-title">
      <h2 id="sample-next-title">Practice plan preview</h2>
      <p>These required skills need more evidence or practice for this role:</p>
      <ul>{#each gaps as gap}<li><strong>{gap.name}</strong><span>Build a small project using {gap.name}, then review whether the work matches the role’s needs.</span></li>{/each}</ul>
    </section>
  {/if}
  <p class="sample-disclaimer">All people, employers, job details and experience on this page are fictional examples.</p>
</section>

<style>
  .sample-evaluation { min-width:0; max-width:100%; padding-bottom: 3rem; }
  .sample-evaluation > * { min-width:0; }
  .sample-banner { display:flex; gap:.8rem; align-items:center; padding:.8rem 1rem; margin:0; border-radius:var(--radius-control); color:var(--accent-deep); background:#e6eee7; font-size:.88rem; }
  .sample-banner span { color:var(--muted); }
  .sample-head { display:flex; justify-content:space-between; gap:1.5rem; align-items:center; }
  .sample-head h1 { margin:.2rem 0; font-family:var(--serif); font-size:clamp(2rem,4vw,3rem); font-weight:500; }
  .sample-head .lede { margin:.2rem 0 0; }
  .job-description { max-width:52rem; margin:.6rem 0 0; color:var(--muted); line-height:1.6; }
  .sample-result { display:flex; justify-content:space-between; gap:1.5rem; align-items:center; padding:1.5rem; background:#f5ece7; border-radius:var(--radius-surface); border:1px solid #ead6cd; }
  .sample-result.sample-ready { background:#e6eee7; border-color:#cad6cc; }
  .sample-verdict { display:flex; gap:1rem; align-items:center; }
  .sample-verdict > span { display:grid; place-items:center; width:2.6rem; height:2.6rem; flex:none; border-radius:50%; color:white; background:#86523f; font-size:1.3rem; }
  .sample-ready .sample-verdict > span { background:var(--accent); }
  .sample-verdict h2 { margin:0; font:500 1.6rem/1.2 var(--serif); }
  .sample-verdict p { margin:.4rem 0 0; color:var(--muted); }
  .sample-score { display:grid; grid-template-columns:auto auto; align-items:baseline; gap:.2rem; }
  .sample-score strong { font:500 2.4rem/1 var(--serif); }
  .sample-score > span { color:var(--muted); }
  .sample-score small { grid-column:1/-1; color:var(--muted); text-align:right; }
  .sample-card { padding:clamp(1.2rem,3vw,2rem); background:var(--paper); border:1px solid var(--line); border-radius:var(--radius-surface); }
  .sample-card h2 { margin:0 0 .8rem; font:500 1.6rem/1.2 var(--serif); }
  .sample-card > p { line-height:1.65; }
  .sample-math { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:0; margin:1.2rem 0 0; }
  .sample-math div { display:flex; justify-content:space-between; gap:1rem; padding:.75rem .4rem; border-bottom:1px solid var(--line); }
  .sample-math dt { color:var(--muted); }
  .sample-math dd { margin:0; font-weight:600; text-align:right; }
  .sample-table-wrap { min-width:0; overflow-x:auto; }
  .sample-table { width:100%; border-collapse:collapse; text-align:left; }
  .sample-table th,.sample-table td { padding:.9rem .7rem; vertical-align:top; border-bottom:1px solid var(--line); }
  .sample-table thead th { font-size:.8rem; color:var(--muted); }
  .sample-table tbody th { min-width:8rem; font-weight:600; }
  .sample-table tbody th small { display:block; margin-top:.3rem; color:var(--muted); font-weight:400; }
  .sample-status { display:inline-block; padding:.25rem .5rem; color:#76503f; background:#f5ece7; border-radius:99px; font-size:.82rem; white-space:nowrap; }
  .sample-status.present { color:var(--accent-deep); background:#e6eee7; }
  .sample-table td p { margin:0; color:var(--muted); }
  .sample-table blockquote { margin:0; padding-left:.75rem; border-left:2px solid #c6d5ca; color:var(--muted); line-height:1.6; }
  .sample-next ul { list-style:none; display:grid; gap:.8rem; margin:1rem 0 0; padding:0; }
  .sample-next li { display:grid; gap:.25rem; padding:.9rem; border-radius:var(--radius-control); background:#f6f7f6; }
  .sample-next li span { color:var(--muted); line-height:1.55; }
  .sample-disclaimer { text-align:center; color:var(--muted); font-size:.84rem; }
  @media(max-width:650px) { .sample-head,.sample-result { align-items:flex-start; flex-direction:column; }.sample-head .button { width:100%; justify-content:center; }.sample-math { grid-template-columns:1fr; }.sample-score small { text-align:left; } }
</style>
