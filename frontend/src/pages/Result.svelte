<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/session.svelte.js';
  import FitStrip from '../lib/FitStrip.svelte';
  import CvSheet from '../lib/CvSheet.svelte';

  let { id } = $props();
  let row = $state(null);
  let error = $state('');

  onMount(async () => {
    try {
      row = await api(`/api/applications/${id}`);
    } catch (err) {
      error = err.message;
    }
  });

  const suitable = $derived(Boolean(row?.suitable) && row?.result?.kind === 'cv');
  const board = $derived(row?.skill_board || { required: [], preferred: [], matched_preferred: [] });
  const preferred = $derived(
    board.preferred?.length
      ? board.preferred
      : (board.matched_preferred || []).map((name) => ({ name, present: true })),
  );
  const gaps = $derived(row?.result?.report?.gaps || []);
  const majors = $derived(gaps.filter((gap) => gap.severity !== 'minor'));
  const minors = $derived(gaps.filter((gap) => gap.severity === 'minor'));
</script>

<section class="stack">
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
  {#if row}
    <header class="page-head">
      <h1>{row.role_title}</h1>
      {#if suitable}
        <a class="button" href="/api/applications/{row.id}/pdf">Download PDF</a>
      {/if}
    </header>
    <div class="result">
      <FitStrip
        score={row.fit_score}
        {suitable}
        required={board.required || []}
        {preferred}
      />
      <div>
        {#if suitable && row.result?.document}
          <CvSheet document={row.result.document} />
        {:else if row.result?.report}
          <div class="roadmap">
            <h2>What to practice</h2>
            <p class="lede">{row.result.report.summary}</p>
            {#if majors.length}
              <p class="group-label">Major gaps</p>
              {#each majors as gap, index}
                <article class="major">
                  <p class="step">{index + 1}</p>
                  <h3>{gap.skill}</h3>
                  <p>{gap.why_it_matters}</p>
                  <h4>Practice</h4>
                  <p>{gap.practice}</p>
                  <h4>A small project</h4>
                  <p>{gap.project}</p>
                </article>
              {/each}
            {/if}
            {#if minors.length}
              <p class="group-label">Minor gaps</p>
              {#each minors as gap, index}
                <article class="minor">
                  <p class="step">{majors.length + index + 1}</p>
                  <h3>{gap.skill}</h3>
                  <p>{gap.why_it_matters}</p>
                  <h4>Practice</h4>
                  <p>{gap.practice}</p>
                  <h4>A small project</h4>
                  <p>{gap.project}</p>
                </article>
              {/each}
            {/if}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</section>
