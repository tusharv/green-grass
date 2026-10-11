<script>
  import { api } from '../lib/session.svelte.js';
  import { navigate } from '../lib/nav.svelte.js';

  let file = $state(null);
  let error = $state('');
  let busy = $state(false);

  async function submit(event) {
    event.preventDefault();
    error = '';
    if (!file) {
      error = 'Choose a PDF or DOCX file.';
      return;
    }
    busy = true;
    const body = new FormData();
    body.set('file', file);
    try {
      const cv = await api('/api/cvs', { method: 'POST', body });
      navigate(`/cvs/${cv.id}`);
    } catch (err) {
      error = err.message;
      busy = false;
    }
  }
</script>

<section class="stack narrow">
  <h1>Upload a CV</h1>
  <p class="lede">Use a text PDF or a DOCX, up to 5 MB. Scans cannot be read. The original file is not kept.</p>
  <form onsubmit={submit} aria-busy={busy}>
    <label>
      CV file
      <input
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        onchange={(event) => (file = event.currentTarget.files?.[0] || null)}
      />
    </label>
    {#if error}<p class="alert" role="alert">{error}</p>{/if}
    <button type="submit" disabled={busy}>{busy ? 'Reading the CV…' : 'Upload CV'}</button>
    <p class="hint">Reading a CV can take up to a minute.</p>
  </form>
</section>
