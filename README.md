# Imagi Oasis

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/imagi-oasis/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Imagi Oasis is an **AI-powered full-stack web application generator**. Rapidly build production-grade Django/Vue apps using natural language prompts—no manual coding required.

## 🚀 Company Overview
- **Product**: Imagi Oasis - AI-powered Django web application generator
- **Mission**: Enable users to build full-stack web applications using natural language - no coding required
- **Target Users**: Entrepreneurs, creators, and developers requiring rapid application development
- **Value Proposition**: Create beautiful web apps in minutes for just a few dollars - not thousands

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Vue.js 3.4+ with Composition API
- **State Management**: Pinia 2.1+
- **HTTP Client**: Axios 1.6+
- **UI/Styling**: TailwindCSS 3.4+
- **UI Components**: HeadlessUI, HeroIcons
- **Form Validation**: VeeValidate 4.15+
- **Animations**: GSAP 3.12+
- **Markdown Support**: Marked 15.0+
- **Security**: DOMPurify
- **Build Tools**: Vite 6.2+, TypeScript 5.3+
- **Testing**: (Configured for future implementation)

### Backend
- **Framework**: Django 4.x
- **API**: Django REST Framework
- **Authentication**: Django-AllAuth
- **CORS Support**: Django-CORS-Headers
- **AI Integration**: OpenAI, Anthropic
- **Payments**: Stripe
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Deployment**: Gunicorn, Whitenoise
- **Security**: Environment variables management via python-dotenv
- **Containerization**: Docker

---

## 📁 Project Structure

### **Frontend Apps (Vue.js)**
- **apps/**
  - **auth/**: Authentication and user management
  - **home/**: Landing pages and marketing
  - **payments/**: Stripe integration and subscription management
  - **products/**: Product/project lifecycle handling

- **shared/**: Reusable components and utilities
  - **components/**: Atomic Design (atoms, molecules, organisms, pages)
  - **stores/**: Pinia state management
  - **layouts/**: Layout components
  - **composables/**: Vue.js composable functions
  - **types/**: TypeScript type definitions
  - **utils/**: Helper functions
  - **assets/**: Static assets

### **Backend Apps (Django)**
- **apps/**
  - **Auth/**: Authentication and authorization
  - **Home/**: Landing pages and static content
  - **Payments/**: Stripe integration for API credits
  - **Products/**: Product and project management
- **api/**: REST API endpoints
  - **v1/**: API version 1 endpoints

---

## 💻 Development Environment

- **OS**: macOS (zsh)
- **Frontend**: npm/yarn
- **Backend**: pipenv
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Editor**: VSCode/Cursor (recommended extensions: Tailwind CSS IntelliSense, Python, Vue.js)
- **Local Servers**:
  - Frontend: `npm run dev` (localhost:5174)
  - Backend: `python manage.py runserver` (localhost:8000)

---

## 🎨 Key Features

- **No Coding Required**: Build web applications by describing what you want in plain English
- **AI-Powered Development**: Choose from various AI models to chat about or build your project
- **Build in Minutes, Not Months**: Create web apps that would take professional developers months
- **Pay Only for What You Use**: Buy AI credits and pay per request - just a few dollars instead of thousands
- **Simple Chat Interface**: Edit files through natural conversation with AI
- **Full-Stack Development**: Generate both frontend and backend code, complete with database structures
- **Iterative Refinement**: Continuously refine your application through conversation with our AI
- **Best Practices Built-in**: Industry standards for security, performance, and maintainability

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (>= 16.x)
- **Python** (>= 3.10)
- **PostgreSQL** (>= 14)

### Installation & Setup

1. **Clone the repository**
   ```sh
   git clone https://github.com/yourusername/imagi-oasis.git
   cd imagi-oasis
   ```

2. **Backend Setup**
   ```sh
   cd backend/django
   pipenv install
   pipenv shell
   cp .env.example .env  # Edit with your keys
   ```

3. **Frontend Setup**
   ```sh
   cd ../../frontend/vuejs
   npm install
   cp .env.example .env  # Edit with your API URL and Stripe key
   ```

4. **Database & Server**
   ```sh
   # In backend/django (pipenv shell)
   python manage.py migrate
   python manage.py runserver
   ```

5. **Frontend Dev Server**
   ```sh
   # In frontend/vuejs
   npm run dev
   ```

### Running Tests
- **Backend**: `cd backend/django && pipenv run pytest`
- **Frontend**: `cd frontend/vuejs && npm run test` (Jest) / `npm run test:e2e` (Cypress)

### Example API Usage
- Access API at `http://localhost:8000/api/v1/`
- Frontend served at `http://localhost:5174/`

---

## 🔄 Deployment

### **Local Development**
- Backend: Django with SQLite, managed using Pipenv, running via Django's development server
- Frontend: Vue.js with Vite development server (localhost:5174)
- API: Django development server (localhost:8000)

### **Production Deployment**
- **Containerization**: Docker configuration available for both frontend and backend
- **Frontend**: Built with Vite and served as static files using Nginx
- **Backend**: Django served via Gunicorn (potential for Uvicorn if adopting async capabilities)
- **Database**: PostgreSQL
- **Hosting Provider**: Railway.com
- **Architecture**: Separate Docker images for frontend and backend, separate Railway services communicating over Railway's private network

---

## 🤝 Contributing
We welcome contributions! Please follow the guidelines in CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🌎 Connect With Us
For updates and community discussions:

- Website: imagi-oasis.com
- GitHub: github.com/yourusername/imagi-oasis

