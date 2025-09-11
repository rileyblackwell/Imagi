---
trigger: always_on
description: 
globs: 
---

# Your rule content

### Backend
- **Framework**: Django 4.x
- **API**: Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Testing**: pytest
- **Authentication**: Django built-in + DRF auth
- **API Version**: `/api/v1/`

## Backend Apps (Django)
- **auth**: Custom authentication and authorization
- **builder**: Core AI generation logic and prompts
- **home**: Landing pages and static content
- **payments**: Stripe integration for API credits
- **agents**: AI workflow management
- **project_manager**: Project lifecycle handling

### Django API Design
- Use **Django REST Framework (DRF)** for API endpoints.
- Follow RESTful API principles with `/api/v1/` versioning.
- Separate views, serializers, and models clearly within each app.
- Implement authentication via **DRF Token Auth** or OAuth2 in future updates.

## Testing Strategy
### Backend (Django)
- **Unit Tests**: Use `pytest` for testing models, views, and APIs.
- **Integration Tests**: Ensure API endpoints work as expected.

- You can @ files here
- You can use markdown but dont have to
