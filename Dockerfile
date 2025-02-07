# Frontend build stage
FROM node:20-slim as frontend-builder

# Set Node.js memory limits and optimization flags
ENV NODE_OPTIONS="--max-old-space-size=4096" \
    NODE_ENV=production

WORKDIR /app/frontend

# Install dependencies first
COPY frontend/vuejs/package*.json ./
RUN npm ci && \
    npm install -g vite@latest

# Copy and build frontend
COPY frontend/vuejs/ .
RUN vite build

# Python dependencies stage
FROM python:3.11-slim as python-deps

WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev && \
    pip install --no-cache-dir pipenv

COPY backend/django/Pipfile backend/django/Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile && \
    apt-get remove -y gcc python3-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Final stage
FROM python:3.11-slim

# Runtime environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DEBUG=0

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -s /bin/bash appuser && \
    mkdir -p /app/backend/staticfiles /app/backend/static && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy only necessary files from previous stages
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist
COPY backend/django/ ./backend/

USER appuser

# Setup runner script
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
python manage.py collectstatic --no-input\n\
python manage.py migrate --no-input\n\
exec gunicorn Imagi.wsgi:application --bind "0.0.0.0:$PORT" --workers 3 --threads 2\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]
