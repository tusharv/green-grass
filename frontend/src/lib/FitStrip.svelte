<script>
  let { score = 0, suitable = false, required = [], preferred = [] } = $props();
  const matched = $derived((preferred || []).filter((mark) => mark.present).map((mark) => mark.name));
  const minor = $derived(suitable ? [] : (preferred || []).filter((mark) => !mark.present));
</script>

<aside class="fit-strip" aria-label="Fit for this role">
  <p class="verdict">{suitable ? 'Ready to send' : 'Gaps to close'}</p>
  <p class="score">{score}</p>
  <p class="score-label">Out of 100</p>
  <ul>
    {#each required as mark}
      <li class={mark.present ? 'have' : 'major'}>
        <span>{mark.present ? 'Present' : 'Major'}</span>
        {mark.name}
      </li>
    {/each}
    {#each minor as mark}
      <li class="minor">
        <span>Minor</span>
        {mark.name}
      </li>
    {/each}
  </ul>
  {#if matched.length}
    <p class="preferred">Also on the CV: {matched.join(', ')}</p>
  {/if}
</aside>
