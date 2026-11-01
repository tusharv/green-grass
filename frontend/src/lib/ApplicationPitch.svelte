<script>
  import { onMount } from 'svelte';
  import Icon from './Icon.svelte';
  import EditorModal from './EditorModal.svelte';
  import { api } from './session.svelte.js';
  let { row, onupdate = () => {} } = $props();
  const sections = [{key:'honest_review',path:'honest-review',title:'Honest review',icon:'eye',id:'honest-title',description:'A candid Ollama review of your strengths, gaps and screening risks.'},{key:'cover_letter',path:'cover-letter',title:'Cover letter',icon:'mail',id:'cover-letter-title',description:'A positive, employer-friendly letter written by Ollama from your saved CV and this role.'}];
  let state = $state(Object.fromEntries(sections.map(s=>[s.key,{busy:false,error:'',editing:false,draft:'',original:'',revision:'',copied:false}])));
  let replaceOpen = $state(false);
  let replacing = $state(null);
  function textFor(s) {
    const item=row[s.key];
    if (!item) return '';
    if (item.text) return item.text;
    return [item.verdict, 'What supports your application', ...(item.strengths || []).map(m=>`${m.name}: ${m.quote || (m.source==='work' ? 'Supported by work evidence' : 'Listed in CV skills')}`), 'Where a recruiter may push back', ...(item.risks || []), 'Will you make the next round?',item.next_round].filter(Boolean).join('\n\n');
  }
  const dirty = $derived(Object.values(state).some(s=>s.editing && s.draft!==s.original));
  onMount(()=>{
    for (const section of sections) if (!row[section.key]) generate(section);
    const unload=e=>{if(dirty){e.preventDefault();e.returnValue='';}};
    const navigate=e=>{
      const link=e.target instanceof Element ? e.target.closest('a') : null;
      if (!dirty || !link || link.target==='_blank') return;
      const url=new URL(link.href,location.href);
      if(url.pathname===location.pathname && url.search===location.search) return;
      if(!window.confirm('Leave this page and discard unsaved text edits?')){e.preventDefault();e.stopImmediatePropagation();}
    };
    window.addEventListener('beforeunload',unload);window.addEventListener('click',navigate,true);
    return ()=>{window.removeEventListener('beforeunload',unload);window.removeEventListener('click',navigate,true);};
  });
  function edit(s){const current=state[s.key];current.original=textFor(s);current.draft=current.original;current.revision=row[s.key].revision;current.editing=true;current.error='';}
  async function save(s){
    const current=state[s.key];current.busy=true;current.error='';
    try {const updated=await api(`/api/applications/${row.id}/${s.path}`,{method:'PATCH',json:{text:current.draft,expected_revision:current.revision}});onupdate({...row,[s.key]:updated[s.key]});current.editing=false;current.copied=false;}
    catch(err){current.error=err.message;}finally{current.busy=false;}
  }
  function requestGenerate(s){if(row[s.key]){replacing=s;replaceOpen=true;}else generate(s);}
  async function generate(s){
    replaceOpen=false;
    if (!s || state[s.key].busy) return;
    const current=state[s.key];current.busy=true;current.error='';current.copied=false;
    try {const updated=await api(`/api/applications/${row.id}/${s.path}`,{method:'POST'});onupdate({...row,[s.key]:updated[s.key]});current.editing=false;}
    catch(err){current.error=err.message;}finally{current.busy=false;}
  }
  async function copy(s){try{await navigator.clipboard.writeText(textFor(s));state[s.key].copied=true;}catch{state[s.key].error='Select the text and copy it manually.';}}
