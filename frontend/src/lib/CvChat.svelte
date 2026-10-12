<script>
  import { onMount, tick } from 'svelte';
  import { api } from './session.svelte.js';
  import Icon from './Icon.svelte';

  let { id, shared = false, blocked = false, onapply = () => {} } = $props();
  let chat = $state(null);
  let message = $state('');
  let error = $state('');
  let status = $state('');
  let busy = $state('');
  let confirmed = $state(false);
  let updateShared = $state(false);
  let transcript = $state();
  let editor = $state();
  const url = $derived(`/api/applications/${id}/chat`);

  async function refresh() {
    try { chat = await api(url); confirmed = false; error = ''; }
    catch (err) { error = err.message; }
  }
  onMount(refresh);

  async function send(event) {
    event.preventDefault();
    if (!message.trim() || !chat || busy) return;
    busy = 'send'; error = ''; status = ''; confirmed = false;
    try {
      chat = await api(url, {method:'POST',json:{message:message.trim(),revision:chat.revision}});
      message = ''; confirmed = false;
      await tick();
      transcript?.scrollTo({top:transcript.scrollHeight,behavior:'instant'});
    } catch (err) {
      error = err.message;
      if (err.status === 409) {
        try { chat = await api(url); confirmed = false; } catch { /* Keep the message for retry. */ }
      }
    } finally { busy = ''; }
  }
  async function apply() {
    if (!confirmed || !chat?.proposal || busy || blocked) return;
    busy = 'apply'; error = ''; status = '';
    try {
      const result = await api(`${url}/apply`, {method:'POST',json:{
        revision:chat.revision,proposal_id:chat.proposal.id,confirmed:true,update_shared_profile:updateShared,
      }});
      chat = result.chat; confirmed = false; updateShared = false;
      onapply(result.application);
      status = `Main CV updated. This role now shows “${result.application.suitable ? 'Ready to send' : 'Gaps to close'}”. ${result.shared_updated ? 'Your shared profile was updated too.' : 'Your shared profile was not changed.'}`;
    } catch (err) {
      error = err.message;
      if (err.status === 409) { try { chat = await api(url); confirmed = false; } catch { /* Keep error visible. */ } }
    } finally { busy = ''; }
  }
  async function discard() {
    busy = 'discard'; error = '';
    try { chat = await api(`${url}/proposal`, {method:'DELETE',json:{revision:chat.revision}}); confirmed = false; }
    catch (err) { error = err.message; }
    finally { busy = ''; }
  }
  function example(text) { message = text; editor?.focus(); }
</script>

