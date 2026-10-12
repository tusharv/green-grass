# Landing page, header logo, and user information

## Overview

Make sure the landing page (Desk workspace) and the global application header feature the official Job Ready logo and clear, polished logged-in user information.

## Decisions

1. **Brand Identity & Logo:**
   - Create a reusable `frontend/src/lib/BrandLogo.svelte` component displaying the official Job Ready emblem (emerald rounded square tile `#1b6b45` with the three stylized curved grass blades `#f4faf6`).
   - The logo accepts an optional `size` prop (default `28` pixels).
   - In the header, replace the plain text wordmark with a unified brand lockup: `<BrandLogo size={28} />` paired with `<span class="wordmark">Job Ready</span>` linking to `/`.

2. **Header User Account Chip (`frontend/src/App.svelte`):**
   - When signed in, the header displays:
     - The Desk link with `<Icon name="desk" size={16} />`.
     - An account chip (`.user-chip`) containing:
       - A 26px round avatar badge displaying the user's initials (derived from their email or name) in white on a forest green background (`#10603f`).
       - The user's email address (`.account`), with tooltip and ellipsis text overflow.
       - A clean "Sign out" button.
   - When signed out, the header retains the "Sign in" and "Create account" navigation links while displaying the brand logo lockup.

3. **Desk Landing Page (`frontend/src/pages/Dashboard.svelte`):**
   - The Desk is the primary landing experience for authenticated users.
   - The top hero/head area is enhanced with a personalized welcome card:
     - Left: A 44px avatar tile with initials, an eyebrow tag (`CAREER DESK`), a personalized greeting (`Welcome back, {session.user.email}`), and contextual lede (`Upload a CV, check it against one role, and remove anything you no longer need.`).
     - Right: Direct action button `<a class="button" href="/cvs/new"><Icon name="upload" size={18} /> Upload a CV</a>`.
   - The existing desk statistics (CVs, Roles, Ready to send, Gaps to close) and lists of uploaded CVs and checked roles remain intact below the welcome hero.

4. **Initials Helper:**
   - A helper extracts 1-2 uppercase characters from the user's email or name (e.g. `alex.morgan@example.com` -> `AM`, `user@domain.com` -> `U`).

5. **Responsive Design:**
   - On screens below 640px, the brand lockup scales gracefully, and the user chip prioritizes the avatar and sign-out button, truncating the email to fit mobile viewports.

## Component Specifications

### `BrandLogo.svelte`
- Props: `size` (number, default 28).
- SVG viewBox: `0 0 32 32`.
- Rounded rect with `rx="7"` fill `#1b6b45`.
- Three path blades in fill `#f4faf6`.
- Accessible markup: `aria-hidden="true"`.

### `App.svelte` Header Lockup
- `.brand-link`: flex container with `gap: 0.6rem`, `align-items: center`, `text-decoration: none`.
- Hover state: wordmark transitions to `var(--accent-deep)`.
- `.user-chip`: flex container with `gap: 0.5rem`, `align-items: center`, background `var(--sheet)`, border `1px solid var(--line)`, border-radius `20px`, padding `0.2rem 0.65rem 0.2rem 0.3rem`.
- `.user-avatar`: 26px circle, background `#10603f`, color `#ffffff`, font-size `0.75rem`, font-weight `700`.

### `Dashboard.svelte` Desk Landing Hero
- `.desk-welcome`: flex container, `justify-content: space-between`, `align-items: center`, `gap: 1.5rem`, `margin-bottom: 2rem`.
- User initials badge: 44px rounded tile (`border-radius: 10px`), background `repeating-linear-gradient(115deg, #10603f 0 10px, #157049 10px 20px)`, color `#ffffff`, font-family `var(--serif)`, font-size `1.1rem`, font-weight `600`.
- Eyebrow: `font-size: 0.8rem`, `font-weight: 700`, `letter-spacing: 0.05em`, color `var(--accent)`.

## Verification Plan

- Backend tests: Run `.venv/bin/pytest` to verify all existing API and fit/screening tests pass without regressions.
- Frontend build: Run `npm run build` in `frontend/` to ensure TypeScript/Svelte compilation succeeds with zero errors.
- Visual inspection: Verify header rendering across unauthenticated (`/login`, `/register`) and authenticated (`/`, `/cvs/new`, etc.) states.
