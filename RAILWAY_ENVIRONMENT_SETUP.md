# Railway Environment Variables Setup

## Current Issues Detected

Based on the console logs, the following environment variables are missing or incorrectly configured:

### ❌ Missing Variables
- `VITE_BACKEND_URL` - Not set (should be `http://backend.railway.internal:8000` for internal networking)
- `NODE_ENV` - Not set (should be `production`)

## Required Environment Variables

### Frontend Service (Vue.js)
Set these in your Railway frontend service environment variables:

```bash
# Required for production
NODE_ENV=production

# Optional - for direct backend connection (recommended for debugging)
VITE_BACKEND_URL=http://backend.railway.internal:8000

# Required if using Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
```

### Backend Service (Django)
Set these in your Railway backend service environment variables:

```bash
# Required
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
RAILWAY_ENVIRONMENT=production

# Database (automatically provided by Railway if using Railway PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Optional - for file storage location
PROJECTS_ROOT=/app/projects

# Required if using Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key_here
```

## How to Set Environment Variables in Railway

### Method 1: Railway Dashboard
1. Go to your Railway project dashboard
2. Click on your frontend service
3. Go to the "Variables" tab
4. Click "Add Variable"
5. Add each variable name and value
6. Click "Deploy" to apply changes

### Method 2: Railway CLI
```bash
# Set frontend variables
railway env set NODE_ENV=production
railway env set VITE_BACKEND_URL=http://backend.railway.internal:8000

# Switch to backend service and set backend variables
railway env set DJANGO_DEBUG=False
railway env set RAILWAY_ENVIRONMENT=production
```

### Method 3: Environment File (for Railway CLI deployment)
Create a `.env` file in your project root (make sure it's in `.gitignore`):

```bash
# Frontend variables
NODE_ENV=production
VITE_BACKEND_URL=http://backend.railway.internal:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key

# Backend variables  
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
RAILWAY_ENVIRONMENT=production
```

## Networking Options

### Option 1: Nginx Proxy (Recommended for Production)
- **DON'T** set `VITE_BACKEND_URL`
- Frontend connects to backend through nginx proxy at relative URLs
- More secure as backend is not directly accessible

### Option 2: Direct Internal Connection (Recommended for Debugging)
- **DO** set `VITE_BACKEND_URL=http://backend.railway.internal:8000`
- Frontend connects directly to backend via Railway internal network
- Better for debugging connection issues

## Verification

After setting the environment variables and redeploying:

1. **Check the console logs** - You should see:
   ```
   🔧 API Configuration:
     Environment: production
     VITE_BACKEND_URL: http://backend.railway.internal:8000
   ```

2. **Run debug diagnostics** in browser console:
   ```javascript
   window.railwayDebug.debugEnvironment()
   ```

3. **Test connectivity**:
   ```javascript
   window.railwayDebug.runFullDiagnostics()
   ```

## Troubleshooting

### If you still get ERR_TOO_MANY_REDIRECTS:
1. Make sure `RAILWAY_ENVIRONMENT=production` is set on backend
2. The backend will automatically disable SSL redirects for Railway
3. Check that nginx isn't causing additional redirects

### If CSRF tokens still fail:
1. Make sure backend can receive requests from frontend
2. Check that cookies are being set properly
3. Use the health check endpoints to verify connectivity:
   - `/health` - Frontend health
   - `/backend-health` - Backend health (proxied)
   - `/api/v1/auth/health/` - Direct backend health

### If environment variables don't appear:
1. Make sure you're setting them on the correct service (frontend vs backend)
2. Redeploy the service after setting variables
3. Check the service logs for any startup errors

## Expected Behavior After Fix

After setting the correct environment variables, you should see:
- ✅ No more "VITE_BACKEND_URL: undefined" messages
- ✅ No more ERR_TOO_MANY_REDIRECTS errors
- ✅ Successful CSRF token requests
- ✅ Working authentication flow 