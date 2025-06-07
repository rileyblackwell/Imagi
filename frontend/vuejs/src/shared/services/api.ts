import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

// Centralized API Configuration
// This ensures all services use the same configuration for API calls
export const API_CONFIG = {
  // Always use relative URLs - proxy handles routing in both dev and production
  // Development: Vite dev server proxies /api/* to VITE_BACKEND_URL
  // Production: Nginx proxies /api/* to backend service
  BASE_URL: '',
  DEFAULT_HEADERS: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  },
  TIMEOUT: 60000, // 1 minute timeout for AI processing
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// Helper functions for token management
function getAuthToken(): string | null {
  try {
    const tokenData = localStorage.getItem('token')
    if (!tokenData) return null
    
    const parsedToken = JSON.parse(tokenData)
    if (!parsedToken?.value) return null
    
    // Check if token is expired
    if (parsedToken.expires && Date.now() > parsedToken.expires) {
      localStorage.removeItem('token')
      return null
    }
    
    return parsedToken.value
  } catch (error) {
    console.error('Error parsing auth token:', error)
    localStorage.removeItem('token')
    return null
  }
}

function getCSRFToken(): string | null {
  try {
    return document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1] || null
  } catch (error) {
    console.error('Error getting CSRF token:', error)
    return null
  }
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

// Request interceptor for authentication and CSRF
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Add authentication token
    const token = getAuthToken()
    if (token && !config.headers['Authorization']) {
      config.headers['Authorization'] = `Token ${token}`
    }
    
    // Add CSRF token for mutation requests
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
      const csrfToken = getCSRFToken()
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      } else {
        // Fetch CSRF token if not available
        try {
          await axios.get('/api/v1/csrf/', { withCredentials: true })
          const newCSRFToken = getCSRFToken()
          if (newCSRFToken) {
            config.headers['X-CSRFToken'] = newCSRFToken
          }
        } catch (error) {
          console.warn('Failed to fetch CSRF token:', error)
        }
      }
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    // Check if response is HTML instead of expected JSON
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('text/html') && !contentType.includes('application/json')) {
      if (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE')) {
        console.error('Received HTML response instead of JSON:', {
          url: response.config?.url,
          method: response.config?.method,
          status: response.status
        })
        throw new Error('Server returned HTML instead of JSON. This may indicate a proxy or server configuration issue.')
      }
    }
    return response
  },
  async (error) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      console.warn('Unauthorized request - clearing auth data')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
      
      // Only redirect if not already on auth page
      if (!window.location.pathname.startsWith('/auth/')) {
        window.location.href = '/auth/login'
      }
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message)
      return Promise.reject(new Error('Network error: Unable to connect to server'))
    }
    
    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout:', error.config?.url)
      return Promise.reject(new Error('Request timeout'))
    }
    
    return Promise.reject(error)
  }
)

// Export the configured API client
export default api

// Export additional utilities for services that need them
export { getAuthToken, getCSRFToken }

// Helper function to build API URLs consistently
export function buildApiUrl(path: string): string {
  // Ensure path starts with /api/ for consistent routing
  if (!path.startsWith('/api/')) {
    path = path.startsWith('/') ? `/api${path}` : `/api/${path}`
  }
  
  // Always use relative URLs - this works in both development and production
  // Development: Vite dev server proxies /api/* to VITE_BACKEND_URL (localhost:8000)
  // Production: Nginx proxies /api/* to backend.railway.internal:8000
  return path
} 