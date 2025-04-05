# Imagi Oasis

Imagi Oasis is an **AI-powered web application generator** that enables users to build full-stack web applications using natural language.

## 🚀 Company Overview
- **Product**: Imagi Oasis - AI-powered web application generator
- **Mission**: Enable users to build full-stack web applications using natural language
- **Target Users**: Developers and technical users requiring rapid application development

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Vue.js 3 with Composition API
- **State Management**: Pinia
- **HTTP Client**: Axios
- **UI/Styling**: TailwindCSS
- **Testing**: Jest, Cypress
- **Build Tools**: Vite

### Backend
- **Framework**: Django 4.x
- **API**: Django REST Framework
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Testing**: pytest
- **Authentication**: Django built-in + DRF auth
- **API Version**: `/api/v1/`

---

## 📁 Project Structure

### **Frontend Apps (Vue.js)**
Each app module is self-contained with:
- Components (following Atomic Design principles)
- Routes
- Store
- Services
- Types
- Tests

The Atomic Design structure includes:
1. **Atoms**: Basic building blocks (buttons, inputs, icons, text)
2. **Molecules**: Simple combinations of atoms (form fields, cards, menu items)
3. **Organisms**: Complex combinations of molecules (forms, headers, feature grids)
4. **Templates**: Page-level components and layouts
5. **Pages**: Specific instances of templates with logic and routing

### **Backend Apps (Django)**
- **auth**: Manages authentication and authorization
- **builder**: Contains core AI generation logic and prompt handling
- **home**: Handles landing pages and static content
- **payments**: Integrates Stripe for managing API credits
- **agents**: Handles AI workflows and interactions
- **project_manager**: Manages project lifecycle (creation, updates, deletion)

---

## 💻 Development Environment

### **System Requirements**
- **OS**: macOS (zsh)
- **Package Managers**: 
  - Frontend: npm/yarn
  - Backend: pipenv
- **Required Tools**:
  - Node.js >= 16.x
  - Python >= 3.10
  - PostgreSQL >= 14
- **Editor Setup**:
  - VSCode / Cursor with recommended extensions:
    - Tailwind CSS IntelliSense
    - Python and Vue.js extensions

---

## 🎨 Imagi Design Principles

### **User Interface**
- Clean, minimalist, modern UI inspired by Stripe, Airbnb, Apple, Twilio
- Responsive layouts using Tailwind utility classes
- Accessible components (**WCAG 2.1** compliance)
- Dark/light mode support

### **Code Style**
- **Python**: Black formatter, 88-character line length
- **JavaScript**: Prettier, 80-character line length
- Clear comments and documentation
- Type hints (**Python**) and TypeScript (**Vue.js**)

### **Architecture**
- **RESTful API** design
- **Modular Components** (Atomic Design Pattern)
- **State Management Best Practices** (Pinia for Vue.js)
- **AI-Powered Code Generation** (Backend AI Agents)

---

## 🚀 Getting Started

### **Prerequisites**
Ensure the following are installed:
- **Node.js** (>= 16.x)
- **Python** (>= 3.10)
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

## 🧪 Running Tests

### **Backend Tests**
```sh
cd backend/django
pytest
```

### **Frontend Tests**
```sh
cd frontend/vuejs
npm run test
```

## 🛡️ Testing Strategy
### Frontend (Vue.js)
- **Unit Tests**: Jest for testing Vue components
- **E2E Tests**: Cypress for end-to-end testing

### Backend (Django)
- **Unit Tests**: pytest for testing models, views, and APIs
- **Integration Tests**: Ensure API endpoints work as expected

**Test Coverage Targets:**
- Authentication & Authorization: 90%+
- API Endpoints: 80%+
- UI Components: 75%+

---

## 🔄 Deployment Considerations
- **Local Development**: SQLite, pipenv, Vite
- **Staging & Production**:
  - Database: PostgreSQL
  - API Deployment: Django on Gunicorn/Uvicorn
  - Frontend Deployment: Vite build, hosted on CDN
  - Future Enhancements: Docker & Kubernetes for scaling

---

## 🤝 Contributing
We welcome contributions! Please follow the guidelines in CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🌎 Connect With Us
For updates and community discussions:

- Website: imagi-oasis.com
- GitHub: github.com/yourusername/imagi-oasis
- Discord: Join Our Community

