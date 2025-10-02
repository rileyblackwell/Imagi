# Build stage - Vue.js application
FROM node:20-slim as build-stage

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy build scripts and make them executable
COPY scripts/build.sh /usr/local/bin/build.sh
COPY scripts/validate-env.sh /usr/local/bin/validate-env.sh
RUN chmod +x /usr/local/bin/*.sh

# Copy package files for better layer caching
COPY package*.json ./

# Install dependencies first (for better Docker layer caching)
RUN npm ci --prefer-offline --no-audit

# Railway build arguments and environment variables
ARG NODE_ENV=production
ARG VITE_BACKEND_URL
ARG VITE_STRIPE_PUBLISHABLE_KEY

# Set environment variables for build process
ENV NODE_ENV=$NODE_ENV
# Make NODE_ENV available to the browser via Vite
ENV VITE_NODE_ENV=$NODE_ENV
# NOTE: For Railway production, we intentionally DON'T set VITE_BACKEND_URL
# This forces the frontend to use relative URLs with nginx proxy instead of direct backend connection
# which avoids mixed content issues (HTTPS frontend -> HTTP backend)
# ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY

# Debug: Display environment variables during build
RUN echo "🔍 Build Environment Variables:" && \
    echo "  NODE_ENV: $NODE_ENV" && \
    echo "  VITE_NODE_ENV: $NODE_ENV (available in browser)" && \
    echo "  VITE_BACKEND_URL: NOT SET (using nginx proxy)" && \
    echo "  VITE_STRIPE_PUBLISHABLE_KEY: ${VITE_STRIPE_PUBLISHABLE_KEY:-undefined}" && \
    echo "🚂 Railway Configuration: Frontend will use relative URLs through nginx proxy"

# Copy source code
COPY . .

# Validate environment and run build process
RUN /usr/local/bin/validate-env.sh && /usr/local/bin/build.sh

# Production stage - Nginx server
FROM nginx:alpine as production-stage

# Install additional tools for health checks and envsubst
RUN apk add --no-cache curl procps gettext

# Create nginx directories
RUN mkdir -p /etc/nginx/conf.d /var/log/nginx

# Copy nginx configuration as template (will be processed at runtime)
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Copy scripts
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/health-check.sh /usr/local/bin/entrypoint.sh

# Copy Vue.js build artifacts from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Set proper ownership for nginx files
RUN chown -R nginx:nginx /usr/share/nginx/html

# Create log directories and set permissions
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx

# Environment variable for backend service URL
# Default to backend.railway.internal:8000, but can be overridden in Railway
ENV BACKEND_SERVICE_URL=http://backend.railway.internal:8000

# Expose HTTP port
EXPOSE 80

# Health check using our script
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Use entrypoint script to substitute environment variables and start nginx
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]