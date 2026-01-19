# Docker Setup - Backend (Django)

This directory contains a modular Docker setup for the Django backend application, following best practices for containerization and deployment.

## Architecture

### Single-Stage Build
- **Base Image**: Python 3.12 slim (Debian bullseye)
- **Runtime**: Gunicorn WSGI server with multiple workers
- **Database**: PostgreSQL (production) / SQLite (development)

### Modular Components

#### Scripts (`scripts/`)
- `install-deps.sh` - Handles Pipenv dependency installation with verification
- `validate-env.sh` - Environment validation before deployment
- `run-server.sh` - Django startup with migrations, static files, and Gunicorn
- `health-check.sh` - Comprehensive health checking with multiple fallbacks

#### Configuration Files
- `.dockerignore` - Excludes unnecessary files from build context
- `docker-compose.yml` - Multi-service orchestration with PostgreSQL and Redis
- `Dockerfile` - Optimized multi-layer build with proper caching

## Usage

### Production Build
```bash
# Build the Docker image
docker build -t imagi-backend .

# Run the container
docker run -p 8000:8000 -e DJANGO_SECRET_KEY=your-secret-key imagi-backend
```

### Development with Docker Compose
```bash
# Basic backend only
docker-compose up backend

# With PostgreSQL database
docker-compose --profile postgres up backend postgres

# With Redis caching
docker-compose --profile redis up backend redis

# Full stack (PostgreSQL + Redis)
docker-compose --profile postgres --profile redis up
```

### Environment Variables

#### Required
- `DJANGO_SECRET_KEY` - Django secret key for cryptographic signing
- `DATABASE_URL` - Database connection string (optional in dev, uses SQLite by default)

#### Optional
- `DJANGO_DEBUG` - Enable Django debug mode (default: 0 for production, set to 1 or true for development)
- `OPENAI_KEY` - OpenAI API key for AI features
- `ANTHROPIC_KEY` - Anthropic API key for Claude integration
- `STRIPE_SECRET_KEY` - Stripe secret key for payments
- `STRIPE_PUBLIC_KEY` - Stripe publishable key
- `FRONTEND_URL` - Frontend application URL (default: http://localhost:5174)
- `WORKERS` - Gunicorn worker processes (default: 3, only used in production)
- `THREADS` - Gunicorn threads per worker (default: 2, only used in production)
- `TIMEOUT` - Request timeout in seconds (default: 120, only used in production)

## Features

### Django Configuration
- **Automatic Migrations**: Runs database migrations on startup
- **Static Files**: Collects and serves static assets
- **Health Endpoint**: `/api/v1/health/` for monitoring
- **CORS Support**: Configured for frontend integration
- **Security Headers**: Production-ready security configuration

### Gunicorn Configuration
- **Multi-worker**: 3 workers with 2 threads each (configurable)
- **Graceful Shutdown**: Proper signal handling
- **Request Limits**: Max 1000 requests per worker with jitter
- **Logging**: Structured logging to stdout/stderr
- **Preload**: Application preloading for better performance

### Health Checks
- **Process Verification**: Checks if Gunicorn is running
- **HTTP Endpoint**: Tests Django health endpoint
- **Multiple Methods**: curl, wget, and Python requests fallbacks
- **Retry Logic**: Multiple attempts with exponential backoff
- **Railway Compatible**: Works with Railway's health monitoring

### Performance Optimizations
- **Layer Caching**: Optimized Dockerfile layer ordering
- **Dependency Caching**: Pipfile changes trigger minimal rebuilds
- **Build Cleanup**: Removes build dependencies from final image
- **Proper Ownership**: Sets appropriate file permissions
- **Memory Efficiency**: Slim base image with minimal dependencies

## Railway Deployment

The setup is optimized for Railway.com deployment:
- **Environment Variables**: Automatic injection from Railway
- **Port Configuration**: Dynamic port binding via $PORT
- **Health Checks**: Compatible with Railway's monitoring
- **Database**: Automatic PostgreSQL provisioning
- **Logging**: Structured logs for Railway's log aggregation

## Development Workflow

### Local Development
```bash
# Install dependencies locally
pipenv install --dev

# Run development server
pipenv run python manage.py runserver

# Run migrations
pipenv run python manage.py migrate

# Create superuser
pipenv run python manage.py createsuperuser
```

### Docker Development
```bash
# Build and run with compose
docker-compose up backend

# Run Django commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell

# View logs
docker-compose logs -f backend
```

## Troubleshooting

### Build Issues
```bash
# Clean build
docker build --no-cache -t imagi-backend .

# Verify environment validation
docker run --rm -it imagi-backend /usr/local/bin/validate-env.sh

# Check dependencies
docker run --rm -it imagi-backend pip list

# Verify Django
docker run --rm -it imagi-backend python -c "import django; print(django.get_version())"
```

### Runtime Issues
```bash
# Check Django configuration
docker exec <container> python manage.py check --deploy

# View application logs
docker logs <container>

# Debug health check
docker exec <container> /usr/local/bin/health-check.sh

# Test database connection
docker exec <container> python manage.py dbshell
```

### Database Issues
```bash
# Reset migrations (development only)
docker-compose exec backend python manage.py migrate --fake-initial

# Check migration status
docker-compose exec backend python manage.py showmigrations

# Access database
docker-compose exec postgres psql -U imagi -d imagi
```

## Security Considerations

- **Environment Variables**: Never commit secrets to version control
- **Database**: Use strong passwords and connection encryption
- **HTTPS**: Always use HTTPS in production
- **Debug Mode**: Ensure DJANGO_DEBUG=0 in production
- **Static Files**: Serve via CDN or reverse proxy in production
- **User Permissions**: Runs as www-data user (non-root) 