<script>
  import { api, session } from '../lib/session.svelte.js';
  import { navigate } from '../lib/nav.svelte.js';

  let email = $state('');
  let password = $state('');
  let error = $state('');
  let busy = $state(false);

  async function submit(event) {
    event.preventDefault();
    error = '';
    busy = true;
    try {
      const user = await api('/api/login', { method: 'POST', json: { email, password } });
      session.user = user;
      navigate('/');
    } catch (err) {
      error = err.message;
    } finally {
      busy = false;
    }
  }
</script>

<section class="auth">
  <h1>Sign in</h1>
  <p class="lede">Welcome back. Pick up where you left off and take the next step toward your next role.</p>
  <form onsubmit={submit}>
    <label>
      Email
      <input type="email" autocomplete="username" bind:value={email} required />
    </label>
    <label>
      Password
      <input type="password" autocomplete="current-password" bind:value={password} required />
    </label>
    {#if error}<p class="alert" role="alert">{error}</p>{/if}
    <button type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
  </form>
  <p class="switch">New here? <a href="/register">Create account</a></p>
</section>
