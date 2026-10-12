<script>
  import { onMount } from 'svelte';
  let { html = '', title = 'CV design preview', logosUrl = '' } = $props();
  let frame;
  let height = $state(900);
  function resize() {
    if (frame?.contentDocument?.body) height = Math.ceil(frame.contentDocument.body.getBoundingClientRect().height) + 4;
  }
  let logoController;
  function loaded() {
    resize();
    logoController?.abort();
    const controller = new AbortController();
    logoController = controller;
    const doc = frame?.contentDocument;
    if (!doc || !logosUrl) return;
    for (const badge of doc.querySelectorAll('[data-company-index]')) {
      fetch(`${logosUrl}/${badge.dataset.companyIndex}`, {signal:controller.signal,credentials:'same-origin'})
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
  onMount(() => {
    const observer = new ResizeObserver(resize);
    if (frame) observer.observe(frame);
    return () => { observer.disconnect(); logoController?.abort(); };
  });
</script>
<iframe bind:this={frame} srcdoc={html} {title} sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox" onload={loaded} style:height="{height}px"></iframe>
<style>
  iframe { display:block; border:0; width:100%; background:white; min-height:250px; }
</style>
