<script>
  import { onMount, tick } from 'svelte';
  import { api, session } from './session.svelte.js';
  import DesignDocument from './DesignDocument.svelte';
  let { id, saved = null, onsave = () => {} } = $props();
  const templates = [
    {id:'classic',name:'Classic',note:'Timeless serif · One column'},
    {id:'modern',name:'Modern',note:'Clean typography · Skills sidebar'},
    {id:'creative',name:'Creative',note:'Bold header · Contrasting sidebar'},
    {id:'minimal',name:'Minimal',note:'Quiet headings · Compact layout'},
  ];
  const palettes = [
    {id:'forest',name:'Forest & mist',accent:'#245747',paper:'#f1f6f2'},
    {id:'navy',name:'Navy & ice',accent:'#203c64',paper:'#f0f4fa'},
    {id:'plum',name:'Plum & pearl',accent:'#603c65',paper:'#f7f2f7'},
    {id:'terracotta',name:'Terracotta & sand',accent:'#8b4535',paper:'#faf4ef'},
    {id:'slate',name:'Slate & silver',accent:'#364454',paper:'#f3f5f7'},
    {id:'teal',name:'Teal & frost',accent:'#15616a',paper:'#eff7f7'},
  ];
  let draft = $state({template:'classic',accent:'#245747',palette:'custom',photo_size:'medium',photo_shape:'round',font:'serif',text_size:'medium',spacing:'comfortable',show_photo:true,sections:['summary','experience','skills','education']});
  let html = $state('');
  let error = $state('');
  let saving = $state(false);
  let previewing = $state(false);
  let savedMessage = $state('');
  let open = $state(false);
  let ready = $state(false);
  onMount(async () => {
    if (saved) draft = {...draft,...JSON.parse(JSON.stringify(saved))};
    open = new URLSearchParams(location.search).get('design') === '1';
    ready = true;
    if (open) {
      await tick();
      const panel = document.getElementById('design-editor');
      panel?.querySelector('button')?.focus({ preventScroll: true });
      panel?.scrollIntoView({ block: 'start' });
    }
  });
  $effect(() => {
    const data = JSON.stringify(draft);
    if (!ready || !open) return;
    savedMessage = '';
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      previewing = true;
      error = '';
      try {
        const response = await fetch(`/api/applications/${id}/design-preview`, {method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':session.csrf},body:data,signal:controller.signal});
        if (!response.ok) throw new Error('Could not load the preview. Change a setting to retry.');
        const next = await response.text();
        if (!controller.signal.aborted) html = next;
      } catch (err) { if (err.name !== 'AbortError') error = err.message; }
      finally { if (!controller.signal.aborted) previewing = false; }
    }, 250);
    return () => {clearTimeout(timer);controller.abort();};
  });
  async function save() {
    saving = true; error = ''; savedMessage = '';
    try {
      const row = await api(`/api/applications/${id}/design`, {method:'POST',json:JSON.parse(JSON.stringify(draft))});
      onsave(row); savedMessage = 'Design saved. Your shared profile and next PDF download use this design.';
    } catch (err) {error = err.message;}
    finally {saving = false;}
  }
  function move(index, direction) {
    const sections = [...draft.sections];
    [sections[index], sections[index+direction]] = [sections[index+direction], sections[index]];
    draft = {...draft,sections};
  }
