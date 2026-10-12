<script>
  let { size = 28, class: extra = '' } = $props();
</script>

<svg
  class="brand-logo {extra}"
  width={size}
  height={size}
  viewBox="0 0 32 32"
  aria-hidden="true"
  focusable="false"
>
  <rect width="32" height="32" rx="7" fill="#1b6b45" />
  <path d="M9 23V16H16V9H23" fill="none" stroke="#f4faf6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
</svg>

<style>
  .brand-logo {
    display: inline-block;
    flex-shrink: 0;
    vertical-align: middle;
  }
</style>
