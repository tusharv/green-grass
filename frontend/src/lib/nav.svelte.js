const start = typeof location === 'undefined' ? '/' : location.pathname + location.search;

export const locationState = $state({ path: start });

export function navigate(href) {
  const next = href || '/';
  if (locationState.path === next) return;
  history.pushState({}, '', next);
  locationState.path = next;
}

export function followLink(event, href) {
  if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
  event.preventDefault();
  navigate(href);
}
