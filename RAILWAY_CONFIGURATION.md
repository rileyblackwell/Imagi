# Railway Configuration Guide

## Overview
This document outlines the Railway environment configuration for Imagi Oasis, ensuring proper communication between frontend and backend services using Railway's private networking.

## Environment Variables

### Frontend Service (Vue.js)

Set the following environment variable in Railway for the **frontend service**:

```bash
BACKEND_URL=http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}
```

**Important Notes:**
- `backend` refers to the **service name** of your Django backend in Railway
- `RAILWAY_PRIVATE_DOMAIN` is automatically provided by Railway for private networking
- `PORT` must be set manually as a service variable on the backend service (typically `8000`)
- Use `http://` protocol (not `https://`) for internal Railway communication

### Backend Service (Django)

Ensure the backend service has the following variable set:

```bash
PORT=8000
```

This allows the frontend to reference `${{backend.PORT}}` in the BACKEND_URL.

## How It Works

### Development (Local)
- Frontend runs on `http://localhost:5174` (Vite dev server)
- Backend runs on `http://localhost:8000` (Django dev server)
- Vite proxy configuration handles API requests (see `vite.config.ts`)
- API calls use relative paths like `/api/v1/auth/login/`

### Production (Railway)
- Frontend uses `BACKEND_URL` environment variable
- API calls are constructed as: `${BACKEND_URL}/api/v1/auth/login/`
- Example: `http://backend.railway.internal:8000/api/v1/auth/login/`
- Railway's private network handles routing between services

## Code Implementation

### Frontend API Configuration

The shared API client (`src/shared/services/api.ts`) automatically handles both environments:

```typescript
export const API_CONFIG = {
  BASE_URL: (() => {
    const backendUrl = import.meta.env.BACKEND_URL || import.meta.env.VITE_BACKEND_URL || ''
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
  
  const backendUrl = import.meta.env.BACKEND_URL || import.meta.env.VITE_BACKEND_URL || ''
  
  if (backendUrl) {
    return `${backendUrl}${path}`  // Production: full URL
  }
  return path  // Development: relative path (proxied)
}
```

### Auth Service Usage

All auth API calls use the shared pattern:

```typescript
import api, { buildApiUrl } from '@/shared/services/api'

// Example: Login
const response = await api.post(buildApiUrl(`${API_PATH}/login/`), credentials)

// This becomes:
// Development: POST /api/v1/auth/login/ (proxied to localhost:8000)
// Production: POST http://backend.railway.internal:8000/api/v1/auth/login/
```

## Verification

### Check Environment Variables in Railway

1. Go to your Railway project
2. Select the **frontend service**
3. Navigate to **Variables** tab
4. Confirm `BACKEND_URL` is set to: `http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}`

### Check Backend Service Name

1. Ensure your Django backend service is named **backend** in Railway
2. If it has a different name, update the `BACKEND_URL` variable accordingly

### Test API Calls

After deployment, check the browser console for API requests:
- They should show full URLs like `http://backend.railway.internal:8000/api/...`
- No CORS errors should appear (private network bypasses CORS)

## Troubleshooting

### Issue: API calls fail with network errors

**Solution:** Verify that:
1. `BACKEND_URL` is correctly set with the reference variable syntax
2. Backend service name matches the one used in `${{backend.RAILWAY_PRIVATE_DOMAIN}}`
3. Backend `PORT` variable is set to `8000`

### Issue: Backend not receiving requests

**Solution:** Ensure Django is configured to listen on IPv6:
- Railway's private network uses IPv6
- Django should bind to `::` (all interfaces) or specifically to IPv6
- Check your `Dockerfile` or start command

### Issue: CORS errors in production

**Solution:** 
- Private network communication should bypass CORS
- If you see CORS errors, the frontend might not be using the private network URL
- Verify `BACKEND_URL` is properly set and being used in API calls

## References

- [Railway Private Networking Documentation](https://docs.railway.app/reference/private-networking)
- [Railway Reference Variables](https://docs.railway.app/develop/variables#reference-variables)
