# Health Check Diagnostics Enhancement

## Overview
Enhanced the health check system with comprehensive diagnostic information to help identify where and why API connectivity is failing, especially in production Railway deployments.

## Changes Made

### 1. Enhanced Auth Health Check (`src/apps/auth/services/api.ts`)
The `healthCheck()` method now provides:

#### **Startup Diagnostics:**
- Timestamp
- Environment (production/development)
- URL details (requested URL, API path, relative vs absolute, protocol)
- Configuration (baseURL, BACKEND_URL, VITE_BACKEND_URL, timeout, credentials)
- Browser information (user agent, online status, location, origin)

#### **Success Information:**
- Response status
- Duration in milliseconds
- Response data
- Response headers (content-type, server, date)

#### **Enhanced Error Diagnostics:**
- **Timestamp & Duration**: When the error occurred and how long the request took
- **Error Type**: Name and message of the error
- **Request Details**: 
  - URL attempted
  - HTTP method
  - Base URL configuration
  - Full request URL
  - Request headers
- **Response Details** (if server responded):
  - Status code and text
  - Response data
  - Response headers
- **Network Details**:
  - Error code (e.g., ECONNABORTED)
  - Whether it's a network error (no response)
  - Whether it's a timeout
  - Browser online status
- **Environment Context**:
  - Production vs development
  - Mode
  - All URL configurations
- **Axios Details**:
  - Whether it's an Axios error
  - Error code
  - Stack trace (first 3 lines)

#### **User-Friendly Messages:**
The health check now provides contextual error messages:
- "No internet connection detected" - when browser is offline
- "Unable to reach backend server at [URL]" - for network errors
- "Server error (5xx)" - for backend errors
- "Health check endpoint not found (404)" - for missing routes
- "Request timeout after Xms" - for timeout errors

### 2. Enhanced API Interceptors (`src/shared/services/api.ts`)

#### **Request Interceptor:**
- Logs detailed information for health check requests
- Shows full URL construction
- Displays all headers

#### **Response Interceptor:**
- **HTML Detection**: Identifies when server returns HTML instead of JSON (common Nginx misconfiguration)
- **Health Check Error Logging**: Detailed logging for health check failures
- **Network Error Diagnostics**: Comprehensive network error information with possible causes:
  - Backend server not running
  - Nginx proxy misconfiguration
  - Railway private network connectivity issue
  - CORS policy blocking
  - DNS resolution failure
  - Firewall blocking

### 3. System Diagnostics Utility (`src/shared/utils/diagnostics.ts`)

New comprehensive diagnostic tool that checks:

1. **Browser Online Status**: Whether browser reports being online
2. **Environment Configuration**: Production/development mode, all URL configs
3. **Current Location**: Origin, protocol, host, pathname
4. **Local Storage Access**: Can access localStorage, has auth token
5. **Cookie Access**: Can access cookies, has CSRF token
6. **Frontend Health Check**: Tests `/health` endpoint (production only)
7. **Backend Health Check**: Tests `/api/v1/auth/health/` through proxy

Each check provides:
- Status: pass/fail/warning
- Message: Human-readable description
- Details: Technical information

#### **Usage:**
```javascript
// In browser console
window.imagiDiagnose()
```

This will run all diagnostics and print a formatted report.

### 4. Updated Register Component (`src/apps/auth/views/Register.vue`)

The health check error handler now:
- Logs the user-friendly message
- Logs the full diagnostic object
- Groups detailed diagnostics in console for easy reading

## Console Output Examples

### Success Case:
```
🏥 Auth Health Check - Starting: {
  timestamp: "2025-10-02T21:31:42.871Z",
  environment: "production",
  url: {
    requested: "/api/v1/auth/health/",
    apiPath: "/api/v1/auth",
    isRelative: true,
    protocol: "relative"
  },
  config: { ... },
  browser: { ... }
}

✅ Auth API health check passed: {
  status: 200,
  duration: "145ms",
  data: { status: "healthy" },
  headers: { ... }
}
```

