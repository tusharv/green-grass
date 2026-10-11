<script>
  let { required = [], preferred = [], suitable = false } = $props();
  const strengths = $derived(required.filter((mark) => mark.present));
  const extras = $derived(preferred.filter((mark) => mark.present));
  const missing = $derived(required.filter((mark) => !mark.present));
  const optional = $derived(preferred.filter((mark) => !mark.present));
</script>

<section class="review-card" aria-labelledby="review-title">
  <div class="review-heading">
    <span class="review-icon" aria-hidden="true">◎</span>
    <div><p class="eyebrow">Your role review</p><h2 id="review-title">Where your experience connects</h2></div>
  </div>
  <p class="review-intro">
    {#if !required.length}
      This posting needs clearer requirements before we can assess your CV. Try a description that names the skills the role needs.
    {:else if suitable}
      Your CV clears the readiness bar for this role. Use the evidence below to see what supports your application{missing.length || optional.length ? ' and where you can still develop' : ''}.
    {:else}
      This CV does not yet clear the readiness bar for this role. Start with the evidence below, then use your practice plan to work towards the requirements.
    {/if}
  </p>
  <dl class="review-counts">
    <div><dt>Required skills evidenced</dt><dd>{strengths.length}<span> / {required.length}</span></dd></div>
    <div><dt>Required skill gaps</dt><dd>{missing.length}</dd></div>
    <div><dt>Preferred skill gaps</dt><dd>{optional.length}</dd></div>
  </dl>
  {#if strengths.length || extras.length}
    <div class="strengths">
      {#if strengths.length}
        <h3><span aria-hidden="true">✓</span> Demonstrated strengths</h3>
        <ul class="skill-tags">{#each strengths as mark}<li>{mark.name}</li>{/each}</ul>
      {/if}
      {#if extras.length}
        <h3>Also on the CV</h3>
        <ul class="skill-tags secondary-tags">{#each extras as mark}<li>{mark.name}</li>{/each}</ul>
      {/if}
    </div>
  {/if}
</section>

{#if required.length || preferred.length}
  <section class="review-card evidence-card" aria-labelledby="comparison-title">
    <div class="review-heading">
      <span class="review-icon" aria-hidden="true">≡</span>
      <div><p class="eyebrow">The evidence behind the review</p><h2 id="comparison-title">Job requirement comparison</h2></div>
    </div>
    <p class="hint">Evidence is quoted from your work history, or matched to your CV skills list. “Not evidenced” describes this CV, not your ability.</p>
    <!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users need to scroll the comparison on narrow screens.) -->
    <div class="evidence-scroll" tabindex="0" role="region" aria-label="Job requirements and CV evidence">
      <table class="evidence-table">
        <caption class="sr-only">Required and preferred skills compared with work-history evidence</caption>
        <thead><tr><th scope="col">Requirement</th><th scope="col">Review</th><th scope="col">CV evidence</th></tr></thead>
        <tbody>
          {#each [{ label: 'Required', marks: required }, { label: 'Preferred', marks: preferred }] as group}
            {#each group.marks as mark}
              <tr>
                <th scope="row">{mark.name}<small>{group.label}</small></th>
                <td><span class:status-present={mark.present} class:status-gap={!mark.present} class="evidence-status"><span aria-hidden="true">{mark.present ? '✓' : '↗'}</span> {mark.present ? 'Evidenced' : group.label === 'Required' ? 'Major gap' : 'Minor gap'}</span></td>
                <td>{#if mark.present && mark.source === 'skills'}<p class="hint">Listed in your CV skills: <strong>{mark.quote}</strong>. No work bullet shows it yet.</p>{:else if mark.present && mark.quote}<blockquote>{mark.quote}</blockquote>{:else if mark.present}<p class="hint">Evidence quote unavailable for this saved review. Check the role again to see it.</p>{:else}<p class="hint">Not evidenced in your CV.</p>{/if}</td>
              </tr>
            {/each}
          {/each}
        </tbody>
      </table>
    </div>
    <p class="evidence-note">Preferred skills add context and never block readiness. Required skill gaps remain visible even when your overall result is ready to send.</p>
  </section>
{/if}
