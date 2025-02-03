#!/bin/bash
set -e

cd /app/backend

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn Imagi.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2 