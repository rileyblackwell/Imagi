#!/bin/bash

# Build script for Vue.js frontend
# This script handles the build process with proper error handling

set -e  # Exit on any error

echo "🏗️  Starting Vue.js build process..."

# Display environment variables for debugging
echo "🔍 Environment variables during build:"
echo "  NODE_ENV: ${NODE_ENV:-undefined}"
echo "  VITE_BACKEND_URL: ${VITE_BACKEND_URL:-undefined}"
echo "  VITE_STRIPE_PUBLISHABLE_KEY: ${VITE_STRIPE_PUBLISHABLE_KEY:-undefined}"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    exit 1
fi

# Check if node_modules exists (dependencies should be pre-installed in Docker)
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm ci --prefer-offline --no-audit
else
    echo "📦 Dependencies already installed, skipping..."
fi

# Build the application
echo "🔨 Building Vue.js application..."
npm run build

# Verify build output
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed - dist directory not found!"
    exit 1
fi

echo "✅ Build completed successfully!"
echo "📁 Build output available in: dist/"

# Optional: Display build size
if command -v du >/dev/null 2>&1; then
    echo "📊 Build size: $(du -sh dist/ | cut -f1)"
fi 