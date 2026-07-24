# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Imagi is an all-in-one platform for building and running a business. Users build their business by creating a web application with AI-powered tools, then run and grow that business with built-in tools for marketing, sales, finance, and more. The product is a monorepo with a Django REST backend and Vue 3 SPA frontend, both containerized with Docker.

## Architecture

- **Backend** (`backend/django/`): Django 6 + Django REST Framework, Python 3.13, managed with Pipenv. Gunicorn for production. Currently SQLite in dev, PostgreSQL-ready via psycopg2-binary.
- **Frontend** (`frontend/vuejs/`): Vue 3 + TypeScript + Vite, with Vue Router (history mode) and Pinia for state management. Nginx serves production builds.
- The SPA talks to the backend under `/api/v1/` (auth, payments, project manager, build). It always uses **relative** URLs — the Vite dev server proxies `/api` in development, nginx does it in production — so nothing in the app hardcodes a backend host or port.

## Development Commands

### Frontend (run from `frontend/vuejs/`)

```bash
npm install              # Install dependencies
npm run dev              # Start Vite dev server
npm run build            # Type-check + production build
npm run build-only       # Production build without type checking
npm run type-check       # Run vue-tsc type checking
npm run lint             # Run oxlint + eslint with auto-fix
npm run format           # Format with Prettier
```

### Backend (run from `backend/django/`)

```bash
pipenv install           # Install dependencies
pipenv shell             # Activate virtual environment
python manage.py runserver        # Start dev server
python manage.py migrate          # Run migrations
python manage.py createsuperuser  # Create admin user
```

## Dev login (for driving the preview browser)

Most of the app sits behind authentication. To get past `/auth/signin` in a preview
browser, use the seeded local account:

| | |
|---|---|
| **Username** | `devuser` |
| **Password** | `imagi-local-dev-only` |

Sign in at `/auth/signin` — the form takes the **username**, not the email.

The dev database is gitignored, so a fresh clone or a reset DB won't have this
account. Recreate it any time (idempotent — it also resets the password, so the
values above are always correct):

```bash
pipenv run python manage.py seed_dev_user
```

**This account is local-only and the password above is deliberately public and
worthless.** It exists solely in the local SQLite dev DB — production uses Postgres
via `DATABASE_URL`, so it can never exist there. `seed_dev_user` enforces this rather
than trusting the reader: it refuses to run when `DEBUG` is off or when the default
database isn't SQLite. Never reuse this password anywhere real, and don't grant the
account staff/superuser.

Note that the dev DB is symlinked to the main checkout (see
`.claude/hooks/dev-setup.sh`), so every worktree and every concurrent Claude Code
instance shares this one login.

## Preview servers and ports

`.claude/launch.json` defines `frontend-vite` and `backend-django`. The harness
assigns each a free port at launch, so several Claude Code instances can run side by
side without colliding — don't assume 5173/8000.

The frontend finds its own backend automatically: `serve-backend` publishes the port
it bound to into `.claude/.dev-ports.json` (gitignored), and `vite.config.ts` resolves
the proxy target from it per request. Boot order doesn't matter. The Vite log prints
`[api proxy] -> …` whenever the target changes, including a warning when it falls back
to `:8000` because this worktree has no backend running — if you see that warning, you
may be talking to another instance's Django.

## Key Configuration

- Frontend path alias: `@/` maps to `./src/`
- Django settings: `imagi.settings` (DEBUG=True in dev, secret key needs env var for production)
- Node version requirement: ^20.19.0 || >=22.12.0
