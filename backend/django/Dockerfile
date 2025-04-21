FROM python:3.13-slim
WORKDIR /app

# Copy only dependency files first
COPY Pipfile Pipfile.lock ./

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
COPY . .

# Create required directories
RUN mkdir -p /app/staticfiles

# Setup simple start script
RUN echo '#!/bin/bash\n\
cd /app\n\
python manage.py collectstatic --no-input\n\
python manage.py migrate --no-input\n\
gunicorn Imagi.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 2\n\
' > /app/start.sh && chmod +x /app/start.sh

# Environment variables
ENV DJANGO_SETTINGS_MODULE=Imagi.settings
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0

# Backend environment variables (will be set by Railway)
ENV OPENAI_KEY=
ENV ANTHROPIC_KEY=
ENV SECRET_KEY=
ENV STRIPE_SECRET_KEY=
ENV FRONTEND_URL=
ENV FRONTEND_REDIRECT_ENABLED=

# Expose port
EXPOSE 8000

CMD ["/app/start.sh"] 