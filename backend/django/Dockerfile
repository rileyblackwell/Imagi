# Set the python version as a build-time argument
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Install pipenv globally
RUN pip install --no-cache-dir pipenv

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define port as ARG with default value
ARG PORT=8000
ENV PORT=$PORT

# Create code directory and set as workdir
RUN mkdir -p /code
WORKDIR /code

# Copy pipenv files first for caching
COPY Pipfile Pipfile.lock ./

# Install dependencies using pipenv (system, deploy)
RUN pipenv install --system --deploy

# Copy project code
COPY . .

# Create static/media/projects directories
RUN mkdir -p /code/staticfiles /code/media /code/projects

# Build-time arguments that will be set by Railway
ARG DJANGO_SETTINGS_MODULE=Imagi.settings
ARG SECRET_KEY
ARG DEBUG=0
ARG OPENAI_KEY
ARG ANTHROPIC_KEY
ARG STRIPE_SECRET_KEY
ARG STRIPE_PUBLIC_KEY
ARG FRONTEND_URL
ARG FRONTEND_REDIRECT_ENABLED=true
ARG PROJECTS_ROOT=/code/projects
ARG DATABASE_URL

# Set runtime environment variables from build args
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
ENV SECRET_KEY=$SECRET_KEY
ENV DEBUG=$DEBUG
ENV OPENAI_KEY=$OPENAI_KEY
ENV ANTHROPIC_KEY=$ANTHROPIC_KEY
ENV STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY
ENV STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY
ENV FRONTEND_URL=$FRONTEND_URL
ENV FRONTEND_REDIRECT_ENABLED=$FRONTEND_REDIRECT_ENABLED
ENV PROJECTS_ROOT=$PROJECTS_ROOT
ENV DATABASE_URL=$DATABASE_URL

# Create runtime script to run migrations and start gunicorn on port 8000
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "python manage.py collectstatic --noinput --clear\n" >> ./paracord_runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./paracord_runner.sh && \
    printf "gunicorn Imagi.wsgi:application --bind [::]:\$RUN_PORT --workers 3 --threads 2 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - --log-level info\n" >> ./paracord_runner.sh

# Make script executable
RUN chmod +x paracord_runner.sh

# Clean up build dependencies to reduce image size
RUN apt-get purge -y gcc && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Expose port 8000
EXPOSE 8000

# Healthcheck for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/v1/health/ || exit 1

# Start the Django project via the runtime script
CMD ./paracord_runner.sh