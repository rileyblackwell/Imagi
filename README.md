# Imagi Oasis

Imagi Oasis is an AI-powered web application generator that enables users to build full-stack web applications using natural language.

## Company Overview
- **Product**: Imagi Oasis - AI-powered web application generator
- **Mission**: Enable users to build full-stack web applications using natural language
- **Target Users**: Developers and technical users requiring rapid application development

## Tech Stack

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

## Project Structure

### Frontend Apps (Vue.js)
- **Authentication**: Handles user login, registration, and password management.
- **Builder**: AI-powered application generator with two modes:
  - **Chat Mode**: Conversational interface for generating applications.
  - **Build Mode**: Visual interface for building applications.
- **Dashboard**: Manages projects and settings.
- **Editor**: Provides a code editor and file management capabilities.
- **Preview**: Allows live preview of the application being built.

### Backend Apps (Django)
- **auth**: Manages custom authentication and authorization.
- **builder**: Contains the core AI generation logic and prompt handling.
- **home**: Manages landing pages and static content.
- **payments**: Integrates Stripe for handling API credits.
- **agents**: Manages AI workflows and interactions.
- **project_manager**: Handles the lifecycle of projects, including creation, updates, and deletion.

## Development Environment
- **OS**: macOS (zsh)
- **Package Managers**: 
  - Frontend: npm/yarn
  - Backend: pipenv
- **Required Tools**:
  - Node.js >= 16.x
  - Python >= 3.10
  - PostgreSQL >= 14
- **Editor Setup**:
  - VSCode/Cursor with provided settings
  - Tailwind CSS IntelliSense
  - Python and Vue.js extensions

## Imagi Design Principles
- **User Interface**:
  - Clean, minimalist design
  - Responsive layouts
  - Accessible components (WCAG 2.1)
  - Dark/light mode support
- **Code Style**:
  - Python: Black formatter, 88 char line length
  - JavaScript: Prettier, 80 char line length
  - Clear comments and documentation
  - Type hints (Python) and TypeScript
- **Architecture**:
  - RESTful API design
  - Modular components
  - Atomic design patterns
  - State management best practices

## Getting Started

### Prerequisites
- Node.js >= 16.x
- Python >= 3.10
- PostgreSQL >= 14

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/imagi-oasis.git
    cd imagi-oasis
    ```

2. Set up the backend:
    ```sh
    cd backend/django
    pipenv install
    pipenv shell
    python manage.py migrate
    python manage.py runserver
    ```

3. Set up the frontend:
    ```sh
    cd frontend/vuejs
    npm install
    npm run dev
    ```

### Running Tests

- Backend tests:
    ```sh
    cd backend/django
    pytest
    ```

- Frontend tests:
    ```sh
    cd frontend/vuejs
    npm run test
    ```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](http://_vscodecontentref_/1) file for details.