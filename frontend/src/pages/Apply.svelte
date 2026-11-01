<script>
  import { onMount } from 'svelte';
  import Icon from '../lib/Icon.svelte';
  import EditorModal from '../lib/EditorModal.svelte';
  import { api } from '../lib/session.svelte.js';
  import { navigate } from '../lib/nav.svelte.js';

  let { cvId } = $props();
  let cvs = $state([]);
  let chosen = $state('');

  $effect(() => {
    if (cvId) chosen = String(cvId);
  });
  let jobUrl = $state('');
  let fetching = $state(false);
  let fetchError = $state('');
  let imported = $state(false);
  let replaceOpen = $state(false);
  async function fetchDescription() {
    replaceOpen = false;
    fetching = true;
    fetchError = '';
    imported = false;
    try {
      const result = await api('/api/job-description', {method:'POST', json:{url:jobUrl}});
      jobDescription = result.job_description;
      if (!roleTitle.trim()) roleTitle = result.role_title;
      imported = true;
    } catch (err) {fetchError = err.message;}
    finally {fetching = false;}
  }
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
    if (fetching || busy) return;
    error = '';
    busy = true;
    try {
      const row = await api('/api/applications', {
        method: 'POST',
        json: {
          cv_id: Number(chosen),
          role_title: roleTitle,
          job_description: jobDescription,
          job_url: jobUrl,
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
  <p class="lede">Bring your next role into focus. Import a job posting or paste its description to see where your experience fits and what to work on next.</p>
  <form onsubmit={submit} aria-busy={busy || fetching}>
    <fieldset disabled={busy || fetching}>
    <label>
      CV
      <select bind:value={chosen} required>
        <option value="" disabled>Choose a CV</option>
        {#each cvs as cv}
          <option value={String(cv.id)}>{cv.name}</option>
        {/each}
      </select>
    </label>
    <div class="job-import">
      <div class="import-heading"><Icon name="link" size={19}/><div><h2>Start with a job link</h2><p>Optional · Saved with this role check</p></div></div>
      <label for="job-url">Original job posting</label>
      <div class="import-controls"><input id="job-url" type="url" bind:value={jobUrl} maxlength="2048" placeholder="https://company.com/careers/role" oninput={() => {imported=false;fetchError='';}}/><button type="button" class="fetch-button" disabled={!jobUrl.trim() || busy || fetching} onclick={() => jobDescription.trim() ? replaceOpen=true : fetchDescription()}><Icon name="download" size={16}/>{fetching ? 'Fetching…' : 'Fetch description'}</button></div>
      <p class="hint">Public job pages work best. If a site needs sign-in or blocks imports, paste the description below and keep the link.</p>
      {#if fetchError}<p class="alert" role="alert">{fetchError}</p>{/if}
      {#if imported}<p class="import-success" role="status"><Icon name="ready" size={16}/> Description imported. Review the title and text before checking this role.</p>{/if}
    </div>
    <label>
      Role title
      <input bind:value={roleTitle} required maxlength="200" />
    </label>
    <label>
      Job description
      <textarea bind:value={jobDescription} required rows="12" maxlength="20000" placeholder="Paste the full job description, including responsibilities and required skills."></textarea>
      <span class="character-count">{jobDescription.length.toLocaleString()} / 20,000 characters</span>
    </label>
    {#if error}<p class="alert" role="alert">{error}</p>{/if}
    <button type="submit" disabled={busy || fetching}>{busy ? 'Checking this role…' : 'Check this role'}</button>
    <p class="hint">Review imported text for missing requirements or unrelated page content. Checking can take up to a minute.</p>
    </fieldset>
  </form>
</section>

<EditorModal bind:open={replaceOpen} title="Replace the description?" labelId="replace-job-title" description="Fetching this link will replace the job description you have entered. Your role title will stay if you have already filled it in.">
  <div class="replace-actions"><button type="button" class="secondary" onclick={() => replaceOpen=false}>Keep current text</button><button type="button" onclick={fetchDescription}>Fetch and replace</button></div>
</EditorModal>
<style>
  fieldset {border:0;padding:0;margin:0;display:grid;gap:20px;min-width:0;}
  .job-import {padding:20px;border:1px solid #cddfd4;background:#f3f8f4;border-radius:12px;display:grid;gap:10px;}
  .import-heading {display:flex;align-items:center;gap:10px;color:#285844;}.import-heading h2 {font-size:16px;margin:0;}.import-heading p {font-size:12px;color:var(--muted);margin:3px 0 0;}
  .import-controls {display:flex;gap:8px;}.import-controls input {min-width:0;flex:1;background:white;}.fetch-button {display:flex;align-items:center;justify-content:center;gap:7px;white-space:nowrap;font-size:12px;}
  .hint {margin:0;font-size:12px;line-height:1.6;}.import-success {display:flex;align-items:flex-start;gap:8px;color:#285844;font-size:13px;line-height:1.5;margin:0;}.character-count {text-align:right;font-size:11px;color:var(--muted);font-weight:400;}
  .replace-actions {display:flex;justify-content:flex-end;gap:10px;}.secondary {background:white;color:var(--ink);border:1px solid var(--line);}
  @media(max-width:600px) {.import-controls {flex-direction:column;}.job-import {padding:16px;}.fetch-button {min-height:42px;}.replace-actions {flex-wrap:wrap;}}
</style>
