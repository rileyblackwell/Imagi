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
frontend/vuejs/ ├── src/ │ ├── apps/ # Feature-specific applications │ │ ├── home/ # Landing pages and public content │ │ ├── auth/ # Authentication and user management │ │ ├── payments/ # Subscription and billing management │ │ └── builder/ # AI application builder │ └── shared/ # Shared resources │ ├── components/ # Reusable components │ ├── layouts/ # Layout templates │ ├── stores/ # Shared state management │ ├── utils/ # Utility functions │ └── composables/# Vue composables


Each app module should be self-contained with its own:
- Components
- Routes
- Store
- Services
- Types
- Tests

### Frontend Apps
- **Home**: Landing pages, documentation, and public content
- **Auth**: User authentication, registration, profile management
- **Payments**: Subscription plans, billing, usage tracking
- **Builder**: AI-powered application generator
  - Chat Mode: Conversational interface
  - Build Mode: Visual interface

Each frontend app should follow atomic design principles:
- **Atoms**: Basic building blocks (buttons, inputs, icons, text)
- **Molecules**: Simple combinations of atoms (form fields, cards, menu items)
- **Organisms**: Complex combinations of molecules (forms, headers, feature grids)
- **Templates**: Page-level components and layouts
- **Pages**: Specific instances of templates

**Guidelines:**
- Keep each component in its designated category (`atoms/`, `molecules/`, etc.).
- Maintain a clear separation of concerns—higher-level components compose lower-level components.
- Prefer the **Composition API** over the Options API for reusable logic.
- Use **TypeScript** where applicable for better type safety.
- **All Vue.js imports should use the `@` symbol to alias the `src` directory**.

### Component directory structure:

app/ └── components/ ├── atoms/ # Basic building blocks │ ├── buttons/ │ ├── inputs/ │ ├── text/ │ └── icons/ ├── molecules/ # Simple combinations │ ├── cards/ │ ├── forms/ │ └── navigation/ ├── organisms/ # Complex combinations │ ├── sections/ │ ├── grids/ │ └── forms/ └── templates/ # Page-level layouts └── layout/


### Shared Directory Structure

shared/ # Global shared resources ├── components/ # Reusable UI components (follows atomic design) │ ├── atoms/ # Base components (buttons, inputs, icons) │ ├── molecules/ # Combined atoms (form fields, cards) │ ├── organisms/ # Complex components (forms, headers) │ └── templates/ # Layout templates ├── layouts/ # Base page layouts (Base, Auth, Dashboard) ├── stores/ # Global state management ├── utils/ # Helper functions and constants ├── composables/ # Reusable Vue.js logic └── types/ # TypeScript definitions


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
  - Atomic design pattern for Vue.js components
    - Clear separation between atoms, molecules, and organisms
    - Components should be reusable and maintainable
    - Higher-level components should compose lower-level ones
    - Each component category should have a clear responsibility
  - Modular component structure
  - State management best practices

## AI Assistant Instructions
- Use `task:` prefix for specific generation tasks
- Use `study:` prefix for documentation/learning tasks
- Follow type hints and documentation standards
- Generate complete, self-contained files
- Include relevant tests with new features
- Follow established naming conventions
