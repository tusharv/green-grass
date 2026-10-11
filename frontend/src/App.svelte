<script>
  import { onMount } from 'svelte';
  import { followLink, locationState, navigate } from './lib/nav.svelte.js';
  import { matchRoute } from './lib/routes.js';
  import { api, loadSession, session } from './lib/session.svelte.js';
  import Login from './pages/Login.svelte';
  import Register from './pages/Register.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  import Upload from './pages/Upload.svelte';
  import CvDetail from './pages/CvDetail.svelte';
  import Apply from './pages/Apply.svelte';
  import Result from './pages/Result.svelte';

  let booted = $state(false);
  const route = $derived(matchRoute(locationState.path));

  onMount(async () => {
    const onPop = () => {
      locationState.path = location.pathname + location.search;
    };
    window.addEventListener('popstate', onPop);
    window.addEventListener('click', onMainClick);
    try {
      await loadSession();
    } catch (error) {
      session.ready = true;
    }
    booted = true;
    return () => {
      window.removeEventListener('popstate', onPop);
      window.removeEventListener('click', onMainClick);
    };
  });

  $effect(() => {
    if (!booted || !session.ready) return;
    if (!session.user && route.auth) navigate('/login');
    if (session.user && (route.name === 'login' || route.name === 'register')) navigate('/');
  });

  function onMainClick(event) {
    const link = event.target instanceof Element ? event.target.closest('a') : null;
    if (!link || !link.href) return;
    const url = new URL(link.href, location.origin);
    if (url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
    followLink(event, url.pathname + url.search);
  }

  async function signOut() {
    try {
      await api('/api/logout', { method: 'POST' });
    } catch {
      /* The session is cleared locally either way. */
    }
    session.user = null;
    navigate('/login');
    await loadSession();
  }
</script>

<div class="frame">
  <header class="bar">
    <a class="wordmark" href="/" onclick={(event) => followLink(event, '/')}>Green Grass</a>
    <nav>
      {#if session.user}
        <span class="account" title={session.user.email}>{session.user.email}</span>
        <button type="button" class="text" onclick={signOut}>Sign out</button>
      {:else}
        <a
          href="/login"
          aria-current={route.name === 'login' ? 'page' : undefined}
          onclick={(event) => followLink(event, '/login')}
        >Sign in</a>
        <a
          href="/register"
          aria-current={route.name === 'register' ? 'page' : undefined}
          onclick={(event) => followLink(event, '/register')}
        >Create account</a>
      {/if}
    </nav>
  </header>
  <main>
    {#if !booted}
      <p class="hint">Loading…</p>
    {:else if route.name === 'login'}
      <Login />
    {:else if route.name === 'register'}
      <Register />
    {:else if route.name === 'home' && session.user}
      <Dashboard />
    {:else if route.auth && !session.user}
      <p class="hint">Loading…</p>
    {:else if route.name === 'upload'}
      <Upload />
    {:else if route.name === 'cv'}
      <CvDetail id={route.id} />
    {:else if route.name === 'apply'}
      <Apply cvId={route.cvId} />
    {:else if route.name === 'result'}
      <Result id={route.id} />
    {:else}
      <section class="stack narrow">
        <h1>That page is not here</h1>
        <p><a href="/">Back to your CVs</a></p>
      </section>
    {/if}
  </main>
</div>
