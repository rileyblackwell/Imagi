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

🔄 Deployment & API Architecture

## Development Environment
- **Frontend**: Vite dev server on `http://localhost:5174`
- **Backend**: Django dev server on `http://localhost:8000`
- **Proxying**: Vite dev server proxies `/api/*` requests to `VITE_BACKEND_URL`
- **Environment Variable**: `VITE_BACKEND_URL=http://localhost:8000`

## Production Environment
- **Frontend**: Nginx serving static files from `https://imagi.up.railway.app`
- **Backend**: Django + Gunicorn on Railway internal network `http://backend.railway.internal:8000`
- **Proxying**: Nginx proxies `/api/*` requests to backend service
- **Environment Variable**: `VITE_BACKEND_URL` is **not used** in production (relative URLs only)

## Key Configuration Files

### Frontend
- `frontend/vuejs/vite.config.ts` - Development proxy configuration
- `frontend/vuejs/Dockerfile` - Production build and deployment with inline Nginx config
- `frontend/vuejs/src/shared/services/api.ts` - API client using relative URLs

### Backend
- `backend/django/Imagi/settings.py` - CORS and CSRF configuration
- Django handles both development and production with different settings

## Railway Deployment

### Frontend Service
```bash
# Uses frontend/vuejs/Dockerfile
# Builds Vue.js app and serves with Nginx
# Proxies /api/* to backend.railway.internal:8000
```

### Backend Service  
```bash
# Uses Python buildpack or custom Dockerfile
# Runs Django + Gunicorn
# Accessible at backend.railway.internal:8000 (internal network only)
```

## Centralized API Client

Use relative URLs for API requests:

```javascript
import api from '@/shared/services/api'
const response = await api.get('/api/v1/projects/')
```

## Important Notes

1. **Never set `VITE_BACKEND_URL` to `backend.railway.internal:8000` in production**
   - Browsers cannot access Railway's internal network
   - Use Nginx proxying instead

2. **Always use relative URLs in frontend code**
   - Development: Vite proxy handles routing
   - Production: Nginx proxy handles routing

3. **CORS Configuration**
   - Development: Allow `localhost:5174`
   - Production: Allow `imagi.up.railway.app`
   - Backend also allows Railway internal origins for service-to-service communication

4. **CSRF Tokens**
   - Required in both development and production
   - Handled automatically by the API client
   - Uses cookie-based CSRF tokens

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