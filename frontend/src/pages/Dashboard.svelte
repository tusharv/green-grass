<script>
  import { onMount } from 'svelte';
  import DeleteControl from '../lib/DeleteControl.svelte';
  import Icon from '../lib/Icon.svelte';
  import { api, session } from '../lib/session.svelte.js';
  import { getInitials } from '../lib/user.js';

  let cvs = $state([]);
  let applications = $state([]);
  let error = $state('');
  let loading = $state(true);
  let pendingKey = $state('');

  const readyCount = $derived(applications.filter((row) => row.suitable).length);
  const gapCount = $derived(applications.length - readyCount);
  const hasWork = $derived(cvs.length > 0 || applications.length > 0);
  const userInitials = $derived(getInitials(session.user?.email));

  onMount(async () => {
    try {
      [cvs, applications] = await Promise.all([api('/api/cvs'), api('/api/applications')]);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  });

  function when(value) {
    return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function rolesFor(cvId) {
    const count = applications.filter((row) => row.cv_id === cvId).length;
    if (count === 0) return 'No roles yet';
    return `${count} ${count === 1 ? 'role' : 'roles'}`;
  }

  function cvName(cvId) {
    return cvs.find((cv) => cv.id === cvId)?.name || 'Saved CV';
  }

  async function remove(key, path) {
    error = '';
    pendingKey = key;
    try {
      await api(path, { method: 'DELETE' });
      if (key.startsWith('cv:')) {
        const id = Number(key.slice(3));
        cvs = cvs.filter((cv) => cv.id !== id);
        applications = applications.filter((row) => row.cv_id !== id);
      } else {
        const id = Number(key.slice(5));
        applications = applications.filter((row) => row.id !== id);
      }
    } catch (err) {
      error = err.message;
    } finally {
      pendingKey = '';
    }
  }
</script>

<section class="desk">
  <header class="desk-welcome">
    <div class="welcome-main">
      <span class="welcome-avatar" aria-hidden="true">{userInitials}</span>
      <div class="welcome-text">
        <p class="eyebrow">Career Desk</p>
        <h1>Welcome back{#if session.user?.email}, <span class="welcome-email">{session.user.email}</span>{/if}</h1>
        <p class="lede">Your next step starts here. Check your CV against a role and see what’s ready or what to build next.</p>
      </div>
    </div>
    <a class="button" href="/cvs/new"><Icon name="upload" size={18} /> Upload a CV</a>
  </header>

  {#if error}<p class="alert" role="alert">{error}</p>{/if}

  {#if loading}
    <p class="hint" role="status">Loading your desk…</p>
  {:else}
    {#if hasWork}
      <dl class="desk-stats">
        <div>
          <dt><Icon name="cv" size={16} /> CVs</dt>
          <dd>{cvs.length}</dd>
        </div>
        <div>
          <dt><Icon name="role" size={16} /> Roles</dt>
          <dd>{applications.length}</dd>
        </div>
        <div>
          <dt><Icon name="ready" size={16} /> Ready to send</dt>
          <dd class="stat-ready">{readyCount}</dd>
        </div>
        <div>
          <dt><Icon name="gap" size={16} /> Gaps to close</dt>
          <dd class="stat-gap">{gapCount}</dd>
        </div>
      </dl>
    {/if}

    <div class="section-head">
      <h2><Icon name="cv" size={18} /> Uploaded CVs</h2>
    </div>
    {#if cvs.length === 0}
      <div class="empty-card">
        <span class="record-icon"><Icon name="cv" /></span>
        <p>Upload a text PDF or DOCX. The original file is not kept.</p>
      </div>
    {:else}
      <ul class="desk-list">
        {#each cvs as cv (cv.id)}
          <li class="record">
            <a class="record-main" href="/cvs/{cv.id}">
              <span class="record-icon"><Icon name="cv" /></span>
              <span>
                <span class="record-title">{cv.name}</span>
                {#if cv.label && cv.label !== cv.name}
                  <span class="meta">{cv.label}</span>
                {/if}
                <span class="meta">
                  {when(cv.created_at)}
                  · {rolesFor(cv.id)}
                </span>
              </span>
            </a>
            <div class="record-actions">
              <a class="button secondary" href="/apply?cv={cv.id}">
                <Icon name="role" size={16} /> Check a role
              </a>
              <DeleteControl
                label="Delete {cv.name}"
                message="Delete this CV and every role checked against it?"
                pending={pendingKey === `cv:${cv.id}`}
                ondelete={() => remove(`cv:${cv.id}`, `/api/cvs/${cv.id}`)}
              />
            </div>
          </li>
        {/each}
      </ul>
    {/if}

    <div class="section-head">
      <h2><Icon name="role" size={18} /> Roles checked</h2>
    </div>
    {#if applications.length === 0}
      <div class="empty-card">
        <span class="record-icon"><Icon name="role" /></span>
        <p>No roles checked yet. Open a CV and paste one job description.</p>
      </div>
    {:else}
      <ul class="desk-list">
        {#each applications as row (row.id)}
          <li class="record">
            <a class="record-main" href="/applications/{row.id}">
              <span class="record-icon {row.suitable ? 'ready' : 'gap'}">
                <Icon name={row.suitable ? 'ready' : 'gap'} />
              </span>
              <span>
                <span class="record-title">{row.role_title}</span>
                <span class="meta">{cvName(row.cv_id)} · {when(row.created_at)}</span>
              </span>
            </a>
            <div class="record-actions">
              <span class="pill {row.suitable ? 'ready' : 'gap'}">
                <Icon name={row.suitable ? 'ready' : 'gap'} size={14} />
                {row.suitable ? 'Ready to send' : 'Gaps to close'}
              </span>
              <span class="score-chip">{row.fit_score}</span>
              <DeleteControl
                label="Delete {row.role_title}"
                message="Delete this role check? The CV stays."
                pending={pendingKey === `role:${row.id}`}
                ondelete={() => remove(`role:${row.id}`, `/api/applications/${row.id}`)}
              />
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  {/if}
</section>
