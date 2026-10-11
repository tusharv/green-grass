<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/session.svelte.js';
  import CvSheet from '../lib/CvSheet.svelte';

  let { id } = $props();
  let cv = $state(null);
  let error = $state('');

  onMount(async () => {
    try {
      cv = await api(`/api/cvs/${id}`);
    } catch (err) {
      error = err.message;
    }
  });
</script>

<section class="stack">
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
  {#if cv}
    <header class="page-head">
      <div>
        <h1>{cv.name}</h1>
        {#if cv.label && cv.label !== cv.name}
          <p class="meta">{cv.label}</p>
        {/if}
      </div>
      <a class="button" href="/apply?cv={cv.id}">Check a role</a>
    </header>
    <CvSheet document={cv.profile} />
    <h2>Roles checked</h2>
    {#if cv.versions?.length}
      <ul class="list">
        {#each cv.versions as version (version.id)}
          <li>
            <div>
              <a href="/applications/{version.id}">{version.role_title}</a>
            </div>
            <div class="outcome">
              <p class={version.suitable ? 'ready' : 'gap'}>{version.suitable ? 'Ready to send' : 'Gaps to close'}</p>
              <p class="outcome-score">{version.fit_score}</p>
            </div>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="empty">No roles checked yet.</p>
    {/if}
  {/if}
</section>
