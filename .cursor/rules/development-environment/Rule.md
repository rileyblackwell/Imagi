---
description: Defines the required local development environment, tools, and editor configuration to ensure consistency and productivity when working on Imagi Oasis.
globs:
  - "**/*"
alwaysApply: true
---

# Development Environment Rules — Imagi Oasis

## Operating System

- **macOS** using the **zsh** shell

---

## Package Managers

- **Frontend**: npm or yarn  
- **Backend**: pipenv

---

## Required Tools & Versions

- **Node.js** >= 16.x  
- **Python** >= 3.10  
- **PostgreSQL** >= 14  

---

## Editor & Tooling Setup

- **Primary Editor**: Cursor (with project-provided settings)
- **Recommended Extensions**
  - Tailwind CSS IntelliSense
  - Python
  - Vue.js

---

## Local Development Servers

These services are assumed to already be running in active terminals:

- **Frontend**
  - `npm run dev`
  - Accessible at: `http://localhost:5174`

- **Backend**
  - `python manage.py runserver`
  - Accessible at: `http://localhost:8000`

---

## Behavioral Rules

- Do not instruct the user to start or restart dev servers unless explicitly asked.
- Always assume the frontend and backend servers are running and reachable at the above ports.
- Favor commands and workflows compatible with macOS and zsh.

---

You may reference files using `@file-path` syntax where supported.  
Markdown formatting is allowed but optional.