export const session = $state({
  user: null,
  csrf: '',
  ready: false,
});

export async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const method = (options.method || 'GET').toUpperCase();
  if (!['GET', 'HEAD'].includes(method) && session.csrf) {
    headers.set('X-CSRF-Token', session.csrf);
  }
  let body = options.body;
  if (options.json !== undefined) {
    headers.set('Content-Type', 'application/json');
    body = JSON.stringify(options.json);
  }
  const response = await fetch(path, { method, body, headers, credentials: 'include' });
  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  if (!response.ok) {
    if (response.status === 401) session.user = null;
    const detail = data && data.detail;
    const message = typeof detail === 'string' ? detail : 'Something went wrong. Try again.';
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
}

export async function loadSession() {
  const data = await api('/api/session');
  session.user = data.user;
  session.csrf = data.csrf;
  session.ready = true;
  return data;
}
