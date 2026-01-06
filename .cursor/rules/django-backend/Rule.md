---
description: Defines the backend architecture, Django conventions, API design standards, and testing practices used throughout the Imagi Oasis backend.
globs:
  - "backend/**"
alwaysApply: true
---

# Django Backend Rules — Imagi Oasis

## Backend Stack

- **Framework**: Django 4.x  
- **API Layer**: Django REST Framework (DRF)  
- **Database**
  - PostgreSQL (Production)
  - SQLite (Local Development)

- **Testing Framework**: pytest  
- **Authentication**
  - Django built-in authentication
  - DRF Token Authentication (OAuth2 planned)

- **API Versioning**
  - All API endpoints must be namespaced under: `/api/v1/`

---

## Backend Apps (Django)

- **auth** — Custom authentication and authorization  
- **builder** — Core AI generation logic and prompt orchestration  
- **home** — Landing pages and static marketing content  
- **payments** — Stripe integration for API credit management  
- **agents** — AI workflow and agent lifecycle management  
- **project_manager** — User project lifecycle and file management  

---

## Django API Design Standards

- Use **Django REST Framework** for all API endpoints.
- Follow strict RESTful conventions for resource naming and HTTP methods.
- Maintain a clean separation of concerns:
  - `models.py` — data models only  
  - `serializers.py` — request / response validation  
  - `views.py` — business logic and request handling  
  - `urls.py` — routing only  

- All new endpoints must:
  - Live under `/api/v1/`
  - Use explicit serializers
  - Enforce authentication where applicable

---

## Testing Strategy

### Backend (Django)

- **Unit Tests**
  - Use `pytest` to test models, serializers, and views in isolation.

- **Integration Tests**
  - Validate complete API workflows including authentication and permissions.

- All new features must include tests that verify:
  - Expected success paths
  - Common failure cases
  - Permission boundaries

---

You may reference files using `@file-path` syntax where supported.  
Markdown formatting is allowed but optional.