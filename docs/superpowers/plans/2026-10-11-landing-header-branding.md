# Landing Page, Header Logo, and User Information Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the official Job Ready logo mark to the application header across all pages and enrich the logged-in user experience with an avatar account chip in the header and a personalized welcome card on the Desk landing page.

**Architecture:** Create a reusable `BrandLogo.svelte` SVG component matching the emerald-and-grass branding. Integrate this component into `App.svelte` alongside the existing wordmark. Add a helper for extracting user initials, render a styled `.user-chip` in the header, and add a personalized `.desk-welcome` card to `Dashboard.svelte`. Update `app.css` with responsive, accessible styling conforming to Job Ready design tokens.

**Tech Stack:** Svelte 5 (runes: `$state`, `$derived`, `$props`), CSS3, Vite, Python/FastAPI backend test suite.

---

### File Structure

- **New Files:**
  - `frontend/src/lib/BrandLogo.svelte` — Reusable SVG logo emblem component.
  - `frontend/src/lib/user.js` — Helper functions for user display (e.g. `getInitials(emailOrName)`).
- **Modified Files:**
  - `frontend/src/App.svelte` — Header layout with logo lockup and user account chip.
  - `frontend/src/pages/Dashboard.svelte` — Desk landing view with personalized welcome hero.
  - `frontend/src/app.css` — Styles for brand link, user account chip, avatar badge, and desk welcome card.
- **Test Files:**
  - `tests/test_api.py` — Existing backend test suite ensuring sessions and pages work seamlessly.

---

### Task 1: Create `BrandLogo.svelte` and User Initials Helper

**Files:**
- Create: `frontend/src/lib/BrandLogo.svelte`
- Create: `frontend/src/lib/user.js`

- [ ] **Step 1: Create `frontend/src/lib/BrandLogo.svelte`**

```svelte
<script>
  let { size = 28, class: extra = '' } = $props();
</script>

<svg
  class="brand-logo {extra}"
  width={size}
  height={size}
  viewBox="0 0 32 32"
  aria-hidden="true"
  focusable="false"
>
  <rect width="32" height="32" rx="7" fill="#1b6b45" />
  <path fill="#f4faf6" d="M7.4 25Q7.2 18 8.6 12.5Q11.4 18 12.2 25Z" />
  <path fill="#f4faf6" d="M13.2 25Q13.5 14 15.2 6Q18.2 14 18.8 25Z" />
  <path fill="#f4faf6" d="M19.4 25Q21.2 18 22.4 13Q25.2 18.5 25.2 25Z" />
</svg>

<style>
  .brand-logo {
    display: inline-block;
    flex-shrink: 0;
    vertical-align: middle;
  }
</style>
```

- [ ] **Step 2: Create `frontend/src/lib/user.js`**

```javascript
/**
 * Extract 1-2 uppercase characters from an email address or full name.
 * e.g., 'alex.morgan@example.com' -> 'AM', 'user@domain.com' -> 'U'
 */
export function getInitials(identifier) {
  if (!identifier || typeof identifier !== 'string') return '·';
  const clean = identifier.trim();
  if (!clean) return '·';

  // If identifier is an email, use the part before '@'
  const namePart = clean.includes('@') ? clean.split('@')[0] : clean;

  // Split by dots, underscores, dashes, or whitespace
  const parts = namePart.split(/[._\-\s]+/).filter(Boolean);
  if (parts.length >= 2) {
    const first = parts[0][0] || '';
    const second = parts[1][0] || '';
    return (first + second).toUpperCase();
  }
  if (parts.length === 1 && parts[0].length >= 2 && !clean.includes('@')) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return (parts[0]?.[0] || '·').toUpperCase();
}
```

- [ ] **Step 3: Verify frontend build compiles with new files**

Run: `cd /Users/tusharvagela/Documents/GitHub/green-grass/frontend && npm run build`
Expected output: `✓ built in ...` with exit code 0.

- [ ] **Step 4: Commit new components**

```bash
git add frontend/src/lib/BrandLogo.svelte frontend/src/lib/user.js
git commit -m "feat: add BrandLogo component and user initials helper"
```

---

### Task 2: Integrate Brand Logo & Account Chip into Global Header

**Files:**
- Modify: `frontend/src/App.svelte`
- Modify: `frontend/src/app.css`

- [ ] **Step 1: Update `frontend/src/App.svelte` to import `BrandLogo` and `getInitials` and render the new header elements**

