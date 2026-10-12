<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/session.svelte.js';
  import { navigate } from '../lib/nav.svelte.js';

  let { cvId } = $props();
  let cvs = $state([]);
  let chosen = $state('');

  $effect(() => {
    if (cvId) chosen = String(cvId);
  });
  let roleTitle = $state('');
  let jobDescription = $state('');
  let error = $state('');
  let busy = $state(false);

  onMount(async () => {
    try {
      cvs = await api('/api/cvs');
      if (!chosen && cvs.length === 1) chosen = String(cvs[0].id);
    } catch (err) {
      error = err.message;
    }
  });

  async function submit(event) {
    event.preventDefault();
    error = '';
    busy = true;
    try {
      const row = await api('/api/applications', {
        method: 'POST',
        json: {
          cv_id: Number(chosen),
          role_title: roleTitle,
          job_description: jobDescription,
        },
      });
      navigate(`/applications/${row.id}`);
    } catch (err) {
      error = err.message;
      busy = false;
    }
  }
</script>

<section class="stack narrow">
  <h1>Check a role</h1>
  <p class="lede">Bring your next role into focus. Paste the job description to see where your experience fits and what to work on next.</p>
  <form onsubmit={submit} aria-busy={busy}>
    <label>
      CV
      <select bind:value={chosen} required>
        <option value="" disabled>Choose a CV</option>
        {#each cvs as cv}
          <option value={String(cv.id)}>{cv.name}</option>
        {/each}
      </select>
    </label>
    <label>
      Role title
      <input bind:value={roleTitle} required maxlength="200" />
    </label>
    <label>
      Job description
      <textarea bind:value={jobDescription} required rows="10"></textarea>
    </label>
    {#if error}<p class="alert" role="alert">{error}</p>{/if}
    <button type="submit" disabled={busy}>{busy ? 'Checking this role…' : 'Check this role'}</button>
    <p class="hint">This can take up to a minute.</p>
  </form>
</section>
