#!/bin/sh

# Nginx entrypoint script for Railway
# Substitutes environment variables into nginx configuration at runtime

set -e

echo "🚀 Starting Nginx with Railway configuration..."
echo "================================================"

# Set default backend URL if not provided
BACKEND_URL="${BACKEND_URL:-http://backend.railway.internal:8000}"

# Extract hostname from BACKEND_URL for the Host header
# e.g., "http://backend.railway.internal:8000" -> "backend.railway.internal"
BACKEND_HOST=$(echo "$BACKEND_URL" | sed -E 's|^https?://||' | sed -E 's|:[0-9]+.*$||' | sed -E 's|/.*$||')

# Export BACKEND_HOST so envsubst can use it
export BACKEND_HOST

echo "📡 Backend URL Configuration:"
echo "   BACKEND_URL: $BACKEND_URL"
echo "   BACKEND_HOST: $BACKEND_HOST (extracted for Host header)"
echo ""

# Validate BACKEND_URL format
if [ -z "$BACKEND_URL" ]; then
    echo "❌ ERROR: BACKEND_URL is empty!"
    echo "   Please set BACKEND_URL in Railway environment variables"
    echo "   Example: BACKEND_URL=http://\${{backend.RAILWAY_PRIVATE_DOMAIN}}:\${{backend.PORT}}"
    exit 1
fi

# Validate BACKEND_HOST was extracted
if [ -z "$BACKEND_HOST" ]; then
    echo "❌ ERROR: Could not extract hostname from BACKEND_URL!"
    echo "   BACKEND_URL must be in format: http://hostname:port"
    exit 1
fi

echo "📝 Processing Nginx configuration..."

# Check if nginx config exists
if [ ! -f /etc/nginx/conf.d/default.conf ]; then
    echo "❌ ERROR: Nginx configuration file not found!"
    echo "   Expected: /etc/nginx/conf.d/default.conf"
    ls -la /etc/nginx/conf.d/ || true
    exit 1
fi

# Substitute environment variables directly in the nginx config
# This replaces ${BACKEND_URL} and ${BACKEND_HOST} with actual values
envsubst '${BACKEND_URL} ${BACKEND_HOST}' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp
mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf

echo "✅ Nginx configuration updated"
echo ""
echo "📋 Configuration details:"
echo "   Proxy pass directives:"
grep "proxy_pass" /etc/nginx/conf.d/default.conf | head -5 | sed 's/^/      /'
echo ""
echo "   Host header directives:"
grep "proxy_set_header Host" /etc/nginx/conf.d/default.conf | head -5 | sed 's/^/      /'
echo ""
echo "   Backend URL verification:"
if grep -q "${BACKEND_URL}" /etc/nginx/conf.d/default.conf; then
    echo "      ✅ BACKEND_URL successfully substituted"
else
    echo "      ⚠️  Warning: BACKEND_URL might not be substituted correctly"
fi
if grep -q "${BACKEND_HOST}" /etc/nginx/conf.d/default.conf; then
    echo "      ✅ BACKEND_HOST successfully substituted"
else
    echo "      ⚠️  Warning: BACKEND_HOST might not be substituted correctly"
fi
echo ""

# Validate nginx configuration
echo "🔍 Validating Nginx configuration..."
if nginx -t 2>&1 | sed 's/^/   /'; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration is invalid"
    echo ""
    echo "📋 Debug: Generated configuration:"
    cat /etc/nginx/conf.d/default.conf | head -100
    exit 1
fi

echo ""
echo "🌐 Starting Nginx server..."
echo "================================================"

# Start nginx
exec nginx -g 'daemon off;'
