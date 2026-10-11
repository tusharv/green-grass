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
      const user = await api('/api/register', { method: 'POST', json: { email, password } });
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
  <h1>Create an account</h1>
  <p class="lede">Your CVs stay on your account. They are not kept as files on the server.</p>
  <form onsubmit={submit}>
    <label>
      Email
      <input type="email" autocomplete="username" bind:value={email} required />
    </label>
    <label>
      Password
      <input type="password" autocomplete="new-password" minlength="8" bind:value={password} required />
    </label>
    {#if error}<p class="alert" role="alert">{error}</p>{/if}
    <button type="submit" disabled={busy}>{busy ? 'Creating account…' : 'Create account'}</button>
  </form>
  <p class="switch">Already registered? <a href="/login">Sign in</a></p>
</section>
