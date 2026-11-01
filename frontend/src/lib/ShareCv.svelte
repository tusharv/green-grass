<script>
  import { api } from './session.svelte.js';
  import EditorModal from './EditorModal.svelte';
  import Icon from './Icon.svelte';
  import DesignDocument from './DesignDocument.svelte';
  import CvSheet from './CvSheet.svelte';
  import Avatar from './Avatar.svelte';
  let { open = $bindable(false), row, dirty = false, busy = false, onpublished = () => {}, onreview = () => {} } = $props();
  let pending = $state(false);
  let loading = $state(false);
  let error = $state('');
  let copied = $state(false);
  let preview = $state(null);
  let requestId = 0;
  const shareUrl = $derived(row?.share_path ? new URL(row.share_path, location.origin).href : '');
  const canDownload = $derived(row?.suitable && row?.result?.kind === 'cv');
  $effect(() => {
    if (!open) {requestId++;return;}
    const current = row;
    loadPreview(current);
  });
  async function loadPreview(current) {
    const request = ++requestId;
    loading=true;error='';copied=false;preview=null;
    try {
      let next;
      if (current.share_path) {
        const publicProfile = await api('/api' + current.share_path);
        next = {document:publicProfile.document, html:publicProfile.design_html, logosUrl:'/api' + current.share_path + '/logos'};
      } else if (current.result?.kind === 'cv') {
        const cv = current.design_html ? null : await api(`/api/cvs/${current.cv_id}`);
        next = {document:current.result.document, photo:cv?.photo, html:current.design_html, logosUrl:`/api/applications/${current.id}/logos`};
      } else {
        const cv = await api(`/api/cvs/${current.cv_id}`);
        next = {document:cv.profile,photo:cv.photo,html:current.design_html,logosUrl:`/api/cvs/${current.cv_id}/logos`};
      }
      if (request === requestId) preview=next;
    } catch(err) {if (request === requestId) error=err.message;}
    finally {if (request === requestId) loading=false;}
  }
  async function publish() {
    if (dirty || busy || pending || row.share_path) return;
    pending=true;error='';
    try {
      const result=await api(`/api/applications/${row.id}/profile`,{method:'POST'});
      onpublished(result.share_path);
    } catch(err) {error=err.message;}
    finally {pending=false;}
  }
  async function copy() {
    if (dirty || busy || !shareUrl) return;
    try {await navigator.clipboard.writeText(shareUrl);copied=true;}
    catch {error='Select the link below and copy it.';}
  }
