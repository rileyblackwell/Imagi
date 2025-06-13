#!/bin/bash

# Dependency installation script for Django backend
# Handles pipenv installation with proper error handling

set -e  # Exit on any error

echo "📦 Installing Django backend dependencies..."

# Check if Pipfile exists
if [ ! -f "Pipfile" ]; then
    echo "❌ Error: Pipfile not found!"
    exit 1
fi

if [ ! -f "Pipfile.lock" ]; then
    echo "❌ Error: Pipfile.lock not found!"
    exit 1
fi

# Install dependencies using pipenv
echo "🔨 Installing packages with pipenv..."
pipenv install --system --deploy --ignore-pipfile

# Verify critical packages
echo "🔍 Verifying Django installation..."
python -c "import django; print(f'✅ Django {django.get_version()} installed successfully')"

echo "🔍 Verifying other critical packages..."
python -c "import gunicorn; print('✅ Gunicorn installed')" || echo "⚠️  Gunicorn not found"
python -c "import psycopg2; print('✅ PostgreSQL adapter installed')" || echo "⚠️  psycopg2 not found"

echo "✅ Dependencies installed successfully!"

# Display package count
PACKAGE_COUNT=$(pip list | wc -l)
echo "📊 Total packages installed: $((PACKAGE_COUNT - 2))" 