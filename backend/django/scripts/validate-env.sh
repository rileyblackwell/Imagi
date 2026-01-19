#!/bin/bash

# Environment validation script for Django backend
# Validates required environment variables and configuration

set -e  # Exit on any error

echo "🔍 Validating backend environment..."

# Configuration checks
VALIDATION_PASSED=true

# Check Python version
echo "📋 Environment information:"
echo "  - Python: $(python --version)"
echo "  - pip: $(pip --version)"

# Check if required files exist
echo "🔍 Checking required files..."
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found!"
    VALIDATION_PASSED=false
fi

if [ ! -f "Pipfile" ]; then
    echo "❌ Error: Pipfile not found!"
    VALIDATION_PASSED=false
fi

if [ ! -f "Pipfile.lock" ]; then
    echo "❌ Error: Pipfile.lock not found!"
    VALIDATION_PASSED=false
fi

# Check critical environment variables
echo "🔍 Checking required environment variables..."

if [ -z "$DJANGO_SECRET_KEY" ]; then
    echo "❌ Error: DJANGO_SECRET_KEY environment variable is required!"
    VALIDATION_PASSED=false
else
    echo "✅ DJANGO_SECRET_KEY is set"
fi

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL not set, will use SQLite default"
else
    echo "✅ DATABASE_URL is set"
fi

# Check optional but important variables
echo "🔍 Checking optional environment variables..."

if [ -n "$OPENAI_KEY" ]; then
    echo "✅ OPENAI_KEY is set"
else
    echo "⚠️  OPENAI_KEY not set (AI features may not work)"
fi

if [ -n "$STRIPE_SECRET_KEY" ]; then
    echo "✅ STRIPE_SECRET_KEY is set"
else
    echo "⚠️  STRIPE_SECRET_KEY not set (payments will not work)"
fi

if [ -n "$FRONTEND_URL" ]; then
    echo "✅ FRONTEND_URL is set: $FRONTEND_URL"
else
    echo "⚠️  FRONTEND_URL not set, using default"
fi

# Validate Django configuration
echo "🔍 Validating Django configuration..."
# Only run deployment checks in production (DJANGO_DEBUG=0 or unset)
if [ "${DJANGO_DEBUG:-0}" = "0" ] || [ "${DJANGO_DEBUG}" = "false" ]; then
    if ! python manage.py check --deploy --quiet 2>/dev/null; then
        echo "❌ Django configuration check failed!"
        echo "ℹ️  Run 'python manage.py check --deploy' for details"
        VALIDATION_PASSED=false
    else
        echo "✅ Django configuration is valid (production mode)"
    fi
else
    if ! python manage.py check --quiet 2>/dev/null; then
        echo "❌ Django configuration check failed!"
        echo "ℹ️  Run 'python manage.py check' for details"
        VALIDATION_PASSED=false
    else
        echo "✅ Django configuration is valid (development mode)"
    fi
fi

# Final validation result
if [ "$VALIDATION_PASSED" = true ]; then
    echo "✅ Environment validation passed!"
    exit 0
else
    echo "❌ Environment validation failed!"
    exit 1
fi 