# Frontend build stage
FROM node:20-slim as frontend-builder

# Build-time arguments for frontend
ARG VITE_API_URL
ARG VITE_STRIPE_PUBLISHABLE_KEY

# Set frontend environment variables
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_STRIPE_PUBLISHABLE_KEY=${VITE_STRIPE_PUBLISHABLE_KEY}
ENV NODE_OPTIONS="--max-old-space-size=2048"
ENV NODE_ENV=production

WORKDIR /app/frontend
COPY frontend/vuejs/package*.json ./
RUN npm install

# Copy and build frontend
COPY frontend/vuejs/ .
RUN npm run build

# Backend stage
FROM python:3.11-slim

# Runtime environment variables
ARG OPENAI_KEY
ARG ANTHROPIC_KEY
ARG STRIPE_PUBLIC_KEY
ARG STRIPE_SECRET_KEY
ARG SECRET_KEY

ENV OPENAI_KEY=${OPENAI_KEY}
ENV ANTHROPIC_KEY=${ANTHROPIC_KEY}
ENV STRIPE_PUBLIC_KEY=${STRIPE_PUBLIC_KEY}
ENV STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
ENV SECRET_KEY=${SECRET_KEY}
ENV DJANGO_SETTINGS_MODULE=Imagi.settings
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

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

# Expose ports
EXPOSE 8000 5173

CMD ["/app/start.sh"]
