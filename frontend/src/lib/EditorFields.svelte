<script>
  import Icon from './Icon.svelte';
  import EditorList from './EditorList.svelte';
  import CompanyLogo from './CompanyLogo.svelte';
  import { companyKey, moveItem } from './editor.js';
  let { profile, design, selected, cvId, onedit, ondesign, onupload, busy = false } = $props();
  let crop = $state(false);
  const lines = value => value.split('\n');
  const customIndex = $derived(profile.custom_sections.findIndex(section => section.id === selected));
  function field(section, index, key, value) {onedit(p => {p[section][index][key] = value;});}
</script>
<div class="fields">
  {#if selected === 'contact'}
    <h3>Contact details</h3>
    {#each [['name','Full name'],['email','Email'],['phone','Phone'],['location','Location']] as [key,label]}
      <label>{label}<input value={profile.contact[key]} oninput={e => onedit(p => {p.contact[key] = e.currentTarget.value;})}/></label>
    {/each}
    <label>Links · one per line<textarea rows="3" value={profile.contact.links.join('\n')} oninput={e => onedit(p => {p.contact.links = lines(e.currentTarget.value);})}></textarea></label>
    <label>Years of professional experience<input type="number" min="0" max="100" step="0.5" value={profile.years_experience} oninput={e => onedit(p => {p.years_experience = Number(e.currentTarget.value);})}/></label>
    <p class="hint">Enter your actual experience. This is used when checking the role.</p>
  {:else if selected === 'summary'}
    <h3>Summary</h3>
    <label>Your introduction<textarea rows="8" value={profile.summary} oninput={e => onedit(p => {p.summary = e.currentTarget.value;})}></textarea></label>
    <p class="hint">You can also click the summary in the canvas to edit it.</p>
  {:else if selected === 'skills'}
    <h3>Skills</h3>
    <p class="hint">List skills you have actually used. Drag to reorder.</p>
    <EditorList items={profile.skills} label="skill" onmove={(a,b) => onedit(p => {p.skills = moveItem(p.skills,a,b);})} onremove={i => onedit(p => {p.skills.splice(i,1);})}>
      {#snippet children(skill,i)}<input aria-label="Skill {i + 1}" placeholder="e.g. Python" value={skill} oninput={e => onedit(p => {p.skills[i] = e.currentTarget.value;})}/>{/snippet}
    </EditorList>
    <button class="add" type="button" onclick={() => onedit(p => {p.skills.push('');})}><Icon name="plus" size={16}/> Add skill</button>
  {:else if selected === 'experience'}
    <h3>Experience</h3>
    <EditorList items={profile.experience} label="experience" onmove={(a,b) => onedit(p => {p.experience = moveItem(p.experience,a,b);})} onremove={i => onedit(p => {p.experience.splice(i,1);})}>
      {#snippet children(role,i)}
        <div class="entry-fields">
          <label>Company<input value={role.employer} oninput={e => field('experience',i,'employer',e.currentTarget.value)}/></label>
          <label>Role title<input value={role.title} oninput={e => field('experience',i,'title',e.currentTarget.value)}/></label>
          <div class="pair"><label>Start<input placeholder="2022" value={role.start} oninput={e => field('experience',i,'start',e.currentTarget.value)}/></label><label>End<input placeholder="Present" value={role.end} oninput={e => field('experience',i,'end',e.currentTarget.value)}/></label></div>
          <label>Work bullets · one per line<textarea rows="6" value={role.bullets.join('\n')} oninput={e => field('experience',i,'bullets',lines(e.currentTarget.value))}></textarea></label>
          <div class="logo-tools">
            {#if design.company_logos[companyKey(role.employer)]}
              <img class="logo-preview" src={design.company_logos[companyKey(role.employer)]} alt="{role.employer} logo"/>
            {:else if !(companyKey(role.employer) in design.company_logos)}
              <CompanyLogo endpoint={`/api/cvs/${cvId}/logos/${i}?employer=${encodeURIComponent(role.employer)}`} company={role.employer}/>
            {/if}
            <strong>Company logo</strong><Icon name="camera" size={15}/>
          </div>
          <label class="check"><input type="checkbox" bind:checked={crop}/> Crop upload to a square</label>
          <label class="upload">Upload or replace logo<input type="file" accept="image/png,image/jpeg,image/webp" disabled={busy || !role.employer.trim()} onchange={e => {const file=e.currentTarget.files?.[0]; if(file) onupload(role.employer,file,crop); e.currentTarget.value='';}}/></label>
          <p class="hint">PNG, JPEG or WebP, up to 3 MB. Unchecked keeps the whole logo.</p>
          <div class="actions"><button type="button" onclick={() => ondesign(d => {d.company_logos[companyKey(role.employer)] = '';})}>Remove logo</button><button type="button" onclick={() => ondesign(d => {delete d.company_logos[companyKey(role.employer)];})}>Use automatic logo</button></div>
        </div>
      {/snippet}
    </EditorList>
    <button class="add" type="button" onclick={() => onedit(p => {p.experience.push({employer:'',title:'',start:'',end:'',bullets:[]});})}><Icon name="plus" size={16}/> Add experience</button>
  {:else if selected === 'education'}
    <h3>Education</h3>
    <EditorList items={profile.education} label="education" onmove={(a,b) => onedit(p => {p.education = moveItem(p.education,a,b);})} onremove={i => onedit(p => {p.education.splice(i,1);})}>
      {#snippet children(school,i)}
        <div class="entry-fields">
          <label>School<input value={school.school} oninput={e => field('education',i,'school',e.currentTarget.value)}/></label>
          <label>Qualification<input value={school.credential} oninput={e => field('education',i,'credential',e.currentTarget.value)}/></label>
          <label>Year<input value={school.year} oninput={e => field('education',i,'year',e.currentTarget.value)}/></label>
        </div>
      {/snippet}
    </EditorList>
    <button class="add" type="button" onclick={() => onedit(p => {p.education.push({school:'',credential:'',year:''});})}><Icon name="plus" size={16}/> Add education</button>
  {:else if customIndex >= 0}
    <h3>Additional section</h3>
    <label>Section title<input value={profile.custom_sections[customIndex].title} oninput={e => onedit(p => {p.custom_sections[customIndex].title = e.currentTarget.value;})}/></label>
    <p class="hint">Use this for projects, certifications, languages or other relevant facts. These entries do not count as required-skill evidence in the role check.</p>
    <EditorList items={profile.custom_sections[customIndex].items} label="entry" onmove={(a,b) => onedit(p => {p.custom_sections[customIndex].items = moveItem(p.custom_sections[customIndex].items,a,b);})} onremove={i => onedit(p => {p.custom_sections[customIndex].items.splice(i,1);})}>
      {#snippet children(item,i)}<textarea aria-label="Entry {i+1}" rows="3" value={item} oninput={e => onedit(p => {p.custom_sections[customIndex].items[i] = e.currentTarget.value;})}></textarea>{/snippet}
    </EditorList>
    <button class="add" type="button" onclick={() => onedit(p => {p.custom_sections[customIndex].items.push('');})}><Icon name="plus" size={16}/> Add entry</button>
  {/if}
</div>
<style>
  .fields,.entry-fields {display:grid;gap:12px;min-width:0;}.fields {padding-top:16px;border-top:1px solid var(--line);}
  h3 {margin:0;font-size:1rem;}label {display:grid;gap:5px;font-size:12px;font-weight:600;}
  input,textarea {width:100%;min-width:0;font:inherit;font-size:13px;}textarea {resize:vertical;line-height:1.5;min-height:0;}
  .pair {display:grid;grid-template-columns:1fr 1fr;gap:8px;}.hint {font-size:11px;line-height:1.5;margin:0;}
  button {color:var(--ink);cursor:pointer;border:1px solid var(--line);border-radius:6px;background:white;padding:9px;font-size:12px;}
  button:hover {background:#e8f0eb;color:var(--ink);}
  .add {border-style:dashed;background:transparent;color:var(--accent);font-weight:600;min-height:40px;}
  .logo-tools {display:flex;gap:8px;align-items:center;font-size:12px;margin-top:4px;}.logo-preview {width:40px;height:40px;object-fit:contain;background:white;border:1px solid var(--line);border-radius:5px;}
  .check {display:flex;align-items:center;font-weight:400;}.check input {width:auto;}.actions {display:flex;gap:6px;flex-wrap:wrap;}.actions button {font-size:11px;}
  .upload input {font-size:11px;padding:6px;}
</style>
