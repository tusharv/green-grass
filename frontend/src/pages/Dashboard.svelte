<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/session.svelte.js';

  let cvs = $state([]);
  let applications = $state([]);
  let error = $state('');

  onMount(async () => {
    try {
      [cvs, applications] = await Promise.all([api('/api/cvs'), api('/api/applications')]);
    } catch (err) {
      error = err.message;
    }
  });

  function when(value) {
    return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }
</script>

<section class="stack">
  <header class="page-head">
    <h1>Your CVs</h1>
    <a class="button" href="/cvs/new">Upload a CV</a>
  </header>
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
  {#if cvs.length === 0}
    <p class="empty">Upload a CV to check it against a role.</p>
  {:else}
    <ul class="list">
      {#each cvs as cv (cv.id)}
        <li>
          <div>
            <a href="/cvs/{cv.id}">{cv.name}</a>
            {#if cv.label && cv.label !== cv.name}
              <p>{cv.label}</p>
            {/if}
            <p class="meta">{when(cv.created_at)}</p>
          </div>
          <a class="button secondary" href="/apply?cv={cv.id}">Check a role</a>
        </li>
      {/each}
    </ul>
  {/if}

  <h2>Roles checked</h2>
  {#if applications.length === 0}
    <p class="empty">No roles checked yet.</p>
  {:else}
    <ul class="list">
      {#each applications as row (row.id)}
        <li>
          <div>
            <a href="/applications/{row.id}">{row.role_title}</a>
            <p class="meta">{when(row.created_at)}</p>
          </div>
          <div class="outcome">
            <p class={row.suitable ? 'ready' : 'gap'}>{row.suitable ? 'Ready to send' : 'Gaps to close'}</p>
            <p class="outcome-score">{row.fit_score}</p>
          </div>
        </li>
      {/each}
    </ul>
  {/if}
</section>
