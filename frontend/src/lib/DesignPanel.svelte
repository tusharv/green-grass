<script>
  import { onMount, tick } from 'svelte';
  import { api, session } from './session.svelte.js';
  import Icon from './Icon.svelte';
  import EditorModal from './EditorModal.svelte';
  import DesignDocument from './DesignDocument.svelte';
  import EditorList from './EditorList.svelte';
  import EditorFields from './EditorFields.svelte';
  import { rememberDraft, recallDraft, forgetDraft } from './editorDrafts.js';
  import { baseSections, changedSections, companyKey, editText, moveItem } from './editor.js';

  let { id, cvId, shared = false, blocked = false, revision = 0, onsave = () => {}, onstatechange = () => {} } = $props();
  let loading = $state(false);
  let saving = $state(false);
  let uploading = $state(false);
  let error = $state('');
  let stale = $state(false);
  let message = $state('');
  let initial = $state(null);
  let draft = $state(null);
  let version = $state('');
  let conversationRevision = $state(0);
  let html = $state('');
  let renderedDraft = $state('');
  let previewing = $state(false);
  let previewError = $state('');
  let panelTab = $state('content');
  let mobileView = $state('tools');
  let addOpen = $state(false);
  let fieldOpen = $state(false);
  let helpOpen = $state(false);
  let deleteSectionOpen = $state(false);
  let selected = $state('summary');
  let canvasEditing = $state(true);
  let canvasFocused = $state(false);
  let review = $state(false);
  let confirmed = $state(false);
  let updateShared = $state(false);
  let history = $state([]);
  let future = $state([]);
  let addChoice = $state('');
  let loadedRevision = $state(0);
  const serialize = value => JSON.stringify(value);
  const clone = value => JSON.parse(serialize(value));
  const busy = $derived(saving || uploading || loading);
  const dirty = $derived(draft && initial && serialize(draft) !== serialize(initial));
  const canvasCurrent = $derived(Boolean(draft) && (renderedDraft === serialize(draft) || canvasFocused));
  const factualChanges = $derived(draft && initial ? changedSections(initial.profile,draft.profile) : []);
  const hidden = $derived(draft ? [...Object.keys(baseSections),...draft.profile.custom_sections.map(s => s.id)].filter(key => !draft.design.sections.includes(key)) : []);
  const templates = [{id:'classic',name:'Classic',note:'Traditional'}, {id:'modern',name:'Modern',note:'Two columns'}, {id:'creative',name:'Creative',note:'Botanical'}, {id:'minimal',name:'Minimal',note:'Clean & simple'}];
  const palettes = [['forest','Forest','#245747'],['navy','Navy','#203c64'],['plum','Plum','#603c65'],['terracotta','Terracotta','#8b4535'],['slate','Slate','#364454'],['teal','Teal','#15616a']];
  const sectionIcon = key => ({summary:'summary',experience:'role',skills:'skills',education:'education',Projects:'folder',Certifications:'award',Languages:'language'})[key] || 'cv';
  const sectionNote = key => ({Projects:'Show practical work and what you contributed.',Certifications:'Include qualifications you have earned.',Languages:'State the languages you use and your proficiency.','Custom section':'Add another relevant part of your story.'})[key] || 'Restore this section and its saved text.';
  const title = key => baseSections[key] || draft?.profile.custom_sections.find(s => s.id === key)?.title || key;

  $effect(() => {onstatechange({dirty:Boolean(dirty),busy});});
  export function reviewChanges() {if (dirty && !busy) review = true;}
  function editSection(key) {selected=key;fieldOpen=true;}
  onMount(() => {
    load(true);
  });
  $effect(() => {
    if (draft && revision !== loadedRevision) stale = true;
  });
  $effect(() => {
    if (!draft || loading) return;
    if (dirty) rememberDraft(session.user?.id,id,{initial:clone(initial),draft:clone(draft),version,conversationRevision,history:[...history],future:[...future]});
    else forgetDraft(session.user?.id,id);
  });
  async function load(restore = false) {
    loading = true; error = ''; stale = false; review = false;
    try {
      const state = await api(`/api/applications/${id}/editor`);
      initial = {profile:state.profile,design:state.design}; draft = clone(initial);
      version = state.version; conversationRevision = state.revision; loadedRevision = revision;
      history = []; future = []; confirmed = false; updateShared = false;
      const cached = restore ? recallDraft(session.user?.id,id) : null;
      if (cached) {
        initial = cached.initial; draft = cached.draft; version = cached.version; conversationRevision = cached.conversationRevision;
        history = cached.history; future = cached.future;
        stale = state.version !== version || state.revision !== conversationRevision;
        message = 'Your unsaved edits were restored.';
      } else forgetDraft(session.user?.id,id);
    } catch(err) {error = err.message;}
    finally {loading = false;}
  }
  function commit(mutator) {
    if (busy) return;
    const previous = serialize(draft);
    const next = clone(draft); mutator(next);
    if (serialize(next) === previous) return;
    history = [...history.slice(-29), previous]; future = []; draft = next;
    confirmed = false; review = false; message = ''; error = '';
  }
  const editProfile = fn => commit(next => fn(next.profile));
  const editDesign = fn => commit(next => fn(next.design));
  function undo() {
    if (!history.length) return;
    future = [...future,serialize(draft)]; draft = JSON.parse(history.at(-1)); history = history.slice(0,-1); review = false; confirmed = false; message = '';
  }
  function redo() {
    if (!future.length) return;
    history = [...history,serialize(draft)]; draft = JSON.parse(future.at(-1)); future = future.slice(0,-1); review = false; confirmed = false; message = '';
  }
  function addSection() {
    if (!addChoice) return;
    let key = addChoice;
    commit(next => {
      if (['Projects','Certifications','Languages','Custom section'].includes(key)) {
        const section = {id:`custom-${crypto.randomUUID()}`,title:key,items:[]};
        next.profile.custom_sections.push(section); key = section.id;
      }
      next.design.sections.push(key);
    });
    selected = key; addChoice = ''; addOpen=false;fieldOpen=true;
  }
  function selectCanvas(path) {
    const root = path.split('.')[0];
    selected = root === 'custom_sections' ? draft.profile.custom_sections[Number(path.split('.')[1])]?.id : root;
    panelTab = 'content';
  }
  async function uploadLogo(company,file,crop) {
    if (file.size > 3 * 1024 * 1024) {error = 'Choose a company logo under 3 MB.'; return;}
    uploading = true; error = '';
    try {
      const form = new FormData(); form.append('file',file); form.append('crop',String(crop));
      const result = await api(`/api/applications/${id}/editor/logo`, {method:'POST',body:form});
      uploading = false;
      editDesign(d => {d.company_logos[companyKey(company)] = result.url;});
      message = 'Logo ready. Save changes to use it on the CV.';
    } catch(err) {error = err.message;}
    finally {uploading = false;}
  }
  $effect(() => {
    const data = draft ? serialize(draft) : '';
    if (!data || canvasFocused) return;
    const controller = new AbortController();
    previewing = true;
    const timer = setTimeout(async () => {
      previewError = '';
      try {
        const response = await fetch(`/api/applications/${id}/editor/preview`,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':session.csrf},body:data,signal:controller.signal});
        if (!response.ok) throw new Error('Preview could not update. Check your fields or try again.');
        const result = await response.text();
        if (!controller.signal.aborted) {html = result; renderedDraft = data;}
      } catch(err) {if (err.name !== 'AbortError') previewError = err.message;}
      finally {if (!controller.signal.aborted) previewing = false;}
    },300);
    return () => {clearTimeout(timer);controller.abort();};
  });
  async function save() {
    const factsChanged = factualChanges.length > 0;
    saving = true; error = ''; message = '';
    try {
      const result = await api(`/api/applications/${id}/editor`, {method:'POST',json:{...clone(draft),version,revision:conversationRevision,confirmed,update_shared_profile:updateShared}});
      forgetDraft(session.user?.id,id);
      initial = {profile:result.editor.profile,design:result.editor.design}; draft = clone(initial);
      version = result.editor.version; conversationRevision = result.editor.revision;
      history = []; future = []; review = false; confirmed = false;
      onsave(result.application);
      await tick(); loadedRevision = revision; stale = false;
      message = result.shared_updated ? 'CV saved, role reassessed and shared profile refreshed.' : factsChanged ? 'CV saved and role reassessed.' : 'Changes saved.';
    } catch(err) {error = err.message; if (err.status === 409) stale = true;}
    finally {saving = false;}
  }
  function leave(event) {if (dirty) {event.preventDefault(); event.returnValue = '';}}
</script>
<svelte:window onbeforeunload={leave}/>
<section class="design-panel" id="design-editor" aria-label="CV editor">
    {#if loading}<p class="loading" role="status">Opening your CV…</p>{/if}
    {#if draft}
      <div class="editor-toolbar">
        <div><span class:unsaved={dirty} class="save-dot"></span><span>{saving ? 'Saving…' : dirty ? 'Unsaved changes' : 'All changes saved'}</span></div>
        <div class="toolbar-actions">
          <button type="button" class="mobile-view" onclick={() => mobileView = mobileView === 'tools' ? 'canvas' : 'tools'}><Icon name={mobileView === 'tools' ? 'eye' : 'edit'} size={16}/>{mobileView === 'tools' ? 'Show CV' : 'Show tools'}</button>
          <button type="button" disabled={busy || !history.length} onclick={undo} aria-label="Undo last edit" title="Undo last edit"><Icon name="undo" size={16}/> <span>Undo</span></button>
          <button type="button" disabled={busy || !future.length} onclick={redo} aria-label="Redo last edit" title="Redo last edit"><Icon name="redo" size={16}/> <span>Redo</span></button>
          <button type="button" class="help-button" aria-label="How to make a shareable CV" title="Editor guide" onclick={() => helpOpen=true}><Icon name="help" size={17}/></button>
          <button type="button" class="save-button" disabled={busy || blocked || !dirty || stale} onclick={() => {review = true; confirmed = false;}}><Icon name="save" size={16}/>{saving ? 'Rechecking this role…' : 'Review and save'}</button>
        </div>
      </div>
      {#if stale}<div class="notice" role="alert">This CV changed elsewhere. Reload before saving to avoid overwriting it. <button type="button" disabled={busy} onclick={() => load()}>Reload editor and discard draft</button></div>{/if}
      {#if error}<p class="notice error" role="alert">{error}</p>{/if}
      {#if message}<p class="notice" role="status">{message}</p>{/if}
      <div class="editor-workspace" data-mobile-view={mobileView} aria-busy={saving}>
        <fieldset class="editor-sidebar" disabled={busy || review}>
          <div class="editor-tabs" role="group" aria-label="Editor tools"><button type="button" class:active={panelTab === 'content'} aria-pressed={panelTab === 'content'} onclick={() => panelTab = 'content'}><Icon name="edit" size={18}/>Content</button><button type="button" class:active={panelTab === 'design'} aria-pressed={panelTab === 'design'} onclick={() => panelTab = 'design'}><Icon name="palette" size={18}/>Design</button></div>
          <div class="sidebar-scroll">
          {#if panelTab === 'content'}
            <div class="section-heading"><h3>On your CV</h3><span>Drag to arrange</span></div>
            <button type="button" class="contact-button" class:active={selected === 'contact'} onclick={() => editSection('contact')}><span class="section-name"><Icon name="user" size={16}/>Contact details</span><Icon name="edit" size={14}/></button>
            <EditorList items={draft.design.sections} label="section" compact removeLabel="Hide" removeIcon="eye-off" confirmRemove={false} onmove={(a,b) => editDesign(d => {d.sections = moveItem(d.sections,a,b);})} onremove={i => editDesign(d => {d.sections.splice(i,1);})}>
              {#snippet children(section)}<button type="button" class="section-select" class:active={selected === section} onclick={() => editSection(section)}><span class="section-name"><Icon name={sectionIcon(section)} size={16}/>{title(section)}</span></button>{/snippet}
            </EditorList>
            <p class="hint">Removing a section hides it from the design. Its source text stays available.</p>
            <button type="button" class="add-component" onclick={() => addOpen=true}><Icon name="plus" size={18}/> Add a section</button>
            <div class="editor-guidance"><Icon name="edit" size={18}/><div><strong>Make your experience clear</strong><p>Click a section to edit its details, or edit text directly on the CV. Use real examples of what you did.</p><button type="button" onclick={() => helpOpen=true}>Open the editor guide <Icon name="arrow" size={13}/></button></div></div>
          {:else}
            <div class="section-heading"><h3>Choose a layout</h3></div>
            <div class="template-list">{#each templates as template}<button type="button" class:selected={draft.design.template === template.id} aria-pressed={draft.design.template === template.id} onclick={() => editDesign(d => {d.template = template.id;})}><span class="mini-page {template.id}" aria-hidden="true"><i></i><b></b><em></em><em></em></span><span class="template-meta"><strong>{template.name}</strong><small>{template.note}</small></span></button>{/each}</div>
            <p class="hint">In two-column layouts, sections move within their column.</p>
            <h3>Colour</h3><div class="palette-list">{#each palettes as [key,name,colour]}<button type="button" aria-label={name} title={name} aria-pressed={draft.design.palette === key} class:chosen={draft.design.palette === key} style:--swatch={colour} onclick={() => editDesign(d => {d.palette=key;d.accent=colour;})}></button>{/each}</div>
            <label>Custom accent<input type="color" value={draft.design.accent} oninput={e => editDesign(d => {d.palette='custom';d.accent=e.currentTarget.value;})}/></label>
            <label>Font pairing<select value={draft.design.font} onchange={e => editDesign(d => {d.font=e.currentTarget.value;})}><option value="serif">Classic serif</option><option value="sans">Clean sans serif</option><option value="editorial">Georgia + Arial</option><option value="humanist">Trebuchet</option><option value="book">Palatino</option><option value="geometric">Verdana</option><option value="mono">Courier</option></select></label>
            <label>Text size<select value={draft.design.text_size} onchange={e => editDesign(d => {d.text_size=e.currentTarget.value;})}><option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option></select></label>
            <label>Spacing<select value={draft.design.spacing} onchange={e => editDesign(d => {d.spacing=e.currentTarget.value;})}><option value="compact">Compact</option><option value="comfortable">Comfortable</option><option value="airy">Airy</option></select></label>
            <label class="check"><input type="checkbox" checked={draft.design.show_photo} onchange={e => editDesign(d => {d.show_photo=e.currentTarget.checked;})}/> Show profile photo</label>
            {#if draft.design.show_photo}
              <label>Photo size<select value={draft.design.photo_size} onchange={e => editDesign(d => {d.photo_size=e.currentTarget.value;})}><option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option></select></label>
              <label>Photo shape<select value={draft.design.photo_shape} onchange={e => editDesign(d => {d.photo_shape=e.currentTarget.value;})}><option value="round">Round</option><option value="square">Square</option><option value="rounded">Rounded square</option><option value="portrait">Arch</option></select></label>
              <p class="hint"><a href={`/cvs/${cvId}`}>Change your profile photo on your saved CV.</a> Save your editor changes before leaving.</p>
            {/if}
          {/if}
          </div>
        </fieldset>
        <div class="canvas-area">
          <div class="canvas-toolbar"><div><strong>{canvasEditing ? 'Edit your source CV' : 'Draft preview'}</strong><small>{previewing ? 'Updating preview…' : 'Changes stay private until you save'}</small></div><button type="button" disabled={busy || review} class:active={!canvasEditing} onclick={() => canvasEditing = !canvasEditing}><Icon name={canvasEditing ? 'eye' : 'edit'} size={16}/>{canvasEditing ? 'Preview' : 'Edit text'}</button></div>
          {#if canvasEditing}<p class="canvas-tip">Click text to edit it. Use Content to add, arrange or remove entries.</p>{/if}
          {#if previewError}<p class="notice error" role="alert">{previewError}</p>{/if}
          <div class="canvas-scroll">
          <div class="canvas-paper" class:canvas-busy={busy || review}>
            {#if html}<DesignDocument {html} logosUrl={`/api/cvs/${cvId}/logos`} title="Editable CV canvas" editable={canvasEditing && !busy && !review && canvasCurrent} onselect={selectCanvas} onfocuschange={focused => canvasFocused = focused && canvasCurrent} onedit={(path,text) => {if (canvasCurrent) commit(next => {next.profile=editText(next.profile,path,text);});}}/>{:else}<p class="loading" role="status">Preparing your canvas…</p>{/if}
          </div>
          </div>
        </div>
      </div>
    {:else if error}<p class="notice error" role="alert">{error} <button type="button" onclick={() => load()}>Try again</button></p>{/if}
</section>
<EditorModal bind:open={addOpen} title="Add to your CV" description="Choose a section that helps someone understand your experience." labelId="add-section-title">
  <div class="section-library">
    {#each [...hidden,'Projects','Certifications','Languages','Custom section'] as choice}
      <button type="button" onclick={() => {addChoice=choice;addSection();}}><span class="library-icon"><Icon name={sectionIcon(choice)} size={22}/></span><span><strong>{title(choice)}</strong><small>{sectionNote(choice)}</small></span><Icon name="plus" size={18}/></button>
    {/each}
  </div>
</EditorModal>
<EditorModal bind:open={fieldOpen} title={selected === 'contact' ? 'Contact details' : title(selected)} description="Edit your own details. Changes stay in your draft until you review and save." labelId="edit-section-title" busy={busy}>
  {#if draft}<fieldset class="popup-fields" disabled={busy}><EditorFields profile={draft.profile} design={draft.design} {selected} {cvId} onedit={editProfile} ondesign={editDesign} onupload={uploadLogo} {busy}/></fieldset>{/if}
  {#if error}<p class="notice error" role="alert">{error}</p>{/if}
  <div class="popup-footer">{#if selected?.startsWith('custom-')}<button type="button" class="delete-section" disabled={busy} onclick={() => {fieldOpen=false;deleteSectionOpen=true;}}><Icon name="trash" size={15}/> Delete section</button>{/if}<button type="button" class="save-button" disabled={busy} onclick={() => fieldOpen=false}><Icon name="ready" size={16}/> Done editing</button></div>
</EditorModal>
<EditorModal bind:open={deleteSectionOpen} title="Delete this section?" description="This removes the section and its text from your draft. You can undo it before saving." labelId="delete-section-title">
  <div class="popup-footer"><button type="button" onclick={() => deleteSectionOpen=false}>Keep section</button><button type="button" class="delete-section" onclick={() => {commit(next => {next.profile.custom_sections=next.profile.custom_sections.filter(s => s.id !== selected);next.design.sections=next.design.sections.filter(s => s !== selected);});selected='summary';deleteSectionOpen=false;}}>Delete section</button></div>
</EditorModal>
<EditorModal bind:open={helpOpen} title="Make a CV worth sharing" description="Keep it relevant, readable and true to your experience." labelId="editor-help-title">
  <div class="help-steps">
    <div><Icon name="edit" size={22}/><section><h3>Explain your contribution</h3><p>Use work bullets to describe what you did, how you did it, and the result. Include numbers only when you can support them.</p></section></div>
    <div><Icon name="palette" size={22}/><section><h3>Make it easy to scan</h3><p>Put relevant sections first. Choose a readable font and leave space between entries. Hide sections that are not useful for this role.</p></section></div>
    <div><Icon name="eye" size={22}/><section><h3>Check the finished version</h3><p>Use Preview to read without editing controls. Check dates, contact details, company logos and spelling before saving.</p></section></div>
    <div><Icon name="share" size={22}/><section><h3>Share deliberately</h3><p>Save your edits, then open Share CV to review what others will see. Anyone with the link can open it. Your assessment and private conversation stay private.</p></section></div>
  </div>
</EditorModal>
<EditorModal bind:open={review} title={factualChanges.length ? 'Review your CV edits' : 'Save your design'} labelId="save-cv-title" busy={saving}>
        <section class="save-review">
          <div>
            {#if factualChanges.length}
              <p>Updated: {factualChanges.join(', ')}. Saving updates your source CV and rechecks this role. Other role checks keep their previous assessments.</p>
              <label class="check"><input type="checkbox" bind:checked={confirmed} disabled={saving}/> I confirm these details are accurate and describe my own experience.</label>
              {#if shared}<label class="check"><input type="checkbox" bind:checked={updateShared} disabled={saving}/> Also refresh the CV on my existing employer link</label>{/if}
            {:else}<p>Your layout and logos will update the employer link and eligible PDF. The assessment stays the same.</p>{/if}
          </div>
          <div class="review-actions"><button class="save-button" type="button" disabled={busy || blocked || stale || (factualChanges.length > 0 && !confirmed)} onclick={save}>{saving ? 'Saving and checking…' : factualChanges.length ? 'Save CV and recheck role' : 'Save design'}</button><button type="button" disabled={saving} onclick={() => review = false}>Keep editing</button></div>
          {#if error}<p class="notice error" role="alert">{error}</p>{/if}
        </section>
</EditorModal>
<style>
.design-panel {display:flex;flex-direction:column;flex:1;min-height:0;min-width:0;border:1px solid #cddbd3;border-radius:10px;background:var(--sheet);overflow:hidden;}
.editor-toolbar {display:flex;flex-shrink:0;justify-content:space-between;align-items:center;gap:12px;padding:10px 16px;background:#f7faf8;border-bottom:1px solid var(--line);font-size:12px;}
.editor-toolbar>div {display:flex;align-items:center;gap:8px;}.save-dot {width:7px;height:7px;flex-shrink:0;border-radius:50%;background:#537a60;}.save-dot.unsaved {background:#b58127;}
button {font:inherit;color:var(--ink);cursor:pointer;min-width:0;}
button:hover {color:var(--ink);background:#e8f0eb;}button:disabled {opacity:.45;cursor:default;}
button:focus-visible,select:focus-visible,input:focus-visible {outline:2px solid #245747;outline-offset:2px;}
.toolbar-actions button,.review-actions button,.canvas-toolbar button,.notice button {border:1px solid var(--line);background:white;min-height:36px;padding:8px 12px;border-radius:6px;font-size:12px;}
button.save-button {background:#245747;color:white;border:1px solid #245747;font-weight:600;padding:9px 16px;border-radius:6px;}
button.save-button:hover {color:white;background:#1c4738;}.toolbar-actions .mobile-view {display:none;}
.editor-workspace {display:grid;grid-template-columns:360px minmax(0,1fr);flex:1;min-height:0;min-width:0;}
.editor-sidebar {display:flex;flex-direction:column;min-width:0;min-height:0;margin:0;padding:0;border:0;border-right:1px solid var(--line);}
.editor-tabs {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));flex-shrink:0;gap:4px;margin:12px;padding:4px;border:1px solid #dbe4dd;background:#edf2ee;border-radius:9px;}
.editor-tabs button {gap:8px;display:flex;align-items:center;justify-content:center;min-width:0;min-height:44px;height:44px;padding:10px 16px;border:0;border-radius:6px;font-size:14px;line-height:20px;font-weight:600;color:#496452;background:transparent;white-space:nowrap;}
.editor-tabs button.active {background:#fff;color:#173f29;box-shadow:0 1px 4px #163d281c;}.editor-tabs button:hover {color:#173f29;background:#f8fbf9;}
.sidebar-scroll {display:flex;flex-direction:column;gap:12px;flex:1;min-height:0;min-width:0;overflow-y:auto;overflow-x:hidden;overscroll-behavior:contain;padding:4px 16px 20px;scrollbar-gutter:stable;}
.sidebar-scroll>* {flex-shrink:0;min-width:0;}
.section-heading {display:flex;align-items:center;justify-content:space-between;gap:6px;}.section-heading h3,h3 {font-size:13px;margin:0;line-height:1.4;}.section-heading span {color:var(--muted);font-size:11px;}
.contact-button,.section-select {display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;min-width:0;min-height:36px;background:transparent;border:0;padding:6px 8px;color:var(--ink);text-align:left;font-size:13px;line-height:1.3;border-radius:5px;overflow-wrap:anywhere;}
.contact-button {border:1px solid var(--line);padding:10px;}.section-select.active,.contact-button.active {background:#e8f1eb;color:#245747;font-weight:600;}.section-select span,.contact-button span {color:#678573;flex-shrink:0;}
.hint {font-size:11px;line-height:1.5;color:var(--muted);margin:0;}
.editor-sidebar label {display:grid;gap:5px;font-size:12px;font-weight:600;}.editor-sidebar select {width:100%;min-width:0;font-size:13px;min-height:36px;padding:7px 10px;}.editor-sidebar input[type=color] {width:100%;height:34px;padding:3px;}
.canvas-area {display:flex;flex-direction:column;min-width:0;min-height:0;background:#e8eeea;}
.canvas-toolbar {display:flex;flex-shrink:0;justify-content:space-between;align-items:center;padding:16px 24px 8px;min-height:58px;font-size:13px;gap:10px;}.canvas-toolbar small {display:block;color:#5d7164;font-size:11px;margin-top:4px;}
.canvas-tip {flex-shrink:0;font-size:11px;color:#597061;margin:0;padding:0 24px 12px;}
.canvas-scroll {flex:1;min-height:0;min-width:0;overflow:auto;overscroll-behavior:contain;padding:8px 24px 32px;scrollbar-gutter:stable;}
.canvas-paper {width:100%;max-width:900px;margin:0 auto;background:white;box-shadow:0 3px 18px #243e2d15;min-height:400px;border:1px solid #d9e0db;border-radius:2px;}.canvas-busy {opacity:.7;}
.template-list {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}
.template-list button {display:flex;align-items:center;justify-content:flex-start;gap:9px;min-width:0;width:100%;min-height:76px;color:var(--ink);padding:10px;text-align:left;border:1px solid var(--line);border-radius:7px;background:white;}
.template-list button.selected {border:2px solid #245747;padding:9px;background:#f4f9f5;}.template-list button:hover {background:#edf4ef;}
.template-meta {display:block;min-width:0;}.template-meta strong {display:block;font-size:13px;font-weight:600;line-height:1.35;}.template-meta small {display:block;color:var(--muted);font-size:10px;font-weight:400;line-height:1.4;margin-top:3px;}
.mini-page {display:block;flex:0 0 32px;width:32px;height:46px;border:1px solid #d5dfd8;padding:5px;margin:0;background:#fff;}.mini-page i,.mini-page b,.mini-page em {display:block;height:2px;background:#91a99a;margin-bottom:4px;}.mini-page i {width:70%;height:4px;background:#245747;}.mini-page b {height:1px;margin:5px 0;}.mini-page.modern {border-right:9px solid #dce9df;}.mini-page.creative {border-top:10px solid #cddfd1;}.mini-page.minimal i {background:#526458;}
.palette-list {display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;}.palette-list button {justify-self:center;width:32px;min-width:32px;height:32px;min-height:32px;padding:0;background:var(--swatch);border:3px solid white;box-shadow:0 0 0 1px #d6dfd9;border-radius:50%;}.palette-list button.chosen {box-shadow:0 0 0 2px #245747;}
.check {display:flex!important;align-items:flex-start;gap:8px!important;font-size:12px!important;font-weight:400!important;line-height:1.5;}.check input {width:auto;flex-shrink:0;margin-top:3px;}
.save-review {display:grid;gap:18px;}.save-review p {margin:0 0 12px;font-size:13px;line-height:1.6;}.save-review label {margin-top:12px;}.review-actions {display:flex;justify-content:flex-end;gap:8px;flex-wrap:wrap;}
.notice {flex-shrink:0;margin:0;padding:12px 16px;background:#edf4ef;color:#245747;font-size:12px;line-height:1.5;}.notice.error {background:#fbeee9;color:#8b3627;}.notice button {margin-left:8px;}.loading {padding:30px;text-align:center;font-size:13px;}.delete-section {background:transparent;border:1px solid #e3c5bc;color:#8b3627;border-radius:6px;font-size:11px;padding:9px;}
.sr-only {position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;}
@media(min-width:801px) and (max-width:1100px) {.editor-workspace {grid-template-columns:320px minmax(0,1fr);}.canvas-toolbar {padding-inline:16px;}.canvas-tip {padding-inline:16px;}.canvas-scroll {padding-inline:16px;}}
@media(max-width:800px) {
  .editor-workspace {grid-template-columns:minmax(0,1fr);}
  .editor-workspace[data-mobile-view=tools] .canvas-area,.editor-workspace[data-mobile-view=canvas] .editor-sidebar {display:none;}
  .editor-sidebar {border-right:0;}.editor-tabs {margin:10px;}.sidebar-scroll {padding:4px 14px 20px;}
  .editor-toolbar {padding:8px 10px;font-size:11px;gap:6px;flex-wrap:wrap;}.editor-toolbar>div {gap:5px;}.toolbar-actions {margin-left:auto;}
  .toolbar-actions .mobile-view {display:inline-flex;}.toolbar-actions button {padding:7px 6px;min-height:36px;}.toolbar-actions button span {display:none;}
  .canvas-toolbar {padding:12px 12px 8px;}.canvas-tip {padding:0 12px 10px;}.canvas-scroll {padding:4px 8px 20px;}
  .review-actions {justify-content:stretch;}.review-actions button {flex:1;}
}
@media(prefers-reduced-motion:reduce) {* {scroll-behavior:auto!important;}}
.section-name {display:flex;align-items:center;gap:9px;color:inherit!important;min-width:0;}
.add-component {display:flex;justify-content:center;gap:8px;min-height:42px;padding:10px;border:1px dashed #92b09c;border-radius:7px;background:#f5faf6;color:#245747;font-size:13px;}
.editor-guidance {display:flex;gap:10px;padding:14px;background:#f1f6f2;border-radius:8px;color:#45654f;font-size:12px;}.editor-guidance strong {font-size:12px;}.editor-guidance p {font-size:12px;line-height:1.6;margin:5px 0;}.editor-guidance button {min-height:30px;background:transparent;border:0;padding:0;font-size:11px;text-decoration:underline;}
.section-library {display:grid;gap:9px;}.section-library button {display:flex;justify-content:flex-start;gap:12px;padding:14px;border:1px solid #dae5dd;border-radius:9px;background:white;text-align:left;}.section-library button:hover {background:#f1f7f3;border-color:#91ae9b;}.section-library button>span:nth-child(2) {flex:1;}.section-library strong {display:block;font-size:14px;}.section-library small {display:block;color:var(--muted);font-size:12px;font-weight:400;line-height:1.5;margin-top:4px;}.library-icon {display:grid;place-items:center;flex-shrink:0;width:42px;height:42px;background:#edf5ef;border-radius:10px;color:#386b4a;}
.popup-fields {border:0;padding:0;margin:0;min-width:0;}.popup-footer {display:flex;justify-content:flex-end;gap:10px;margin-top:20px;}.popup-footer button {padding:10px 14px;border-radius:6px;font-size:12px;}.popup-footer .delete-section {margin-right:auto;}
.help-steps {display:grid;gap:20px;}.help-steps>div {display:flex;gap:14px;color:#386b4a;}.help-steps h3 {font-size:14px;color:var(--ink);margin:0;}.help-steps p {font-size:13px;line-height:1.65;color:var(--muted);margin:5px 0 0;}
</style>
