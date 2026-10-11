<script>
  import Icon from './Icon.svelte';

  let { endpoint = '', company = '' } = $props();
  let logo = $state(null);
  let loaded = $state(false);

  $effect(() => {
    const url = endpoint;
    const controller = new AbortController();
    logo = null;
    loaded = false;
    if (url) {
      fetch(url, { signal: controller.signal, credentials: 'same-origin' })
        .then(response => response.ok ? response.json() : null)
        .then(result => { if (!controller.signal.aborted) logo = result?.url ? result : null; })
        .catch(() => {});
    }
    return () => controller.abort();
  });
</script>

<span class="company-logo" aria-hidden="true">
  {#if !loaded}<Icon name="role" size={16} />{/if}
  {#if logo}
    <img src={logo.url} alt="" title={`${company} logo`} class:loaded
      width="28" height="28" referrerpolicy="no-referrer"
      onload={() => loaded = true} onerror={() => { loaded = false; logo = null; }} />
  {/if}
</span>

<style>
  .company-logo {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 32px;
    width: 32px;
    height: 32px;
    border: 1px solid #d8ded9;
    border-radius: 6px;
    background: #f1f3f1;
    color: #66736a;
  }
  img { position: absolute; inset: 1px; object-fit: contain; opacity: 0; }
  img.loaded { opacity: 1; }
</style>
