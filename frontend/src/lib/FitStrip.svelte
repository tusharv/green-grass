<script>
  let { score = 0, suitable = false, required = [], preferred = [], yearsShown = null, yearsNeeded = null, yearsScore = null, coverage = null, hasPlan = false } = $props();
  const explained = $derived(coverage != null && yearsScore != null);
</script>

<aside class="fit-strip" aria-label="Fit for this role">
  <span class="verdict-icon" aria-hidden="true">{suitable ? '✓' : '↗'}</span>
  <p class="verdict">{suitable ? 'Ready to send' : 'Gaps to close'}</p>
  <p class="verdict-note">{suitable ? 'Your experience gives you a foundation to apply.' : 'A clear next step for your development.'}</p>
  <p class="score">{score}<span> / 100</span></p>
  <p class="score-label">Readiness score</p>
  <details class="score-explanation">
    <summary>How this is assessed</summary>
    <p>Required skill evidence contributes 70 points. Experience contributes 30 points. The combined score is rounded.</p>
    {#if explained}
      <dl><div><dt>Skill evidence</dt><dd>{(coverage * 70).toFixed(1)} / 70</dd></div><div><dt>Experience</dt><dd>{(yearsScore * 30).toFixed(1)} / 30</dd></div></dl>
    {/if}
    <p>Ready to send needs at least one required skill in the posting and a score above 60. Preferred skills do not affect the score.</p>
  </details>
  {#if yearsShown != null && yearsNeeded != null}
    <div class="experience-review">
      <h2>Experience in context</h2>
      <p><strong>{yearsShown} years</strong> shown on the CV</p>
      <p>{#if yearsNeeded > 0}<strong>{yearsNeeded} years</strong> used for this role{:else}No minimum years required{/if}</p>
      <small>The higher of the posting’s minimum and its seniority level is used. Missing years count as zero.</small>
    </div>
  {/if}
  <nav class="review-nav" aria-label="Review sections">
    <a href="#review-title">Role overview <span aria-hidden="true">→</span></a>
    {#if required.length || preferred.length}<a href="#comparison-title">Requirement comparison <span aria-hidden="true">→</span></a>{/if}
    {#if hasPlan}<a href="#learning-title">Your upskilling plan <span aria-hidden="true">→</span></a>{/if}
    {#if suitable}<a href="#next-step">Your tailored CV <span aria-hidden="true">→</span></a>{/if}
  </nav>
</aside>