In `frontend/src/App.svelte`:
1. Import `BrandLogo` from `./lib/BrandLogo.svelte` and `getInitials` from `./lib/user.js`.
2. Compute `userInitials` via `$derived(getInitials(session.user?.email))`.
3. Update `.bar`:
   - Replace `<a class="wordmark" ...>Job Ready</a>` with:
     ```svelte
     <a class="brand-link" href="/" onclick={(event) => followLink(event, '/')}>
       <BrandLogo size={28} />
       <span class="wordmark">Job Ready</span>
     </a>
     ```
   - In `<nav>` for authenticated user:
     ```svelte
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
     ```

- [ ] **Step 2: Add styles in `frontend/src/app.css` for `.brand-link`, `.user-chip`, `.user-avatar`, and `.signout-btn`**

Add CSS rules:
```css
.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: var(--ink);
}

.brand-link:hover .wordmark {
  color: var(--accent-deep);
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--sheet);
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 0.2rem 0.65rem 0.2rem 0.25rem;
  min-width: 0;
}

.user-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--accent);
  color: #ffffff;
  font-family: var(--sans);
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
  flex-shrink: 0;
}

.signout-btn {
  margin-left: 0.25rem;
}
```

- [ ] **Step 3: Run frontend build to verify syntax and bundle generation**

Run: `cd /Users/tusharvagela/Documents/GitHub/green-grass/frontend && npm run build`
Expected output: `✓ built in ...` with zero errors.

- [ ] **Step 4: Commit header changes**

```bash
git add frontend/src/App.svelte frontend/src/app.css
git commit -m "feat: add logo brand lockup and user account chip to header"
```

---

### Task 3: Enhance Desk Landing Page with Personalized Welcome Hero

**Files:**
- Modify: `frontend/src/pages/Dashboard.svelte`
- Modify: `frontend/src/app.css`

- [ ] **Step 1: Update `frontend/src/pages/Dashboard.svelte`**

1. Import `session` from `../lib/session.svelte.js` and `getInitials` from `../lib/user.js`.
2. Compute `userInitials = $derived(getInitials(session.user?.email))`.
3. Enhance the desk header with the personalized welcome hero card:
   ```svelte
   <header class="desk-welcome">
     <div class="welcome-main">
       <span class="welcome-avatar" aria-hidden="true">{userInitials}</span>
       <div class="welcome-text">
         <p class="eyebrow">Career Desk</p>
         <h1>Welcome back{#if session.user?.email}, {session.user.email}{/if}</h1>
         <p class="lede">Upload a CV, check it against one role, and remove anything you no longer need.</p>
       </div>
     </div>
     <a class="button" href="/cvs/new"><Icon name="upload" size={18} /> Upload a CV</a>
   </header>
   ```

- [ ] **Step 2: Add styles in `frontend/src/app.css` for `.desk-welcome`, `.welcome-main`, `.welcome-avatar`, and `.welcome-text`**

```css
.desk-welcome {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2.25rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--line);
}

.welcome-main {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  min-width: 0;
}

.welcome-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  background: repeating-linear-gradient(115deg, #10603f 0 14px, #157049 14px 28px);
  color: #ffffff;
  font-family: var(--serif);
  font-size: 1.25rem;
  font-weight: 600;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(16, 96, 63, 0.2);
}

.welcome-text {
  min-width: 0;
}

.welcome-text h1 {
  margin: 0.15rem 0 0.4rem;
  font-size: 1.85rem;
  word-break: break-word;
}

.welcome-text .lede {
  margin: 0;
  font-size: 1.05rem;
  color: var(--muted);
}

@media (max-width: 768px) {
  .desk-welcome {
    flex-direction: column;
    align-items: flex-start;
    gap: 1.25rem;
  }
}
```

- [ ] **Step 3: Run frontend build to verify compilation**

Run: `cd /Users/tusharvagela/Documents/GitHub/green-grass/frontend && npm run build`
Expected output: `✓ built in ...` with zero errors.

- [ ] **Step 4: Commit Desk landing hero changes**

```bash
git add frontend/src/pages/Dashboard.svelte frontend/src/app.css
git commit -m "feat: add personalized welcome hero to Desk landing page"
```

---

### Task 4: Full System Verification & Regression Testing

**Files:**
- Test verification across client and server.

- [ ] **Step 1: Run the full backend test suite**

Run: `.venv/bin/pytest`
Expected output: 69 passed (or current total) with zero failures.

- [ ] **Step 2: Build the frontend for production**

Run: `cd /Users/tusharvagela/Documents/GitHub/green-grass/frontend && npm run build`
Expected output: Production build succeeded into `frontend/dist`.

- [ ] **Step 3: Verify git status is clean**

Run: `git status`
Expected output: Clean working tree (no unstaged or untracked changes other than the expected plan file).
