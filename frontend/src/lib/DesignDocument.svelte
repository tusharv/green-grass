<script>
  import { onMount } from 'svelte';
  let { html = '', title = 'CV design preview', logosUrl = '', editable = false, onedit = () => {}, onselect = () => {}, onfocuschange = () => {} } = $props();
  let generation = $state(0);
  let bodyObserver;
  let frame;
  let height = $state(900);
  function resize() {
    if (frame?.contentDocument?.body) height = Math.ceil(frame.contentDocument.body.getBoundingClientRect().height) + 4;
  }
  let logoController;
  function loaded() {
    resize();
    generation += 1;
    bodyObserver?.disconnect();
    bodyObserver = new ResizeObserver(resize);
    if (frame?.contentDocument?.body) bodyObserver.observe(frame.contentDocument.body);
    logoController?.abort();
    const controller = new AbortController();
    logoController = controller;
    const doc = frame?.contentDocument;
    if (!doc || !logosUrl) return;
    for (const badge of doc.querySelectorAll('[data-company-index]')) {
      if (badge.dataset.logoCustom === 'true') continue;
      fetch(`${logosUrl}/${badge.dataset.companyIndex}?employer=${encodeURIComponent(badge.dataset.companyName || '')}`, {signal:controller.signal,credentials:'same-origin'})
        .then(response => response.ok ? response.json() : null)
        .then(logo => {
          if (!logo?.url || controller.signal.aborted || frame?.contentDocument !== doc) return;
          const url = new URL(logo.url);
          if (url.protocol !== 'https:' || !['upload.wikimedia.org','thumb.wikimedia.org'].includes(url.hostname)) return;
          const image = doc.createElement('img');
          image.alt = '';
          image.referrerPolicy = 'no-referrer';
          image.onload = () => { if (!controller.signal.aborted) badge.append(image); };
          image.src = url.href;
        }).catch(() => {});
    }
  }
  $effect(() => {
    generation;
    const active = editable;
    const doc = frame?.contentDocument;
    if (!doc?.body) return;
    const style = doc.createElement('style');
    style.textContent = '[contenteditable] {cursor:text;border-radius:3px;outline:1px dashed transparent;outline-offset:4px;white-space:pre-wrap;} [contenteditable]:hover {outline-color:#7d9f89;background:#edf6ef88;} [contenteditable]:focus {outline:2px solid #245747;background:#f4faf5;}';
    doc.head.append(style);
    const nodes = [...doc.querySelectorAll('[data-edit-path]')];
    for (const node of nodes) {
      if (active) {node.setAttribute('contenteditable','plaintext-only');node.setAttribute('role','textbox');node.setAttribute('aria-label',node.dataset.editPath.replaceAll('.', ' '));node.setAttribute('tabindex','0');}
      else {node.removeAttribute('contenteditable');node.removeAttribute('role');node.removeAttribute('aria-label');node.removeAttribute('tabindex');}
    }
    function focus(event) {if (event.target.dataset?.editPath) {onfocuschange(true);onselect(event.target.dataset.editPath);}}
    function input(event) {const node = event.target; if (node.dataset?.editPath) onedit(node.dataset.editPath,node.innerText);}
    function blur(event) {if (event.target.dataset?.editPath) onfocuschange(false);}
    function click(event) {if (event.target.closest('a')) event.preventDefault();}
    if (active) {doc.addEventListener('input',input);doc.addEventListener('focus',focus,true);doc.addEventListener('blur',blur,true);doc.addEventListener('click',click);}
    return () => {style.remove();doc.removeEventListener('input',input);doc.removeEventListener('focus',focus,true);doc.removeEventListener('blur',blur,true);doc.removeEventListener('click',click);};
  });
  onMount(() => {
    const observer = new ResizeObserver(resize);
    if (frame) observer.observe(frame);
    return () => { observer.disconnect(); bodyObserver?.disconnect(); logoController?.abort(); };
  });
</script>
<iframe bind:this={frame} srcdoc={html} {title} sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox" onload={loaded} style:height="{height}px"></iframe>
<style>
  iframe { display:block; border:0; width:100%; background:white; min-height:250px; }
</style>
