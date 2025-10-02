#!/bin/sh

# Nginx entrypoint script for Railway
# Substitutes environment variables into nginx configuration at runtime

set -e

echo "🚀 Starting Nginx with Railway configuration..."

# Set default backend URL if not provided
BACKEND_SERVICE_URL="${BACKEND_SERVICE_URL:-http://backend.railway.internal:8000}"

echo "📡 Backend Service URL: $BACKEND_SERVICE_URL"

# Substitute environment variables in nginx config
# Use a template approach to avoid hardcoding the backend URL
envsubst '${BACKEND_SERVICE_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "✅ Nginx configuration updated"
echo "📋 Configuration details:"
grep "proxy_pass" /etc/nginx/conf.d/default.conf | head -3

# Validate nginx configuration
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration is invalid"
    exit 1
fi

# Start nginx
echo "🌐 Starting Nginx..."
exec nginx -g 'daemon off;'
