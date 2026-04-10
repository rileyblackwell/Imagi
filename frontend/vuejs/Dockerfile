## Build stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY frontend/vuejs/package*.json ./
RUN npm ci

COPY frontend/vuejs/ .
RUN npm run build-only

## Production stage
FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/vuejs/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
