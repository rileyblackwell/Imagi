import axios from 'axios'
import { handleAPIError } from '../utils/errors'
import type { 
  AxiosInstance, 
  InternalAxiosRequestConfig 
} from 'axios'

// Constants for API configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || window.location.origin,
  DEFAULT_HEADERS: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

const api: AxiosInstance = axios.create({
  baseURL: `${API_CONFIG.BASE_URL}/api/v1`,
  withCredentials: true,
  headers: API_CONFIG.DEFAULT_HEADERS,
  timeout: API_CONFIG.TIMEOUT
})

// Update interceptor to handle CSRF token properly
api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  // Only fetch CSRF token for mutation requests
  if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
    if (!document.cookie.includes('csrftoken')) {
      await axios.get(`${API_CONFIG.BASE_URL}/api/v1/csrf/`)
    }
    
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1]

    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  
  return config
}, (error) => Promise.reject(handleAPIError(error)))

// Add response interceptor
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    // Implement retry logic for network errors or 5xx responses
    if (
      (error.message.includes('Network Error') || 
       (error.response?.status >= 500 && error.response?.status <= 599)) &&
      originalRequest._retry !== API_CONFIG.RETRY_ATTEMPTS
    ) {
      originalRequest._retry = (originalRequest._retry || 0) + 1
      
      // Exponential backoff
      const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, originalRequest._retry - 1)
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return api(originalRequest)
    }

    if (error.response?.status === 401) {
      // Handle authentication errors
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      console.error('Permission denied:', error.response.data)
    } else if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data)
    }
    return Promise.reject(handleAPIError(error))
  }
)

// Type guard function
export function isString(value: any): value is string {
  return typeof value === 'string';
}

// Export the API client as default export for services
export default api