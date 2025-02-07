# Imagi Platform Development Guidelines

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
### Root Directory
```
Imagi/
├── frontend/vuejs/     # Vue.js application
├── backend/django/     # Django application
├── docs/              # Documentation
└── scripts/           # Deployment/utility scripts
```

### Frontend Apps (Vue.js)
- **Authentication**: User login, registration, password management
- **Builder**: AI-powered application generator
  - Chat Mode: Conversational interface
  - Build Mode: Visual interface
- **Dashboard**: Project management and settings
- **Editor**: Code editor and file management
- **Preview**: Live application preview

### Backend Apps (Django)
- **auth**: Custom authentication and authorization
- **builder**: Core AI generation logic and prompts
- **home**: Landing pages and static content
- **payments**: Stripe integration for API credits
- **agents**: AI workflow management
- **project_manager**: Project lifecycle handling

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

## AI Assistant Instructions
- Use `task:` prefix for specific generation tasks
- Use `study:` prefix for documentation/learning tasks
- Follow type hints and documentation standards
- Generate complete, self-contained files
- Include relevant tests with new features
- Follow established naming conventions
