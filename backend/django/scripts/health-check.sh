#!/bin/bash

# Health check script for Django backend
# Verifies both the application server and Django health endpoint

set -e

# Configuration
HEALTH_URL="http://localhost:${PORT:-8000}/api/v1/health/"
TIMEOUT=10
MAX_RETRIES=3

echo "🏥 Django backend health check..."

# Function to check if Gunicorn is running
check_gunicorn() {
    if pgrep -f "gunicorn" > /dev/null; then
        echo "✅ Gunicorn process is running"
        return 0
    else
        echo "❌ Gunicorn process not found"
        return 1
    fi
}

# Function to check Django health endpoint
check_django_health() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        echo "🔍 Health check attempt $((retry_count + 1))/$MAX_RETRIES..."
        
        # Try curl first
        if command -v curl >/dev/null 2>&1; then
            if curl -f -s --max-time $TIMEOUT "$HEALTH_URL" > /dev/null 2>&1; then
                echo "✅ Django health endpoint responding (curl)"
                return 0
            fi
        fi
        
        # Fallback to wget
        if command -v wget >/dev/null 2>&1; then
            if wget -q -T $TIMEOUT -O /dev/null "$HEALTH_URL" 2>/dev/null; then
                echo "✅ Django health endpoint responding (wget)"
                return 0
            fi
        fi
        
        # Fallback to python requests
        if python -c "
import requests
import sys
try:
    response = requests.get('$HEALTH_URL', timeout=$TIMEOUT)
    if response.status_code == 200:
        print('✅ Django health endpoint responding (python)')
        sys.exit(0)
    else:
        print(f'❌ Health endpoint returned status {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        [ $retry_count -lt $MAX_RETRIES ] && sleep 2
    done
    
    echo "❌ Django health endpoint not responding after $MAX_RETRIES attempts"
    return 1
}

# Run checks
if check_gunicorn && check_django_health; then
    echo "✅ Backend health check passed"
    exit 0
else
    echo "❌ Backend health check failed"
    exit 1
fi 