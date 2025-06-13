#!/bin/bash

# Build script for Vue.js frontend
# This script handles the build process with proper error handling

set -e  # Exit on any error

echo "🏗️  Starting Vue.js build process..."

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --prefer-offline --no-audit

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