import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

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
// Uses relative /api path in both dev and prod:
// - Dev: Vite proxy forwards to localhost:8000
// - Prod: Nginx forwards to backend service
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 60000,
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
})


// Request interceptor
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Attach Authorization header from localStorage
    try {
      if (!config.headers['Authorization']) {
        const raw = typeof window !== 'undefined' ? localStorage.getItem('token') : null
        if (raw) {
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

    // Attach CSRF token for unsafe methods
    const method = (config.method || 'get').toLowerCase()
    const unsafe = ['post', 'put', 'patch', 'delete'].includes(method)
    if (unsafe) {
      const csrfToken = getCookie('csrftoken')
      if (csrfToken && !config.headers['X-CSRFToken']) {
        config.headers['X-CSRFToken'] = csrfToken
      }
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle 401 Unauthorized
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

// CSRF token helper
export async function getCsrfToken(): Promise<void> {
  try {
    await api.get('/v1/auth/csrf/')
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error)
  }
}

// Export the configured API client
export default api