<script>
  let { plans = [], summary = '', pending = false, error = '', incomplete = false, onretry = () => {} } = $props();
</script>

<section class="roadmap" aria-labelledby="learning-title">
  <div>
    <p class="eyebrow">AI learning roadmap</p>
    <h2 id="learning-title" class="artifact-heading"><span aria-hidden="true">↗</span> Your upskilling plan</h2>
    <p class="lede">{summary || 'Build evidence for the gaps below, one practical task at a time.'}</p>
    <p class="hint">These are learning suggestions, not skills already demonstrated on your CV.</p>
  </div>
  {#if pending}
    <p class="hint" role="status">Creating a learning plan from your CV, this job, and the missing skills…</p>
  {:else if error}
    <div role="alert"><p>{error}</p><button type="button" class="button secondary" onclick={onretry}>Retry AI learning plan</button></div>
  {:else if incomplete}
    <div><p class="hint">The saved plan is missing learning steps or materials. Ask AI to expand it using your CV and this job.</p><button type="button" class="button secondary" onclick={onretry}>Expand AI learning plan</button></div>
  {/if}
  {#each plans as gap, index}
    {#if index === 0 || gap.severity !== plans[index - 1].severity}
      <p class="group-label">{gap.severity === 'minor' ? 'Preferred skills · Build on your progress' : 'Major gaps · Start here'}</p>
    {/if}
    <article class:major={gap.severity !== 'minor'} class:minor={gap.severity === 'minor'} id="gap-plan-{index}" aria-labelledby="gap-title-{index}">
      <p class="step">{index + 1}</p>
      <h3 id="gap-title-{index}">{gap.skill}</h3>
      <p>{gap.why_it_matters}</p>
      {#if gap.learn.length}
        <h4>What to learn</h4>
        <ol class="learning-steps">{#each gap.learn as step}<li>{step}</li>{/each}</ol>
      {/if}
      <h4>Practice task</h4>
      <p>{gap.practice}</p>
      <h4>{gap.resources.length ? 'Mini-project' : 'Next step'}</h4>
      <p>{gap.project}</p>
      {#if gap.verify}
        <h4>Check your work</h4>
        <p>{gap.verify}</p>
      {/if}
      {#if gap.resources.length}
        <div class="learning-materials">
          <h4>Learning materials</h4>
          <ul>{#each gap.resources as resource}<li><a href={resource.url} target="_blank" rel="noopener noreferrer">{resource.title} <span aria-hidden="true">↗</span><span class="sr-only"> (opens in a new tab)</span></a></li>{/each}</ul>
          <p class="hint">Suggested by AI. Links and course availability have not been independently verified.</p>
        </div>
      {/if}
    </article>
  {/each}
</section>

<style>
  article { scroll-margin-top: 2rem; }
  article:target { outline: 2px solid var(--accent); outline-offset: 3px; }
  .learning-steps, .learning-materials { grid-column: 2; }
  .learning-steps { padding-left: 1.2rem; margin: 0.25rem 0; }
  .learning-steps li + li { margin-top: 0.5rem; }
  .learning-materials { margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid var(--line); }
  .learning-materials h4 { margin-top: 0; }
  .learning-materials ul { list-style: none; padding: 0; margin: 0.5rem 0; display: grid; gap: 0.6rem; }
  .learning-materials li { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.3rem 0.8rem; }
  .learning-materials a { overflow-wrap: anywhere; }
</style>
