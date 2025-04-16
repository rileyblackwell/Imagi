# Frontend build stage
FROM node:20-slim as frontend-builder
WORKDIR /app/frontend
COPY frontend/vuejs/package*.json ./
RUN npm install

# Copy and build frontend
COPY frontend/vuejs/ .
RUN npm run build

# Backend stage
FROM python:3.13-slim
WORKDIR /app

# Copy only dependency files first
COPY backend/django/Pipfile backend/django/Pipfile.lock ./

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && pip install pipenv \
    && pipenv install --system --deploy --dev \
    && apt-get remove -y build-essential gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Then copy application code
COPY backend/django/ ./backend/
# Copy built frontend files to Django's static directory
COPY --from=frontend-builder /app/frontend/dist ./backend/static/

# Create required directories
RUN mkdir -p /app/backend/staticfiles

# Create a minimal .env file with placeholder values
RUN echo "# This file is created by the Dockerfile and will be overridden by Railway environment variables\n\
OPENAI_KEY=\"\"\n\
ANTHROPIC_KEY=\"\"\n\
SECRET_KEY=\"\"\n\
STRIPE_PUBLIC_KEY=\"\"\n\
STRIPE_SECRET_KEY=\"\"\n\
FRONTEND_URL=\"http://localhost:5174\"\n\
FRONTEND_REDIRECT_ENABLED=\"true\"\n\
" > /app/backend/.env

# Setup runner script with environment variable validation
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
\n\
# Check for required environment variables\n\
if [ -z "$OPENAI_KEY" ]; then\n\
  echo "ERROR: OPENAI_KEY environment variable is not set!"\n\
  exit 1\n\
fi\n\
\n\
if [ -z "$SECRET_KEY" ]; then\n\
  echo "ERROR: SECRET_KEY environment variable is not set!"\n\
  exit 1\n\
fi\n\
\n\
# Update the .env file with environment variables from Railway\n\
if [ ! -z "$OPENAI_KEY" ]; then\n\
  sed -i "s/^OPENAI_KEY=.*/OPENAI_KEY=\"$OPENAI_KEY\"/g" .env\n\
  echo "- Updated OPENAI_KEY in .env file"\n\
fi\n\
\n\
if [ ! -z "$ANTHROPIC_KEY" ]; then\n\
  sed -i "s/^ANTHROPIC_KEY=.*/ANTHROPIC_KEY=\"$ANTHROPIC_KEY\"/g" .env\n\
  echo "- Updated ANTHROPIC_KEY in .env file"\n\
fi\n\
\n\
if [ ! -z "$SECRET_KEY" ]; then\n\
  sed -i "s/^SECRET_KEY=.*/SECRET_KEY=\"$SECRET_KEY\"/g" .env\n\
  echo "- Updated SECRET_KEY in .env file"\n\
fi\n\
\n\
if [ ! -z "$STRIPE_PUBLIC_KEY" ]; then\n\
  sed -i "s/^STRIPE_PUBLIC_KEY=.*/STRIPE_PUBLIC_KEY=\"$STRIPE_PUBLIC_KEY\"/g" .env\n\
  echo "- Updated STRIPE_PUBLIC_KEY in .env file"\n\
fi\n\
\n\
if [ ! -z "$STRIPE_SECRET_KEY" ]; then\n\
  sed -i "s/^STRIPE_SECRET_KEY=.*/STRIPE_SECRET_KEY=\"$STRIPE_SECRET_KEY\"/g" .env\n\
  echo "- Updated STRIPE_SECRET_KEY in .env file"\n\
fi\n\
\n\
if [ ! -z "$FRONTEND_URL" ]; then\n\
  sed -i "s|^FRONTEND_URL=.*|FRONTEND_URL=\"$FRONTEND_URL\"|g" .env\n\
  echo "- Updated FRONTEND_URL in .env file"\n\
fi\n\
\n\
if [ ! -z "$FRONTEND_REDIRECT_ENABLED" ]; then\n\
  sed -i "s/^FRONTEND_REDIRECT_ENABLED=.*/FRONTEND_REDIRECT_ENABLED=\"$FRONTEND_REDIRECT_ENABLED\"/g" .env\n\
  echo "- Updated FRONTEND_REDIRECT_ENABLED in .env file"\n\
fi\n\
\n\
# Print environment configuration for debugging\n\
echo "Environment configuration:"\n\
echo "- OPENAI_KEY: [Set but not displayed]"\n\
echo "- ANTHROPIC_KEY: [Set but not displayed]"\n\
echo "- DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"\n\
echo "- FRONTEND_URL: $FRONTEND_URL"\n\
echo "- FRONTEND_REDIRECT_ENABLED: $FRONTEND_REDIRECT_ENABLED"\n\
\n\
python manage.py collectstatic --no-input\n\
python manage.py migrate --no-input\n\
gunicorn Imagi.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2\n\
' > /app/start.sh && chmod +x /app/start.sh

# Environment variables
ENV DJANGO_SETTINGS_MODULE=Imagi.settings
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

# These are fallback values - Railway should provide these at runtime
# API Keys (placeholder values - these will be overridden by Railway environment variables)
ENV OPENAI_KEY=""
ENV ANTHROPIC_KEY=""

# Django Settings
ENV SECRET_KEY=""

# Stripe Settings
ENV STRIPE_PUBLIC_KEY=""
ENV STRIPE_SECRET_KEY=""

# Frontend Settings
ENV FRONTEND_URL="http://localhost:5174"
ENV FRONTEND_REDIRECT_ENABLED="true"

# Expose port
EXPOSE 8000

CMD ["/app/start.sh"]
