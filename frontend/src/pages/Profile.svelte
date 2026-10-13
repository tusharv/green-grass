<script>
  import { onMount } from 'svelte';
  import DesignDocument from '../lib/DesignDocument.svelte';
  import Avatar from '../lib/Avatar.svelte';
  import CompanyLogo from '../lib/CompanyLogo.svelte';
  import Icon from '../lib/Icon.svelte';
  import { api } from '../lib/session.svelte.js';
  import { getSample } from '../lib/samples.js';

  const SKILL_PREVIEW = 18;

  let { token } = $props();
  let profile = $state(null);
  let error = $state('');
  let active = $state('');
  let allSkills = $state(false);

  const doc = $derived(profile?.document || {});
  const contact = $derived(doc.contact || {});
  const roles = $derived(doc.experience || []);
  const skills = $derived(doc.skills || []);
  const schools = $derived((doc.education || []).filter((school) => school.school || school.credential));
  const firstName = $derived((profile?.name || '').split(/\s+/)[0] || 'the candidate');
  const current = $derived(roles.find((role) => isCurrent(role)) || null);
  const lead = $derived(current || roles[0] || null);
  const since = $derived(earliestYear(roles));
  const employers = $derived(new Set(roles.map((role) => (role.employer || '').trim().toLowerCase()).filter(Boolean)).size);
  const links = $derived((contact.links || []).filter(Boolean).map(describeLink));
  const intro = $derived(emphasize(doc.summary || '', skills));
  const shownSkills = $derived(allSkills ? skills : skills.slice(0, SKILL_PREVIEW));
  const logos = $derived(`/api/profiles/${encodeURIComponent(token)}/logos`);
  const sections = $derived(
    [
      doc.summary && { id: 'about', label: 'About' },
      roles.length && { id: 'experience', label: 'Experience' },
      skills.length && { id: 'skills', label: 'Skills' },
      schools.length && { id: 'education', label: 'Education' },
    ].filter(Boolean),
  );

  onMount(async () => {
    if (token.startsWith('sample-')) {
      const sample = getSample(token.slice('sample-'.length));
      if (sample) {
        profile = { ...sample.profile, sample: true };
        return;
      }
    }
    try {
      profile = await api(`/api/profiles/${encodeURIComponent(token)}`);
    } catch (err) {
      error = err.status === 404 ? 'missing' : err.message;
    }
  });

  $effect(() => {
    if (!profile || !sections.length) return;
    const ids = sections.map((section) => section.id);
    let frame = 0;
    const update = () => {
      frame = 0;
      const atBottom = innerHeight + scrollY >= document.documentElement.scrollHeight - 4;
      if (atBottom) {
        active = ids[ids.length - 1];
        return;
      }
      let current = ids[0];
      for (const id of ids) {
        const target = document.getElementById(id);
        if (target && target.getBoundingClientRect().top <= innerHeight * 0.3) current = id;
      }
      active = current;
    };
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    update();
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll);
    return () => {
      removeEventListener('scroll', onScroll);
      removeEventListener('resize', onScroll);
      if (frame) cancelAnimationFrame(frame);
    };
  });

  function jump(event, id) {
    const target = document.getElementById(id);
    if (!target) return;
    event.preventDefault();
    const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
    target.scrollIntoView({ behavior: still ? 'auto' : 'smooth', block: 'start' });
    history.replaceState(null, '', `#${id}`);
  }

  function isCurrent(role) {
    return /present|current|now|today/i.test(role?.end || '');
  }

  function earliestYear(list) {
    const years = list
      .map((role) => (role.start || '').match(/\b(19|20)\d{2}\b/))
      .filter(Boolean)
      .map((found) => Number(found[0]));
    return years.length ? Math.min(...years) : null;
  }

  function dates(role) {
    return [role.start, role.end].filter(Boolean).join(' – ');
  }

  function describeLink(link) {
    const href = /^https?:\/\//i.test(link) ? link : `https://${link}`;
    const label = link.replace(/^https?:\/\//i, '').replace(/^www\./i, '').replace(/\/$/, '');
    if (/linkedin\.com/i.test(link)) return { href, label: 'LinkedIn', title: label, icon: 'linkedin' };
    if (/github\.com/i.test(link)) return { href, label: 'GitHub', title: label, icon: 'github' };
    return { href, label, title: label, icon: 'link' };
  }

  function escape(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function emphasize(text, terms) {
    if (!text) return [];
    const names = [...new Set(terms.map((term) => term.trim()).filter((term) => term.length > 1))].sort(
      (a, b) => b.length - a.length,
    );
    const figure = String.raw`[~$]?\d[\d,.]*(?:\s?%|[KMB]\+?|\+)?(?:\s(?:years?|RPM|users))?`;
    const parts = names.length ? `${names.map(escape).join('|')}|${figure}` : figure;
    const pattern = new RegExp(`(?<![\\w+#])(${parts})(?![\\w+#])`, 'g');
    const seen = new Set();
    const pieces = [];
    let cursor = 0;
    for (const match of text.matchAll(pattern)) {
      const word = match[0];
      const isSkill = names.includes(word);
      if (isSkill && seen.has(word)) continue;
      if (isSkill) seen.add(word);
      if (match.index > cursor) pieces.push({ text: text.slice(cursor, match.index), kind: '' });
      pieces.push({ text: word, kind: isSkill ? 'skill' : 'figure' });
      cursor = match.index + word.length;
    }
    if (cursor < text.length) pieces.push({ text: text.slice(cursor), kind: '' });
    return pieces;
  }

  function leadIn(bullet) {
    const found = (bullet || '').match(/^([^:.]{2,48}):\s*(\S[\s\S]*)$/);
    return found ? { lead: found[1].trim(), text: found[2] } : { lead: '', text: bullet };
  }
</script>

<svelte:head>
  {#if profile}
    <title>{profile.name}{lead?.title ? ` — ${lead.title}` : ''}</title>
  {/if}
  <meta name="robots" content="noindex" />
</svelte:head>

{#if profile?.application_id}
  <div class="profile-owner-actions">
    <a class="customize-float" href="/applications/{profile.application_id}?design=1" aria-label="Customize design" title="Customize design"><Icon name="skills" size={23} /><span class="customize-label" aria-hidden="true">Customize design</span></a>
  </div>
{/if}

{#if error === 'missing'}
  <section class="pf-missing">
    <span class="pf-missing-turf" aria-hidden="true"></span>
    <h1>This profile is no longer shared</h1>
    <p>The candidate turned the link off, or it was copied incompletely. Ask them for a fresh link.</p>
  </section>
{:else if error}
  <p class="alert" role="alert">{error}</p>
{:else if !profile}
  <div class="pf-loading" role="status" aria-label="Loading profile">
    <span class="pf-loading-band"></span>
    <span class="pf-loading-line wide"></span>
    <span class="pf-loading-line"></span>
  </div>
{:else if profile.design_html}
  <DesignDocument logosUrl={logos} html={profile.design_html} title={`${profile.name} — shared profile`} />
{:else}
  <article class="pf" class:sample-ink={profile.variant === 'ink'} class:sample-studio={profile.variant === 'studio'}>
    {#if profile.sample}<p class="pf-sample-note"><strong>Fictional sample profile</strong><span>This example uses fictional details to show how a shared profile can look.</span><a href="/samples/{token.slice('sample-'.length)}/evaluation">View sample evaluation</a></p>{/if}
    <header class="pf-hero">
      <div class="pf-turf" aria-hidden="true"></div>
      <p class="pf-for"><span>Shared for</span> {profile.role_title}</p>
      <div class="pf-id">
        <Avatar name={profile.name} url={profile.photo?.url || ''} class="pf-portrait" />
        <div class="pf-name">
          <h1>{profile.name}</h1>
          {#if lead?.title}
            <p class="pf-headline">
              {lead.title}{#if lead.employer}<span class="pf-at">{' at '}{lead.employer}</span>{/if}
            </p>
          {/if}
          {#if contact.location || links.length}
            <ul class="pf-meta">
              {#if contact.location}
                <li><Icon name="pin" size={16} /> {contact.location}</li>
              {/if}
              {#each links as link (link.href)}
                <li>
                  <a href={link.href} title={link.title} target="_blank" rel="noopener noreferrer">
                    <Icon name={link.icon} size={16} /> {link.label}
                  </a>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
        {#if contact.email || contact.phone}
          <div class="pf-actions">
            {#if contact.email}
              <a class="button pf-cta" href="mailto:{contact.email}"><Icon name="mail" size={17} /> Email {firstName}</a>
            {/if}
            {#if contact.phone}
              <a class="button secondary" href="tel:{contact.phone.replace(/[^\d+]/g, '')}"><Icon name="phone" size={16} /> {contact.phone}</a>
            {/if}
          </div>
        {/if}
      </div>
    </header>

    {#if sections.length > 1}
      <nav class="pf-tabs" aria-label="Profile sections">
        {#each sections as section (section.id)}
          <a
            href="#{section.id}"
            aria-current={active === section.id ? 'true' : undefined}
            onclick={(event) => jump(event, section.id)}
          >{section.label}</a>
        {/each}
      </nav>
    {/if}

    <div class="pf-body">
      <div class="pf-main">
        {#if doc.summary}
          <section id="about" class="pf-section" aria-labelledby="about-title">
            <h2 id="about-title" class="pf-label">About</h2>
            <p class="pf-intro">
              {#each intro as piece, index (index)}
                {#if piece.kind === 'skill'}<strong>{piece.text}</strong>{:else if piece.kind === 'figure'}<b class="pf-figure">{piece.text}</b>{:else}{piece.text}{/if}
              {/each}
            </p>
          </section>
        {/if}

        {#if roles.length}
          <section id="experience" class="pf-section" aria-labelledby="experience-title">
            <h2 id="experience-title" class="pf-label">Experience</h2>
            <ol class="pf-roles">
              {#each roles as role, index (index)}
                <li class="pf-role">
                  <span class="pf-logo"><CompanyLogo company={role.employer} endpoint="{logos}/{index}" /></span>
                  <div class="pf-role-body">
                    <div class="pf-role-head">
                      <div>
                        <h3>{role.title}</h3>
                        {#if role.employer}<p class="pf-employer">{role.employer}</p>{/if}
                      </div>
                      {#if dates(role)}
                        <p class="pf-dates">
                          {#if isCurrent(role)}<span class="pf-now">Current</span>{/if}
                          {dates(role)}
                        </p>
                      {/if}
                    </div>
                    {#if role.bullets?.length}
                      <ul class="pf-bullets">
                        {#each role.bullets as bullet, bulletIndex (bulletIndex)}
                          {@const line = leadIn(bullet)}
                          <li>{#if line.lead}<strong>{line.lead}.</strong>{' '}{/if}{line.text}</li>
                        {/each}
                      </ul>
                    {/if}
                  </div>
                </li>
              {/each}
            </ol>
          </section>
        {/if}
      </div>

      <aside class="pf-side">
        <section class="pf-card pf-glance" aria-labelledby="glance-title">
          <h2 id="glance-title" class="pf-label">At a glance</h2>
          <dl>
            <div><dt>Shared for</dt><dd>{profile.role_title}</dd></div>
            {#if since}<div><dt>Working since</dt><dd class="pf-num">{since}</dd></div>{/if}
            {#if roles.length}
              <div>
                <dt>Experience</dt>
                <dd>{roles.length} {roles.length === 1 ? 'role' : 'roles'}{#if employers > 1}, {employers} employers{/if}</dd>
              </div>
            {/if}
            {#if contact.location}<div><dt>Based in</dt><dd>{contact.location}</dd></div>{/if}
          </dl>
        </section>

        {#if skills.length}
          <section id="skills" class="pf-card pf-section" aria-labelledby="skills-title">
            <h2 id="skills-title" class="pf-label">Skills <span class="pf-count">{skills.length}</span></h2>
            <ul class="pf-skills">
              {#each shownSkills as skill (skill)}<li>{skill}</li>{/each}
            </ul>
            {#if skills.length > SKILL_PREVIEW}
              <button type="button" class="text pf-more" aria-expanded={allSkills} onclick={() => (allSkills = !allSkills)}>
                {allSkills ? 'Show fewer' : `Show all ${skills.length}`}
              </button>
            {/if}
          </section>
        {/if}

        {#if schools.length}
          <section id="education" class="pf-card pf-section" aria-labelledby="education-title">
            <h2 id="education-title" class="pf-label">Education</h2>
            <ul class="pf-schools">
              {#each schools as school, index (index)}
                <li>
                  <p class="pf-credential">{school.credential || school.school}</p>
                  {#if school.credential && school.school}<p>{school.school}</p>{/if}
                  {#if school.year}<p class="pf-num pf-year">{school.year}</p>{/if}
                </li>
              {/each}
            </ul>
          </section>
        {/if}
      </aside>
    </div>
  </article>
{/if}

<style>
  .profile-owner-actions { position:fixed; left:max(1.25rem, env(safe-area-inset-left)); bottom:max(1.25rem, env(safe-area-inset-bottom)); z-index:50; }
  .customize-float { position:relative; display:flex; align-items:center; justify-content:center; width:52px; height:52px; border-radius:50%; background:#245747; color:white; border:2px solid white; box-shadow:0 4px 16px #0003; text-decoration:none; }
  .customize-float:hover { background:#173c31; }
  .customize-float:focus-visible { outline:3px solid #245747; outline-offset:3px; }
  .customize-label { position:absolute; left:calc(100% + 10px); white-space:nowrap; background:#173c31; color:white; border-radius:6px; padding:7px 11px; font-size:.8rem; opacity:0; pointer-events:none; }
  .customize-float:hover .customize-label, .customize-float:focus-visible .customize-label { opacity:1; }
  @media print { .profile-owner-actions { display:none; } }

  .pf-sample-note { display: flex; align-items: center; gap: 0.8rem; padding: 0.8rem 1.2rem; margin: 0; color: var(--accent-deep); background: #e6eee7; border-bottom: 1px solid var(--line); font-size: 0.86rem; }
  .pf-sample-note strong { white-space: nowrap; }
  .pf-sample-note span { color: var(--muted); }
  .pf-sample-note a { margin-left:auto; flex:none; font-weight:600; }
  .pf {
    --turf: #0f5a3c;
    --turf-light: #146a48;
    --turf-ink: #0b3f2a;
    --highlight: #cdeedc;
    --soft: #f3f7f4;
    --shadow: 0 1px 0 rgba(14, 50, 32, 0.04), 0 22px 44px -30px rgba(8, 40, 24, 0.38);
    display: grid;
    gap: 1.25rem;
    padding-top: 0.5rem;
  }
  .pf.sample-ink { --turf:#202f49; --turf-light:#344967; --turf-ink:#142239; --highlight:#d8e5f2; --soft:#f4f7fa; --line:#d3dce7; }
  .pf.sample-ink .pf-turf { background:linear-gradient(180deg,rgba(9,18,34,0) 40%,rgba(9,18,34,.3)), repeating-linear-gradient(112deg,var(--turf) 0 54px,var(--turf-light) 54px 108px); }
  .pf.sample-ink .pf-for { background:rgba(221,233,247,.15); }
  .pf.sample-studio { --turf:#a9583f; --turf-light:#d48661; --turf-ink:#703725; --highlight:#fde0c7; --soft:#fff8f2; --line:#ecd9cc; --shadow:0 12px 30px -30px rgba(112,55,37,.38); gap:1rem; }
  .pf.sample-studio .pf-turf { background:linear-gradient(180deg,rgba(80,27,12,0) 40%,rgba(80,27,12,.28)), repeating-linear-gradient(112deg,var(--turf) 0 54px,var(--turf-light) 54px 108px); }
  .pf.sample-studio .pf-for { background:rgba(255,244,232,.16); }

  /* Hero */
  .pf-hero {
    position: relative;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 24px;
    overflow: hidden;
    box-shadow: var(--shadow);
  }
  .pf-turf {
    height: 176px;
    background:
      linear-gradient(180deg, rgba(4, 30, 18, 0) 40%, rgba(4, 30, 18, 0.28)),
      repeating-linear-gradient(112deg, var(--turf) 0 54px, var(--turf-light) 54px 108px);
    animation: mow 1200ms cubic-bezier(0.65, 0, 0.25, 1) both;
  }
  @keyframes mow {
    from { clip-path: inset(0 100% 0 0); }
    to { clip-path: inset(0 0 0 0); }
  }
  .pf-for {
    position: absolute;
    top: 1.1rem;
    right: 1.25rem;
    margin: 0;
    max-width: calc(100% - 2.5rem);
    padding: 0.38rem 0.85rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(6px);
    color: #fff;
    font-size: 0.86rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .pf-for span {
    margin-right: 0.35rem;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.78;
  }
  .pf-id {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) auto;
    column-gap: 1.75rem;
    align-items: end;
    padding: 0 2.25rem 2rem;
    margin-top: -96px;
  }
  .pf-id :global(.pf-portrait) {
    --size: 184px;
    position: relative;
    box-shadow: 0 0 0 6px #fff, 0 18px 34px -14px rgba(6, 36, 22, 0.55);
  }
  .pf-name { min-width: 0; padding-top: 108px; }
  .pf-name h1 {
    margin: 0;
    font-family: var(--serif);
    font-weight: 600;
    font-size: clamp(2.2rem, 4.4vw, 3.25rem);
    line-height: 1.02;
    letter-spacing: -0.02em;
    color: var(--ink);
  }
  .pf-headline {
    margin: 0.5rem 0 0;
    font-size: 1.16rem;
    font-weight: 600;
    color: var(--ink);
  }
  .pf-at { font-weight: 400; color: var(--muted); }
  .pf-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem 1.2rem;
    margin: 0.9rem 0 0;
    padding: 0;
    list-style: none;
    color: var(--muted);
    font-size: 0.95rem;
  }
  .pf-meta li, .pf-meta a { display: inline-flex; align-items: center; gap: 0.38rem; }
  .pf-meta a { color: var(--muted); text-decoration: none; font-weight: 600; }
  .pf-meta a:hover { color: var(--turf); text-decoration: underline; }
  .pf-actions { display: flex; flex-direction: column; gap: 0.55rem; align-items: stretch; }
  .pf-cta { background: var(--turf); }
  .pf-cta:hover { background: var(--turf-ink); }

  /* The studio sample uses a compact editorial masthead instead of the portrait-over-cover layout. */
  .pf.sample-studio .pf-hero { border-radius: 10px 10px 28px 28px; background: var(--soft); }
  .pf.sample-studio .pf-turf { height: 108px; }
  .pf.sample-studio .pf-id {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-rows: auto auto;
    column-gap: 1.25rem;
    row-gap: 0.25rem;
    margin-top: 0;
    padding: 1.55rem 2rem 1.85rem;
  }
  .pf.sample-studio .pf-id :global(.pf-portrait) {
    --size: 98px;
    grid-column: 2;
    grid-row: 1 / span 2;
    box-shadow: 0 0 0 5px #fff, 0 13px 26px -17px rgba(112, 55, 37, 0.65);
  }
  .pf.sample-studio .pf-name { grid-column: 1; grid-row: 1; padding-top: 0; }
  .pf.sample-studio .pf-actions { grid-column: 1; grid-row: 2; flex-direction: row; align-items: flex-start; margin-top: 0.8rem; }
  .pf.sample-studio .pf-tabs { width: 100%; border-radius: 10px; background: var(--soft); box-shadow: none; }
  .pf.sample-studio .pf-main, .pf.sample-studio .pf-card { border-radius: 10px; box-shadow: none; }
  .pf.sample-studio .pf-logo :global(.company-logo) { border-radius: 50%; background: var(--highlight); }
  .pf.sample-studio .pf-bullets li::before { border-radius: 50%; }

  /* Section tabs */
  .pf-tabs {
    position: sticky;
    top: 0.6rem;
    z-index: 5;
    display: flex;
    gap: 0.2rem;
    width: fit-content;
    max-width: 100%;
    overflow-x: auto;
    padding: 0.32rem;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.86);
    backdrop-filter: blur(12px);
    box-shadow: 0 10px 24px -20px rgba(8, 40, 24, 0.5);
    scrollbar-width: none;
  }
  .pf-tabs a {
    flex: 0 0 auto;
    padding: 0.42rem 1rem;
    border-radius: 999px;
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    text-decoration: none;
    transition: background 180ms ease, color 180ms ease;
  }
  .pf-tabs a:hover { color: var(--ink); background: var(--soft); }
  .pf-tabs a[aria-current='true'] { background: var(--turf); color: #fff; }

  /* Body */
  .pf-body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 21.5rem;
    gap: 1.25rem;
    align-items: start;
  }
  .pf-main {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 20px;
    box-shadow: var(--shadow);
    padding: 0.4rem 2.25rem;
  }
  .pf-section { scroll-margin-top: 5rem; }
  .pf-main .pf-section { padding: 1.9rem 0; }
  .pf-main .pf-section + .pf-section { border-top: 1px solid var(--line); }
  .pf-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0 0 1rem;
    font-family: var(--sans);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--turf);
  }
  .pf-count {
    padding: 0.05rem 0.45rem;
    border-radius: 999px;
    background: var(--soft);
    color: var(--muted);
    letter-spacing: 0;
    font-variant-numeric: tabular-nums;
  }
  .pf-intro {
    margin: 0;
    max-width: 62ch;
    font-size: 1.24rem;
    line-height: 1.62;
    color: #4a5c53;
  }
  .pf-intro strong {
    color: var(--ink);
    font-weight: 600;
    background: linear-gradient(var(--highlight), var(--highlight)) 0 88% / 100% 0.32em no-repeat;
  }
  .pf-figure { color: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }

  /* Experience */
  .pf-roles { margin: 0; padding: 0; list-style: none; }
  .pf-role {
    position: relative;
    display: grid;
    grid-template-columns: 46px minmax(0, 1fr);
    gap: 1.1rem;
    padding-bottom: 1.8rem;
  }
  .pf-role:last-child { padding-bottom: 0; }
  .pf-role:not(:last-child)::before {
    content: '';
    position: absolute;
    left: 22px;
    top: 54px;
    bottom: 6px;
    width: 1px;
    background: linear-gradient(var(--line), rgba(213, 224, 218, 0.2));
  }
  .pf-logo :global(.company-logo) {
    width: 46px;
    height: 46px;
    flex-basis: 46px;
    border-radius: 12px;
    border-color: var(--line);
    background: #fff;
    box-shadow: 0 6px 14px -10px rgba(8, 40, 24, 0.5);
  }
  .pf-logo :global(.company-logo img) { top: 7px; left: 7px; width: 30px; height: 30px; }
  .pf-role-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.4rem 1rem;
    flex-wrap: wrap;
  }
  .pf-role h3 {
    margin: 0;
    font-family: var(--serif);
    font-size: 1.28rem;
    font-weight: 600;
    line-height: 1.25;
  }
  .pf-employer { margin: 0.15rem 0 0; font-weight: 600; color: var(--muted); }
  .pf-dates {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    color: var(--muted);
    font-size: 0.9rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
  .pf-now {
    padding: 0.1rem 0.5rem;
    border-radius: 999px;
    background: var(--highlight);
    color: var(--turf-ink);
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .pf-bullets { display: grid; gap: 0.55rem; margin: 0.9rem 0 0; padding: 0; list-style: none; }
  .pf-bullets li {
    position: relative;
    padding-left: 1.15rem;
    color: #34463d;
    line-height: 1.58;
  }
  .pf-bullets li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.68em;
    width: 6px;
    height: 6px;
    border-radius: 2px;
    background: var(--turf-light);
    opacity: 0.7;
  }
  .pf-bullets strong { color: var(--ink); font-weight: 700; }

  /* Side */
  .pf-side { display: grid; gap: 1.25rem; position: sticky; top: 4.6rem; }
  .pf-card {
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 20px;
    box-shadow: var(--shadow);
    padding: 1.5rem 1.5rem 1.6rem;
  }
  .pf-glance dl { display: grid; gap: 0.85rem; margin: 0; }
  .pf-glance dl div { display: grid; gap: 0.1rem; }
  .pf-glance dt { font-size: 0.82rem; color: var(--muted); }
  .pf-glance dd { margin: 0; font-weight: 600; }
  .pf-num { font-variant-numeric: tabular-nums; }
  .pf-skills { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0; padding: 0; list-style: none; }
  .pf-skills li {
    padding: 0.3rem 0.68rem;
    border: 1px solid #dbe6df;
    border-radius: 8px;
    background: var(--soft);
    font-size: 0.9rem;
    font-weight: 600;
    color: #23332b;
  }
  .pf-more { margin-top: 0.85rem; color: var(--turf); }
  .pf-schools { display: grid; gap: 1.1rem; margin: 0; padding: 0; list-style: none; }
  .pf-schools p { margin: 0; color: var(--muted); }
  .pf-schools .pf-credential { font-family: var(--serif); font-size: 1.05rem; font-weight: 600; color: var(--ink); line-height: 1.3; }
  .pf-year { font-size: 0.9rem; font-weight: 600; margin-top: 0.15rem !important; }

  /* Empty and loading */
  .pf-missing {
    max-width: 34rem;
    margin: 3rem auto;
    padding: 0 0 2rem;
    background: #fff;
    border: 1px solid var(--line);
    border-radius: 24px;
    overflow: hidden;
    text-align: center;
  }
  .pf-missing-turf {
    display: block;
    height: 72px;
    margin-bottom: 1.5rem;
    background: repeating-linear-gradient(112deg, #0f5a3c 0 40px, #146a48 40px 80px);
  }
  .pf-missing h1 { font-family: var(--serif); font-size: 1.7rem; margin: 0 1.5rem 0.5rem; }
  .pf-missing p { margin: 0 2rem; color: var(--muted); }
  .pf-loading { display: grid; gap: 0.8rem; padding-top: 0.5rem; }
  .pf-loading span { display: block; border-radius: 14px; background: #e6ece8; animation: pulse 1.4s ease-in-out infinite; }
  .pf-loading-band { height: 260px; border-radius: 24px !important; }
  .pf-loading-line { height: 18px; width: 40%; }
  .pf-loading-line.wide { width: 65%; }
  @keyframes pulse { 50% { opacity: 0.55; } }

  @media (max-width: 980px) {
    .pf-body { grid-template-columns: 1fr; }
    .pf-side { position: static; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); }
  }

  @media (max-width: 760px) {
    .pf-sample-note { align-items:flex-start; flex-direction:column; gap:.35rem; }
    .pf-sample-note a { margin-left:0; }
    .pf-turf { height: 132px; }
    .pf-id {
      grid-template-columns: 1fr;
      justify-items: center;
      text-align: center;
      row-gap: 1.1rem;
      padding: 0 1.25rem 1.5rem;
      margin-top: -70px;
    }
    .pf-id :global(.pf-portrait) { --size: 132px; }
    .pf-name { padding-top: 0; }
    .pf-meta { justify-content: center; }
    .pf-actions { width: 100%; }
    .pf-for { left: 1rem; right: auto; top: 0.9rem; }
    .pf-tabs { width: 100%; justify-content: space-between; }
    .pf-tabs a { padding: 0.42rem 0.7rem; letter-spacing: 0.05em; font-size: 0.74rem; }
    .pf-main { padding: 0.2rem 1.25rem; }
    .pf-intro { font-size: 1.1rem; }
    .pf-role { grid-template-columns: 38px minmax(0, 1fr); gap: 0.85rem; }
    .pf-role:not(:last-child)::before { left: 18px; top: 46px; }
    .pf-logo :global(.company-logo) { width: 38px; height: 38px; flex-basis: 38px; border-radius: 10px; }
    .pf-logo :global(.company-logo img) { top: 5px; left: 5px; width: 26px; height: 26px; }
    .pf-dates { white-space: normal; }
    .pf.sample-studio .pf-id { grid-template-columns: 1fr; grid-template-rows: auto; padding: 0 1.25rem 1.5rem; margin-top: -54px; }
    .pf.sample-studio .pf-id :global(.pf-portrait), .pf.sample-studio .pf-name, .pf.sample-studio .pf-actions { grid-column: auto; grid-row: auto; }
    .pf.sample-studio .pf-id :global(.pf-portrait) { --size: 112px; }
    .pf.sample-studio .pf-actions { align-items: stretch; margin-top: 0; }
  }

  @media (prefers-reduced-motion: reduce) {
    .pf-turf, .pf-loading span { animation: none; }
    .pf-tabs a { transition: none; }
  }

  @media print {
    .pf-tabs, .pf-actions, .pf-more { display: none; }
    .pf-hero, .pf-main, .pf-card { box-shadow: none; }
    .pf-turf { height: 90px; animation: none; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
    .pf-side { position: static; }
    .pf-body { grid-template-columns: 1fr; }
  }
</style>
