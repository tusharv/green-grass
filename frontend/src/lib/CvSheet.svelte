<script>
  let { document } = $props();
  const contact = $derived(document?.contact || {});
  const bits = $derived(
    [contact.email, contact.phone, contact.location, ...(contact.links || [])].filter(Boolean),
  );

  function dates(role) {
    return [role.start, role.end].filter(Boolean).join(' - ');
  }

  function schoolLine(school) {
    return [school.credential, school.school, school.year].filter(Boolean).join(', ');
  }
</script>

<article class="ivy">
  <header>
    <h2>{contact.name || 'CV'}</h2>
    {#if bits.length}
      <p class="contact-line">{bits.join(' · ')}</p>
    {/if}
  </header>
  {#if document.summary}
    <section>
      <h3>Summary</h3>
      <p>{document.summary}</p>
    </section>
  {/if}
  {#if document.experience?.length}
    <section>
      <h3>Experience</h3>
      {#each document.experience as role}
        <div class="role">
          <p class="role-line">
            <strong>{role.title}</strong>
            {#if dates(role)}<span>{dates(role)}</span>{/if}
          </p>
          {#if role.employer}<p class="employer"><em>{role.employer}</em></p>{/if}
          {#if role.bullets?.length}
            <ul>
              {#each role.bullets as bullet}
                <li>{bullet}</li>
              {/each}
            </ul>
          {/if}
        </div>
      {/each}
    </section>
  {/if}
  {#if document.skills?.length}
    <section>
      <h3>Skills</h3>
      <p>{document.skills.join(' · ')}</p>
    </section>
  {/if}
  {#if document.education?.length}
    <section>
      <h3>Education</h3>
      {#each document.education as school}
        {@const line = schoolLine(school)}
        {#if line}<p>{line}</p>{/if}
      {/each}
    </section>
  {/if}
</article>