</script>
<EditorModal bind:open title="Share your CV" description="Review the saved version before sending it to a client or employer." labelId="share-cv-title" wide busy={pending}>
  <div class="share-layout">
    <div class="share-controls">
      <div class="visibility"><Icon name={shareUrl ? 'link' : 'lock'} size={18}/><span>{shareUrl ? 'Shared by link' : 'Not shared yet'}</span></div>
      <h3>{row.candidate_name}</h3><p class="role-name">{row.role_title}</p>
      {#if dirty || busy}
        <div class="draft-warning" role="status"><Icon name="edit" size={19}/><div><strong>{busy ? 'Your CV is being updated' : 'Save your edits first'}</strong><p>{busy ? 'Wait for the update to finish before sharing.' : 'This preview shows saved content. Review and save your draft before sharing.'}</p>{#if dirty}<button type="button" disabled={busy} onclick={onreview}>Review and save edits</button>{/if}</div></div>
      {/if}
      <div class="sharing-note"><Icon name="eye" size={18}/><p>Anyone with the link can read this profile, including its contact details. Your role assessment, practice plan and private chat are not shared.</p></div>
      {#if shareUrl}
        <label>Shareable link<input aria-label="Shareable CV link" readonly value={shareUrl} onclick={event => event.currentTarget.select()}/></label>
        <button class="primary" type="button" disabled={dirty || busy} onclick={copy}><Icon name={copied ? 'ready' : 'copy'} size={17}/>{copied ? 'Link copied' : 'Copy link'}</button>
        <a class="secondary" href={row.share_path} target="_blank" rel="noopener noreferrer"><Icon name="arrow" size={16}/>Open shared profile</a>
        <p class="small">This is your existing shared snapshot. To refresh its content, select that option when saving CV edits.</p>
      {:else}
        <button class="primary" type="button" disabled={dirty || busy || pending || loading || !preview} onclick={publish}><Icon name="share" size={17}/>{pending ? 'Creating link…' : 'Create share link'}</button>
        <p class="small">Nothing is published until you create the link.</p>
      {/if}
      {#if canDownload}
        {#if dirty || busy}<span class="pdf-note"><Icon name="download" size={17}/> Save before downloading the updated PDF.</span>
        {:else}<a class="secondary" href={`/api/applications/${row.id}/pdf`}><Icon name="download" size={17}/>Download saved PDF</a>{/if}
      {:else}<p class="small">You can share your source CV. A tailored CV and PDF become available when this role check is Ready to send.</p>{/if}
      {#if error}<p class="alert" role="alert">{error}</p>{/if}
      <a class="manage" href={`/applications/${row.id}`}>Manage sharing on the role check</a>
    </div>
    <div class="preview-column"><p class="preview-heading"><Icon name="eye" size={15}/>{shareUrl ? 'What your link currently shows' : 'Saved profile preview'}</p><div class="share-preview">
      {#if loading}<p class="loading" role="status">Loading saved CV…</p>
      {:else if preview?.html}<DesignDocument html={preview.html} logosUrl={preview.logosUrl} title="Saved CV sharing preview"/>
      {:else if preview?.document && shareUrl}<iframe class="public-preview" src={row.share_path} title="Current shared profile preview"></iframe>
      {:else if preview?.document}{#if preview.photo?.url}<div class="preview-photo"><Avatar name={row.candidate_name} url={preview.photo.url}/><span>Profile photo included in your shared CV</span></div>{/if}<CvSheet document={preview.document} logosUrl={preview.logosUrl}/>
      {:else}<p class="loading">Preview unavailable. <button type="button" onclick={() => loadPreview(row)}>Try again</button></p>{/if}
    </div></div>
  </div>
</EditorModal>
<style>
  .share-layout {display:grid;grid-template-columns:290px minmax(0,1fr);gap:24px;}.share-controls {display:flex;flex-direction:column;gap:12px;min-width:0;}
  .visibility {display:flex;gap:8px;align-items:center;color:#45694f;font-size:12px;}.share-controls h3 {margin:0;font-size:22px;line-height:1.2;}.role-name {margin:-7px 0 0;font-size:13px;color:var(--muted);}
  .sharing-note {display:flex;align-items:flex-start;gap:9px;padding:12px;background:#f0f6f2;border-radius:8px;color:#47634f;}.sharing-note p {font-size:12px;line-height:1.6;margin:0;}
  label {font-size:12px;font-weight:600;display:grid;gap:6px;}input {font-size:12px;min-width:0;width:100%;}
  .primary,.secondary {display:flex;justify-content:center;align-items:center;gap:8px;min-height:42px;border-radius:7px;padding:10px 14px;font-size:13px;text-decoration:none;}.primary {background:#245747;color:white;border:1px solid #245747;}.secondary {background:white;color:#245747;border:1px solid #cedcd2;}.primary:disabled {opacity:.5;}
  .small,.pdf-note {font-size:11px;line-height:1.6;color:var(--muted);margin:0;}.pdf-note {display:flex;gap:8px;}.manage {font-size:11px;color:#45694f;margin-top:4px;}
  .draft-warning {display:flex;gap:9px;padding:12px;background:#fff6e7;border:1px solid #ecd7ae;border-radius:8px;color:#745123;}.draft-warning strong {font-size:13px;}.draft-warning p {font-size:12px;line-height:1.5;margin:5px 0;}.draft-warning button {min-height:30px;padding:5px 0;background:transparent;color:#745123;font-size:12px;border:0;text-decoration:underline;}
  .preview-photo {display:flex;align-items:center;gap:12px;padding:16px;background:white;font-size:12px;color:var(--muted);}.public-preview {display:block;width:100%;height:60dvh;border:0;background:white;}.preview-column {min-width:0;}.preview-heading {display:flex;align-items:center;gap:8px;font-size:12px;color:#52675a;margin:0 0 10px;}.share-preview {max-height:62dvh;overflow:auto;border:1px solid #dce5df;border-radius:7px;background:#f0f4f1;}.loading {padding:30px;font-size:13px;text-align:center;}
  @media(max-width:720px) {.share-layout {grid-template-columns:1fr;gap:20px;}.share-preview {max-height:45dvh;}}
</style>
