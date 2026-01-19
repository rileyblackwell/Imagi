# Set the python version as a build-time argument
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    gcc \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir pipenv

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code

# Define port as ARG with default value
ARG PORT=8000
ENV PORT=$PORT

# Create code directory and set as workdir
WORKDIR /code

# Copy scripts and make them executable
COPY scripts/install-deps.sh /usr/local/bin/install-deps.sh
COPY scripts/run-server.sh /usr/local/bin/run-server.sh
COPY scripts/health-check.sh /usr/local/bin/health-check.sh
COPY scripts/validate-env.sh /usr/local/bin/validate-env.sh
RUN chmod +x /usr/local/bin/*.sh

# Copy pipenv files first for better caching
COPY Pipfile Pipfile.lock ./

# Install dependencies using our script
RUN /usr/local/bin/install-deps.sh

# Copy project code
COPY . .

# Create required directories
RUN mkdir -p /code/staticfiles /code/media /code/projects

# Build-time arguments that will be set by Railway
ARG DJANGO_SETTINGS_MODULE=Imagi.settings
ARG DJANGO_SECRET_KEY
ARG DJANGO_DEBUG=0
ARG OPENAI_KEY
ARG ANTHROPIC_KEY
ARG STRIPE_SECRET_KEY
ARG STRIPE_PUBLIC_KEY
ARG FRONTEND_URL
ARG FRONTEND_REDIRECT_ENABLED=true
ARG PROJECTS_ROOT=/code/projects
ARG DATABASE_URL

# Set runtime environment variables from build args
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE \
    DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY \
    DJANGO_DEBUG=$DJANGO_DEBUG \
    OPENAI_KEY=$OPENAI_KEY \
    ANTHROPIC_KEY=$ANTHROPIC_KEY \
    STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY \
    STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY \
    FRONTEND_URL=$FRONTEND_URL \
    FRONTEND_REDIRECT_ENABLED=$FRONTEND_REDIRECT_ENABLED \
    PROJECTS_ROOT=$PROJECTS_ROOT \
    DATABASE_URL=$DATABASE_URL

# Clean up build dependencies to reduce image size
RUN apt-get purge -y gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set proper ownership
RUN chown -R www-data:www-data /code

# Expose port 8000
EXPOSE 8000

# Health check using our script
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/health-check.sh

# Use our startup script
CMD ["/usr/local/bin/run-server.sh"]