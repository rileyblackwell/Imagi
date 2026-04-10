# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Imagi is a monorepo with a Django REST backend and Vue 3 SPA frontend, both containerized with Docker.

## Architecture

- **Backend** (`backend/django/`): Django 6 + Django REST Framework, Python 3.13, managed with Pipenv. Gunicorn for production. Currently SQLite in dev, PostgreSQL-ready via psycopg2-binary.
- **Frontend** (`frontend/vuejs/`): Vue 3 + TypeScript + Vite, with Vue Router (history mode) and Pinia for state management. Nginx serves production builds.
- No frontend-backend API integration exists yet. The backend only has the Django admin endpoint (`/admin/`).

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

## Key Configuration

- Frontend path alias: `@/` maps to `./src/`
- Django settings: `imagi.settings` (DEBUG=True in dev, secret key needs env var for production)
- Node version requirement: ^20.19.0 || >=22.12.0
