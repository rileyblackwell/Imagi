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

🔄 Deployment

API Proxy Setup
	•	Development (Vite): Proxies API to http://localhost:8000
	•	Production (Nginx): Proxies API via internal Railway network

Centralized API Client

Use relative URLs for API requests:

import api from '@/shared/services/api'
const response = await api.get('/api/v1/projects/')

Proxy Configurations
	•	Vite (vite.config.ts)
	•	Nginx (Production)

Benefits
	•	Consistency, simplicity, security, flexibility, avoids CORS issues

⸻

Troubleshooting

Common Issues
	•	Check environment variables and proxy configurations

Debugging
	•	Development: Check Vite proxy logs
	•	Production: Check Nginx logs

⸻

🤝 Contributing

Follow guidelines in CONTRIBUTING.md

📜 License

MIT License. See LICENSE.

🌎 Connect With Us
	•	Website: imagi-oasis.com
	•	GitHub: github.com/yourusername/imagi-oasis