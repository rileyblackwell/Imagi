---
trigger: always_on
description: 
globs: 
---

# Your rule content

Local Development:
	•	Backend: Django with SQLite3, managed using Pipenv, running via Django’s development server.
	•	Frontend: Vue.js with Vite development server.
	
Staging & Production:
	•	Backend:
	•	Database: PostgreSQL
	•	Deployment: Django backend served via Gunicorn (potential for Uvicorn if adopting async capabilities)
	•	Frontend:
	•	Deployment: Vue.js app built via vite build and served as static files using Nginx.
	•	Hosting Provider: Railway.com
	•	Separate Docker images for frontend and backend.
	•	Separate Railway services communicating over Railway’s private network.

Future Enhancements:
	•	Container orchestration and scaling via Kubernetes.
  
- You can @ files here
- You can use markdown but dont have to
