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
  {:else if name === 'edit'}
    <path d="m15 4 5 5M4 20l4.5-1L20 7.5a2 2 0 0 0-3-3L5 16z"/>
  {:else if name === 'palette'}
    <path d="M12 3a9 9 0 1 0 0 18h1a2 2 0 0 0 1-3.7c-.8-.5-.4-1.8.5-1.8H17a4 4 0 0 0 4-4C21 6.7 17 3 12 3Z"/><circle cx="7" cy="10" r=".7"/><circle cx="10" cy="6.5" r=".7"/><circle cx="15" cy="7" r=".7"/>
  {:else if name === 'eye' || name === 'eye-off'}
    <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>{#if name === 'eye-off'}<path d="m3 3 18 18"/>{/if}
  {:else if name === 'plus'}<path d="M12 5v14M5 12h14"/>
  {:else if name === 'close'}<path d="m6 6 12 12M6 18 18 6"/>
  {:else if name === 'help'}<circle cx="12" cy="12" r="9"/><path d="M9.5 8a2.5 2.5 0 1 1 4 2c-1.5 1-1.5 1.5-1.5 3M12 16.5h.01"/>
  {:else if name === 'grip'}<path d="M9 5h.01M15 5h.01M9 12h.01M15 12h.01M9 19h.01M15 19h.01" stroke-width="3"/>
  {:else if name === 'up'}<path d="m6 14 6-6 6 6"/>
  {:else if name === 'down'}<path d="m6 10 6 6 6-6"/>
  {:else if name === 'back'}<path d="M20 12H4m6-6-6 6 6 6"/>
  {:else if name === 'undo'}<path d="M4 10h10a6 6 0 0 1 0 12M4 10l5-5M4 10l5 5" transform="translate(0 -2)"/>
  {:else if name === 'redo'}<path d="M20 10H10a6 6 0 0 0 0 12M20 10l-5-5M20 10l-5 5" transform="translate(0 -2)"/>
  {:else if name === 'save'}<path d="M5 3h12l4 4v14H3V3zM7 3v6h10V3M7 21v-8h10v8"/>
  {:else if name === 'copy'}<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>
  {:else if name === 'share'}<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 10.5 6.8-4M8.6 13.5l6.8 4"/>
  {:else if name === 'lock'}<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>
  {:else if name === 'folder'}<path d="M3 7V4h7l2 3h9v13H3z"/>
  {:else if name === 'award'}<circle cx="12" cy="8" r="5"/><path d="m8 12-1 9 5-3 5 3-1-9"/>
  {:else if name === 'language'}<path d="M3 5h12M9 3v2M5 5c0 6 5 9 8 10M12 5c0 6-5 9-9 10M13 21l4-10 4 10M14.5 17h5"/>
  {:else if name === 'user'}
    <circle cx="12" cy="8" r="3.1" />
    <path d="M5 19.2a7 7 0 0 1 14 0" />
  {/if}
</svg>

<style>.icon {flex-shrink:0;vertical-align:middle;}</style>
