<script>
  import Icon from './Icon.svelte';

  let { document, roleTitle = '' } = $props();
  const contact = $derived(document?.contact || {});
  const contacts = $derived.by(() => contactItems(contact));
  const hasSummary = $derived(Boolean(document?.summary));
  const hasExperience = $derived(Boolean(document?.experience?.length));
  const hasSkills = $derived(Boolean(document?.skills?.length));
  const hasEducation = $derived(Boolean(document?.education?.length));
  const hasMain = $derived(hasSummary || hasExperience);
  const hasSide = $derived(hasSkills || hasEducation);

  function dates(role) {
    return [role.start, role.end].filter(Boolean).join(' - ');
  }

  function contactItems(person) {
    const items = [];
    if (person.email) {
      items.push({ icon: 'mail', label: person.email, href: `mailto:${person.email}` });
    }
    if (person.phone) {
      const dial = person.phone.replace(/[^\d+]/g, '');
      items.push({ icon: 'phone', label: person.phone, href: dial ? `tel:${dial}` : '' });
    }
    if (person.location) {
      items.push({ icon: 'pin', label: person.location, href: '' });
    }
    for (const link of person.links || []) {
      if (!link) continue;
      items.push({ icon: 'link', label: linkText(link), href: linkHref(link) });
    }
    return items;
  }

  function linkHref(link) {
    if (/^https?:\/\//i.test(link)) return link;
    if (link.includes('@') && !link.includes('/')) return `mailto:${link}`;
    return `https://${link}`;
  }

  function linkText(link) {
    return link.replace(/^https?:\/\//i, '').replace(/\/$/, '');
  }
</script>

<article class="ivy">
  <header class="ivy-top">
    <h2>{contact.name || 'CV'}</h2>
    {#if roleTitle}<p class="for-role">{roleTitle}</p>{/if}
    {#if contacts.length}
      <address>
        <ul class="contact-row">
          {#each contacts as item (item.icon + item.label)}
            <li>
              <span class="mark"><Icon name={item.icon} size={15} /></span>
              {#if item.href}
                <a href={item.href}>{item.label}</a>
              {:else}
                <span>{item.label}</span>
              {/if}
            </li>
          {/each}
        </ul>
      </address>
    {/if}
  </header>
  {#if hasMain || hasSide}
    <div class="ivy-grid" class:split={hasMain && hasSide}>
      {#if hasMain}
        <div class="ivy-main">
          {#if hasSummary}
            <section>
              <h3><span class="mark"><Icon name="summary" size={15} /></span> Summary</h3>
              <p class="summary">{document.summary}</p>
            </section>
          {/if}
          {#if hasExperience}
            <section class="experience">
              <h3><span class="mark"><Icon name="role" size={15} /></span> Experience</h3>
              {#each document.experience as role, index (index)}
                <div class="role">
                  <p class="role-line">
                    <strong>{role.title}</strong>
                    {#if dates(role)}<span class="dates">{dates(role)}</span>{/if}
                  </p>
                  {#if role.employer}<p class="employer">{role.employer}</p>{/if}
                  {#if role.bullets?.length}
                    <ul>
                      {#each role.bullets as bullet, bulletIndex (bulletIndex)}
                        <li>{bullet}</li>
                      {/each}
                    </ul>
                  {/if}
                </div>
              {/each}
            </section>
          {/if}
        </div>
      {/if}
      {#if hasSide}
        <aside class="ivy-side">
          {#if hasSkills}
            <section>
              <h3><span class="mark"><Icon name="skills" size={15} /></span> Skills</h3>
              <ul class="skill-pills">
                {#each document.skills as skill (skill)}
                  <li>{skill}</li>
                {/each}
              </ul>
            </section>
          {/if}
          {#if hasEducation}
            <section>
              <h3><span class="mark"><Icon name="education" size={15} /></span> Education</h3>
              {#each document.education as school, index (index)}
                {@const title = school.credential || school.school}
                {#if title || school.year}
                  <div class="school">
                    {#if title}<p class="school-title">{title}</p>{/if}
                    {#if school.credential && school.school}<p>{school.school}</p>{/if}
                    {#if school.year}<p class="school-year">{school.year}</p>{/if}
                  </div>
                {/if}
              {/each}
            </section>
          {/if}
        </aside>
      {/if}
    </div>
  {/if}
</article>
