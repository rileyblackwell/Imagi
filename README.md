# Imagi

A platform that gives non-technical developers tools to design, build, and deploy web applications.

## About

**Mission:** Make it fast, affordable, and approachable for anyone to turn ideas into web applications.

### What Imagi Provides

- **AI Agent** — Chat, plan, and collaboratively write code
- **Visual Builder** — Simple graphical interface for building and shaping applications
- **Deployment Service** — Launch applications to the web with ease

### Target Users

- Non-technical employees prototyping ideas inside companies
- Technical employees who want a faster, easier interface for experimentation
- Non-technical startup founders validating early products
- Hobbyists building personal projects

Imagi is often the first step in a product's lifecycle: users can prototype, test, and launch quickly, then later bring in professional engineers to extend or scale what they've built.

## Core Philosophy

Imagi acts as a practical product-building partner, not just a code generator. It focuses on enabling momentum while preserving a clear upgrade path for future engineering teams.

Every output prioritizes:
- **Simplicity** over sophistication
- **Safety** over speed
- **Learnability** over maximal configurability
- **Early traction** with room to mature

### UX Principles

- Assume users may have little or no programming background
- Present complex technical work through simple, guided interactions
- Prefer visual workflows and conversational planning to raw configuration
- Generate systems that feel approachable, predictable, easy to reason about, and safe to iterate on
- Avoid unnecessary technical jargon unless it meaningfully helps the user move forward

## Tech Stack

### Local Development

#### Backend
- Django 4.x
- SQLite (local only)
- Pipenv for environment management
- Run via Django development server

#### Frontend
- Vue.js 3 (Composition API)
- Vite dev server (HMR enabled)

#### Local Servers
- **Frontend:** http://localhost:5174 (`npm run dev`)
- **Backend:** http://localhost:8000 (`python manage.py runserver`)

### Staging & Production

#### Backend
- Django served with Gunicorn
- May migrate to Uvicorn when async is required

#### Database
- PostgreSQL ≥ 14

#### Frontend
- Built using `vite build`
- Served as static assets via Nginx

#### Hosting
- Railway.com
- Separate Docker images for frontend and backend
- Separate Railway services per container
- Services communicate only over Railway's private network

## Development Environment

### Requirements
- **OS:** macOS with zsh
- **Python:** ≥ 3.10
- **Node.js:** ≥ 16.x

### Package Managers
- **Backend:** pipenv
- **Frontend:** npm or yarn

### Editor
- **Primary:** Cursor
- **Recommended Extensions:**
  - Python
  - Vue
  - Tailwind IntelliSense

## Backend Stack & Conventions

### Core Stack
- Django REST Framework
- pytest for testing
- Django auth + DRF token auth (OAuth2 planned)

### API Rules
- All endpoints must live under `/api/v1/`
- RESTful naming and methods
- **Separation of concerns:**
  - `models.py` — data
  - `serializers.py` — validation
  - `views.py` — logic
  - `urls.py` — routing

### Backend Apps
- `auth`
- `builder`
- `agents`
- `project_manager`
- `payments`
- `home`

### Testing
- Unit + integration tests required for all new features
- Must test success paths, failures, and permissions

## Frontend Stack & Conventions

### Core Stack
- Vue 3 + Composition API
- Pinia (state management)
- Axios (HTTP client)
- TailwindCSS (styling)
- TypeScript (preferred)
- Vite (build tooling)

### Testing
- **Unit:** Jest
- **E2E:** Cypress

### Module Structure

Each module must contain:
- `components/`
- `routes/`
- `store/`
- `services/`
- `types/`
- `tests/`

### Architecture
- **Atomic Design** (atoms → molecules → organisms → templates)
- Shared logic belongs in composables
- All imports must use the `@` alias

### UI / UX
- Minimal, modern aesthetic
- Fully responsive
- WCAG 2.1 compliant
- Dark + light mode required

## Getting Started

### Backend Setup

1. Navigate to the backend directory
2. Install dependencies with Pipenv:
   ```bash
   pipenv install
   ```
3. Activate the virtual environment:
   ```bash
   pipenv shell
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend/vuejs directory
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5174 and the backend at http://localhost:8000.

## Design Principles

When building with or contributing to Imagi:

- **Treat users as builders and decision-makers**, not traditional developers
- **Translate rough ideas** into workable starting points
- **Encourage quick prototyping** while avoiding obviously fragile or unsafe designs
- **Favor straightforward structures** that future engineers can understand and extend
- **Reduce friction, setup time, and cognitive load** wherever possible
- When trade-offs exist, **default toward what accelerates early progress** without blocking future growth

## License

See the [LICENSE](LICENSE) file for details.
