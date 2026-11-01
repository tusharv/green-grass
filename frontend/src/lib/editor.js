export const baseSections = {summary:'Summary', experience:'Experience', skills:'Skills', education:'Education'};
export function moveItem(items, from, to) {
  if (from < 0 || to < 0 || from >= items.length || to >= items.length || from === to) return items;
  const result = [...items];
  result.splice(to, 0, result.splice(from, 1)[0]);
  return result;
}
export function editText(profile, path, text) {
  // Only paths emitted by the document renderer may be edited in the canvas.
  if (!/^(summary|contact\.name|skills\.\d+|experience\.\d+\.(title|employer|bullets\.\d+)|education\.\d+\.(school|credential|year)|custom_sections\.\d+\.items\.\d+)$/.test(path)) return profile;
  const next = structuredClone(profile);
  const parts = path.split('.');
  const field = parts.pop();
  let target = next;
  for (const part of parts) { target = target?.[part]; if (target == null) return profile; }
  if (typeof target[field] !== 'string') return profile;
  target[field] = text;
  return next;
}
export function companyKey(name) { return name.trim().toLowerCase().replace(/\s+/g, ' '); }
export function changedSections(before, after) {
  return ['contact','summary','experience','skills','education','years_experience','custom_sections']
    .filter(key => JSON.stringify(before[key]) !== JSON.stringify(after[key]))
    .map(key => ({contact:'Contact details', years_experience:'Years of experience', custom_sections:'Additional sections', ...baseSections})[key]);
}
