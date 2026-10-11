<script>
  import { onMount } from 'svelte';
  import CvSheet from '../lib/CvSheet.svelte';
  import { api } from '../lib/session.svelte.js';

  let { token } = $props();
  let profile = $state(null);
  let error = $state('');

  onMount(async () => {
    try {
      profile = await api(`/api/profiles/${encodeURIComponent(token)}`);
    } catch (err) {
      error = err.message;
    }
  });
</script>

<svelte:head>
  {#if profile}
    <title>{profile.name} — {profile.role_title}</title>
  {/if}
  <meta name="robots" content="noindex" />
</svelte:head>

<section class="stack cv-page">
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
  {#if profile}
    <CvSheet document={profile.document} roleTitle={profile.role_title} />
    {#if profile.application_id}
      <p class="meta">
        <a href="/cvs/{profile.cv_id}">Saved CV</a>
        ·
        <a href="/applications/{profile.application_id}">Role check</a>
      </p>
    {/if}
  {:else if !error}
    <p class="hint" role="status">Loading profile…</p>
  {/if}
</section>
