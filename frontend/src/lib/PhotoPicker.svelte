<script>
  import Avatar from './Avatar.svelte';
  import Icon from './Icon.svelte';
  import { api } from './session.svelte.js';

  let { cvId, name = '', photo = $bindable(null), github = null, hasLinkedin = false } = $props();
  let pending = $state('');
  let error = $state('');
  let input;

  const sourceNote = $derived(
    photo?.source === 'upload'
      ? 'Your uploaded photo'
      : photo?.source === 'github'
        ? `Your GitHub photo (@${github})`
        : 'No photo. Employers see your initials.',
  );

  async function upload(event) {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file) return;
    error = '';
    if (file.size > 3 * 1024 * 1024) {
      error = 'This photo is larger than 3 MB.';
      return;
    }
    pending = 'upload';
    try {
      const body = new FormData();
      body.append('file', file);
      photo = (await api(`/api/cvs/${cvId}/photo`, { method: 'POST', body })).photo;
    } catch (err) {
      error = err.message;
    } finally {
      pending = '';
    }
  }

  async function useGithub() {
    error = '';
    pending = 'github';
    try {
      photo = (await api(`/api/cvs/${cvId}/photo/github`, { method: 'POST' })).photo;
    } catch (err) {
      error = err.message;
    } finally {
      pending = '';
    }
  }

  async function remove() {
    error = '';
    pending = 'remove';
    try {
      await api(`/api/cvs/${cvId}/photo`, { method: 'DELETE' });
      photo = null;
    } catch (err) {
      error = err.message;
    } finally {
      pending = '';
    }
  }
</script>

<section class="photo-picker" aria-labelledby="photo-title">
  <Avatar {name} url={photo?.url || ''} size={76} />
  <div class="photo-copy">
    <h2 id="photo-title">Profile photo</h2>
    <p>{sourceNote}. It appears on employer profiles you share.</p>
    {#if hasLinkedin && photo?.source !== 'upload'}
      <p class="hint">LinkedIn does not let other sites load profile photos. Upload the same photo here instead.</p>
    {/if}
    {#if error}<p class="photo-error" role="alert">{error}</p>{/if}
  </div>
  <div class="photo-actions">
    <input
      bind:this={input}
      class="sr-only"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      aria-label="Upload a profile photo"
      onchange={upload}
    />
    <button type="button" class="button secondary" disabled={Boolean(pending)} onclick={() => input.click()}>
      <Icon name="camera" size={16} /> {pending === 'upload' ? 'Uploading…' : photo?.source === 'upload' ? 'Replace photo' : 'Upload photo'}
    </button>
    {#if github && photo?.source !== 'github'}
      <button type="button" class="button secondary" disabled={Boolean(pending)} onclick={useGithub}>
        <Icon name="github" size={16} /> Use GitHub photo
      </button>
    {/if}
    {#if photo}
      <button type="button" class="text" disabled={Boolean(pending)} onclick={remove}>Remove photo</button>
    {/if}
  </div>
</section>

<style>
  .photo-picker {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    gap: 1.1rem;
    align-items: center;
    padding: 1rem 1.25rem;
    background: var(--sheet);
    border: 1px solid var(--line);
    border-radius: var(--radius-surface);
  }
  h2 { margin: 0; font-size: 1.05rem; }
  p { margin: 0.15rem 0 0; color: var(--muted); font-size: 0.95rem; }
  .photo-error { color: var(--clay); font-weight: 600; }
  .photo-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; justify-content: flex-end; }
  @media (max-width: 760px) {
    .photo-picker { grid-template-columns: auto minmax(0, 1fr); }
    .photo-actions { grid-column: 1 / -1; justify-content: flex-start; }
  }
</style>
