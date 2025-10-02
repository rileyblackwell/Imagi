# Railway Private Network Debugging Guide

## Issue Overview
The private network connection between frontend (Nginx) and backend (Django) is failing on Railway, resulting in "Network error: Unable to connect to server" when making API calls.

## Root Cause Analysis

### Expected Request Flow
```
Browser → Frontend (https://imagi.up.railway.app)
         ↓ (relative URL: /api/v1/auth/health/)
       Nginx (proxy_pass)
         ↓ (Railway private network)
       Backend (http://backend.railway.internal:8000/api/v1/auth/health/)
         ↓
       Django Response
```

### Common Failure Points

1. **BACKEND_URL not properly set in Railway**
   - Symptom: Nginx cannot resolve backend hostname
   - Solution: Set `BACKEND_URL` using Railway reference variables

2. **Incorrect service name in BACKEND_URL**
   - Symptom: DNS resolution fails for backend.railway.internal
   - Solution: Ensure backend service name matches

3. **Backend not listening on correct port or interface**
   - Symptom: Connection refused or timeout
   - Solution: Ensure backend listens on `0.0.0.0:8000` or `:::8000`

4. **Host header mismatch causing Django to reject requests**
   - Symptom: 400 Bad Request from Django
   - Solution: Configure nginx to send correct Host header

## Configuration Verification Checklist

### Step 1: Verify Railway Environment Variables

#### Frontend Service Variables
Navigate to Railway → Frontend Service → Variables tab and verify:

```bash
# REQUIRED: Backend URL for Nginx proxy (server-side only)
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}

# MUST NOT BE SET: Browser should use relative URLs
# ❌ Remove if present:
# VITE_BACKEND_URL=...

# Optional: Stripe key for frontend
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

**Critical Notes:**
- `${{backend.RAILWAY_PRIVATE_DOMAIN}}` references the backend service's private domain
- `backend` must match your Django service name exactly (case-sensitive)
- Use `http://` not `https://` for private network
- `VITE_BACKEND_URL` should NOT be set (causes browser to bypass nginx)

#### Backend Service Variables
Navigate to Railway → Backend Service → Variables tab and verify:

```bash
# REQUIRED: Port for backend to listen on
PORT=8000

# REQUIRED: Database connection
DATABASE_URL=postgresql://...

# Django settings
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False

# Railway environment identifier
RAILWAY_ENVIRONMENT_NAME=production

# API Keys
OPENAI_KEY=...
ANTHROPIC_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_PUBLIC_KEY=...
```

### Step 2: Verify Service Names

1. In Railway dashboard, check the **service name** of your Django backend
2. It should be exactly `backend` (lowercase)
3. If different, update the `BACKEND_URL` variable accordingly:
   ```bash
   # If your service is named "django-backend"
   BACKEND_URL=http://${{django-backend.RAILWAY_PRIVATE_DOMAIN}}:${{django-backend.PORT}}
   ```

### Step 3: Check Backend Logs

Look for these startup messages in your backend service logs:

```
✅ Expected:
🔒 Railway production configured: SSL redirects DISABLED for internal network...
ALLOWED_HOSTS includes: backend.railway.internal, .railway.internal

❌ If missing:
Check Django settings.py is properly configured for Railway
```

### Step 4: Check Frontend Logs

Look for these startup messages in your frontend service logs:

```
✅ Expected:
🚀 Starting Nginx with Railway configuration...
📡 Backend URL Configuration:
   BACKEND_URL: http://backend.railway.internal:8000
✅ BACKEND_URL successfully substituted
✅ Nginx configuration is valid
🌐 Starting Nginx server...

❌ If you see errors:
- "BACKEND_URL is empty" → Variable not set in Railway
- "Nginx configuration is invalid" → Template substitution failed
- "${BACKEND_URL}" in proxy_pass → envsubst didn't run
```

### Step 5: Test Backend Health Endpoint Directly

Use Railway's internal health check proxy:

1. Open browser to: `https://imagi.up.railway.app/backend-health`
2. This endpoint bypasses the frontend app and directly tests nginx → backend connection
3. **Expected response:**
   ```json
   {
     "status": "healthy",
     "message": "Auth service is running"
   }
   ```
4. **If 502/504:** Nginx cannot reach backend
5. **If 400:** Django rejecting the request (ALLOWED_HOSTS issue)

### Step 6: Check Browser Console

Open DevTools → Network tab and look for the health check request:

```
✅ Expected:
Request URL: https://imagi.up.railway.app/api/v1/auth/health/
Status: 200 OK
Type: xhr

❌ If network error:
- Check Request URL (should be relative path, not backend.railway.internal)
- Check Console logs for detailed error messages
- Verify frontend service is deployed with latest changes
```

## Django Configuration Fixes

Ensure these settings are correct in `backend/django/Imagi/settings.py`:

### ALLOWED_HOSTS
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '.railway.app',  # Matches *.railway.app domains
    'backend.railway.internal',  # ✅ CRITICAL: Private network hostname
    '.railway.internal',  # Matches *.railway.internal domains
    '[::1]',  # IPv6 localhost
]
```

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",  # Development
    "https://imagi.up.railway.app",  # Production frontend
]

# Don't add backend.railway.internal to CORS_ALLOWED_ORIGINS
# The request comes from the frontend's public domain, not the internal domain
```

### CSRF Configuration
```python
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5174',
    'https://imagi.up.railway.app',  # Frontend public domain
]
```

