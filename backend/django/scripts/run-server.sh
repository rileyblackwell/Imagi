#!/bin/bash

# Django server startup script
# Handles database migration, static files, and Gunicorn startup

set -e  # Exit on any error

# Configuration - Force port 8000 for consistency
RUN_PORT="8000"
WORKERS="${WORKERS:-3}"
THREADS="${THREADS:-2}"
TIMEOUT="${TIMEOUT:-120}"
MAX_REQUESTS="${MAX_REQUESTS:-1000}"

echo "🚀 Starting Django backend server..."

# Check Django setup
if ! python manage.py check --deploy; then
    echo "❌ Django configuration check failed!"
    exit 1
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --no-input

# Show migration status
echo "📊 Migration status:"
python manage.py showmigrations --plan | tail -10

# Create necessary directories
mkdir -p /code/staticfiles /code/media /code/projects

# Start Gunicorn server
echo "🌐 Starting Gunicorn server on port $RUN_PORT..."
exec gunicorn Imagi.wsgi:application \
    --bind [::]:$RUN_PORT \
    --workers $WORKERS \
    --threads $THREADS \
    --timeout $TIMEOUT \
    --keep-alive 2 \
    --max-requests $MAX_REQUESTS \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --worker-class sync \
    --preload 