<script>
  import { onMount } from 'svelte';
  import CvSheet from '../lib/CvSheet.svelte';
  import DeleteControl from '../lib/DeleteControl.svelte';
  import Icon from '../lib/Icon.svelte';
  import PhotoPicker from '../lib/PhotoPicker.svelte';
  import { navigate } from '../lib/nav.svelte.js';
  import { api } from '../lib/session.svelte.js';

  let { id } = $props();
  let cv = $state(null);
  let error = $state('');
  let pending = $state('');

  onMount(async () => {
    try {
      cv = await api(`/api/cvs/${id}`);
    } catch (err) {
      error = err.message;
    }
  });

  async function removeCv() {
    error = '';
    pending = 'cv';
    try {
      await api(`/api/cvs/${id}`, { method: 'DELETE' });
      navigate('/');
    } catch (err) {
      error = err.message;
      pending = '';
    }
  }

  async function removeRole(roleId) {
    error = '';
    pending = `role:${roleId}`;
    try {
      await api(`/api/applications/${roleId}`, { method: 'DELETE' });
      cv = { ...cv, versions: cv.versions.filter((version) => version.id !== roleId) };
    } catch (err) {
      error = err.message;
    } finally {
      pending = '';
    }
  }
</script>

<section class="stack cv-page">
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
  {#if cv}
    <header class="page-head">
      <div>
        <h1>{cv.name}</h1>
        {#if cv.label && cv.label !== cv.name}
          <p class="meta">{cv.label}</p>
        {/if}
      </div>
      <div class="page-actions">
        <a class="button" href="/apply?cv={cv.id}"><Icon name="role" size={16} /> Check a role</a>
        <DeleteControl
          label="Delete {cv.name}"
          message="Delete this CV and every role checked against it?"
          pending={pending === 'cv'}
          ondelete={removeCv}
        />
      </div>
    </header>
    <PhotoPicker
      cvId={cv.id}
      name={cv.name}
      bind:photo={cv.photo}
      github={cv.github}
      hasLinkedin={(cv.profile?.contact?.links || []).some((link) => /linkedin\.com/i.test(link))}
    />
    <CvSheet document={cv.profile} logosUrl={`/api/cvs/${id}/logos`} />
    <div class="section-head">
      <h2><Icon name="role" size={18} /> Roles checked</h2>
    </div>
    {#if cv.versions?.length}
      <ul class="desk-list">
        {#each cv.versions as version (version.id)}
          <li class="record">
            <a class="record-main" href="/applications/{version.id}">
              <span class="record-icon {version.suitable ? 'ready' : 'gap'}">
                <Icon name={version.suitable ? 'ready' : 'gap'} />
              </span>
              <span>
                <span class="record-title">{version.role_title}</span>
              </span>
            </a>
            <div class="record-actions">
              {#if version.share_path}
                <a class="button secondary" href={version.share_path}>Employer profile</a>
              {/if}
              <span class="pill {version.suitable ? 'ready' : 'gap'}">
                <Icon name={version.suitable ? 'ready' : 'gap'} size={14} />
                {version.suitable ? 'Ready to send' : 'Gaps to close'}
              </span>
              <span class="score-chip">{version.fit_score}</span>
              <DeleteControl
                label="Delete {version.role_title}"
                message="Delete this role check? The CV stays."
                pending={pending === `role:${version.id}`}
                ondelete={() => removeRole(version.id)}
              />
            </div>
          </li>
        {/each}
      </ul>
    {:else}
      <div class="empty-card">
        <span class="record-icon"><Icon name="role" /></span>
        <p>No roles checked yet. Paste one job description to see if this CV is ready.</p>
      </div>
    {/if}
  {/if}
</section>
