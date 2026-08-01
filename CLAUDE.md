# CLAUDE.md

## Project Overview

Imagi is an all-in-one platform for building and running a business. Each business
lives as a project, and every project gets two halves. The **build** half is an
AI-powered workspace where an agent writes the business's web application from a
chat conversation — scaffolding and editing a real Vue 3 + Django codebase, showing
it in a live preview, and deploying it. The **run** half is a suite of business
tools attached to that same project: **Marketing** (campaigns, contacts, ad
connections, and a message inbox), **Sell** (products, customers, orders, and
Stripe-backed payment pages), and **Operate** (invoices, income and expense
tracking, and operational tasks). The goal is that one person can go from an idea
to a running business — app included — without leaving Imagi or stitching together
separate products.

## Test logins

Dev and prod test credentials live outside the repo in `~/.config/imagi/test-credentials.env`
— source it and use `$IMAGI_DEV_*` / `$IMAGI_PROD_*`. That file documents the rest.

```bash
set -a; . ~/.config/imagi/test-credentials.env; set +a
```

### Signing in during development

Don't type the password into the sign-in form. Get the dev account's auth token
and seed it into the frontend's storage instead:

```bash
bash .claude/hooks/dev-setup.sh dev-token
```

That prints `{"token": ..., "user": ...}` in exactly the shape `/auth/signin`
returns. Run it from anywhere in the worktree — it resolves its own paths, and
it is pre-approved in `.claude/settings.json` so it won't prompt. It reads the
existing account without touching it, and creates the account from the
credentials file above if the DB was reset. Then, in the preview browser:

```js
localStorage.setItem('token', JSON.stringify({ value: TOKEN, expires: Date.now() + 864e5 }))
localStorage.setItem('user', JSON.stringify(USER))
```

Navigate after setting both — `frontend/vuejs/src/shared/stores/auth.ts` reads
them on store init. The underlying command is
`apps/Auth/management/commands/seed_dev_user.py`; call it directly only to
create or reset an account, and pass `--password "$IMAGI_DEV_PASSWORD"` when you
do, or it will overwrite the documented credentials with its fallback defaults.

## Verification

Don't report work as done until it has been verified two ways.

**1. Run both test suites.** Frontend (Vitest):

```bash
cd frontend/vuejs && npm test
```

Backend (Django test runner):

```bash
cd backend/django && pipenv run python manage.py test
```

Frontend specs sit next to the code they cover, in `src/**/__tests__/*.spec.ts` —
e.g. `src/apps/imagi/build/stores/__tests__/projectStore.spec.ts` and
`src/shared/stores/__tests__/auth.spec.ts`. Backend tests are the per-app
`tests.py` (`apps/Auth/`, `apps/Payments/`, `apps/Imagi/Sell/`, …) plus the
package at `apps/Imagi/Build/tests/`. Add coverage alongside the change in
whichever of those the code belongs to.

**2. Exercise it in the preview browser.** For anything the running app renders
or serves, start the dev servers from `.claude/launch.json` (`frontend-vite`,
`backend-django`) with `preview_start` — never `npm run dev` or `runserver` in a
shell. The harness assigns each a free port, so don't assume 5173/8000. Sign in
with the dev credentials above, drive the actual flow that changed, and read the
browser console, the network requests, and the server logs for errors before
calling it good. Verify it directly and show the result — a screenshot, a
response body, a log line — rather than asking the user to check by hand.
