<script>
  import { onMount } from 'svelte';
  import Icon from '../lib/Icon.svelte';
  import DeleteControl from '../lib/DeleteControl.svelte';
  import { api, applySessionUser, session } from '../lib/session.svelte.js';
  import { navigate } from '../lib/nav.svelte.js';

  let users = $state([]);
  let selectedUser = $state(null);
  let selectedCv = $state(null);
  let selectedApp = $state(null);
  let error = $state('');
  let loading = $state(true);
  let saving = $state(false);
  let cvLabel = $state('');
  let cvProfileText = $state('');
  let cvExtracted = $state('');
  let appRole = $state('');
  let appJob = $state('');
  let appScore = $state(0);
  let appSuitable = $state(false);
  let appBoardText = $state('');
  let appResultText = $state('');

  onMount(loadUsers);

  async function loadUsers() {
    error = '';
    loading = true;
    try {
      users = await api('/api/admin/users');
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function openUser(id) {
    error = '';
    selectedCv = null;
    selectedApp = null;
    try {
      selectedUser = await api(`/api/admin/users/${id}`);
    } catch (err) {
      error = err.message;
    }
  }

  async function openCv(id) {
    error = '';
    selectedApp = null;
    try {
      selectedCv = await api(`/api/admin/cvs/${id}`);
      cvLabel = selectedCv.label || '';
      cvProfileText = JSON.stringify(selectedCv.profile_json || {}, null, 2);
      cvExtracted = selectedCv.extracted_text || '';
    } catch (err) {
      error = err.message;
    }
  }

  async function openApp(id) {
    error = '';
    selectedCv = null;
    try {
      selectedApp = await api(`/api/admin/applications/${id}`);
      appRole = selectedApp.role_title || '';
      appJob = selectedApp.job_description || '';
      appScore = selectedApp.fit_score ?? 0;
      appSuitable = Boolean(selectedApp.suitable);
      appBoardText = JSON.stringify(selectedApp.skill_board_json || {}, null, 2);
      appResultText = JSON.stringify(selectedApp.result_json || {}, null, 2);
    } catch (err) {
      error = err.message;
    }
  }

  async function saveCv() {
    error = '';
    saving = true;
    try {
      const profile_json = JSON.parse(cvProfileText);
      selectedCv = await api(`/api/admin/cvs/${selectedCv.id}`, {
        method: 'PATCH',
        json: { label: cvLabel, profile_json, extracted_text: cvExtracted },
      });
      cvLabel = selectedCv.label || '';
      cvProfileText = JSON.stringify(selectedCv.profile_json || {}, null, 2);
      cvExtracted = selectedCv.extracted_text || '';
      if (selectedUser) await openUser(selectedUser.id);
    } catch (err) {
      error = err.message;
    } finally {
      saving = false;
    }
  }

  async function saveApp() {
    error = '';
    saving = true;
    try {
      const skill_board_json = JSON.parse(appBoardText);
      const result_json = JSON.parse(appResultText);
      selectedApp = await api(`/api/admin/applications/${selectedApp.id}`, {
        method: 'PATCH',
        json: {
          role_title: appRole,
          job_description: appJob,
          fit_score: Number(appScore),
          suitable: appSuitable,
          skill_board_json,
          result_json,
        },
      });
      appRole = selectedApp.role_title || '';
      appJob = selectedApp.job_description || '';
      appScore = selectedApp.fit_score ?? 0;
      appSuitable = Boolean(selectedApp.suitable);
      appBoardText = JSON.stringify(selectedApp.skill_board_json || {}, null, 2);
      appResultText = JSON.stringify(selectedApp.result_json || {}, null, 2);
      if (selectedUser) await openUser(selectedUser.id);
    } catch (err) {
      error = err.message;
    } finally {
      saving = false;
    }
  }

  async function removeCv(id) {
    error = '';
    try {
      await api(`/api/admin/cvs/${id}`, { method: 'DELETE' });
      selectedCv = null;
      if (selectedUser) await openUser(selectedUser.id);
      await loadUsers();
    } catch (err) {
      error = err.message;
    }
  }

  async function removeApp(id) {
    error = '';
    try {
      await api(`/api/admin/applications/${id}`, { method: 'DELETE' });
      selectedApp = null;
      if (selectedUser) await openUser(selectedUser.id);
      await loadUsers();
    } catch (err) {
      error = err.message;
    }
  }

  async function viewAs(userId) {
    error = '';
    try {
      const data = await api(`/api/admin/impersonate/${userId}`, { method: 'POST' });
      applySessionUser(data.user, data.impersonating);
      navigate('/');
    } catch (err) {
      error = err.message;
    }
  }

  function when(value) {
    return new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function backToUsers() {
    selectedUser = null;
    selectedCv = null;
    selectedApp = null;
    loadUsers();
  }
</script>

<section class="desk admin-console">
  <header class="desk-welcome">
    <div class="welcome-main">
      <div class="welcome-text">
        <p class="eyebrow">Ops</p>
        <h1>Admin console</h1>
        <p class="lede">Browse accounts, inspect CVs and role checks, fix bad data, or view the desk as that person.</p>
      </div>
    </div>
    <a class="button secondary" href="/">Back to desk</a>
  </header>

  {#if error}<p class="alert" role="alert">{error}</p>{/if}

  {#if loading && !selectedUser}
    <p class="hint" role="status">Loading users…</p>
  {:else if !selectedUser}
    <div class="section-head">
      <h2><Icon name="user" size={18} /> Users</h2>
    </div>
    {#if users.length === 0}
      <p class="hint">No accounts yet.</p>
    {:else}
      <ul class="desk-list">
        {#each users as user (user.id)}
          <li class="record">
            <button type="button" class="record-main" onclick={() => openUser(user.id)}>
              <span class="record-icon"><Icon name="user" /></span>
              <span class="record-copy">
                <span class="record-title">{user.email}</span>
                <span class="meta">
                  {when(user.created_at)}
                  · {user.cv_count} {user.cv_count === 1 ? 'CV' : 'CVs'}
                  · {user.application_count} {user.application_count === 1 ? 'role' : 'roles'}
                  {#if user.is_admin} · admin{/if}
                </span>
              </span>
            </button>
            <div class="record-actions user-actions">
              {#if user.is_admin}
                <span class="record-action-slot" aria-hidden="true"></span>
              {:else}
                <button type="button" class="button secondary" onclick={() => viewAs(user.id)}>
                  View as user
                </button>
              {/if}
              <button type="button" class="button secondary" onclick={() => openUser(user.id)}>Open</button>
            </div>
          </li>
        {/each}
      </ul>
    {/if}
  {:else}
    <p class="hint">
      <button type="button" class="text" onclick={backToUsers}>← All users</button>
    </p>
    <header class="section-head">
      <h2>{selectedUser.email}</h2>
      {#if !selectedUser.is_admin}
        <button type="button" class="button" onclick={() => viewAs(selectedUser.id)}>View as user</button>
      {/if}
    </header>
    <p class="meta">
      Joined {when(selectedUser.created_at)}
      {#if selectedUser.is_admin} · admin{/if}
    </p>

    {#if selectedCv}
      <div class="admin-editor stack">
        <div class="section-head">
          <h2>CV #{selectedCv.id}</h2>
          <button type="button" class="text" onclick={() => (selectedCv = null)}>Close</button>
        </div>
        <label>
          Label
          <input bind:value={cvLabel} />
        </label>
        <label>
          Profile JSON
          <textarea rows="14" bind:value={cvProfileText} class="admin-json"></textarea>
        </label>
        <label>
          Extracted text
          <textarea rows="8" bind:value={cvExtracted} class="admin-json"></textarea>
        </label>
        <div class="record-actions">
          <button type="button" class="button" disabled={saving} onclick={saveCv}>
            {saving ? 'Saving…' : 'Save CV'}
          </button>
          <DeleteControl
            label="Delete CV"
            message="Delete this CV and every role checked against it?"
            ondelete={() => removeCv(selectedCv.id)}
          />
        </div>
      </div>
    {:else if selectedApp}
      <div class="admin-editor stack">
        <div class="section-head">
          <h2>Role check #{selectedApp.id}</h2>
          <button type="button" class="text" onclick={() => (selectedApp = null)}>Close</button>
        </div>
        <label>
          Role title
          <input bind:value={appRole} />
        </label>
        <label>
          Job description
          <textarea rows="6" bind:value={appJob}></textarea>
        </label>
        <div class="admin-row">
          <label>
            Fit score
            <input type="number" min="0" max="100" bind:value={appScore} />
          </label>
          <label class="admin-check">
            <input type="checkbox" bind:checked={appSuitable} />
            Suitable (Ready to send)
          </label>
        </div>
        <label>
          Skill board JSON
          <textarea rows="10" bind:value={appBoardText} class="admin-json"></textarea>
        </label>
        <label>
          Result JSON
          <textarea rows="12" bind:value={appResultText} class="admin-json"></textarea>
        </label>
        <div class="record-actions">
          <button type="button" class="button" disabled={saving} onclick={saveApp}>
            {saving ? 'Saving…' : 'Save role check'}
          </button>
          <DeleteControl
            label="Delete role check"
            message="Delete this role check?"
            ondelete={() => removeApp(selectedApp.id)}
          />
        </div>
      </div>
    {:else}
      <div class="section-head">
        <h2><Icon name="cv" size={18} /> CVs</h2>
      </div>
      {#if selectedUser.cvs.length === 0}
        <p class="hint">No CVs.</p>
      {:else}
        <ul class="desk-list">
          {#each selectedUser.cvs as cv (cv.id)}
            <li class="record">
              <button type="button" class="record-main" onclick={() => openCv(cv.id)}>
                <span class="record-icon"><Icon name="cv" /></span>
                <span class="record-copy">
                  <span class="record-title">{cv.name}</span>
                  <span class="meta">{cv.label} · {when(cv.created_at)}</span>
                </span>
              </button>
              <div class="record-actions">
                <button type="button" class="button secondary" onclick={() => openCv(cv.id)}>Inspect</button>
              </div>
            </li>
          {/each}
        </ul>
      {/if}

      <div class="section-head">
        <h2><Icon name="role" size={18} /> Role checks</h2>
      </div>
      {#if selectedUser.applications.length === 0}
        <p class="hint">No role checks.</p>
      {:else}
        <ul class="desk-list">
          {#each selectedUser.applications as row (row.id)}
            <li class="record">
              <button type="button" class="record-main" onclick={() => openApp(row.id)}>
                <span class="record-icon" class:gap={!row.suitable}><Icon name={row.suitable ? 'ready' : 'gap'} /></span>
                <span class="record-copy">
                  <span class="record-title">{row.role_title}</span>
                  <span class="meta">
                    CV #{row.cv_id} · score {row.fit_score} · {row.suitable ? 'Ready to send' : 'Gaps to close'}
                    · {when(row.created_at)}
                  </span>
                </span>
              </button>
              <div class="record-actions">
                <button type="button" class="button secondary" onclick={() => openApp(row.id)}>Inspect</button>
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    {/if}
  {/if}
</section>

<style>
  /* Global button styles center content and add padding; row mains must look like desk links. */
  .admin-console :global(button.record-main) {
    justify-content: flex-start;
    align-items: center;
    width: 100%;
    min-height: 0;
    margin: 0;
    padding: 0;
    background: transparent;
    border: 0;
    border-radius: 0;
    color: inherit;
    font: inherit;
    font-weight: inherit;
    font-size: inherit;
    line-height: inherit;
    text-align: left;
    transform: none;
    gap: 0.85rem;
  }

  .admin-console :global(button.record-main:hover),
  .admin-console :global(button.record-main:active) {
    background: transparent;
    color: inherit;
    transform: none;
  }

  .admin-console :global(.record-copy) {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    min-width: 0;
  }

  .admin-console :global(.user-actions) {
    display: grid;
    grid-template-columns: minmax(8.5rem, max-content) max-content;
    align-items: center;
    justify-content: end;
    gap: 0.55rem;
  }

  .admin-console :global(.record-action-slot) {
    display: block;
    min-height: 2.75rem;
  }

  .admin-editor {
    margin-top: 1rem;
  }

  .admin-json {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.85rem;
  }

  .admin-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: end;
  }

  .admin-check {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }
</style>
