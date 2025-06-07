# Build stage - Vue.js application
FROM node:20-slim as build-stage

WORKDIR /app

# Copy and install dependencies (better layer caching)
COPY package*.json ./
RUN npm ci

# Railway build arguments and environment variables
ARG VITE_STRIPE_PUBLISHABLE_KEY

# Set Vite env vars (embedded in built code)
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY

# Copy source and build application
COPY . .
RUN npm run build

# Production stage - Nginx server
FROM nginx:alpine as production-stage

# Set up Nginx configuration for Railway proxy architecture
RUN mkdir -p /etc/nginx/templates
COPY <<EOF /etc/nginx/templates/default.conf.template
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    # API request proxy to backend via Railway internal network
    location /api/ {
        # Proxy to backend service via Railway internal networking
        proxy_pass http://backend.railway.internal:8000;
        
        # Standard proxy headers for Django
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        
        # Handle streaming responses and prevent buffering
        proxy_buffering off;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts for AI processing
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Logging for debugging
        access_log /var/log/nginx/api_access.log;
        error_log /var/log/nginx/api_error.log;
    }

    # SPA client-side routing
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

# Copy Vue.js build artifacts
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]