### Security Settings for Railway
```python
if IS_RAILWAY_PRODUCTION:
    # CRITICAL: Must be False to allow internal HTTP communication
    SECURE_SSL_REDIRECT = False
    
    # Trust proxy headers from Nginx
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
```

## Nginx Configuration Fixes

The updated `nginx.conf` includes:

### Critical Changes
```nginx
location /api/ {
    # Use Railway reference variable (substituted at runtime)
    proxy_pass ${BACKEND_URL};
    
    # ✅ CRITICAL FIX: Set Host header to internal hostname
    # This allows Django to validate against ALLOWED_HOSTS
    proxy_set_header Host backend.railway.internal;
    
    # Still preserve original host for logging
    proxy_set_header X-Original-Host $host;
    proxy_set_header X-Forwarded-Host $host;
    
    # Always HTTPS from browser perspective
    proxy_set_header X-Forwarded-Proto https;
    
    # Railway debugging headers
    proxy_set_header X-Railway-Frontend "frontend.railway.internal";
}
```

## Testing & Verification

### 1. Health Check Test
```bash
# Should return 200 OK
curl https://imagi.up.railway.app/api/v1/auth/health/
```

### 2. CSRF Token Test
```bash
# Should return CSRF cookie
curl -v https://imagi.up.railway.app/api/v1/auth/csrf/
```

### 3. Browser Console Test
Open DevTools console and run:
```javascript
// Check if health check works
fetch('/api/v1/auth/health/')
  .then(r => r.json())
  .then(data => console.log('✅ Success:', data))
  .catch(err => console.error('❌ Failed:', err))
```

## Deployment Steps

After making configuration changes:

### 1. Commit and Push Changes
```bash
git add .
git commit -m "fix: improve Railway private network configuration"
git push origin main
```

### 2. Verify Railway Environment Variables
- Frontend: Check `BACKEND_URL` is set correctly
- Backend: Check `PORT=8000` is set
- Remove any `VITE_BACKEND_URL` from frontend

### 3. Trigger Redeploy
- Railway auto-deploys on git push
- Or manually trigger from Railway dashboard
- Watch the deployment logs carefully

### 4. Monitor Logs

**Frontend logs should show:**
```
📡 Backend URL: http://backend.railway.internal:8000
✅ BACKEND_URL successfully substituted
✅ Nginx configuration is valid
```

**Backend logs should show:**
```
🔒 Railway production configured
System check identified no issues (0 silenced).
Listening at: http://0.0.0.0:8000
```

### 5. Test in Browser
- Navigate to `https://imagi.up.railway.app`
- Open DevTools → Console
- Look for health check logs with 🏥, 🔍, ✅ emojis
- Should see `✅ Auth API health check passed`

## Common Issues & Solutions

### Issue: "Network error: Unable to connect to server"

**Possible Causes:**
1. ❌ BACKEND_URL not set or incorrect
2. ❌ Service name doesn't match
3. ❌ Backend not running or crashed
4. ❌ Backend not listening on correct port/interface

**Debug Steps:**
```bash
# Check frontend logs for BACKEND_URL value
# Check backend logs for startup success
# Test /backend-health endpoint
# Verify service names match
```

### Issue: "502 Bad Gateway"

**Cause:** Nginx can reach backend but backend isn't responding

**Solutions:**
1. Check backend service status in Railway dashboard
2. Verify backend is listening on `PORT=8000`
3. Check backend logs for crashes or errors
4. Ensure backend Dockerfile exposes port 8000

### Issue: "400 Bad Request"

**Cause:** Django rejecting request due to Host header validation

**Solutions:**
1. Add `backend.railway.internal` to `ALLOWED_HOSTS`
2. Ensure nginx sets `proxy_set_header Host backend.railway.internal;`
3. Check Django middleware isn't blocking requests

### Issue: CORS errors

**Cause:** Frontend trying to make requests to wrong origin

**Solutions:**
1. Remove `VITE_BACKEND_URL` from frontend environment variables
2. Verify frontend uses relative URLs (`/api/v1/...`)
3. Check nginx CORS headers in config

## Architecture Review

### Why This Architecture?

**Browser → Nginx → Railway Private Network → Django**

✅ **Advantages:**
- Backend stays private (not exposed to internet)
- No CORS issues (same-origin from browser perspective)
- Fast internal communication via Railway private network
- SSL handled at edge by Railway

❌ **Why not browser → backend directly?**
- Railway private network only accessible server-to-server
- Browser can't reach `backend.railway.internal`
- Would require exposing backend publicly (security risk)
- Would cause CORS complexity

### Key Insight

**Two types of URLs in play:**

1. **Browser URLs** (client-side):
   - Always relative: `/api/v1/auth/login/`
   - Browser sees: `https://imagi.up.railway.app/api/v1/auth/login/`
   - Defined in frontend code

2. **Nginx URLs** (server-side):
   - Internal Railway network: `http://backend.railway.internal:8000/api/v1/auth/login/`
   - Set via `BACKEND_URL` environment variable
   - Nginx does the proxying

## Additional Resources

- [Railway Private Networking Docs](https://docs.railway.app/reference/private-networking)
- [Railway Reference Variables](https://docs.railway.app/develop/variables#reference-variables)
- [Django ALLOWED_HOSTS](https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts)

## Need Help?

If still experiencing issues after following this guide:

1. Share frontend service logs (look for BACKEND_URL value)
2. Share backend service logs (startup messages)
3. Share browser console logs (API call errors)
4. Verify Railway environment variables screenshot
5. Confirm service names in Railway dashboard
