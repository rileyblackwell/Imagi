# Build stage for Vue.js frontend
FROM node:20-slim as frontend-builder

WORKDIR /app/frontend
COPY frontend/vuejs/package*.json ./
RUN npm install

COPY frontend/vuejs/ .
RUN npm run build

# Final stage for Django and serving frontend
ARG PYTHON_VERSION=3.13-slim-bullseye
FROM python:${PYTHON_VERSION}

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # for postgres
    libpq-dev \
    # for building packages
    build-essential \
    # for node setup
    curl \
    # for image processing
    libjpeg-dev \
    # other utilities
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for potential SSR needs
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install pip and pipenv
RUN pip install --upgrade pip
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and install Python dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

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