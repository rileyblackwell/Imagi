# Railway Configuration Guide

## Overview
This document outlines the Railway environment configuration for Imagi Oasis, ensuring proper communication between frontend and backend services using Railway's private networking.

## Architecture Overview

**Request Flow:**
```
Browser → Frontend (Nginx) → Railway Private Network → Backend (Django)
         (relative URL)      (backend.railway.internal:8000)
```

The browser makes requests to relative URLs (e.g., `/api/v1/auth/login/`), which Nginx proxies to the backend via Railway's private network.

## Environment Variables

### Frontend Service (Vue.js + Nginx)

Set the following environment variable in Railway for the **frontend service**:

```bash
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}
```

**Important Notes:**
- This variable is used by **Nginx** (not browser JavaScript) to proxy API requests
- `backend` refers to the **service name** of your Django backend in Railway
- `RAILWAY_PRIVATE_DOMAIN` is automatically provided by Railway for private networking
- `PORT` must be set manually as a service variable on the backend service (typically `8000`)
- Use `http://` protocol (not `https://`) for internal Railway communication
- **DO NOT** set `VITE_BACKEND_URL` in the frontend service (browser uses relative URLs)

### Backend Service (Django)

Ensure the backend service has the following variable set:

```bash
PORT=8000
```

This allows the frontend Nginx to reference `${{backend.PORT}}` in the BACKEND_URL.

## How It Works

### Development (Local)
- Frontend runs on `http://localhost:5174` (Vite dev server)
- Backend runs on `http://localhost:8000` (Django dev server)
- Vite proxy configuration handles API requests (see `vite.config.ts`)
- API calls use relative paths like `/api/v1/auth/login/`

### Production (Railway)
- Browser makes API calls using relative paths: `/api/v1/auth/login/`
- Nginx intercepts these requests and proxies them to: `http://backend.railway.internal:8000/api/v1/auth/login/`
- Railway's private network handles routing between Nginx and Django
- This architecture prevents CORS issues and keeps the backend private

## Code Implementation

### Frontend API Configuration

The shared API client (`src/shared/services/api.ts`) automatically handles both environments:

```typescript
export const API_CONFIG = {
  BASE_URL: (() => {
    const isProduction = import.meta.env.PROD
    const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
    
    // In production, always use relative URLs (Nginx proxy handles routing)
    if (isProduction) {
      return ''
    }
    
    // In development, use VITE_BACKEND_URL if set, otherwise relative URLs
    return backendUrl ? String(backendUrl).replace(/\/+$/, '') : ''
  })(),
  // ... other config
}
```

### Building API URLs

The `buildApiUrl` helper function constructs proper URLs:

```typescript
export function buildApiUrl(path: string): string {
  if (!path.startsWith('/api/')) {
    path = path.startsWith('/') ? `/api${path}` : `/api/${path}`
  }
  
  const isProduction = import.meta.env.PROD
  const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
  
  // In production, always use relative paths (Nginx handles proxying)
  if (isProduction) {
    return path
  }
  
  // In development, use full URL if VITE_BACKEND_URL is set
  if (backendUrl) {
    return `${backendUrl}${path}`
  }
  return path
}
```

### Auth Service Usage

All auth API calls use the shared pattern:

```typescript
import api, { buildApiUrl } from '@/shared/services/api'

// Example: Login
const response = await api.post(buildApiUrl(`${API_PATH}/login/`), credentials)

// This becomes:
// Development: POST /api/v1/auth/login/ (Vite proxies to localhost:8000)
// Production: POST /api/v1/auth/login/ (Nginx proxies to backend.railway.internal:8000)
```

## Verification

### Check Environment Variables in Railway

**Frontend Service:**
1. Go to your Railway project
2. Select the **frontend service**
3. Navigate to **Variables** tab
4. Confirm `BACKEND_URL` is set to: `http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}`
5. **Ensure `VITE_BACKEND_URL` is NOT set** (remove it if present)

**Backend Service:**
1. Select the **backend service**
2. Navigate to **Variables** tab  
3. Confirm `PORT` is set to: `8000`

### Check Backend Service Name

1. Ensure your Django backend service is named **backend** in Railway
2. If it has a different name, update the `BACKEND_URL` variable accordingly

### Test API Calls

After deployment, check the browser console (DevTools → Network tab):
- API requests should use **relative URLs**: `/api/v1/auth/login/`, `/api/v1/auth/csrf/`, etc.
- Requests should NOT show `backend.railway.internal` (that's internal to Nginx)
- No CORS errors should appear
- HTTP status codes should be 200/201 (success) or expected error codes (400/401/etc.)

## Troubleshooting

### Issue: API calls show `ERR_TOO_MANY_REDIRECTS` or `Network error: Unable to connect to server`

**Cause:** Frontend is trying to make requests to the public backend URL instead of using relative URLs, OR Nginx cannot reach the backend.

**Solution:**
1. **Remove `VITE_BACKEND_URL`** from the frontend service environment variables in Railway (if present)
2. Ensure `BACKEND_URL` is set correctly (used by Nginx, not browser JavaScript)
3. Verify `BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}`
4. Check that backend service name is exactly `backend` (case-sensitive)
5. Redeploy the frontend service
6. Browser should now use relative URLs like `/api/v1/auth/login/`
7. Check browser console for detailed debug logs starting with 🏥, 🔍, ✅, or ❌

### Issue: API calls fail with `502 Bad Gateway`

**Cause:** Nginx can't connect to the backend via Railway's private network.

**Solution:** Verify that:
1. `BACKEND_URL` is correctly set with the reference variable syntax
2. Backend service name matches the one used in `${{backend.RAILWAY_PRIVATE_DOMAIN}}`
3. Backend `PORT` variable is set to `8000`
4. Both services are in the same Railway project and environment

### Issue: Backend not receiving requests

**Solution:** Ensure Django is configured to listen on IPv6:
- Railway's private network uses IPv6
- Django should bind to `::` (all interfaces) or specifically to IPv6
- Check your `Dockerfile` or start command (should use `0.0.0.0` or `::`)

### Issue: CORS errors in production

**Solution:** 
- When using Nginx proxy with relative URLs, CORS should not be an issue
- If you see CORS errors, check that browser is using relative URLs (not full URLs)
- Verify Nginx configuration has proper CORS headers in `nginx.conf`
- Check Django CORS settings if you modified `ALLOWED_HOSTS` or CORS configuration

## Key Architecture Notes

**Why not use Railway reference variables directly in browser code?**

Railway's private networking (`backend.railway.internal`) is only accessible **server-to-server**. Since our Vue.js app is a Single Page Application (SPA) that runs in the user's browser, the browser cannot access Railway's private network.

**Our Solution:**
- Browser → Makes requests to relative URLs (e.g., `/api/v1/auth/login/`)
- Nginx (frontend container) → Proxies these to Railway's private network
- Backend (Django) → Receives requests via private network

This architecture:
- ✅ Keeps backend services private (not directly exposed)
- ✅ Avoids CORS issues (same-origin requests from browser perspective)
- ✅ Uses Railway's private network for fast, secure server-to-server communication
- ✅ Works seamlessly with HTTPS termination at Railway's edge

## References

- [Railway Private Networking Documentation](https://docs.railway.app/reference/private-networking)
- [Railway Reference Variables](https://docs.railway.app/develop/variables#reference-variables)
- **Note:** Reference variables work for server-side code (like Nginx config), not browser JavaScript
