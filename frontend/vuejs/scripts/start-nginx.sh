#!/bin/bash

# Nginx startup script with proper initialization
# Handles configuration validation and graceful startup

set -e

echo "🚀 Starting Nginx frontend server..."

# Validate nginx configuration
echo "🔍 Validating nginx configuration..."
if ! nginx -t; then
    echo "❌ Nginx configuration validation failed!"
    exit 1
fi

echo "✅ Nginx configuration is valid"

# Create log directories if they don't exist
mkdir -p /var/log/nginx

# Set proper permissions for nginx
chown -R nginx:nginx /var/log/nginx 2>/dev/null || true

# Display configuration info
echo "📋 Nginx configuration:"
echo "  - Config file: /etc/nginx/conf.d/default.conf"
echo "  - Document root: /usr/share/nginx/html"
echo "  - Access log: /var/log/nginx/access.log"
echo "  - Error log: /var/log/nginx/error.log"

# Start nginx in foreground
echo "🌐 Starting nginx server..."
exec nginx -g "daemon off;" 