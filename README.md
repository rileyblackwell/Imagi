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
- **Authentication**: Handles user login, registration, and password management.
- **Builder**: AI-powered application generator with two modes:
  - **Chat Mode**: Conversational interface for generating applications.
  - **Build Mode**: Visual interface for building applications.
- **Dashboard**: Manages user projects and settings.
- **Editor**: Provides a code editor and file management capabilities.
- **Preview**: Allows live preview of the application being built.

### **Backend Apps (Django)**
- **auth**: Manages authentication and authorization.
- **builder**: Contains core AI generation logic and prompt handling.
- **home**: Handles landing pages and static content.
- **payments**: Integrates Stripe for managing API credits.
- **agents**: Handles AI workflows and interactions.
- **project_manager**: Manages project lifecycle (creation, updates, deletion).

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
- Clean, minimalist design
- Responsive layouts
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
    python manage.py migrate
    python manage.py runserver
    ```

3. **Set up the frontend**:
    ```sh
    cd frontend/vuejs
    npm install
    npm run dev
    ```

---

## 🧪 Running Tests

### **Backend Tests**
```sh
cd backend/django
pytest
cd frontend/vuejs
npm run test

🤝 Contributing
We welcome contributions! Please follow the guidelines in CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

🌎 Connect With Us
For updates and community discussions:

Website: imagi-oasis.com
GitHub: github.com/yourusername/imagi-oasis
Discord: Join Our Community


---

### **What’s Updated?**
✅ **Improved Readability** – Sections are clearer with structured headings.  
✅ **Better Formatting** – Uses icons/emojis for easy navigation.  
✅ **Additional Details** – Adds a **Connect With Us** section for future community growth.  
✅ **More Organized Instructions** – **Installation & Setup** and **Running Tests** sections are now structured for clarity.  

This version makes the **README** **more user-friendly and professional** while maintaining clarity and usability for **Imagi Oasis** developers. 🚀

