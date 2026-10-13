<script>
  import { onMount } from 'svelte';
  import { followLink, locationState, navigate } from './lib/nav.svelte.js';
  import { matchRoute } from './lib/routes.js';
  import { api, loadSession, session } from './lib/session.svelte.js';
  import Icon from './lib/Icon.svelte';
  import BrandLogo from './lib/BrandLogo.svelte';
  import Credits from './lib/Credits.svelte';
  import { getInitials } from './lib/user.js';
  import Login from './pages/Login.svelte';
  import Register from './pages/Register.svelte';
  import Dashboard from './pages/Dashboard.svelte';
  import Landing from './pages/Landing.svelte';
  import Upload from './pages/Upload.svelte';
  import CvDetail from './pages/CvDetail.svelte';
  import Apply from './pages/Apply.svelte';
  import Result from './pages/Result.svelte';
  import Profile from './pages/Profile.svelte';
  import Legal from './pages/Legal.svelte';
  import SampleEvaluation from './pages/SampleEvaluation.svelte';
  import { getSample } from './lib/samples.js';

  let booted = $state(false);
  const route = $derived(matchRoute(locationState.path));
  const userInitials = $derived(getInitials(session.user?.email));

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
    if (url.hash && url.pathname === location.pathname && url.search === location.search) return;
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

<svelte:head>
  <title>{route.name === 'home' && !session.user
    ? 'Job Ready | Show why you fit. One role at a time.'
    : route.name === 'privacy'
      ? 'Privacy | Job Ready'
      : route.name === 'terms'
        ? 'Terms and conditions | Job Ready'
        : route.name === 'sample-evaluation'
          ? `${getSample(route.sample)?.name || 'Sample'} evaluation | Job Ready`
        : 'Job Ready'}</title>
</svelte:head>

<div class="frame" class:bare={route.name === 'profile' || route.name === 'sample-profile'} class:landing-frame={route.name === 'home' && !session.user}>
  {#if route.name !== 'profile' && route.name !== 'sample-profile'}
  <header class="bar">
    <a class="brand-link" href="/" onclick={(event) => followLink(event, '/')}>
      <BrandLogo size={28} />
      <span class="wordmark">Job Ready</span>
    </a>
    <nav>
      {#if session.user}
        <a
          class="desk-link"
          href="/"
          aria-current={route.name === 'home' ? 'page' : undefined}
          onclick={(event) => followLink(event, '/')}
        ><Icon name="desk" size={16} /> Desk</a>
        <div class="user-chip" title={session.user.email}>
          <span class="user-avatar" aria-hidden="true">{userInitials}</span>
          <span class="account">{session.user.email}</span>
        </div>
        <button type="button" class="text signout-btn" onclick={signOut}>Sign out</button>
      {:else if route.name !== 'profile'}
        <a
          class="button secondary"
          href="/login"
          aria-current={route.name === 'login' ? 'page' : undefined}
          onclick={(event) => followLink(event, '/login')}
        ><Icon name="signin" size={16} /> Sign in</a>
        <a
          class="button"
          href="/register"
          aria-current={route.name === 'register' ? 'page' : undefined}
          onclick={(event) => followLink(event, '/register')}
        ><Icon name="account" size={16} /> Create account</a>
      {/if}
    </nav>
  </header>
  {/if}
  <main>
    {#if !booted}
      {#if route.name !== 'profile'}<p class="hint">Loading…</p>{/if}
    {:else if route.name === 'login'}
      <Login />
    {:else if route.name === 'register'}
      <Register />
    {:else if route.name === 'home' && session.user}
      <Dashboard />
    {:else if route.name === 'home'}
      <Landing />
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
    {:else if route.name === 'profile'}
      <Profile token={route.token} />
    {:else if route.name === 'sample-profile'}
      <Profile token={`sample-${route.sample}`} />
    {:else if route.name === 'sample-evaluation'}
      {@const sample = getSample(route.sample)}
      {#if sample}<SampleEvaluation {sample} />{:else}<p class="hint">That sample is unavailable.</p>{/if}
    {:else if route.name === 'privacy' || route.name === 'terms'}
      <Legal page={route.name} />
    {:else}
      <section class="stack narrow">
        <h1>That page is not here</h1>
        <p><a href="/">Back to your CVs</a></p>
      </section>
    {/if}
  </main>
  {#if booted && route.name !== 'profile' && route.name !== 'sample-profile'}
    <Credits quiet={route.name === 'home' && !session.user} />
  {/if}
</div>
