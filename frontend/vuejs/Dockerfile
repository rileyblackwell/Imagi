# Build stage - Vue.js application
FROM node:20-slim as build-stage

WORKDIR /app

# Copy and install dependencies (better layer caching)
COPY package*.json ./
RUN npm ci

# Railway build arguments and environment variables
ARG VITE_STRIPE_PUBLISHABLE_KEY
ARG VITE_BACKEND_URL

# Set Vite env vars (embedded in built code)
ENV VITE_STRIPE_PUBLISHABLE_KEY=$VITE_STRIPE_PUBLISHABLE_KEY
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

# Copy source and build application
COPY . .
RUN npm run build

# Production stage - Nginx server
FROM nginx:alpine as production-stage

# Install envsubst utility
RUN apk add --no-cache bash gettext

# Re-set backend URL for Nginx configuration
ARG VITE_BACKEND_URL
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

# Log backend URL for debugging
RUN echo "Backend URL will be set to: ${VITE_BACKEND_URL}"

# Set up Nginx configuration template (env vars processed at runtime)
RUN mkdir -p /etc/nginx/templates
COPY <<EOF /etc/nginx/templates/default.conf.template
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    
    # API request proxy to backend
    location /api/ {
        proxy_pass \${VITE_BACKEND_URL};
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
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        # OPTIONS request handling
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

# Start Nginx (templates processed automatically)
CMD ["nginx", "-g", "daemon off;"]