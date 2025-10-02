# Railway Deployment Guide for Imagi Oasis

## Backend-Frontend Connection Issue Fix

### Problem
The frontend was getting **504 Gateway Timeout** and **ERR_TOO_MANY_REDIRECTS** when trying to connect to the backend in Railway production.

### Root Causes
1. **Redirect Loop**: Django's `SECURE_SSL_REDIRECT=True` was causing infinite redirects because nginx was setting `X-Forwarded-Proto: $scheme` (http) instead of `https`
2. **Backend Unreachable**: Hardcoded `backend.railway.internal:8000` might not match the actual Railway service name

### Solutions Applied

#### 1. Fixed SSL Redirect Loop
Updated `frontend/vuejs/nginx.conf.template` to set:
```nginx
proxy_set_header X-Forwarded-Proto https;
```
This tells Django the original request was HTTPS, preventing redirect loops.

#### 2. Made Backend URL Configurable
- Created `frontend/vuejs/scripts/entrypoint.sh` to substitute environment variables at runtime
- Updated `frontend/vuejs/Dockerfile` to use nginx template with `BACKEND_SERVICE_URL`
- Default value: `http://backend.railway.internal:8000`

## Railway Configuration Steps

### Step 1: Verify Backend Service Name
1. Go to your Railway dashboard
2. Navigate to your project
3. Check the **exact name** of your backend service (e.g., "backend", "django", "backend-django")

### Step 2: Configure Frontend Environment Variable (If Needed)
If your backend service is NOT named "backend", you need to set an environment variable:

1. In Railway dashboard, go to your **frontend service**
2. Go to **Variables** tab
3. Add a new variable:
   - **Variable Name**: `BACKEND_SERVICE_URL`
   - **Variable Value**: `http://<your-backend-service-name>.railway.internal:8000`
   
   Examples:
   - If service is named "django": `http://django.railway.internal:8000`
   - If service is named "backend-api": `http://backend-api.railway.internal:8000`

### Step 3: Deploy Updated Code
```bash
cd frontend/vuejs
git add nginx.conf.template scripts/entrypoint.sh Dockerfile
git commit -m "Fix Railway backend connectivity with configurable backend URL"
git push
```

Railway will automatically rebuild and redeploy both services.

### Step 4: Verify Backend is Running
1. In Railway dashboard, check that backend service is **running** (green)
2. Check backend logs for startup messages:
   ```
   🚀 Starting Django backend server...
   🌐 Starting Gunicorn server on port 8000...
   ```

### Step 5: Test the Connection
After deployment completes, test the following endpoints:

1. **Frontend Health**: https://imagi.up.railway.app/health
   - Should return: `{"status":"healthy","service":"frontend",...}`

2. **Backend Health (via nginx proxy)**: https://imagi.up.railway.app/backend-health
   - Should return: `{"status":"healthy","message":"Auth API is running",...}`
   - If this fails, check the backend service name configuration

3. **Direct API Test**: https://imagi.up.railway.app/api/v1/auth/csrf/
   - Should set a cookie and return JSON

## Troubleshooting

### Still Getting 504 Gateway Timeout?

**Check 1: Backend Service Name**
```bash
# In Railway dashboard, verify:
# - Backend service name matches BACKEND_SERVICE_URL
# - Default is "backend", but yours might be different
```

**Check 2: Backend is Listening on IPv6**
The backend startup script should show:
```
🌐 Starting Gunicorn server on port 8000...
gunicorn ... --bind [::]:8000
```

The `[::]` means it's binding to IPv6, which is required for Railway's private network.

**Check 3: Both Services in Same Project**
Railway's private network only works within the same project and environment.

### Still Getting ERR_TOO_MANY_REDIRECTS?

This means the `X-Forwarded-Proto: https` fix didn't apply. Verify:
```bash
# Check the deployed nginx config has the fix:
railway run --service frontend cat /etc/nginx/conf.d/default.conf | grep X-Forwarded-Proto
# Should output: proxy_set_header X-Forwarded-Proto https;
```

### Backend Logs Show "Connection Refused"?

The backend service isn't starting properly. Check backend logs for:
- Database connection errors
- Missing environment variables
- Python errors during startup

## Environment Variables Reference

### Frontend Service
- `BACKEND_SERVICE_URL` (optional): Backend internal URL
  - Default: `http://backend.railway.internal:8000`
  - Format: `http://<service-name>.railway.internal:8000`

### Backend Service
- `DATABASE_URL`: PostgreSQL connection string (set by Railway)
- `DJANGO_SECRET_KEY`: Django secret key
- `OPENAI_KEY`: OpenAI API key
- `ANTHROPIC_KEY`: Anthropic API key
- `STRIPE_SECRET_KEY`: Stripe secret key
- `STRIPE_PUBLIC_KEY`: Stripe publishable key
- `FRONTEND_URL`: `https://imagi.up.railway.app`
- `RAILWAY_ENVIRONMENT_NAME`: Set to `production` by Railway

## Architecture Diagram

```
External User (HTTPS)
    ↓
Railway Load Balancer (SSL Termination)
    ↓
Frontend Service (nginx) - imagi.up.railway.app
    ↓ X-Forwarded-Proto: https
Railway Private Network (HTTP over IPv6)
    ↓
Backend Service (gunicorn) - backend.railway.internal:8000
    ↓
PostgreSQL Database
```

## Key Points

1. **External connections use HTTPS** (handled by Railway)
2. **Internal connections use HTTP** (Railway private network)
3. **Django sees HTTPS** via `X-Forwarded-Proto: https` header
4. **No redirect loops** because Django thinks request is HTTPS
5. **Backend service name must match** the URL in nginx config

## Testing Locally

To test the nginx configuration locally:
```bash
cd frontend/vuejs
docker build -t imagi-frontend .
docker run -p 8080:80 -e BACKEND_SERVICE_URL=http://localhost:8000 imagi-frontend

# In another terminal, start the backend:
cd backend/django
python manage.py runserver 8000
```

Then visit: http://localhost:8080
