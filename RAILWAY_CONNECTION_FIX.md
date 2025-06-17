# Railway Frontend-Backend Connection Fixes

## Issue Summary
The frontend was unable to connect to the backend in Railway production environment. The error occurred when trying to fetch CSRF tokens from `/api/v1/auth/csrf/`, resulting in "Network error: Unable to connect to server" messages.

## Root Causes Identified
1. **CORS Configuration**: The CORS settings weren't properly configured for Railway's internal networking
2. **CSRF Cookie Settings**: Cross-domain CSRF settings were too restrictive for Railway's internal network
3. **API URL Configuration**: The frontend wasn't properly configured to use Railway's internal backend URL
4. **Insufficient Logging**: Limited debugging information to diagnose connection issues

## Fixes Implemented

### 1. Backend Django Settings (`backend/django/Imagi/settings.py`)
- **CORS Settings**: Updated to allow Railway internal origins and temporarily allow all origins for debugging
- **CSRF Settings**: Simplified cookie settings for Railway internal networking
- **Session Settings**: Made cookie settings more permissive for internal network communication
- **Logging**: Added comprehensive logging with emojis for better debugging

### 2. Backend Middleware (`backend/django/apps/Auth/middleware.py`)
- **Enhanced CORS Middleware**: Added Railway-specific origin handling and detailed logging
- **Error Handling**: Improved error responses with CORS headers
- **Request Logging**: Added comprehensive request/response logging for debugging

### 3. Backend API Views (`backend/django/apps/Auth/api/views.py`)
- **CSRF Token View**: Enhanced with Railway environment detection and debugging info
- **Health Check View**: Added comprehensive health check with environment details
- **URL Mapping**: Fixed URL mapping inconsistencies

### 4. Frontend API Configuration (`frontend/vuejs/src/shared/services/api.ts`)
- **Base URL Logic**: Added Railway-specific URL configuration logic
- **Request/Response Interceptors**: Enhanced with detailed logging for debugging
- **Error Handling**: Added Railway-specific error detection and logging

### 5. Frontend Auth Service (`frontend/vuejs/src/apps/auth/services/api.ts`)
- **CSRF Token Handling**: Enhanced with comprehensive logging and Railway-specific error handling
- **Network Debugging**: Added detailed request/response logging

### 6. Nginx Configuration (`frontend/vuejs/nginx.conf`)
- **Enhanced Logging**: Added debug-level logging for API requests
- **Error Handling**: Added custom error handling for backend connection failures
- **Headers**: Added Railway-specific headers for debugging
- **Health Checks**: Added backend health check proxy endpoint

### 7. Debug Utilities (`frontend/vuejs/src/shared/utils/railway-debug.ts`)
- **Comprehensive Diagnostics**: Created utility class for Railway environment debugging
- **Health Check Tests**: Multiple endpoint testing functions
- **Network Reachability**: Direct backend connection testing
- **Environment Analysis**: Detailed environment variable and configuration analysis

### 8. Main Application (`frontend/vuejs/src/main.ts`)
- **Production Debugging**: Automatic Railway diagnostics in production environment
- **Global Debug Access**: Made debugging tools available globally for console access

## Key Configuration Changes

### Environment Variables Expected
- `VITE_BACKEND_URL`: Should be set to `http://backend.railway.internal:8000` in Railway production
- `RAILWAY_ENVIRONMENT`: Set by Railway to indicate production environment

### Railway Internal Networking
- Frontend: `http://frontend.railway.internal:80`
- Backend: `http://backend.railway.internal:8000`

### Debug Endpoints Added
- `/backend-health`: Proxied health check to backend
- `/api/v1/auth/health/`: Enhanced backend health check with environment info

## Testing & Debugging

### Console Commands Available in Production
```javascript
// Run full diagnostics
window.railwayDebug.runFullDiagnostics()

// Test specific endpoints
window.railwayDebug.testBackendConnectivity()
window.railwayDebug.testCSRFEndpoint()
window.railwayDebug.testNetworkReachability()

// Environment debug info
window.railwayDebug.debugEnvironment()
```

### Endpoints for Manual Testing
- `GET /health` - Frontend health check
- `GET /backend-health` - Backend health check (proxied)
- `GET /api/v1/auth/health/` - Backend health check (direct)
- `GET /api/v1/auth/csrf/` - CSRF token endpoint

## Next Steps

1. **Deploy Changes**: Deploy both frontend and backend with these changes
2. **Monitor Logs**: Check both services' logs for the new debug information
3. **Test Endpoints**: Use the debug utilities to test connectivity
4. **Environment Variables**: Ensure `VITE_BACKEND_URL` is properly set in Railway
5. **Gradual Restriction**: Once working, gradually restrict CORS settings for security

## Important Notes

- **Temporary Debug Mode**: CORS is temporarily set to allow all origins for debugging
- **Comprehensive Logging**: Extensive logging is enabled - monitor log volume in production
- **Railway Specific**: These fixes are optimized for Railway's internal networking architecture
- **Security**: Remember to restrict CORS settings once connectivity is confirmed

## Expected Behavior After Fix

1. Frontend should successfully connect to backend via Railway internal network
2. CSRF tokens should be properly generated and set as cookies
3. Comprehensive logging should provide clear debugging information
4. Health check endpoints should confirm service connectivity
5. Debug tools should provide detailed environment analysis 