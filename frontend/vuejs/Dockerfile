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
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY

# Copy source code
COPY . .

# Validate environment and run build process
RUN /usr/local/bin/validate-env.sh && /usr/local/bin/build.sh

# Production stage - Nginx server
FROM nginx:alpine as production-stage

# Install additional tools for health checks
RUN apk add --no-cache curl procps

# Create nginx directories
RUN mkdir -p /etc/nginx/conf.d /var/log/nginx

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy health check script only
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
RUN chmod +x /usr/local/bin/health-check.sh

# Copy Vue.js build artifacts from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Set proper ownership for nginx files
RUN chown -R nginx:nginx /usr/share/nginx/html

# Create log directories and set permissions
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /var/log/nginx

# Expose HTTP port
EXPOSE 80

# Health check using our script
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Start nginx directly
CMD ["nginx", "-g", "daemon off;"]