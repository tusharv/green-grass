<script>
  import { onMount } from 'svelte';
  import CvSheet from '../lib/CvSheet.svelte';
  import DeleteControl from '../lib/DeleteControl.svelte';
  import FitStrip from '../lib/FitStrip.svelte';
  import GapRoadmap from '../lib/GapRoadmap.svelte';
  import { learningPlan, hasLearningDetails } from '../lib/learning.js';
  import Icon from '../lib/Icon.svelte';
  import { navigate } from '../lib/nav.svelte.js';
  import RoleReview from '../lib/RoleReview.svelte';
  import { api } from '../lib/session.svelte.js';

  let { id } = $props();
  let row = $state(null);
  let error = $state('');
  let pending = $state(false);
  let sharePending = $state(false);
  let copied = $state(false);
  let learningPending = $state(false);
  let learningError = $state('');

  onMount(async () => {
    try {
      row = await api(`/api/applications/${id}`);
      if (canLearn && !hasLearningDetails(report)) {
        await generateLearningPlan();
      }
    } catch (err) {
      error = err.message;
    }
  });

  const suitable = $derived(Boolean(row?.suitable) && row?.result?.kind === 'cv');
  const shareUrl = $derived(row?.share_path ? new URL(row.share_path, location.origin).href : '');
  const board = $derived(row?.skill_board || { required: [], preferred: [], matched_preferred: [] });
  const preferred = $derived(
    board.preferred?.length
      ? board.preferred
      : (board.matched_preferred || []).map((name) => ({ name, present: true })),
  );
  const report = $derived(row?.result?.learning_plan || row?.result?.report);
  const plans = $derived(learningPlan(report));
  const canLearn = $derived(Boolean(board.required?.length) &&
    (suitable || board.required.some((mark) => !mark.present)) &&
    [...(board.required || []), ...preferred].some((mark) => !mark.present));

  async function generateLearningPlan() {
    learningPending = true;
    learningError = '';
    try {
      const updated = await api(`/api/applications/${id}/learning-plan`, { method: 'POST' });
      row = { ...row, result: updated.result };
    } catch (err) {
      learningError = err.message;
    } finally {
      learningPending = false;
    }
  }

  async function publishProfile() {
    error = '';
    copied = false;
    sharePending = true;
    try {
      const body = await api(`/api/applications/${id}/profile`, { method: 'POST' });
      row = { ...row, share_path: body.share_path };
    } catch (err) {
      error = err.message;
    } finally {
      sharePending = false;
    }
  }

  async function copyLink() {
    error = '';
    try {
      await navigator.clipboard.writeText(shareUrl);
      copied = true;
    } catch {
      copied = false;
      error = 'Select the link and copy it.';
    }
  }

  async function stopSharing() {
    error = '';
    copied = false;
    sharePending = true;
    try {
      await api(`/api/applications/${id}/profile`, { method: 'DELETE' });
      row = { ...row, share_path: null };
    } catch (err) {
      error = err.message;
    } finally {
      sharePending = false;
    }
  }

  async function removeRole() {
    error = '';
    pending = true;
    try {
      await api(`/api/applications/${id}`, { method: 'DELETE' });
      navigate('/');
    } catch (err) {
      error = err.message;
      pending = false;
    }
  }
</script>

<section class="stack">
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
  {#if row}
    <header class="page-head">
      <div>
        <p class="eyebrow">Role check</p>
        <h1>{row.candidate_name}</h1>
        <p class="lede">{row.role_title}</p>
        <p class="meta"><a href="/cvs/{row.cv_id}">Saved CV</a></p>
      </div>
      <div class="page-actions">
        {#if suitable}
          <a class="button" href="/api/applications/{row.id}/pdf"><Icon name="download" size={16} /> Download PDF</a>
        {/if}
        <DeleteControl
          label="Delete {row.role_title}"
          message="Delete this role check? The CV stays."
          {pending}
          ondelete={removeRole}
        />
      </div>
    </header>
    <div class="share-bar">
      {#if shareUrl}
        <p>Anyone with this link can read {row.candidate_name}'s profile for this role. The fit review on this page stays private.</p>
        <input readonly value={shareUrl} aria-label="Employer profile link" onclick={(event) => event.currentTarget.select()} />
        <a class="button secondary" href={row.share_path}><Icon name="link" size={16} /> Open employer profile</a>
        <button type="button" class="button secondary" disabled={sharePending} onclick={copyLink}>
          {copied ? 'Copied' : 'Copy link'}
        </button>
        <button type="button" class="text" disabled={sharePending} onclick={stopSharing}>Stop sharing</button>
      {:else}
        <p>Share a profile employers can open without an account. It shows the saved CV for this role.</p>
        <button type="button" class="button" disabled={sharePending} onclick={publishProfile}>
          <Icon name="link" size={16} /> Share with employers
        </button>
      {/if}
    </div>
    <div class="result">
      <FitStrip
        score={row.fit_score}
        {suitable}
        required={board.required || []}
        {preferred}
        yearsShown={board.years_shown}
        yearsNeeded={board.years_needed}
        yearsScore={board.years_score}
        coverage={board.coverage}
        hasPlan={plans.length > 0 || canLearn}
      />
      <div class="review-content">
        <RoleReview required={board.required || []} {preferred} {suitable} {plans} {canLearn} />
        {#if plans.length || canLearn}
          <GapRoadmap {plans} summary={report?.summary || ''} pending={learningPending} error={learningError} incomplete={canLearn && !hasLearningDetails(report)} onretry={generateLearningPlan} />
        {/if}
        {#if suitable && row.result?.document}
          <section aria-labelledby="next-step">
            <h2 id="next-step" class="artifact-heading"><span aria-hidden="true">✓</span> Your tailored CV</h2>
            <p class="artifact-note">Review the wording below before downloading your PDF.</p>
            <CvSheet document={row.result.document} logosUrl={`/api/applications/${id}/logos`} />
          </section>
        {/if}
      </div>
    </div>
  {:else if !error}
    <p class="hint" role="status">Loading your role review…</p>
  {/if}
</section>
