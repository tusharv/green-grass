<script>
  let { quiet = false } = $props();

  /** Tags a credit click so the destination can see it came from the Job Ready footer. */
  function creditLink(url, content) {
    const link = new URL(url);
    link.searchParams.set('utm_source', 'jobready');
    link.searchParams.set('utm_medium', 'referral');
    link.searchParams.set('utm_campaign', 'credits');
    link.searchParams.set('utm_content', content);
    return link.toString();
  }

  const credits = [
    {
      href: creditLink('https://hacktoberfest.com/', 'hacktoberfest'),
      label: 'Built at Hacktoberfest 2026',
      mark: '/credits/hacktoberfest.svg',
    },
    {
      href: creditLink('https://render.com/', 'render'),
      label: 'Hosted on Render',
      mark: '/credits/render.svg',
    },
    {
      href: creditLink('https://get.tech/', 'tech'),
      label: 'Domain by .TECH',
      mark: '/credits/tech.svg',
      wide: true,
    },
    {
      href: creditLink('https://ollama.com/', 'ollama'),
      label: 'Super intelligence by Ollama',
      mark: '/credits/ollama.svg',
    },
    {
      href: creditLink('https://deepmind.google/models/gemma/gemma-4/', 'gemma'),
      label: 'Powered by Gemma4',
      mark: '/credits/gemma.png',
    },
    {
      href: creditLink('https://cursor.com/', 'cursor'),
      label: 'Built with Cursor',
      mark: '/credits/cursor.svg',
    },
  ];
</script>

<footer class="credits" class:quiet>
  <p>
    {#each credits as item (item.href)}
      <a href={item.href} target="_blank" rel="noopener noreferrer">
        <span class="mark" class:wide={item.wide} style:--mark="url('{item.mark}')" aria-hidden="true"></span>
        <span class="label">{item.label}</span><span class="sr-only"> (opens in a new tab)</span>
      </a>
    {/each}
  </p>
  <nav aria-label="Policies">
    <a href="/privacy">Privacy</a>
    <a href="/terms">Terms and conditions</a>
  </nav>
</footer>

<style>
  .credits {
    margin-top: 2.5rem;
    padding-top: 1.1rem;
    border-top: 1px solid var(--line);
    font-size: 0.82rem;
    line-height: 1.45;
  }

  .credits.quiet {
    margin-top: 0.85rem;
    padding-top: 0;
    border-top: 0;
  }

  p {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.45rem 1.15rem;
    margin: 0;
    color: var(--muted);
  }

  a {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--muted);
    font-weight: 600;
    text-decoration: none;
  }

  a:hover {
    color: var(--ink);
    text-decoration: none;
  }

  a:hover .label {
    text-decoration: underline;
  }

  .mark {
    width: 1.05rem;
    height: 1.05rem;
    flex: none;
    background: currentColor;
    -webkit-mask-image: var(--mark);
    mask-image: var(--mark);
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    -webkit-mask-position: center;
    mask-position: center;
    -webkit-mask-size: contain;
    mask-size: contain;
  }

  .mark.wide {
    width: 2.55rem;
  }

  nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem 1.15rem;
    margin-top: 0.7rem;
  }

  nav a:hover {
    text-decoration: underline;
  }
</style>
