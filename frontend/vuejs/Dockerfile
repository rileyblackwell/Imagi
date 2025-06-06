# Build stage
FROM node:20-slim as build-stage

WORKDIR /app

# Copy dependency files first for better caching
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci

# Environment variables for build time (will be set by Railway)
ARG VITE_API_URL
ARG VITE_STRIPE_PUBLISHABLE_KEY
ARG BACKEND_URL

# Set environment variables for Vite build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY


# Copy application code
COPY . .

# Build the Vue.js application
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage

# Copy custom nginx configuration
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Handle client-side routing (SPA)
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Copy the built files from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80 (Railway will map this to the public port)
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 