#!/bin/bash

# Environment validation script for Vue.js frontend
# Validates required environment variables and configuration

set -e  # Exit on any error

echo "🔍 Validating frontend environment..."

# Configuration checks
VALIDATION_PASSED=true

# Check Node.js version
echo "📋 Environment information:"
echo "  - Node.js: $(node --version)"
echo "  - npm: $(npm --version)"

# Check if required files exist
echo "🔍 Checking required files..."
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    VALIDATION_PASSED=false
fi

if [ ! -f "vite.config.ts" ]; then
    echo "❌ Error: vite.config.ts not found!"
    VALIDATION_PASSED=false
fi

if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found!"
    VALIDATION_PASSED=false
fi

# Check environment variables (optional for build time)
echo "🔍 Checking environment variables..."
if [ -n "$VITE_STRIPE_PUBLISHABLE_KEY" ]; then
    echo "✅ VITE_STRIPE_PUBLISHABLE_KEY is set"
else
    echo "⚠️  VITE_STRIPE_PUBLISHABLE_KEY is not set (optional for build)"
fi

# Validate package.json structure
echo "🔍 Validating package.json..."
if ! node -e "
const pkg = require('./package.json');
if (!pkg.scripts || !pkg.scripts.build) {
    console.error('❌ Missing build script in package.json');
    process.exit(1);
}
if (!pkg.scripts.dev) {
    console.error('❌ Missing dev script in package.json');
    process.exit(1);
}
console.log('✅ package.json structure is valid');
"; then
    VALIDATION_PASSED=false
fi

# Final validation result
if [ "$VALIDATION_PASSED" = true ]; then
    echo "✅ Environment validation passed!"
    exit 0
else
    echo "❌ Environment validation failed!"
    exit 1
fi 