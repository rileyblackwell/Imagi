## Build stage
# Official images via AWS's public mirror of Docker Hub, which rate-limits
# Railway's builders (429) and fails the deploy.
FROM public.ecr.aws/docker/library/node:22-alpine AS builder

WORKDIR /app

COPY frontend/vuejs/package*.json ./
RUN npm ci

COPY frontend/vuejs/ .
RUN npm run build-only

## Production stage
FROM public.ecr.aws/docker/library/nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/vuejs/nginx.conf /etc/nginx/conf.d/default.conf
COPY frontend/vuejs/docker-entrypoint.d/10-set-resolver.sh /docker-entrypoint.d/10-set-resolver.sh
RUN chmod +x /docker-entrypoint.d/10-set-resolver.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
