<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/session.svelte.js';
  import Icon from '../lib/Icon.svelte';
  import ShareCv from '../lib/ShareCv.svelte';
  import DesignPanel from '../lib/DesignPanel.svelte';
  let { id } = $props();
  let row = $state(null);
  let error = $state('');
  let shareOpen = $state(false);
  let editor = $state();
  let editorState = $state({dirty:false,busy:false});
  let revision = $state(0);
  async function load() {
    error = '';
    try {row = await api(`/api/applications/${id}`);}
    catch (err) {error = err.message;}
  }
  onMount(load);
</script>
<section class="editor-page">
  <header class="editor-page-header">
    <div class="editor-title"><a class="back" href={`/applications/${id}`} aria-label="Back to role check"><Icon name="back" size={17}/> <span>Role check</span></a><div><h1>Design and edit your CV</h1>{#if row}<p>{row.candidate_name}<span aria-hidden="true"> · </span>{row.role_title}</p>{/if}</div></div>
    {#if row}<button type="button" class="share-button" onclick={() => shareOpen=true}><Icon name="share" size={17}/> Share CV</button>{/if}
  </header>
  {#if error}<p class="alert" role="alert">{error} <button type="button" onclick={load}>Try again</button></p>
  {:else if row}<DesignPanel bind:this={editor} onstatechange={state => editorState=state} {id} cvId={row.cv_id} shared={Boolean(row.share_path)} {revision} onsave={updated => {row = updated; revision += 1;}}/>
  {:else}<p class="hint" role="status">Loading your CV editor…</p>{/if}
</section>
{#if row}<ShareCv bind:open={shareOpen} {row} dirty={editorState.dirty} busy={editorState.busy} onpublished={share_path => row={...row,share_path}} onreview={() => {shareOpen=false;editor?.reviewChanges();}}/>{/if}
<style>
  .editor-page {display:flex;flex-direction:column;flex:1;min-width:0;min-height:0;}
  .editor-page-header {display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px 0;flex-shrink:0;}
  .editor-title {display:flex;gap:22px;align-items:center;min-width:0;}.editor-title>div {min-width:0;}
  h1 {font-size:22px;line-height:1.2;margin:0;letter-spacing:-.025em;}p {font-size:12px;color:var(--muted);margin:5px 0 0;overflow-wrap:anywhere;}
  .editor-title p span {margin:0 6px;}
  .back {display:flex;align-items:center;gap:8px;white-space:nowrap;font-size:12px;color:var(--muted);text-decoration:none;padding:10px 12px;border:1px solid var(--line);border-radius:7px;background:white;}
  .back:hover {color:var(--accent);background:#edf4ef;}.share-button {display:flex;align-items:center;gap:8px;background:#245747;color:white;border:1px solid #245747;border-radius:7px;min-height:38px;padding:9px 15px;font-size:13px;white-space:nowrap;}
  @media(max-width:800px) {.editor-page-header {padding:12px 0;gap:8px;flex-wrap:wrap;}.editor-title {gap:12px;}h1 {font-size:18px;}.back {padding:8px;}.back span {display:none;}.share-button {margin-left:46px;min-height:34px;padding:7px 12px;font-size:12px;}}
</style>
