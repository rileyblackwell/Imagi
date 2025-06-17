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

# Railway build arguments and environment variables
ARG VITE_STRIPE_PUBLISHABLE_KEY
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

# Copy nginx scripts directly and make them executable
COPY scripts/ /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

# Copy Vue.js build artifacts from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Set proper ownership for nginx files
RUN chown -R nginx:nginx /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Health check using our script
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Use our startup script with fallback
CMD ["/bin/sh", "-c", "if [ -f /usr/local/bin/start-nginx.sh ]; then /usr/local/bin/start-nginx.sh; else nginx -g 'daemon off;'; fi"]