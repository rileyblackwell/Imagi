# Frontend build stage
FROM node:20-slim as frontend-builder
WORKDIR /app/frontend
COPY frontend/vuejs/package*.json ./
RUN npm install

# Copy and build frontend
COPY frontend/vuejs/ .
RUN npm run build

# Backend stage
FROM python:3.13-slim
WORKDIR /app

# Copy only dependency files first
COPY backend/django/Pipfile backend/django/Pipfile.lock ./

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && pip install pipenv \
    && pipenv install --system --deploy \
    && apt-get remove -y build-essential gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Then copy application code
COPY backend/django/ ./backend/
# Copy built frontend files
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# Create required directories
RUN mkdir -p /app/backend/staticfiles /app/backend/static

# Setup runner script
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
python manage.py collectstatic --no-input\n\
python manage.py migrate --no-input\n\
gunicorn Imagi.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2 &\n\
cd /app/frontend\n\
npm run preview -- --host 0.0.0.0 --port 5173\n\
' > /app/start.sh && chmod +x /app/start.sh

# Environment variables
ENV DJANGO_SETTINGS_MODULE=Imagi.settings
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

# Expose ports
EXPOSE 8000 5173

CMD ["/app/start.sh"]
