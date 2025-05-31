# Use Python 3.13 slim image for smaller size
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy dependency files first for better Docker layer caching
COPY Pipfile Pipfile.lock ./

# Install Python dependencies
# Use --system to install packages globally (not in virtual env)
# Use --deploy for production-like installation
RUN pipenv install --system --deploy

# Copy Django project code
COPY . .

# Create required directories
RUN mkdir -p /app/staticfiles /app/media

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=Imagi.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Production environment variables (will be set by Railway)
ENV SECRET_KEY=""
ENV DEBUG=0
ENV OPENAI_KEY=""
ENV ANTHROPIC_KEY=""
ENV STRIPE_SECRET_KEY=""
ENV STRIPE_PUBLIC_KEY=""
ENV FRONTEND_URL=""
ENV FRONTEND_REDIRECT_ENABLED="true"
ENV PROJECTS_ROOT="/app/projects"

# Database environment variables for Railway PostgreSQL
ENV DATABASE_URL=""
ENV PGDATABASE=""
ENV PGHOST=""
ENV PGPASSWORD=""
ENV PGPORT=""
ENV PGUSER=""

# Create projects directory
RUN mkdir -p /app/projects

# Create startup script for Railway deployment
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Django application..."\n\
\n\
# Collect static files\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput --clear\n\
\n\
# Run database migrations\n\
echo "Running database migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Start Gunicorn server\n\
echo "Starting Gunicorn server on port $PORT..."\n\
exec gunicorn Imagi.wsgi:application \\\n\
    --bind 0.0.0.0:$PORT \\\n\
    --workers 3 \\\n\
    --threads 2 \\\n\
    --timeout 120 \\\n\
    --keep-alive 2 \\\n\
    --max-requests 1000 \\\n\
    --max-requests-jitter 100 \\\n\
    --access-logfile - \\\n\
    --error-logfile - \\\n\
    --log-level info\n\
' > /app/start.sh && chmod +x /app/start.sh

# Clean up build dependencies to reduce image size
RUN apt-get purge -y build-essential gcc && apt-get autoremove -y

# Expose port (Railway will map this to public port)
EXPOSE 8000

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/v1/health/ || exit 1

# Start the application
CMD ["/app/start.sh"] 