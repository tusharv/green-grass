<script>
  import Icon from './Icon.svelte';
  import EditorModal from './EditorModal.svelte';
  let { items, label, onmove, onremove = null, compact = false, removeLabel = 'Delete', removeIcon = 'trash', confirmRemove = true, children } = $props();
  let removing = $state(-1);
  let removeOpen = $state(false);
  let dragging = $state(-1);
  let over = $state(-1);
</script>
<ol class="editor-list" class:compact aria-label={label}>
  {#each items as item, index}
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <li class:over={over === index && dragging !== index}
      ondragover={(event) => {if (dragging >= 0) {event.preventDefault(); over = index;}}}
      ondrop={(event) => {event.preventDefault(); if (dragging >= 0) onmove(dragging, index); dragging = -1; over = -1;}}>
      <div class="item-tools">
        <button class="grip" type="button" draggable="true" aria-label="Drag {label} item {index + 1}" title="Drag to reorder, or use the arrow buttons"
          ondragstart={(event) => {dragging = index; event.dataTransfer.effectAllowed = 'move'; event.dataTransfer.setData('text/plain', String(index));}}
          ondragend={() => {dragging = -1; over = -1;}}><Icon name="grip" size={16}/></button>
        <span class="item-number">{index + 1}</span>
        <button type="button" aria-label="Move {label} item {index + 1} up" disabled={index === 0} onclick={() => onmove(index,index - 1)}><Icon name="up" size={16}/></button>
        <button type="button" aria-label="Move {label} item {index + 1} down" disabled={index === items.length - 1} onclick={() => onmove(index,index + 1)}><Icon name="down" size={16}/></button>
        {#if onremove}<button class="remove" type="button" aria-label="{removeLabel} {label} item {index + 1}" title="{removeLabel} {label}" onclick={() => {if (confirmRemove) {removing=index;removeOpen=true;} else onremove(index);}}><Icon name={removeIcon} size={15}/></button>{/if}
      </div>
      <div class="item-content">{@render children(item,index)}</div>
    </li>
  {/each}
</ol>
<EditorModal bind:open={removeOpen} title="Delete this {label}?" labelId={`remove-${label}-title`}>
  <p>This removes the entry from your draft. You can undo it before saving.</p>
  <div class="remove-actions"><button type="button" onclick={() => removeOpen = false}>Keep entry</button><button type="button" class="confirm-remove" onclick={() => {onremove(removing);removeOpen=false;}}>Delete entry</button></div>
</EditorModal>
<style>
  .remove-actions {display:flex;justify-content:flex-end;gap:10px;margin-top:20px;}.remove-actions button {padding:10px 16px;border:1px solid var(--line);font-size:13px;}.remove-actions .confirm-remove {background:#8b3627;color:white;}
  .editor-list {list-style:none;padding:0;margin:0;display:grid;gap:12px;}
  li {border:1px solid var(--line);border-radius:8px;padding:10px;background:var(--sheet);min-width:0;}
  li.over {outline:2px solid var(--accent);outline-offset:2px;}
  .item-tools {display:flex;gap:3px;align-items:center;margin:-4px -4px 8px;}
  button {border:0;background:transparent;color:var(--ink);min-width:30px;min-height:32px;padding:0;flex-shrink:0;border-radius:4px;cursor:pointer;font-size:17px;}
  button:hover {background:#e7efeb;color:var(--ink);} button:disabled {opacity:.25;cursor:default;}
  .grip {cursor:grab;font-size:22px;}.item-number {flex:1;color:var(--muted);font-size:11px;}
  .remove:hover {background:#fbe9e6;color:#922c20;}
  .item-content {min-width:0;}
  .compact li {display:flex;align-items:center;gap:2px;padding:4px;}
  .compact .item-content {flex:1;order:-1;}
  .compact .item-tools {margin:0;gap:0;}
  .compact .item-number {display:none;}
  .compact button {min-width:28px;width:28px;min-height:32px;font-size:15px;}
  .compact {gap:6px;}
  button:focus-visible {outline:2px solid var(--accent);outline-offset:1px;}
</style>
