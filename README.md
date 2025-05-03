# Imagi Oasis

Imagi Oasis is an **AI-powered web application generator** that enables users to build full-stack web applications using natural language.

## 🚀 Company Overview
- **Product**: Imagi Oasis - AI-powered web application generator
- **Mission**: Enable users to build full-stack web applications using natural language
- **Target Users**: Developers and technical users requiring rapid application development

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
  - **products/**: Product listings and details

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
  - **Auth/**: Authentication and user management
  - **Home/**: Content for landing pages
  - **Payments/**: Stripe integration and subscription handling
  - **Products/**: Product information and management
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

## 🎨 Imagi Design Principles

### **User Interface**
- Clean, minimalist, modern UI using HeadlessUI and HeroIcons
- Responsive layouts using Tailwind utility classes
- Accessible components (**WCAG 2.1** compliance)
- Dark/light mode support
- Rich animations with GSAP

### **Code Style**
- **Frontend**: ESLint, Prettier with standardized configuration
- **Backend**: Uses Django's standard code style
- Type safety with TypeScript for frontend
- Security measures including DOMPurify for sanitizing

### **Architecture**
- **RESTful API** design
- **Modular Components** (Atomic Design Pattern)
- **State Management** with Pinia
- **AI Integration** with OpenAI and Anthropic

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

## 🧪 Testing

### **Frontend Tests**
```sh
cd frontend/vuejs
npm run type-check   # Run TypeScript type checking
npm run lint         # Run ESLint checks
```

### **Backend Tests**
Testing infrastructure is ready for implementation with Django's testing framework.

---

## 🔄 Deployment

### **Local Development**
- Backend: Django with SQLite
- Frontend: Vite development server (localhost:5174)
- API: Django development server (localhost:8000)

### **Production Deployment**
- **Containerization**: Docker configuration available for both frontend and backend
- **Frontend**: Built with Vite and served as static files
- **Backend**: Django served via Gunicorn
- **Static Files**: Served via WhiteNoise
- **Database**: PostgreSQL (configured for production)

---

## 🤝 Contributing
We welcome contributions! Please follow the guidelines in CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🌎 Connect With Us
For updates and community discussions:

- Website: imagi-oasis.com
- GitHub: github.com/yourusername/imagi-oasis

