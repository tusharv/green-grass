<script>
  import Icon from './Icon.svelte';
  let { open = $bindable(false), title, labelId, description = '', wide = false, busy = false, children } = $props();
  let dialog;
  $effect(() => {
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    else if (!open && dialog.open) dialog.close();
  });
</script>
<dialog bind:this={dialog} class:wide aria-labelledby={labelId} onclose={() => open = false} oncancel={event => {if (busy) event.preventDefault();}}>
  <header><div><h2 id={labelId}>{title}</h2>{#if description}<p>{description}</p>{/if}</div><button type="button" class="close" aria-label="Close {title}" disabled={busy} onclick={() => open = false}><Icon name="close" size={20}/></button></header>
  <div class="modal-body">{@render children()}</div>
</dialog>
<style>
  dialog {width:min(560px,calc(100vw - 32px));max-width:none;max-height:88dvh;padding:0;border:1px solid #d4e0d7;border-radius:14px;background:white;color:var(--ink);box-shadow:0 24px 90px #10261d40;overflow:auto;}
  dialog.wide {width:min(1000px,calc(100vw - 32px));}dialog::backdrop {background:#13251e75;backdrop-filter:blur(3px);}
  header {position:sticky;top:0;z-index:2;display:flex;align-items:flex-start;justify-content:space-between;gap:16px;padding:20px 22px 16px;border-bottom:1px solid var(--line);background:white;}
  h2 {margin:0;font-size:20px;line-height:1.3;letter-spacing:-.02em;}p {margin:6px 0 0;font-size:13px;line-height:1.5;color:var(--muted);}
  .close {display:grid;place-items:center;width:36px;height:36px;min-height:36px;flex-shrink:0;padding:0;background:#f0f5f1;border:0;color:#385843;border-radius:8px;}.close:hover {background:#e0ece3;}.modal-body {padding:20px 22px 24px;}
  @media(max-width:600px) {dialog,dialog.wide {width:calc(100vw - 20px);max-height:92dvh;border-radius:12px;}header {padding:16px;}h2 {font-size:18px;}.modal-body {padding:16px;}}
</style>