</script>
{#each sections as section}
  {@const current=state[section.key]}
  {@const item=row[section.key]}
  <section class="review-card" aria-labelledby={section.id} aria-busy={current.busy}>
    <div class="heading"><span class="mark"><Icon name={section.icon} size={21}/></span><div><p class="eyebrow">{section.key==='honest_review' ? 'A candid assessment' : 'Your evidence, your pitch'}</p><h2 id={section.id}>{section.title}</h2></div></div>
    <p class="hint">{section.description} Private to you; nothing is sent or published.</p>
    <div class="toolbar">
      {#if current.editing}
        <button class="button" disabled={current.busy || !current.draft.trim()} onclick={()=>save(section)}><Icon name="save" size={16}/>Save changes</button>
        <button class="button secondary" disabled={current.busy} onclick={()=>{current.editing=false;current.error='';}}>Cancel edits</button>
      {:else}
        <button class="button" disabled={current.busy} onclick={()=>requestGenerate(section)}><Icon name="redo" size={16}/>{current.busy ? 'Writing and checking…' : item ? `Regenerate ${section.title.toLowerCase()}` : `Generate ${section.title.toLowerCase()}`}</button>
        {#if item}<button class="button secondary" disabled={current.busy} onclick={()=>edit(section)}><Icon name="edit" size={16}/>Edit {section.title.toLowerCase()}</button><button class="button secondary" onclick={()=>copy(section)}><Icon name="copy" size={16}/>{current.copied ? 'Copied' : 'Copy'}</button>{/if}
      {/if}
    </div>
    {#if current.busy}<p class="hint" role="status">{current.editing ? 'Saving your changes…' : 'Ollama is preparing this section. Your other section stays unchanged.'}</p>{/if}
    {#if current.error}<p class="alert" role="alert">{current.error}</p>{/if}
    {#if current.editing}
      <label class="edit-label">{section.title} text<textarea rows="16" maxlength="16000" disabled={current.busy} bind:value={current.draft}></textarea></label>
      <p class="hint">Your edits are saved as your own text, not as AI-verified claims. They do not change your CV or assessment.</p>
    {:else if item}
      <p class="status">{item.edited_by_user ? 'Edited by you · Review accuracy before using' : 'Ollama draft · Review before using'}</p>
      <div class="document" class:letter={section.key==='cover_letter'}>{textFor(section)}</div>
      {#if section.key==='cover_letter' && !item.edited_by_user}
        <details><summary>Evidence used in this draft</summary>{#each item.sources || [] as source}<p><strong>{source.kind}{source.employer ? ' · '+source.employer : ''}</strong></p><blockquote>{source.text}</blockquote>{/each}</details>
      {/if}
    {:else}<div class="empty-draft"><Icon name={section.icon} size={24}/><p>Your {section.title.toLowerCase()} will appear here.<br/>Generate it when you’re ready, then edit or regenerate as needed.</p></div>{/if}
  </section>
{/each}
<EditorModal bind:open={replaceOpen} title="Replace the saved draft?" labelId="replace-insight-title" description="Ollama will write a new version of this section. It replaces your current text only after generation succeeds. Your other section stays unchanged.">
  <div class="toolbar"><button class="button secondary" onclick={()=>replaceOpen=false}>Keep current draft</button><button class="button" onclick={()=>generate(replacing)}>Regenerate draft</button></div>
</EditorModal>
<style>
  .heading {display:flex;align-items:center;gap:12px;margin-bottom:14px;}.heading h2 {margin:0;scroll-margin-top:32px;}.mark {display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#e5efe8;color:var(--accent);flex-shrink:0;}
  .toolbar {display:flex;gap:8px;flex-wrap:wrap;margin:18px 0;}.toolbar button {gap:7px;font-size:13px;}.status {font-size:12px;color:var(--muted);margin:12px 0;}
  .document {white-space:pre-wrap;overflow-wrap:anywhere;padding:24px;border:1px solid var(--line);border-radius:8px;line-height:1.75;font-size:15px;}.document.letter {font-family:var(--serif);background:var(--paper);font-weight:400;}
  .empty-draft {display:flex;gap:14px;align-items:center;padding:20px;background:var(--canvas);border:1px dashed var(--line);border-radius:8px;color:var(--muted);}.empty-draft p {margin:0;font-size:13px;line-height:1.6;}
  .edit-label {font-size:13px;}textarea {width:100%;font-size:15px;line-height:1.65;resize:vertical;}.hint {font-size:13px;line-height:1.6;}
  details {margin-top:16px;font-size:13px;}summary {cursor:pointer;color:var(--accent);font-weight:600;padding:8px 0;}blockquote {border-left:2px solid var(--line);padding-left:12px;margin:8px 0;color:var(--muted);}
  @media(max-width:600px){.document{padding:16px;}.toolbar button {min-height:40px;}}
</style>
