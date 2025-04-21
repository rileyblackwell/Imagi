FROM node:20-slim

WORKDIR /app

# Copy dependency files first for better caching
COPY package*.json ./
RUN npm install

# Frontend environment variables (will be set by Railway)
ENV VITE_API_URL=
ENV VITE_STRIPE_PUBLISHABLE_KEY=

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Use a lightweight server for production
FROM nginx:alpine

# Copy the built files to nginx serve directory
COPY --from=0 /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 