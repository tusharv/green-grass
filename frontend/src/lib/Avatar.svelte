<script>
  let { name = '', url = '', size = 0, class: extra = '' } = $props();
  let failed = $state(false);
  let loaded = $state(false);
  const initials = $derived(
    name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join('') || '·',
  );
  const showPhoto = $derived(Boolean(url) && !failed);

  $effect(() => {
    url;
    failed = false;
    loaded = false;
  });
</script>

<span class="avatar {extra}" style={size ? `--size: ${size}px` : undefined} role="img" aria-label={showPhoto ? `Photo of ${name}` : `${name || 'Candidate'}, no photo`}>
  <span class="initials" aria-hidden="true">{initials}</span>
  {#if showPhoto}
    <img
      src={url}
      alt=""
      width="640"
      height="640"
      class:loaded
      referrerpolicy="no-referrer"
      onload={() => (loaded = true)}
      onerror={() => (failed = true)}
    />
  {/if}
</span>

<style>
  .avatar {
    position: relative;
    display: inline-grid;
    place-items: center;
    flex: 0 0 auto;
    width: var(--size, 72px);
    height: var(--size, 72px);
    overflow: hidden;
    border-radius: calc(var(--size, 72px) * 0.22);
    background: repeating-linear-gradient(115deg, #10603f 0 14px, #157049 14px 28px);
    color: #e9f4ee;
  }
  img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: opacity 260ms ease;
  }
  img.loaded { opacity: 1; }
  .initials {
    font-family: var(--serif);
    font-weight: 600;
    font-size: calc(var(--size, 72px) * 0.36);
    letter-spacing: 0.02em;
    line-height: 1;
  }
  @media (prefers-reduced-motion: reduce) {
    img { transition: none; }
  }
</style>
