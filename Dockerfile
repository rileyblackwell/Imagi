# Build stage for Vue.js frontend
FROM node:20-slim as frontend-builder

# Set Node.js memory limits and optimization flags
ENV NODE_OPTIONS="--max-old-space-size=2048"
ENV VITE_BUILD_LEGACY=false
ENV NODE_ENV=production

WORKDIR /app/frontend/vuejs

# Copy package files
COPY frontend/vuejs/package*.json ./

# Install build essentials for node-gyp with better cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies with specific npm settings for optimization
RUN npm config set fetch-retries 3 && \
    npm config set fetch-retry-mintimeout 5000 && \
    npm config set fetch-retry-maxtimeout 60000 && \
    npm install && \
    npm install vite@^5.0.12 @vitejs/plugin-vue@^5.0.3 && \
    npm ls vite

# Copy Vue.js source code and configuration files
COPY frontend/vuejs/ .

# Build frontend with production mode and better error handling
RUN NODE_ENV=production npx vite build || (echo "Build failed. Check the error above." && exit 1)

# Final stage for Django backend and serving frontend
FROM python:3.11-slim-bullseye

# Set Python-related environment variables for optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONMALLOC=malloc \
    MALLOC_TRIM_THRESHOLD_=65536

# Install system dependencies with better cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    curl \
    libjpeg-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install pip and pipenv with memory optimization and better error handling
RUN pip install --no-cache-dir --upgrade pip && \
    for i in 1 2 3; do \
        pip install --no-cache-dir pipenv && break || \
        { echo "Retry pip install $i..."; sleep 15; }; \
    done

# Copy Pipfile and install Python dependencies
COPY backend/django/Pipfile backend/django/Pipfile.lock ./
RUN for i in 1 2 3; do \
        PIPENV_NOSPIN=1 PIPENV_HIDE_EMOJIS=1 \
        pipenv install --system --deploy --verbose && break || \
        { echo "Retry pipenv install $i..."; sleep 15; }; \
    done

# Copy Django backend code
COPY backend/django/ ./backend/

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/vuejs/dist ./frontend/dist/

# Create directory for static files
RUN mkdir -p /app/backend/staticfiles

# Create and configure the runner script
RUN printf "#!/bin/bash\n" > /app/runner.sh && \
    printf "cd /app/backend\n" >> /app/runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n" >> /app/runner.sh && \
    printf "python manage.py migrate --no-input\n" >> /app/runner.sh && \
    printf "python manage.py collectstatic --no-input\n" >> /app/runner.sh && \
    printf "exec gunicorn Imagi.wsgi:application --bind \"0.0.0.0:\$RUN_PORT\" --workers 3 --threads 2\n" >> /app/runner.sh && \
    chmod +x /app/runner.sh

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=Imagi.settings
ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
ARG DJANGO_DEBUG=0
ENV DJANGO_DEBUG=${DJANGO_DEBUG}

# Expose the port
EXPOSE 8000

# Run the application
CMD ["/app/runner.sh"]
