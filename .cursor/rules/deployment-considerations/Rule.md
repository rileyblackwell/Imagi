---
description: Defines how Imagi Oasis is developed locally, deployed to staging and production, and structured across services to ensure scalability, reliability, and ease of operation.
globs:
  - "**/*"
alwaysApply: true
---

# Deployment & Infrastructure Rules — Imagi Oasis

## Local Development

- **Backend**
  - Django
  - SQLite3
  - Environment managed with Pipenv
  - Run using Django’s built-in development server

- **Frontend**
  - Vue.js
  - Vite development server for hot-module reloading

---

## Staging & Production

- **Backend**
  - Django served via Gunicorn  
  - Option to migrate to Uvicorn when async features are required

- **Database**
  - PostgreSQL

- **Frontend**
  - Vue.js application built using `vite build`
  - Output served as static assets through Nginx

- **Hosting Provider**
  - Railway.com

- **Architecture**
  - Separate Docker images for frontend and backend
  - Separate Railway services for each container
  - Services communicate exclusively over Railway’s private network

---

## Operational Principles

- Local development must mirror production as closely as possible without sacrificing simplicity.
- No production service may depend on SQLite or Django’s development server.
- All secrets must be stored in environment variables — never in source control.
- Each service must be independently restartable without impacting others.

---

## Future Enhancements

- Container orchestration and scaling via Kubernetes (target platform: GCP GKE or Railway-managed Kubernetes when available).
- Zero-downtime deployments with rolling container updates.
- Automated health checks and service monitoring.

---

You may reference files using `@file-path` syntax where supported.  
Markdown formatting is allowed but optional.