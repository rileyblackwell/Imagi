---
description: Defines the frontend technology stack, architectural patterns, UI/UX principles, and testing standards for the Imagi Oasis Vue.js application.
globs:
  - "frontend/**"
alwaysApply: true
---

# Vue.js Frontend Rules — Imagi Oasis

## Frontend Stack

- **Framework**: Vue.js 3 (Composition API)  
- **State Management**: Pinia  
- **HTTP Client**: Axios  
- **UI / Styling**: TailwindCSS  
- **Testing**
  - Unit: Jest  
  - End-to-End: Cypress  
- **Build Tooling**: Vite  

---

## Module Structure

Each frontend app module must be fully self-contained and include:

- `components/`  
- `routes/`  
- `store/`  
- `services/`  
- `types/`  
- `tests/`  

---

## Code Architecture

### Atomic Design (Vue.js)

1. **Atoms** — Buttons, inputs, icons, text primitives  
2. **Molecules** — Form fields, cards, menu items  
3. **Organisms** — Forms, headers, feature grids  
4. **Templates** — Page-level components and layouts  

### Engineering Guidelines

- Prefer the **Composition API** for all new components.
- Use **TypeScript** wherever practical for improved safety and maintainability.
- **All imports must use the `@` alias for the `src` directory.**
- Shared logic belongs in composables, not components.

---

## UI / UX Principles

- **Minimalist, modern aesthetic** inspired by Stripe, Airbnb, Apple, and Twilio.
- Fully **responsive layouts** using Tailwind utility classes.
- Must meet **WCAG 2.1 accessibility standards**.
- Support **dark and light modes** across all UI surfaces.

---

## Testing Strategy

### Frontend (Vue.js)

- **Unit Tests**
  - Use **Jest** to test components, composables, and stores.

- **End-to-End Tests**
  - Use **Cypress** to validate complete user flows.

- All new UI features must include:
  - Unit tests for logic
  - At least one E2E test covering the happy path

---

You may reference files using `@file-path` syntax where supported.  
Markdown formatting is allowed but optional.