</script>
<section class="design-panel" id="design-editor">
  <button class="design-toggle" type="button" aria-expanded={open} onclick={() => open = !open}>
    <span><strong>Design your profile &amp; CV</strong><small>Four templates. Your colour, type and layout.</small></span><span aria-hidden="true">{open ? '−' : '+'}</span>
  </button>
  {#if open}
    <div class="template-list" aria-label="Choose a template">
      {#each templates as template}
        <button type="button" disabled={saving} class:selected={draft.template === template.id} aria-pressed={draft.template === template.id} onclick={() => draft = {...draft,template:template.id}}>
          <span class="thumbnail {template.id}" style:--ink={draft.accent} aria-hidden="true"><i></i><b></b><em></em><em></em><em></em></span>
          <strong>{template.name}</strong><small>{template.note}</small>
        </button>
      {/each}
    </div>
    <div class="design-workspace">
      <fieldset class="controls" disabled={saving}>
        <h3>Make it yours</h3>
        <h4>Colour combinations</h4>
        <div class="palette-list" aria-label="Colour combinations">
          {#each palettes as palette}
            <button type="button" class:chosen={draft.palette === palette.id} aria-pressed={draft.palette === palette.id} onclick={() => draft = {...draft,palette:palette.id,accent:palette.accent}}>
              <span class="swatches" aria-hidden="true"><i style:background={palette.accent}></i><i style:background={palette.paper}></i></span>{palette.name}
            </button>
          {/each}
        </div>
        <details><summary>Custom colour</summary><label>Choose your own<input type="color" value={draft.accent} oninput={(event) => draft = {...draft,palette:'custom',accent:event.currentTarget.value}}/></label></details>
        <label>Font pairing<select bind:value={draft.font}><option value="serif">Classic serif</option><option value="sans">Clean sans serif</option><option value="editorial">Editorial · Georgia + Arial</option><option value="humanist">Humanist · Trebuchet</option><option value="book">Bookish · Palatino</option><option value="geometric">Geometric · Verdana</option><option value="mono">Technical · Courier</option></select></label>
        <label>Text size<select bind:value={draft.text_size}><option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option></select></label>
        <label>Spacing<select bind:value={draft.spacing}><option value="compact">Compact</option><option value="comfortable">Comfortable</option><option value="airy">Airy</option></select></label>
        <label class="photo-toggle"><input type="checkbox" bind:checked={draft.show_photo}/> Show profile photo</label>
        {#if draft.show_photo}
          <label>Photo size<select bind:value={draft.photo_size}><option value="small">Small</option><option value="medium">Medium</option><option value="large">Large</option></select></label>
          <label>Photo shape<select bind:value={draft.photo_shape}><option value="round">Round</option><option value="square">Square</option><option value="rounded">Rounded square</option><option value="portrait">Arch</option></select></label>
        {/if}
        <p class="hint">Uses your uploaded photo or selected GitHub photo. Fonts use local fallbacks when unavailable.</p>
        <h4>Section order</h4>
        <p class="hint">In sidebar templates, order applies within each column.</p>
        <ol class="section-order">{#each draft.sections as section,index}<li><span>{section}</span><button type="button" aria-label="Move {section} up" disabled={index === 0} title="Move {section} up" onclick={() => move(index,-1)}><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 20V4m-7 7 7-7 7 7"/></svg><small>Up</small></button><button type="button" aria-label="Move {section} down" disabled={index === 3} title="Move {section} down" onclick={() => move(index,1)}><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 4v16m-7-7 7 7 7-7"/></svg><small>Down</small></button></li>{/each}</ol>
        <button type="button" class="button" disabled={saving} onclick={save}>{saving ? 'Saving…' : 'Save design'}</button>
        <p class="hint">Saving updates the existing employer link. PDFs remain available for ready results only.</p>
        {#if savedMessage}<p role="status">{savedMessage}</p>{/if}
        {#if error}<p class="alert" role="alert">{error}</p>{/if}
      </fieldset>
      <div class="preview"><p class="preview-label" role="status">{previewing ? 'Updating preview…' : 'Live preview · Unsaved changes stay private'}</p>{#if html}<DesignDocument {html} logosUrl={`/api/applications/${id}/logos`}/>{/if}</div>
    </div>
  {/if}
</section>
<style>
.design-panel { scroll-margin-top:1rem; border:1px solid var(--line); border-radius:12px; background:var(--sheet); overflow:hidden; }
.design-toggle { width:100%; display:flex; justify-content:space-between; align-items:center; border:0; padding:20px; background:transparent; text-align:left; color:var(--ink); cursor:pointer; }
.design-toggle strong { font-size:1.1rem; } small { display:block; color:var(--muted); margin-top:5px; font-size:.8rem; font-weight:400; }
.template-list { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; padding:0 20px 20px; }
.template-list button { display:block; text-align:left; padding:12px; background:white; border:2px solid var(--line); border-radius:8px; cursor:pointer; color:var(--ink); }
.template-list button.selected { border-color:var(--accent); background:#f2f7f4; }
.thumbnail { display:block; width:80px; height:102px; padding:10px; background:white; border:1px solid #ddd; margin-bottom:12px; }
.thumbnail i { display:block; width:70%; height:8px; background:var(--ink); margin-bottom:8px; }
.thumbnail b { display:block; height:2px; background:var(--ink); margin-bottom:10px; }
.thumbnail em { display:block; height:12px; margin:5px 0; background:repeating-linear-gradient(#d4d9dd 0 2px,transparent 2px 5px); }
.thumbnail.modern { border-left:16px solid var(--ink); }.thumbnail.creative { border-top:25px solid var(--ink); border-left:14px solid #e3e9ed; }.thumbnail.minimal b { background:#ddd; }.thumbnail.minimal i { height:5px; }
.design-workspace { display:grid; grid-template-columns:280px minmax(0,1fr); border-top:1px solid var(--line); }
.controls { border:0; margin:0; min-width:0; padding:20px; display:flex; flex-direction:column; gap:12px; }.controls h3,.controls h4,.controls p {margin:0;}.controls label {display:grid;gap:6px;font-size:.85rem;font-weight:600;}.controls select {width:100%;}.controls input[type="color"] {height:42px;padding:4px;cursor:pointer;}.controls .photo-toggle {display:flex;align-items:center;}.photo-toggle input {width:auto;}
.section-order {list-style:none;padding:0;margin:0;}.section-order li {display:flex;gap:4px;align-items:center;margin:7px 0;}.section-order span {flex:1;text-transform:capitalize;}.section-order button {color:var(--ink);display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:44px;min-height:44px;padding:5px;background:white;border:1px solid var(--line);border-radius:4px;cursor:pointer;}.section-order button:disabled {opacity:.35;cursor:default;}
.section-order button small {font-size:10px;margin:0;color:inherit;}
.palette-list {display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.palette-list button {display:flex;flex-direction:column;gap:7px;align-items:flex-start;padding:10px;border:1px solid var(--line);border-radius:7px;background:white;color:var(--ink);font-size:12px;text-align:left;cursor:pointer;}
.palette-list button.chosen {outline:2px solid var(--accent);outline-offset:1px;}
.swatches {display:flex;gap:4px;}.swatches i {display:block;width:24px;height:24px;border-radius:50%;border:1px solid #0002;}
.controls details {font-size:.8rem;}.controls summary {cursor:pointer;}.controls details label {margin-top:8px;}
.preview { background:#e9edee; padding:18px; min-width:0; }.preview-label {font-size:.75rem;color:var(--muted);margin:0 0 12px;}
@media(max-width:800px) {.design-workspace {grid-template-columns:1fr;}.template-list {grid-template-columns:repeat(2,1fr);}.preview {padding:6px;}.preview-label {padding:8px;}}
</style>
