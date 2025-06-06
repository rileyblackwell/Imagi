# Build stage
FROM node:20-slim as build-stage

WORKDIR /app

# Copy dependency files first for better caching
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci

# Build-time arguments that will be set by Railway
ARG VITE_STRIPE_PUBLISHABLE_KEY
ARG BACKEND_URL

# Set build-time environment variables for Vite
# VITE_* variables are automatically embedded in the built code
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY
# BACKEND_URL is also needed at build time for any API base URL references in the code
ENV BACKEND_URL=$BACKEND_URL

# Copy application code
COPY . .

# Build the Vue.js application
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage

# Install envsubst for environment variable substitution
RUN apk add --no-cache bash gettext

# Re-declare ARGs in production stage (Docker ARGs don't persist between stages)
ARG BACKEND_URL
# Set as environment variable for runtime nginx configuration
ENV BACKEND_URL=$BACKEND_URL

# Create script to update nginx config at runtime with environment variables
RUN echo '#!/bin/bash\n\
echo "Using backend URL: ${BACKEND_URL}"\n\
envsubst < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf\n\
exec "$@"' > /docker-entrypoint.sh && \
chmod +x /docker-entrypoint.sh

# Create nginx configuration template with environment variables
RUN mkdir -p /etc/nginx/templates
COPY <<EOF /etc/nginx/templates/default.conf.template
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    # Proxy all API requests to the backend
    location /api/ {
        proxy_pass \${BACKEND_URL};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_buffering off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Add CORS headers for development
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

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

# Start nginx with our custom entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"] 