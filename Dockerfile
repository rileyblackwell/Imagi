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

# Install production-only system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash appuser && \
    mkdir -p /app/backend/staticfiles /app/backend/static && \
    chown -R appuser:appuser /app

WORKDIR /app

# Install Python dependencies
COPY backend/django/Pipfile backend/django/Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --ignore-pipfile

# Copy application code
COPY backend/django/ ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

# Switch to non-root user
USER appuser

# Setup runner script (removed npm commands)
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
python manage.py collectstatic --no-input\n\
python manage.py migrate --no-input\n\
exec gunicorn Imagi.wsgi:application --bind "0.0.0.0:$PORT" --workers 3 --threads 2\n\
' > /app/start.sh && chmod +x /app/start.sh

# Only expose Django port
EXPOSE 8000

CMD ["/app/start.sh"]
