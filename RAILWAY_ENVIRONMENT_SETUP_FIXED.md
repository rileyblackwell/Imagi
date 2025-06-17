# Railway Environment Variables Setup - Updated Guide

## 🔧 Fixed Issues

### Dockerfile Updates
- ✅ Added `NODE_ENV` as build argument with default value `production`
- ✅ Added `VITE_BACKEND_URL` as build argument
- ✅ Properly set environment variables during build stage
- ✅ All Vite environment variables now available at build time

## 📋 Required Environment Variables in Railway

### Frontend Service Environment Variables
Set these in your Railway **frontend service** environment variables:

```bash
# Required - Build arguments
NODE_ENV=production
VITE_BACKEND_URL=http://backend.railway.internal:8000

# Optional - If using Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
```

### Backend Service Environment Variables  
Set these in your Railway **backend service** environment variables:

```bash
# Required
DJANGO_SECRET_KEY=your-super-secret-key-here-min-50-characters
DJANGO_DEBUG=False
RAILWAY_ENVIRONMENT=production

# Database (automatically provided by Railway PostgreSQL addon)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Optional
PROJECTS_ROOT=/app/projects

# If using Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
```

## 🚂 How to Set Variables in Railway

### Method 1: Railway Dashboard (Recommended)
1. Go to your Railway project dashboard
2. Click on your **frontend service**
3. Click the "Variables" tab
4. Add these variables:
   ```
   NODE_ENV = production
   VITE_BACKEND_URL = http://backend.railway.internal:8000
   VITE_STRIPE_PUBLISHABLE_KEY = pk_test_your_key (if needed)
   ```
5. Click "Deploy" to trigger a new deployment

6. Switch to your **backend service**
7. Click the "Variables" tab  
8. Add these variables:
   ```
   DJANGO_SECRET_KEY = your-secret-key-here
   DJANGO_DEBUG = False
   RAILWAY_ENVIRONMENT = production
   ```
9. Click "Deploy" to trigger a new deployment

### Method 2: Railway CLI
```bash
# For frontend service
railway service frontend
railway variables set NODE_ENV=production
railway variables set VITE_BACKEND_URL=http://backend.railway.internal:8000

# For backend service  
railway service backend
railway variables set DJANGO_DEBUG=False
railway variables set RAILWAY_ENVIRONMENT=production
railway variables set DJANGO_SECRET_KEY=your-secret-key-here
```

## 🔍 Verification Steps

After setting environment variables and redeploying:

### 1. Check Build Logs
In Railway deployment logs, you should see:
```
✅ Environment variables passed to build:
  NODE_ENV=production
  VITE_BACKEND_URL=http://backend.railway.internal:8000
```

### 2. Test in Browser Console
Open your deployed app and run:
```javascript
// Check environment info
window.railwayDebug.debugEnvironment()

// Should show:
// NODE_ENV: production (not undefined)
// VITE_BACKEND_URL: http://backend.railway.internal:8000 (not undefined)
```

### 3. Test Connectivity
```javascript
// Run full diagnostics
window.railwayDebug.runFullDiagnostics()

// Should see successful connections, not ERR_TOO_MANY_REDIRECTS
```

## 🐛 Troubleshooting

### If you still see "undefined" values:
1. **Check correct service**: Make sure you set variables on the frontend service (not backend)
2. **Redeploy required**: Environment variables need a new deployment to take effect
3. **Build arguments**: The updated Dockerfile now properly handles these as build arguments

### If you get ERR_TOO_MANY_REDIRECTS:
1. **Backend variables**: Ensure `RAILWAY_ENVIRONMENT=production` is set on backend service
2. **SSL redirects**: The backend automatically disables SSL redirects in Railway environment
3. **Django debug**: Make sure `DJANGO_DEBUG=False` on backend

### If CSRF still fails:
1. **Check backend health**: Visit `/backend-health` endpoint
2. **Direct health check**: Visit `/api/v1/auth/health/`
3. **CORS settings**: Backend should automatically allow Railway origins

## 🎯 Expected Results

After implementing these fixes, you should see:

✅ **Environment Variables**:
```
NODE_ENV: production
VITE_BACKEND_URL: http://backend.railway.internal:8000
```

✅ **API Connectivity**:
```
/health: 200 OK
/backend-health: 200 OK  
/api/v1/auth/health/: 200 OK
/api/v1/auth/csrf/: 200 OK (with CSRF token)
```

✅ **No More Errors**:
- No "undefined" environment variables
- No ERR_TOO_MANY_REDIRECTS
- Successful CSRF token requests
- Working authentication flow

## 🔄 Deployment Order

1. **Set environment variables** on both services
2. **Deploy backend service** first (wait for completion)
3. **Deploy frontend service** second
4. **Test connectivity** using browser console tools

## 📞 Support

If you continue to experience issues after following this guide:
1. Check Railway service logs for build/runtime errors
2. Use the browser console debug tools: `window.railwayDebug.runFullDiagnostics()`
3. Verify all environment variables are set on the correct services
4. Ensure both services are deployed and running 