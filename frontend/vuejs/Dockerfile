## Build stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY frontend/vuejs/package*.json ./
RUN npm ci

COPY frontend/vuejs/ .
RUN npm run build-only
# Deploy identification: exposes the build time at /version.txt
RUN date -u +"%Y-%m-%dT%H:%M:%SZ" > dist/version.txt

## Production stage
FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/vuejs/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/vuejs/docker-entrypoint.d/10-set-resolver.sh /docker-entrypoint.d/10-set-resolver.sh
RUN chmod +x /docker-entrypoint.d/10-set-resolver.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
