#!/bin/bash

# Health check script for nginx frontend
# More robust health checking than just wget

set -e

# Configuration
HEALTH_URL="http://localhost/health"
TIMEOUT=3
MAX_RETRIES=3

echo "🏥 Frontend health check..."

# Function to check if service is healthy
check_health() {
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        echo "🏥 Health check attempt $((retry_count + 1))/$MAX_RETRIES..."
        
        # Check if nginx is running
        if ! pgrep nginx > /dev/null; then
            echo "❌ Nginx process not found"
            return 1
        fi
        
        # Check health endpoint
        if curl -f -s --max-time $TIMEOUT "$HEALTH_URL" > /dev/null 2>&1; then
            echo "✅ Health check passed"
            return 0
        elif wget -q -T $TIMEOUT -O /dev/null "$HEALTH_URL" 2>/dev/null; then
            echo "✅ Health check passed (fallback)"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        [ $retry_count -lt $MAX_RETRIES ] && sleep 1
    done
    
    echo "❌ Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Run health check
check_health 