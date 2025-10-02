import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

// Centralized API Configuration for Railway environment
// This ensures all services use the same configuration for API calls
// IMPORTANT: This is the SINGLE shared API client used by ALL frontend services
// including builder workspace, dashboard, payments, auth, etc.
export const API_CONFIG = {
  // Base URL configuration
  // In production (Railway): Use empty string for relative URLs (Nginx proxies to backend)
  // In development: Use VITE_BACKEND_URL or empty string (Vite dev proxy handles it)
  // Note: BACKEND_URL is used by Nginx, not by browser JavaScript
  BASE_URL: (() => {
    const isProduction = import.meta.env.PROD
    const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
    
    // In production, always use relative URLs (Nginx proxy handles routing)
    if (isProduction) {
      return ''
    }
    
    // In development, use VITE_BACKEND_URL if set, otherwise use relative URLs (Vite proxy)
    return backendUrl ? String(backendUrl).replace(/\/+$/, '') : ''
  })(),
  DEFAULT_HEADERS: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  TIMEOUT: 60000, // 1 minute timeout for AI processing
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// Helper: read a cookie by name (used for CSRF)
function getCookie(name: string): string | null {
  let cookieValue: string | null = null
  if (typeof document !== 'undefined' && document.cookie) {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Create the centralized API client
const api: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  withCredentials: true,
  headers: {
    ...API_CONFIG.DEFAULT_HEADERS,
    'X-API-Client': 'Imagi-Frontend-Vue'
  }
})

// Initialize Authorization header from localStorage if present
try {
  const raw = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  if (raw) {
    const parsed = JSON.parse(raw)
    const token = typeof parsed === 'string' ? parsed : parsed?.value
    const expires = parsed?.expires
    if (token && (!expires || Date.now() < Number(expires))) {
      api.defaults.headers.common['Authorization'] = `Token ${token}`
    }
  }
} catch (e) {
  // ignore
}

// Enhanced request interceptor for Railway debugging
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Attach Authorization header from localStorage if not already present
    try {
      if (!config.headers['Authorization']) {
        const raw = typeof window !== 'undefined' ? localStorage.getItem('token') : null
        if (raw) {
          // Parse token from JSON format used by the auth store
          let token: string | null = null
          try {
            const parsed = JSON.parse(raw)
            token = typeof parsed === 'string' ? parsed : parsed?.value
            const expires = parsed?.expires
            if (expires && Date.now() > Number(expires)) {
              token = null
            }
          } catch {
            token = raw
          }
          if (token) {
            config.headers['Authorization'] = `Token ${token}`
          }
        }
      }
    } catch (_) {}

    // Attach CSRF token for unsafe methods when using session authentication
    const method = (config.method || 'get').toLowerCase()
    const unsafe = ['post', 'put', 'patch', 'delete'].includes(method)
    if (unsafe) {
      const csrfToken = getCookie('csrftoken')
      if (csrfToken && !config.headers['X-CSRFToken']) {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }

    // Add environment info to headers for backend debugging
    config.headers['X-Frontend-Environment'] = import.meta.env.PROD ? 'production' : 'development'
    config.headers['X-Frontend-Version'] = '1.0.0'
    
    return config
  },
  (error) => Promise.reject(error)
)

// Enhanced response interceptor for Railway debugging
api.interceptors.response.use(
  (response) => {
    // Check if response is HTML instead of expected JSON
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('text/html') && !contentType.includes('application/json')) {
      if (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE')) {
        throw new Error('Server returned HTML instead of JSON')
      }
    }
    return response
  },
  async (error) => {
    // Handle 401 Unauthorized more gracefully: do NOT auto-clear auth state.
    // Let route guards and the auth store decide next steps to avoid random logouts.
    if (error.response?.status === 401) {
      try {
        window.dispatchEvent(new CustomEvent('imagi:auth-unauthorized', { detail: { url: error.config?.url } }))
      } catch {}
    }
    
    if (!error.response) {
      return Promise.reject(new Error('Network error: Unable to connect to server'))
    }
    
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Request timeout'))
    }
    
    return Promise.reject(error)
  }
)

// Export the configured API client
export default api

// Helper function to build API URLs consistently
// Architecture:
//   - Browser → Relative URL → Nginx → Railway Private Network → Backend
// Production (Railway): Uses relative paths (e.g., /api/v1/auth/login/)
//   - Nginx proxies these to backend.railway.internal:8000 via Railway private network
// Development: Uses relative paths or VITE_BACKEND_URL
//   - Vite dev server proxies to localhost:8000
export function buildApiUrl(path: string): string {
  // Ensure path starts with /api/
  if (!path.startsWith('/api/')) {
    path = path.startsWith('/') ? `/api${path}` : `/api/${path}`
  }
  
  const isProduction = import.meta.env.PROD
  const backendUrl = import.meta.env.VITE_BACKEND_URL || ''
  
  // In production, always use relative paths (Nginx handles proxying)
  if (isProduction) {
    return path
  }
  
  // In development, use full URL if VITE_BACKEND_URL is set, otherwise relative path
  if (backendUrl) {
    return `${backendUrl}${path}`
  }
  return path
}