/*
 * Imagi Frontend Configuration
 * 
 * PROXY ARCHITECTURE:
 * - Development: Vite dev server → Django backend, both on harness-assigned ports
 * - Production: Nginx (imagi.up.railway.app) → Django backend (backend.railway.internal:8000)
 *
 * ENVIRONMENT SETUP:
 * - Development: nothing to set. Each worktree's backend publishes its port and
 *   vite.config.ts finds it, so concurrent Claude Code instances stay isolated.
 *   VITE_BACKEND_URL still overrides if you need to point somewhere specific.
 * - Production: Set VITE_BACKEND_URL=http://backend.railway.internal:8000 in environment
 *
 * All API calls use relative URLs (/api/*) and are proxied by:
 * - Vite dev server in development (see vite.config.ts)
 * - Nginx in production (configured via Dockerfile)
 */

const config = {
  // API Configuration
  apiUrl: (() => {
    // Always use relative URLs for API requests
    // Development: Vite dev server proxies /api/* to http://localhost:8000
    // Production: Nginx proxies /api/* to http://backend.railway.internal:8000
    return '/api'
  })(),
  
  // Authentication Configuration
  auth: {
    tokenKey: 'token',
    refreshTokenKey: 'refreshToken',
    tokenType: 'Bearer'
  },
  
  // App Configuration
  app: {
    name: 'Imagi',
    description: 'Natural language to code platform',
    version: '1.0.0'
  },

  // Payment Configuration
  payments: {
    stripePublishableKey: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || ''
  },
  
  // Feature Flags
  features: {
    enablePasswordReset: true,
    enableSocialAuth: false,
    enableTwoFactorAuth: false
  }
}

export default config 