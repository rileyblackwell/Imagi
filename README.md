Imagi Oasis

Imagi Oasis is an AI-powered full-stack web application generator. Rapidly build production-grade Django/Vue apps using natural language prompts—no manual coding required.

🚀 Company Overview
	•	Product: Imagi Oasis - AI-powered Django web application generator
	•	Mission: Enable users to build full-stack web applications using natural language - no coding required
	•	Target Users: Entrepreneurs, creators, and developers requiring rapid application development
	•	Value Proposition: Create beautiful web apps in minutes for just a few dollars—not thousands

⸻

🛠️ Tech Stack

Frontend
	•	Framework: Vue.js 3.4+ (Composition API)
	•	State Management: Pinia 2.1+
	•	HTTP Client: Axios 1.6+
	•	Styling: TailwindCSS 3.4+
	•	UI Components: HeadlessUI, HeroIcons
	•	Form Validation: VeeValidate 4.15+
	•	Animations: GSAP 3.12+
	•	Markdown: Marked 15.0+
	•	Security: DOMPurify
	•	Build Tools: Vite 6.2+, TypeScript 5.3+

Backend
	•	Framework: Django 4.x
	•	API: Django REST Framework
	•	Auth: Django-AllAuth
	•	CORS: Django-CORS-Headers
	•	AI Integration: OpenAI, Anthropic
	•	Payments: Stripe
	•	Database: PostgreSQL (Prod), SQLite (Dev)
	•	Server: Gunicorn, Whitenoise
	•	Security: python-dotenv
	•	Containerization: Docker

⸻

📁 Project Structure
	•	Frontend Apps (Vue.js)
	•	apps/ (auth, home, payments, products)
	•	shared/ (components, stores, layouts, composables, types, utils, assets)
	•	Backend Apps (Django)
	•	apps/ (Auth, Home, Payments, Products)
	•	api/ (v1 endpoints)

⸻

💻 Development Environment
	•	OS: macOS (zsh)
	•	Frontend: npm/yarn
	•	Backend: pipenv
	•	Editor: VSCode/Cursor

⸻

🎨 Key Features
	•	Build apps via natural language
	•	AI-assisted full-stack development
	•	Quick and cost-effective app creation
	•	Iterative, conversational refinement
	•	Built-in best practices for security and performance

⸻

🚀 Getting Started

Prerequisites
	•	Node.js (>= 16.x)
	•	Python (>= 3.10)
	•	PostgreSQL (>= 14)

Installation

git clone https://github.com/yourusername/imagi-oasis.git
cd imagi-oasis

# Backend Setup
cd backend/django
pipenv install
pipenv shell
cp .env.example .env

# Frontend Setup
cd ../../frontend/vuejs
npm install
cp .env.example .env

Run Development Servers

# Backend
cd backend/django
python manage.py migrate
python manage.py runserver

# Frontend
cd frontend/vuejs
npm run dev

Running Tests
	•	Backend: pipenv run pytest
	•	Frontend: npm run test (Jest), npm run test:e2e (Cypress)

⸻

🔄 Development & Production Architecture

This project follows a clean separation between development and production environments, controlled by a single `DJANGO_DEBUG` flag.

## Architecture Overview

### Development (Local)
```
┌─────────────────┐         ┌──────────────────┐
│  Vite Dev       │  /api/* │  Django          │
│  localhost:5174 ├────────►│  runserver:8000  │
│  (Proxy)        │         │  (Local only)    │
└─────────────────┘         └──────────────────┘
```

### Production (Railway)
```
┌─────────────────┐         ┌──────────────────┐
│  NGINX          │  /api/* │  Gunicorn        │
│  (Public)       ├────────►│  (Private)       │
│  Static Files   │         │  Django WSGI     │
└─────────────────┘         └──────────────────┘
```

## Development Environment

### Backend
- **Server**: Django development server (`python manage.py runserver`)
- **Port**: `8000`
- **Network**: Local machine only
- **Toggle**: Set `DJANGO_DEBUG=1` or `DJANGO_DEBUG=true`

### Frontend
- **Server**: Vite dev server with HMR
- **Port**: `5174`
- **Proxy**: `/api/*` → `http://localhost:8000` (configurable via `VITE_BACKEND_URL`)
- **Network**: Local machine only

### Running Locally

```bash
# Backend (Terminal 1)
cd backend/django
export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY="dev-secret-key"
python manage.py migrate
python manage.py runserver

# Frontend (Terminal 2)
cd frontend/vuejs
npm run dev
# Visit http://localhost:5174
```

## Production Environment (Railway)

### Backend Service
- **Server**: Gunicorn WSGI server (3 workers, 2 threads)
- **Port**: `8000` (internal only)
- **Network**: Railway private network (`backend.railway.internal:8000`)
- **Toggle**: Set `DJANGO_DEBUG=0` (default)
- **Dockerfile**: `backend/django/Dockerfile`
- **Entrypoint**: `/usr/local/bin/run-server.sh`

