# Build stage for Vue.js frontend
FROM node:20.11.1-slim as frontend-builder

WORKDIR /app/frontend
COPY frontend/vuejs/package*.json ./

# Add retry logic for npm install
RUN for i in 1 2 3; do npm install && break || sleep 15; done

COPY frontend/vuejs/ .
RUN npm run build

# Final stage for Django and serving frontend
ARG PYTHON_VERSION=3.13.0a4-slim-bullseye
FROM python:${PYTHON_VERSION}

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies with retry logic
RUN for i in 1 2 3; \
    do apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    curl \
    libjpeg-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && break || sleep 15; \
    done

# Install Node.js with retry logic
RUN for i in 1 2 3; \
    do curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && break || sleep 15; \
    done

# Set working directory
WORKDIR /app

# Install pip and pipenv with retry logic
RUN pip install --upgrade pip
RUN for i in 1 2 3; do pip install --no-cache-dir pipenv && break || sleep 15; done

# Copy Pipfile and install Python dependencies
COPY Pipfile Pipfile.lock ./
RUN for i in 1 2 3; do pipenv install --system --deploy && break || sleep 15; done

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