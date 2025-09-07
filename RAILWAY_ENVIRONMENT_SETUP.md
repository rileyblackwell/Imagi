# Railway Environment Variables Setup - FIXED

## 🚨 IMMEDIATE FIXES NEEDED

Based on your console logs, here are the exact changes to fix the network connection issues:

### ❌ Current Issues in Console Logs
- `NODE_ENV: undefined` - Frontend missing NODE_ENV
- `ERR_TOO_MANY_REDIRECTS` - Backend missing RAILWAY_ENVIRONMENT=production
- `Mixed Content` errors - HTTPS frontend → HTTP backend direct connection
- CSRF token failures - Related to missing Railway environment detection

## ✅ EXACT SOLUTION

### 1. Frontend Service Environment Variables

In your Railway **frontend** service dashboard:

**REMOVE these variables:**
```bash
VITE_BACKEND_URL  # This causes mixed content errors
```

**ADD these variables:**
```bash
NODE_ENV=production
```

**KEEP these (if you have them):**
```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
```

### 2. Backend Service Environment Variables

In your Railway **backend** service dashboard:

**ENSURE these variables are set:**
```bash
# CRITICAL: This is automatically provided by Railway
# RAILWAY_ENVIRONMENT_NAME=production (automatically set)

# Core Django settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False

# Database (automatically provided by Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Required API keys for production
OPENAI_KEY=your-openai-key-here
ANTHROPIC_KEY=your-anthropic-key-here
STRIPE_SECRET_KEY=sk_test_or_live_your_stripe_secret_key
STRIPE_PUBLIC_KEY=pk_test_or_live_your_stripe_public_key
```

## 🔧 How to Apply These Changes

### Method 1: Railway Dashboard (Recommended)
1. Go to your Railway project dashboard
2. Click on **frontend** service → **Variables** tab
3. **DELETE** `VITE_BACKEND_URL` variable
4. **ADD** `NODE_ENV` = `production`
5. Click on **backend** service → **Variables** tab  
6. **Verify** other required variables are set (RAILWAY_ENVIRONMENT_NAME is automatically provided)
7. **Deploy** both services

### Method 2: Railway CLI
```bash
# Frontend changes
railway service frontend
railway variables set NODE_ENV=production
railway variables delete VITE_BACKEND_URL

# Backend changes  
railway service backend
railway variables set DJANGO_DEBUG=False
# Note: RAILWAY_ENVIRONMENT_NAME=production is automatically provided by Railway
```

## 📊 Expected Results After Fix

### Console Logs Should Show:
```javascript
🔧 API Configuration:
  Environment: production  
  VITE_BACKEND_URL: NOT SET
⚠️ VITE_BACKEND_URL not set in Railway - using nginx proxy
🚂 Using relative URLs for Railway nginx proxy

🚂 Railway Environment Debug Information:
  NODE_ENV: production  // ✅ Fixed (was undefined)
  PROD: true
  DEV: false
  VITE_BACKEND_URL: NOT SET  // ✅ Fixed (removed mixed content)
```

### Diagnostic Tests Should Show:
```javascript
✅ /health: 200
✅ /backend-health: 200          // ✅ Fixed (no more redirects)
✅ /api/v1/auth/csrf/: 200       // ✅ Fixed (CSRF working)
✅ Network connectivity: Working  // ✅ Fixed (no mixed content)
```

## 🔍 How This Fix Works

### 1. **Removes Mixed Content Error**
- Removing `VITE_BACKEND_URL` forces frontend to use relative URLs
- Nginx proxy handles `HTTPS frontend → HTTP backend` conversion internally
- No more `Mixed Content: The page at 'https://...' requested an insecure resource 'http://...'`

### 2. **Fixes Redirect Loops**
- Setting `RAILWAY_ENVIRONMENT=production` activates Railway-specific Django settings
- Disables `SECURE_SSL_REDIRECT` which causes redirect loops in Railway
- Enables proper CORS and CSRF configuration for Railway internal networking

### 3. **Enables Nginx Proxy Architecture**
- Frontend: `https://imagi.up.railway.app/api/...` → Nginx → `http://backend.railway.internal:8000/api/...`
- All communication happens on Railway's private network
- Proper security headers and CORS handling

## 🧪 Test the Fix

After redeploying both services:

1. **Open browser console** and try registering a user
2. **Run diagnostics** in console:
   ```javascript
   window.railwayDebug.runFullDiagnostics()
   ```
3. **Check results** - all endpoints should return ✅ status
4. **Try user registration** - should work without errors

## 🎯 Why This Architecture is Optimal

- ✅ **Security**: No direct HTTP connections from HTTPS frontend
- ✅ **Performance**: Railway internal network communication
- ✅ **Reliability**: Nginx handles connection pooling and retries  
- ✅ **Debugging**: Comprehensive logging and error handling
- ✅ **Scalability**: Standard Railway microservices pattern

This follows Railway's recommended architecture for production full-stack applications. 