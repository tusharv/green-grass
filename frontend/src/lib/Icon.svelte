<script>
  let { name, size = 20 } = $props();
</script>

<svg
  class="icon"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.75"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  {#if name === 'desk'}
    <rect x="3.5" y="3.5" width="7" height="7" rx="1.5" />
    <rect x="13.5" y="3.5" width="7" height="7" rx="1.5" />
    <rect x="3.5" y="13.5" width="7" height="7" rx="1.5" />
    <rect x="13.5" y="13.5" width="7" height="7" rx="1.5" />
  {:else if name === 'cv'}
    <path d="M7 3.5h7.2L19.5 8.8V20.5H7z" />
    <path d="M14.2 3.7V8.8h5" />
    <path d="M10 13h6.2M10 16.4h4" />
  {:else if name === 'role'}
    <rect x="3.5" y="7.5" width="17" height="12" rx="1.5" />
    <path d="M9 7.5V6.2A1.7 1.7 0 0 1 10.7 4.5h2.6A1.7 1.7 0 0 1 15 6.2v1.3" />
    <path d="M3.5 12.5h17" />
  {:else if name === 'upload'}
    <path d="M12 15.5V4.5" />
    <path d="M8 8.2 12 4.2l4 4" />
    <path d="M5 19.5h14" />
  {:else if name === 'ready'}
    <circle cx="12" cy="12" r="8.25" />
    <path d="m8.4 12.2 2.4 2.4 4.8-5.2" />
  {:else if name === 'gap'}
    <circle cx="12" cy="12" r="8.25" />
    <path d="M12 8.2v4.3" />
    <path d="M12 15.8h.01" />
  {:else if name === 'trash'}
    <path d="M5 7.5h14" />
    <path d="M9.2 7.4V5.6h5.6v1.8" />
    <path d="M7.2 7.5l.7 11.2h8.2l.7-11.2" />
    <path d="M10.2 11.2v4.4M13.8 11.2v4.4" />
  {:else if name === 'link'}
    <path d="M10 13.2a4.2 4.2 0 0 0 6 0l1.6-1.6a4.2 4.2 0 0 0-6-6L10.2 7" />
    <path d="M14 10.8a4.2 4.2 0 0 0-6 0l-1.6 1.6a4.2 4.2 0 0 0 6 6L13.8 17" />
  {:else if name === 'download'}
    <path d="M12 4.5v11" />
    <path d="m8 12 4 4 4-4" />
    <path d="M5 19.5h14" />
  {:else if name === 'mail'}
    <rect x="3.5" y="5.5" width="17" height="13" rx="2" />
    <path d="m4.2 7.2 7.8 5.4L19.8 7.2" />
  {:else if name === 'phone'}
    <path d="M8.2 3.8h2.1c.5 0 .8.4.8.8l.3 2.2a.9.9 0 0 1-.5.9l-1.4.6a10.6 10.6 0 0 0 5.2 5.2l.6-1.4a.9.9 0 0 1 .9-.5l2.2.3c.4 0 .8.4.8.8v2.1a1.5 1.5 0 0 1-1.6 1.5A14.2 14.2 0 0 1 6.7 5.4a1.5 1.5 0 0 1 1.5-1.6z" />
  {:else if name === 'pin'}
    <path d="M12 21s5.6-4.9 5.6-9.6a5.6 5.6 0 1 0-11.2 0C6.4 16.1 12 21 12 21z" />
    <circle cx="12" cy="11.2" r="1.7" />
  {:else if name === 'summary'}
    <path d="M5 7h14M5 12h14M5 17h8" />
  {:else if name === 'skills'}
    <path d="m12 3.8 7.4 3.6L12 11 4.6 7.4 12 3.8z" />
    <path d="m4.6 12 7.4 3.6 7.4-3.6" />
    <path d="m4.6 16.2 7.4 3.6 7.4-3.6" />
  {:else if name === 'education'}
    <path d="m3.4 9.4 8.6-4.2 8.6 4.2-8.6 4.2-8.6-4.2z" />
    <path d="M7.4 11.5v3.6c1.4 1.2 3 1.8 4.6 1.8s3.2-.6 4.6-1.8v-3.6" />
    <path d="M20.2 9.6v5" />
  {:else if name === 'github'}
    <path d="M9.2 19.6c-3.6 1.1-3.6-1.9-5-2.3m10 4.2v-3.1a2.7 2.7 0 0 0-.8-2.1c2.6-.3 5.4-1.3 5.4-5.8a4.5 4.5 0 0 0-1.2-3.1 4.2 4.2 0 0 0-.1-3.1s-1-.3-3.2 1.2a11 11 0 0 0-5.8 0C6.3 4.1 5.3 4.4 5.3 4.4a4.2 4.2 0 0 0-.1 3.1A4.5 4.5 0 0 0 4 10.6c0 4.5 2.8 5.5 5.4 5.8a2.7 2.7 0 0 0-.8 2.1v3.1" />
  {:else if name === 'linkedin'}
    <rect x="3.5" y="3.5" width="17" height="17" rx="2.5" />
    <path d="M8 10.5v6M8 7.6v.01M11.6 16.5v-6M11.6 13.2c0-1.6 1-2.7 2.4-2.7s2.2 1 2.2 2.6v3.4" />
  {:else if name === 'camera'}
    <path d="M4.5 8.2A1.7 1.7 0 0 1 6.2 6.5h1.9l1.4-2h5l1.4 2h1.9a1.7 1.7 0 0 1 1.7 1.7v9.6a1.7 1.7 0 0 1-1.7 1.7H6.2a1.7 1.7 0 0 1-1.7-1.7z" />
    <circle cx="12" cy="13" r="3.4" />
  {:else if name === 'arrow'}
    <path d="M7 17 17 7M9 7h8v8" />
  {:else if name === 'signin'}
    <path d="M10 4.5H6.2A1.7 1.7 0 0 0 4.5 6.2v11.6A1.7 1.7 0 0 0 6.2 19.5H10" />
    <path d="M10.2 12h9.3" />
    <path d="m15.8 8.4 3.6 3.6-3.6 3.6" />
  {:else if name === 'account'}
    <circle cx="9.2" cy="8" r="2.8" />
    <path d="M4.2 19.2a5 5 0 0 1 10 0" />
    <path d="M17 7.6v5M14.5 10.1h5" />
  {/if}
</svg>
