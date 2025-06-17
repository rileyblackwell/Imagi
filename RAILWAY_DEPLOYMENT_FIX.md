# Railway Deployment Fix Guide

## ✅ Fixed Issues

### 1. Frontend Build Process
- **Problem**: `vue-tsc: not found` during Docker build
- **Solution**: Added `npm ci` installation step before running build script
- **Status**: ✅ **FIXED** - Build now completes successfully

### 2. Mixed Content Security Issues  
- **Problem**: HTTPS frontend trying to access HTTP backend directly
- **Solution**: Removed `VITE_BACKEND_URL` from production build to force nginx proxy usage
- **Status**: ✅ **FIXED** - Frontend will now use relative URLs through nginx proxy

## ⚠️ Remaining Issues to Fix

### 1. Backend Redirect Loop (`ERR_TOO_MANY_REDIRECTS`)

**Problem**: Backend is causing infinite redirects when accessed through nginx proxy

**Likely Causes**:
- Django `SECURE_SSL_REDIRECT = True` in production
- Django `ALLOWED_HOSTS` configuration
- Django `CSRF_TRUSTED_ORIGINS` missing Railway domains

**Solution**: Add these to your Railway backend service environment variables:

```bash
# Backend service environment variables in Railway
RAILWAY_ENVIRONMENT=production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=backend.railway.internal,frontend.railway.internal,imagi.up.railway.app,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://imagi.up.railway.app,http://backend.railway.internal:8000,http://frontend.railway.internal
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

### 2. Environment Variables

**Required Railway Environment Variables**:

#### Frontend Service:
```bash
NODE_ENV=production
# DON'T set VITE_BACKEND_URL (let it use nginx proxy)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
```

#### Backend Service:
```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
RAILWAY_ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@host:port/dbname
DJANGO_ALLOWED_HOSTS=backend.railway.internal,frontend.railway.internal,imagi.up.railway.app,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://imagi.up.railway.app,http://backend.railway.internal:8000,http://frontend.railway.internal
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

## 🚀 Expected Results After Fix

After setting the correct backend environment variables and redeploying:

1. **Console logs should show**:
   ```
   🔧 API Configuration:
     Environment: production
     VITE_BACKEND_URL: NOT SET
   🚂 Using relative URLs for Railway nginx proxy
   ```

2. **No more errors**:
   - ❌ `ERR_TOO_MANY_REDIRECTS`
   - ❌ `Mixed Content` errors
   - ❌ CSRF token failures

3. **Working features**:
   - ✅ Authentication flow
   - ✅ API calls through nginx proxy
   - ✅ Health check endpoints

## 🔧 How to Apply the Backend Fix

### Option 1: Railway Dashboard
1. Go to your Railway project dashboard
2. Click on your **backend** service
3. Go to "Variables" tab
4. Add each environment variable listed above
5. Click "Deploy" to redeploy the backend

### Option 2: Railway CLI
```bash
# Select backend service
railway environment set --name production

# Add the required variables
railway env set RAILWAY_ENVIRONMENT=production
railway env set DJANGO_SECURE_SSL_REDIRECT=False
railway env set DJANGO_ALLOWED_HOSTS="backend.railway.internal,frontend.railway.internal,imagi.up.railway.app,localhost,127.0.0.1"
railway env set DJANGO_CSRF_TRUSTED_ORIGINS="https://imagi.up.railway.app,http://backend.railway.internal:8000,http://frontend.railway.internal"
```

## 🧪 Testing After Deployment

1. **Rebuild and redeploy both services**
2. **Check console logs** for the expected output
3. **Test authentication flow**
4. **Run diagnostics** in browser console:
   ```javascript
   window.railwayDebug.runFullDiagnostics()
   ```

## 📋 Architecture Summary

**Current Fixed Setup**:
- Frontend (nginx) serves static files and proxies `/api/*` to backend
- Backend handles API requests on Railway internal network
- No direct frontend->backend HTTP connections (avoids mixed content)
- All external traffic flows: `User -> HTTPS Frontend -> nginx proxy -> HTTP Backend`

This is the recommended Railway production architecture for full-stack applications. 