export function matchRoute(full) {
  const url = new URL(full || '/', 'http://green-grass.local');
  const path = url.pathname.replace(/\/+$/, '') || '/';
  const cv = url.searchParams.get('cv');

  if (path === '/login') return { name: 'login', auth: false };
  if (path === '/register') return { name: 'register', auth: false };
  if (path === '/cvs/new') return { name: 'upload', auth: true };
  if (path === '/apply') return { name: 'apply', auth: true, cvId: Number(cv || 0) };

  let found = path.match(/^\/cvs\/(\d+)$/);
  if (found) return { name: 'cv', auth: true, id: Number(found[1]) };

  found = path.match(/^\/applications\/(\d+)$/);
  if (found) return { name: 'result', auth: true, id: Number(found[1]) };

  if (path === '/') return { name: 'home', auth: true };
  return { name: 'missing', auth: false };
}