### Failure Case:
```
❌ Auth API health check failed: {
  timestamp: "2025-10-02T21:31:42.895Z",
  duration: "24ms",
  errorType: "Error",
  message: "Network error: Unable to connect to server",
  request: {
    url: "/api/v1/auth/health/",
    method: "GET",
    baseURL: "",
    fullRequestUrl: "/api/v1/auth/health/",
    headers: { ... }
  },
  response: null,
  network: {
    code: undefined,
    isNetworkError: true,
    isTimeout: false,
    browserOnline: true
  },
  environment: {
    isProd: true,
    mode: "production",
    baseURL: "",
    backendUrl: "not set",
    viteBackendUrl: "not set"
  },
  axios: { ... }
}

🌐 Network Error Details: {
  url: "/api/v1/auth/health/",
  baseURL: "",
  fullURL: "/api/v1/auth/health/",
  method: "get",
  errorCode: undefined,
  errorMessage: "Network error: Unable to connect to server",
  browserOnline: true,
  timestamp: "2025-10-02T21:31:42.895Z",
  possibleCauses: [
    "Backend server is not running",
    "Nginx proxy misconfiguration",
    "Railway private network connectivity issue",
    "CORS policy blocking the request",
    "DNS resolution failure",
    "Firewall blocking the connection"
  ]
}
```

## Debugging Workflow

### Step 1: Check Console Logs
Look for the enhanced health check logs. They will tell you:
- What URL was attempted
- Whether it's using relative or absolute URLs
- What the base URL configuration is
- Whether the browser is online
- Whether a response was received

### Step 2: Run System Diagnostics
In the browser console:
```javascript
window.imagiDiagnose()
```

This will test:
- Frontend health endpoint
- Backend health endpoint through proxy
- All environment configurations
- Browser capabilities

### Step 3: Identify the Issue

#### If `isNetworkError: true` and `browserOnline: true`:
- Backend is not reachable
- Check if backend service is running on Railway
- Check Nginx proxy configuration
- Check BACKEND_URL environment variable

#### If `response.status: 502/503/504`:
- Backend is unreachable from Nginx
- Check Railway private network configuration
- Verify backend service name matches Nginx config
- Check backend is listening on correct port

#### If `response.status: 404`:
- Health check endpoint doesn't exist
- Check Django URL configuration
- Verify `/api/v1/auth/health/` route is registered

#### If `isTimeout: true`:
- Backend is too slow to respond
- Check backend logs for performance issues
- Increase timeout if needed

## Railway-Specific Debugging

### Check Environment Variables:
```bash
# In Railway backend service
echo $PORT  # Should be 8000 or Railway-assigned port
echo $RAILWAY_PRIVATE_DOMAIN  # Should be backend.railway.internal

# In Railway frontend service
echo $BACKEND_URL  # Should be http://backend.railway.internal:8000
```

### Check Nginx Configuration:
The entrypoint script logs detailed information about:
- BACKEND_URL substitution
- Nginx configuration validation
- Proxy pass directives

### Check Backend Connectivity:
From the frontend container:
```bash
# Test backend health directly
curl http://backend.railway.internal:8000/api/v1/auth/health/

# Test DNS resolution
nslookup backend.railway.internal
```

## Files Modified

1. `/frontend/vuejs/src/apps/auth/services/api.ts` - Enhanced health check
2. `/frontend/vuejs/src/shared/services/api.ts` - Enhanced interceptors
3. `/frontend/vuejs/src/apps/auth/views/Register.vue` - Updated error handling
4. `/frontend/vuejs/src/main.ts` - Exposed diagnostic utility
5. `/frontend/vuejs/src/shared/utils/diagnostics.ts` - New diagnostic utility

## Benefits

1. **Faster Debugging**: Immediately see where the failure is occurring
2. **Better Context**: Understand the environment and configuration
3. **Actionable Information**: Get possible causes and solutions
4. **Production-Ready**: Works in both development and production
5. **User-Friendly**: Console output is organized and easy to read
6. **Manual Diagnostics**: Can run comprehensive checks on demand