<section class="cv-chat" id="cv-chat" aria-labelledby="cv-chat-title">
  <header class="chat-heading">
    <span class="chat-icon"><Icon name="cv" size={22}/></span>
    <div><p class="eyebrow">Your experience, in your words</p><h2 id="cv-chat-title">Update my CV</h2></div>
    <span class="private-label">Private conversation</span>
  </header>
  <p class="intro">Something missing from your CV? Tell us what you did, where, and how. Review the proposed edits before updating your main CV and checking this role again.</p>
  <p class="scope">This chat can update your summary, skills and work bullets. Employers, job titles, dates, education and total years stay as recorded.</p>
  {#if !chat}
    <p role="status">{error ? 'The conversation could not be loaded.' : 'Loading your conversation…'}</p>
    {#if error}<button class="button secondary" onclick={refresh}>Retry</button>{/if}
  {:else}
    {#if chat.messages.length}
      <!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users need to scroll the conversation.) -->
      <div class="transcript" bind:this={transcript} role="log" aria-label="CV update conversation" aria-live="polite" tabindex="0">
        {#each chat.messages as entry (entry.id)}
          <article class:user={entry.role === 'user'} class="message">
            <div class="message-label">{entry.role === 'user' ? 'You' : 'CV assistant'}{#if entry.application_id !== Number(id)}<span> · {entry.role_title}</span>{/if}</div>
            <p>{entry.text}</p>
            {#if entry.applied_changes?.length}<details><summary>View applied changes</summary>{#each entry.applied_changes as change}<p><strong>{change.label}</strong><br/>{change.after || `Removed: ${change.before}`}</p>{/each}</details>{/if}
          </article>
        {/each}
      </div>
    {:else}
      <div class="examples" aria-label="Ideas for your first message">
        <button type="button" onclick={() => example('I have experience with a skill marked as missing. ')}>Explain a missing skill <span aria-hidden="true">↗</span></button>
        <button type="button" onclick={() => example('I would like to add more detail about a project at ')}>Describe a project <span aria-hidden="true">↗</span></button>
        <button type="button" onclick={() => example('There is a detail in my work history I want to correct: ')}>Correct a work detail <span aria-hidden="true">↗</span></button>
      </div>
    {/if}
    {#if chat.notice}<p class="notice">{chat.notice}</p>{/if}
    <form onsubmit={send}>
      <label for="cv-chat-message">Tell us about your experience</label>
      <textarea id="cv-chat-message" bind:this={editor} bind:value={message} maxlength="3000" rows="3" disabled={Boolean(busy)} placeholder="For example: At Acme, I used GitHub for two years to review pull requests. Before that, I used it for college projects."></textarea>
      <div class="composer-actions"><span>{message.length} / 3,000</span><button class="button" type="submit" disabled={Boolean(busy) || !message.trim()}>{busy === 'send' ? 'Preparing a reply…' : 'Send message'}<span aria-hidden="true">↑</span></button></div>
    </form>
    {#if chat.proposal}
      <section class="proposal" aria-labelledby="proposal-title">
        <div class="proposal-heading"><div><p class="eyebrow">Not saved yet</p><h3 id="proposal-title">Review your CV changes</h3></div><span>{chat.proposal.changes.length} {chat.proposal.changes.length === 1 ? 'edit' : 'edits'}</span></div>
        <p>Check that each statement is accurate. To adjust these edits, send another message above.</p>
        {#each chat.proposal.changes as change}
          <article class="change">
            <h4>{change.label}</h4>
            {#if change.before}<div class="before"><small>Current</small><p>{change.before}</p></div>{/if}
            <div class="after"><small>{change.after ? 'Proposed' : 'Remove'}</small><p>{change.after || 'Remove this entry from your CV.'}</p></div>
            <details><summary>Based on your words</summary>{#each change.evidence as source}<blockquote>{source.quote}</blockquote>{/each}</details>
          </article>
        {/each}
        <label class="check"><input type="checkbox" bind:checked={confirmed} disabled={Boolean(busy)}/> I confirm these edits accurately describe my experience.</label>
        {#if shared}<label class="check"><input type="checkbox" bind:checked={updateShared} disabled={Boolean(busy)}/> Update my shared profile with this revised CV too</label>{/if}
        <div class="apply-actions"><button type="button" class="button" onclick={apply} disabled={!confirmed || Boolean(busy) || blocked}>{busy === 'apply' ? 'Updating CV and reassessing…' : 'Apply & reassess'}</button><button class="button secondary" type="button" disabled={Boolean(busy)} onclick={discard}>Discard proposal</button></div>
        <p class="scope">Updates your main CV and this role check. Other role checks keep their previous assessments.{#if blocked} Please wait for the current assessment update to finish.{/if}</p>
      </section>
    {/if}
  {/if}
  {#if busy === 'apply'}<p class="notice" role="status">Checking the proposed CV against this role. This can take a minute; your saved CV stays unchanged until the check succeeds.</p>{/if}
  {#if status}<p class="success" role="status">{status}</p>{/if}
  {#if error}<p class="alert" role="alert">{error}</p>{/if}
</section>

<style>
  .cv-chat {scroll-margin-top:24px;border:1px solid var(--line);border-radius:14px;padding:28px;background:var(--sheet);}
  .chat-heading {display:flex;align-items:center;gap:12px;}.chat-heading h2 {margin:0;font-size:1.5rem;}.eyebrow {margin:0 0 4px;}.chat-icon {display:flex;padding:10px;border-radius:10px;color:var(--accent);background:#edf5ef;}.private-label {margin-left:auto;font-size:.75rem;color:var(--muted);}
  .intro {max-width:75ch;margin:18px 0 8px;}.scope {font-size:.8rem;color:var(--muted);line-height:1.6;}.examples {display:flex;flex-wrap:wrap;gap:8px;margin:20px 0;}.examples button {display:flex;gap:16px;border:1px solid var(--line);border-radius:7px;padding:10px 12px;background:white;color:var(--ink);font-size:.8rem;cursor:pointer;}
  .transcript {max-height:420px;overflow-y:auto;overscroll-behavior:contain;padding:16px;margin:20px 0;background:#f5f7f6;border-radius:10px;}.message {max-width:88%;padding:14px 16px;margin:0 0 12px;border:1px solid var(--line);border-radius:10px;background:white;}.message.user {margin-left:auto;background:#eef5ef;border-color:#d1e1d6;}.message-label {font-size:.72rem;font-weight:700;color:var(--muted);}.message p {margin:6px 0 0;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.65;}.message-label span {font-weight:400;}
  form label {display:block;font-weight:600;font-size:.85rem;margin:16px 0 8px;}textarea {width:100%;resize:vertical;min-height:100px;}.composer-actions {display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px;}.composer-actions > span {color:var(--muted);font-size:.75rem;}
  .proposal {margin-top:28px;padding-top:24px;border-top:1px solid var(--line);}.proposal-heading {display:flex;align-items:center;justify-content:space-between;}.proposal-heading h3 {margin:0;}.proposal-heading > span {font-size:.8rem;color:var(--muted);}.proposal > p {font-size:.85rem;}.change {margin:16px 0;border:1px solid var(--line);border-radius:8px;overflow:hidden;}.change h4 {margin:0;padding:12px 16px;background:#f5f7f6;font-size:.85rem;}.before,.after {padding:12px 16px;}.before {background:#faf4f1;}.after {background:#eff7f1;}.change small {font-size:.7rem;font-weight:700;text-transform:uppercase;color:var(--muted);}.change p {margin:4px 0;white-space:pre-wrap;overflow-wrap:anywhere;}.change details {padding:10px 16px;font-size:.8rem;}summary {cursor:pointer;color:var(--muted);}blockquote {margin:10px 0;padding-left:12px;border-left:2px solid var(--line);white-space:pre-wrap;}
  .check {display:flex;align-items:flex-start;gap:10px;font-size:.85rem;margin:14px 0;}.check input {width:18px;height:18px;flex:0 0 18px;margin-top:2px;}.apply-actions {display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;}.notice,.success {padding:12px 16px;background:#eef5f0;border-radius:8px;font-size:.85rem;}
  @media(max-width:600px) {.cv-chat {padding:18px;}.chat-heading {flex-wrap:wrap;}.private-label {margin-left:0;width:100%;}.message {max-width:100%;}.transcript {padding:10px;}.apply-actions .button {width:100%;}.examples {flex-direction:column;}.examples button {justify-content:space-between;}}
</style>
