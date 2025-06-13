# Docker Setup - Frontend (Vue.js)

This directory contains a modular Docker setup for the Vue.js frontend application, following best practices for containerization.

## Architecture

### Multi-Stage Build
- **Build Stage**: Node.js environment for building the Vue.js application
- **Production Stage**: Nginx Alpine for serving static files and proxying API requests

### Modular Components

#### Scripts (`scripts/`)
- `build.sh` - Handles the build process with error checking
- `validate-env.sh` - Environment validation before build
- `health-check.sh` - Robust health checking with fallbacks
- `start-nginx.sh` - Nginx startup with configuration validation

#### Configuration Files
- `nginx.conf.template` - Nginx configuration with Railway proxy setup
- `.dockerignore` - Excludes unnecessary files from build context
- `docker-compose.yml` - Multi-environment orchestration

## Usage

### Production Build
```bash
# Build the Docker image
docker build -t imagi-frontend .

# Run the container
docker run -p 3000:80 imagi-frontend
```

### Development with Docker Compose
```bash
# Production mode
docker-compose up frontend

# Development mode (with hot reload)
docker-compose --profile dev up frontend-dev
```

### Environment Variables
- `VITE_STRIPE_PUBLISHABLE_KEY` - Stripe publishable key for payments

## Features

### Nginx Configuration
- **API Proxying**: Routes `/api/*` requests to backend service
- **SPA Routing**: Handles client-side routing with fallback to `index.html`
- **Static Asset Caching**: Optimized caching headers for performance
- **CORS Handling**: Proper CORS setup for API requests
- **Security Headers**: XSS protection, content type sniffing prevention
- **Gzip Compression**: Reduces bandwidth usage

### Health Checks
- **Process Check**: Verifies nginx is running
- **HTTP Check**: Tests the `/health` endpoint
- **Fallback Support**: Uses both curl and wget for compatibility
- **Retry Logic**: Multiple attempts with backoff

### Performance Optimizations
- **Layer Caching**: Optimized Dockerfile layer structure
- **Multi-stage Build**: Minimal production image size
- **Build Dependencies**: Separated from runtime dependencies
- **Static Asset Optimization**: Proper cache headers and compression

## Railway Deployment

The setup is optimized for Railway.com deployment:
- Internal networking via `backend.railway.internal:8000`
- Environment variable substitution in nginx config
- Health checks compatible with Railway's monitoring
- Port 80 exposure for Railway's load balancer

## Troubleshooting

### Build Issues
```bash
# Check build logs
docker build --no-cache -t imagi-frontend .

# Verify environment validation
docker run --rm -it node:20-slim /bin/bash
/usr/local/bin/validate-env.sh

# Verify build script
docker run --rm -it imagi-frontend /usr/local/bin/build.sh
```

### Runtime Issues
```bash
# Check nginx configuration
docker exec <container> nginx -t

# View logs
docker logs <container>
docker exec <container> cat /var/log/nginx/error.log
```

### Health Check Debugging
```bash
# Test health check manually
docker exec <container> /usr/local/bin/health-check.sh

# Check health endpoint
curl http://localhost:3000/health
``` 