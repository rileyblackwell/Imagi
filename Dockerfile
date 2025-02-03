# Build stage for Vue.js frontend
FROM node:20-slim as frontend-builder

# Set Node.js memory limits and optimization flags
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV VITE_BUILD_LEGACY=false

WORKDIR /app/frontend
COPY frontend/vuejs/package*.json ./

# Install build essentials for node-gyp
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install ALL dependencies including devDependencies needed for build
RUN npm ci --legacy-peer-deps

COPY frontend/vuejs/ .

# Build with production mode (but we installed dev dependencies above)
ENV NODE_ENV=production
RUN npm run build || (cat /app/frontend/node_modules/vite/dist/node/chunks/dep-CHZK6zbr.js && exit 1)

# Final stage for Django and serving frontend
FROM python:3.11-slim-bullseye

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with retry logic and cleanup in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    build-essential \
    curl \
    libjpeg-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Node.js with retry logic
RUN for i in 1 2 3; \
    do curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && break || sleep 15; \
    done

# Set working directory
WORKDIR /app

# Install pip and pipenv with retry logic and memory optimization
RUN pip install --no-cache-dir --upgrade pip && \
    for i in 1 2 3; do \
        pip install --no-cache-dir pipenv && break || sleep 15; \
    done

# Copy Pipfile and install Python dependencies with memory optimization
COPY Pipfile Pipfile.lock ./
RUN for i in 1 2 3; do \
        PIPENV_NOSPIN=1 PIPENV_HIDE_EMOJIS=1 pipenv install --system --deploy --verbose && break || sleep 15; \
    done

# Copy the Django backend
COPY backend/django/ ./backend/

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist/

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

# Clean up
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Expose the port
EXPOSE 8000

# Run the application
CMD ["/app/runner.sh"] 