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
  <path fill="#f4faf6" d="M7.4 25Q7.2 18 8.6 12.5Q11.4 18 12.2 25Z" />
  <path fill="#f4faf6" d="M13.2 25Q13.5 14 15.2 6Q18.2 14 18.8 25Z" />
  <path fill="#f4faf6" d="M19.4 25Q21.2 18 22.4 13Q25.2 18.5 25.2 25Z" />
</svg>

<style>
  .brand-logo {
    display: inline-block;
    flex-shrink: 0;
    vertical-align: middle;
  }
</style>