### Frontend Service
- **Server**: NGINX
- **Port**: `80` (public)
- **Proxy**: `/api/*` → `http://backend.railway.internal:8000`
- **Static Files**: Serves built Vue.js app from `/usr/share/nginx/html`
- **Dockerfile**: `frontend/vuejs/Dockerfile`
- **Entrypoint**: `/usr/local/bin/entrypoint.sh` (substitutes `BACKEND_URL` into NGINX config)

### Railway Environment Variables

#### Backend Service
```bash
# Required
DJANGO_SECRET_KEY=<your-secret-key>
DJANGO_DEBUG=0
DATABASE_URL=<postgresql-url>
OPENAI_KEY=<your-openai-key>
ANTHROPIC_KEY=<your-anthropic-key>
STRIPE_SECRET_KEY=<your-stripe-secret>
STRIPE_PUBLIC_KEY=<your-stripe-public>

# Optional
FRONTEND_URL=https://your-frontend.railway.app
FRONTEND_REDIRECT_ENABLED=true
```

#### Frontend Service
```bash
# Required
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}

# Optional
VITE_STRIPE_PUBLISHABLE_KEY=<your-stripe-public>
```

## Key Configuration Files

### Backend
- `backend/django/Imagi/settings.py` - Django settings (uses `DJANGO_DEBUG` flag)
- `backend/django/scripts/run-server.sh` - Startup script (switches between runserver/Gunicorn)
- `backend/django/Dockerfile` - Production container
- `backend/django/railway.json` - Railway deployment config

### Frontend
- `frontend/vuejs/vite.config.ts` - Vite dev proxy (uses `VITE_BACKEND_URL`)
- `frontend/vuejs/nginx.conf` - NGINX reverse proxy config
- `frontend/vuejs/scripts/entrypoint.sh` - Runtime NGINX config substitution
- `frontend/vuejs/Dockerfile` - Production container
- `frontend/vuejs/railway.json` - Railway deployment config
- `frontend/vuejs/src/shared/services/api.ts` - Centralized API client (uses relative `/api` URLs)

## API Client Architecture

The frontend uses **relative URLs** for all API calls, which works seamlessly in both environments:

```typescript
// frontend/vuejs/src/shared/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',  // Relative URL - no hardcoded backend URL
  withCredentials: true
})

// Usage
import api from '@/shared/services/api'
const response = await api.get('/v1/projects/')
```

### How It Works
- **Development**: Vite proxy intercepts `/api/*` and forwards to `http://localhost:8000`
- **Production**: NGINX intercepts `/api/*` and forwards to `http://backend.railway.internal:8000`
- **Browser**: Always calls same-origin `/api/*` (no CORS issues, no mixed content warnings)

## Environment Toggle Behavior

The `DJANGO_DEBUG` flag controls:

| Aspect | Development (`DJANGO_DEBUG=1`) | Production (`DJANGO_DEBUG=0`) |
|--------|-------------------------------|------------------------------|
| Backend Server | Django `runserver` | Gunicorn WSGI |
| Django Checks | `manage.py check` | `manage.py check --deploy` |
| Static Files | Not collected | `collectstatic` runs |
| Security | Relaxed (HTTP, insecure cookies) | Strict (HTTPS, secure cookies) |
| CORS | `localhost:5174` | `*.railway.app` |
| Debug Toolbar | Enabled | Disabled |
| AI/Stripe Keys | Optional (warnings only) | Required (validation enforced) |
| Database | SQLite (default) | PostgreSQL (via `DATABASE_URL`) |

## Important Notes

1. **All network calls are local in development**
   - Backend: `localhost:8000`
   - Frontend: `localhost:5174`
   - No external services required

2. **Production uses internal networking**
   - Browser never calls backend directly
   - NGINX proxies all `/api/*` requests
   - Backend is not publicly accessible

3. **Single source of truth: `DJANGO_DEBUG`**
   - Controls both Django settings and server behavior
   - Use `1`, `true`, `True`, `yes`, or `Yes` for development
   - Use `0`, `false`, `False`, `no`, or `No` for production

4. **CSRF Tokens**
   - Required in both environments
   - Handled automatically by the API client
   - Uses cookie-based tokens

⸻

Troubleshooting

## Common Issues

### "Network Error: Unable to connect to server"
- Check that proxying is properly configured
- Verify CORS settings in Django
- Ensure relative URLs are being used

### "CSRF token missing or incorrect"
- Check that cookies are being sent with requests
- Verify CSRF_TRUSTED_ORIGINS includes your domain
- Ensure CSRF_COOKIE_SAMESITE and CSRF_COOKIE_SECURE are properly configured

### "HTML response instead of JSON"  
- Usually indicates a proxy configuration issue
- Check Nginx configuration
- Verify backend service is running and accessible

## Debugging
- **Development**: Check Vite proxy logs in terminal
- **Production**: Check Nginx logs and Railway service logs

⸻

🤝 Contributing

Follow guidelines in CONTRIBUTING.md

📜 License

MIT License. See LICENSE.

🌎 Connect With Us
	•	Website: imagi-oasis.com
	•	GitHub: github.com/yourusername/imagi-oasis