// Private, in-memory drafts survive SPA navigation but never go into browser storage.
let owner = null;
const drafts = new Map();
function forOwner(userId) {
  if (owner !== userId) { drafts.clear(); owner = userId; }
}
export function rememberDraft(userId, id, value) {
  forOwner(userId);
  drafts.set(String(id), JSON.stringify(value));
}
export function recallDraft(userId, id) {
  forOwner(userId);
  const saved = drafts.get(String(id));
  return saved ? JSON.parse(saved) : null;
}
export function forgetDraft(userId, id) {
  forOwner(userId);
  drafts.delete(String(id));
}
export function clearEditorDrafts() { drafts.clear(); owner = null; }
export function hasEditorDrafts() { return drafts.size > 0; }
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', event => {
    if (hasEditorDrafts()) { event.preventDefault(); event.returnValue = ''; }
  });
}
