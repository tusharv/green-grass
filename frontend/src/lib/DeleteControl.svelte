<script>
  import Icon from './Icon.svelte';

  let { label, message, pending = false, ondelete } = $props();
  let armed = $state(false);
</script>

{#if armed}
  <div class="confirm-pop" role="group" aria-label={message}>
    <p>{message}</p>
    <div class="confirm-actions">
      <button type="button" class="button secondary" disabled={pending} onclick={() => (armed = false)}>
        Cancel
      </button>
      <button type="button" class="button danger" disabled={pending} onclick={ondelete}>
        <Icon name="trash" size={16} />
        {pending ? 'Deleting…' : 'Delete'}
      </button>
    </div>
  </div>
{:else}
  <button type="button" class="icon-button" aria-label={label} onclick={() => (armed = true)}>
    <Icon name="trash" size={18} />
  </button>
{/if}
