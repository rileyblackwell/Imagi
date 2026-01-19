#!/bin/bash

# Django server startup script
# Handles database migration, static files, and server startup (dev or prod)

set -e  # Exit on any error

# Configuration - Respect PORT environment variable (Railway sets this)
RUN_PORT="${PORT:-8000}"
WORKERS="${WORKERS:-3}"
THREADS="${THREADS:-2}"
TIMEOUT="${TIMEOUT:-120}"
MAX_REQUESTS="${MAX_REQUESTS:-1000}"

# Determine if we're in development or production mode
# DJANGO_DEBUG can be: 1, true, True, yes, Yes (development) or 0, false, False, no, No (production)
DJANGO_DEBUG="${DJANGO_DEBUG:-0}"
IS_DEV=false

if [ "$DJANGO_DEBUG" = "1" ] || [ "$DJANGO_DEBUG" = "true" ] || [ "$DJANGO_DEBUG" = "True" ] || [ "$DJANGO_DEBUG" = "yes" ] || [ "$DJANGO_DEBUG" = "Yes" ]; then
    IS_DEV=true
fi

echo "🚀 Starting Django backend server..."
echo "📋 Mode: $([ "$IS_DEV" = true ] && echo "DEVELOPMENT" || echo "PRODUCTION")"

# Check Django setup (skip --deploy flag in development)
if [ "$IS_DEV" = true ]; then
    echo "🔍 Running Django configuration check (development mode)..."
    if ! python manage.py check; then
        echo "❌ Django configuration check failed!"
        exit 1
    fi
else
    echo "🔍 Running Django configuration check (production mode)..."
    if ! python manage.py check --deploy; then
        echo "❌ Django configuration check failed!"
        exit 1
    fi
fi

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --no-input

# Show migration status
echo "📊 Migration status:"
python manage.py showmigrations --plan | tail -10

# Create necessary directories
mkdir -p /code/staticfiles /code/media /code/projects

if [ "$IS_DEV" = true ]; then
    # Development mode - use Django's runserver
    echo "🌐 Starting Django development server on port $RUN_PORT..."
    echo "⚠️  WARNING: This is a development server. Do not use it in production!"
    exec python manage.py runserver 0.0.0.0:$RUN_PORT
else
    # Production mode - collect static files and use Gunicorn
    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput --clear
    
    echo "🌐 Starting Gunicorn server on port $RUN_PORT..."
    exec gunicorn Imagi.wsgi:application \
        --bind 0.0.0.0:$RUN_PORT \
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
fi 