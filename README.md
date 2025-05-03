# Imagi Oasis

Imagi Oasis is an **AI-powered web application generator** that enables users to build full-stack Django web applications using natural language.

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
  - **builder/**: AI-powered application generation
  - **payments/**: Stripe integration and subscription management
  - **project_manager/**: Project lifecycle handling

- **shared/**: Reusable components and utilities
  - **components/**: Following Atomic Design principles
    - **atoms/**: Basic UI elements
    - **molecules/**: Compound components
    - **organisms/**: Complex UI sections
    - **pages/**: Complete page templates
  - **stores/**: Pinia state management
  - **layouts/**: Layout components
  - **composables/**: Vue.js composable functions
  - **types/**: TypeScript type definitions
  - **utils/**: Helper functions
  - **assets/**: Static assets

### **Backend Apps (Django)**
- **apps/**
  - **auth/**: Custom authentication and authorization
  - **builder/**: Core AI generation logic and prompts
  - **home/**: Landing pages and static content
  - **payments/**: Stripe integration for API credits
  - **agents/**: AI workflow management
  - **project_manager/**: Project lifecycle handling
- **api/**: REST API endpoints
  - **v1/**: API version 1 endpoints

---

## 💻 Development Environment

### **System Requirements**
- **OS**: macOS (zsh)
- **Package Managers**: 
  - Frontend: npm
  - Backend: pipenv
- **Required Tools**:
  - Node.js >= 16.x
  - Python >= 3.13
  - PostgreSQL >= 14
- **Editor Setup**:
  - VSCode / Cursor with recommended extensions:
    - Tailwind CSS IntelliSense
    - Python and Vue.js extensions

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

### **Prerequisites**
Ensure the following are installed:
- **Node.js** (>= 16.x)
- **Python** (>= 3.13)
- **PostgreSQL** (>= 14)

### **Installation & Setup**

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/imagi-oasis.git
    cd imagi-oasis
    ```

2. **Set up the backend**:
    ```sh
    cd backend/django
    pipenv install
    pipenv shell
    ```

3. **Create a .env file in the Django root directory with the following variables**:
    ```
    OPENAI_KEY=your_openai_api_key
    ANTHROPIC_KEY=your_anthropic_api_key
    SECRET_KEY=your_django_secret_key
    STRIPE_PUBLIC_KEY=your_stripe_public_key
    STRIPE_SECRET_KEY=your_stripe_secret_key
    FRONTEND_URL=http://localhost:5174
    FRONTEND_REDIRECT_ENABLED=true
    ```

4. **Run the database migrations and start the server**:
    ```sh
    python manage.py migrate
    python manage.py runserver
    ```

5. **Set up the frontend**:
    ```sh
    cd frontend/vuejs
    npm install
    ```

6. **Create a .env file in the Vue.js root directory with the following variables**:
    ```
    VITE_API_URL=http://localhost:8000
    VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
    ```

7. **Start the frontend development server**:
    ```sh
    npm run dev
    ```

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

