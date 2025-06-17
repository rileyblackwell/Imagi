import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'

// Centralized API Configuration for Railway environment
// This ensures all services use the same configuration for API calls
// IMPORTANT: This is the SINGLE shared API client used by ALL frontend services
// including builder workspace, dashboard, payments, auth, etc.
export const API_CONFIG = {
  // Base URL configuration for Railway
  BASE_URL: (() => {
    // Check if we're in production (Railway environment)
    const isProduction = import.meta.env.PROD
    const backendUrl = import.meta.env.VITE_BACKEND_URL
    
    console.log('🔧 API Configuration:')
    console.log('  Environment:', isProduction ? 'production' : 'development')
    console.log('  VITE_BACKEND_URL:', backendUrl)
    
    if (isProduction && backendUrl) {
      // Production: Use the backend URL directly for Railway internal networking
      console.log('🚂 Using Railway backend URL:', backendUrl)
      return backendUrl
    } else if (isProduction) {
      // Production fallback: Use relative URLs with nginx proxy
      console.log('🚂 Using relative URLs for Railway nginx proxy')
      return ''
    } else {
      // Development: Use relative URLs with Vite proxy
      console.log('🛠️ Using relative URLs for Vite dev server proxy')
      return ''
    }
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

// Enhanced request interceptor for Railway debugging
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Enhanced logging for Railway debugging
    console.log('📤 API Request:')
    console.log('  URL:', config.url)
    console.log('  Method:', config.method?.toUpperCase())
    console.log('  Base URL:', config.baseURL)
    console.log('  Full URL:', `${config.baseURL || ''}${config.url || ''}`)
    console.log('  Headers:', config.headers)
    
    // Add environment info to headers for backend debugging
    config.headers['X-Frontend-Environment'] = import.meta.env.PROD ? 'production' : 'development'
    config.headers['X-Frontend-Version'] = '1.0.0'
    
    return config
  },
  (error) => {
    console.error('❌ Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Enhanced response interceptor for Railway debugging
api.interceptors.response.use(
  (response) => {
    // Enhanced response logging
    console.log('📥 API Response:')
    console.log('  Status:', response.status)
    console.log('  URL:', response.config.url)
    console.log('  Headers:', response.headers)
    
    // Check if response is HTML instead of expected JSON
    const contentType = response.headers['content-type'] || ''
    if (contentType.includes('text/html') && !contentType.includes('application/json')) {
      if (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE')) {
        console.error('❌ Received HTML response instead of JSON:', {
          url: response.config?.url,
          method: response.config?.method,
          status: response.status,
          contentType
        })
        throw new Error('Server returned HTML instead of JSON. This may indicate a proxy or server configuration issue.')
      }
    }
    return response
  },
  async (error) => {
    // Enhanced error logging for Railway debugging
    console.error('❌ API Error Details:')
    console.error('  Message:', error.message)
    console.error('  Code:', error.code)
    console.error('  URL:', error.config?.url)
    console.error('  Method:', error.config?.method)
    console.error('  Base URL:', error.config?.baseURL)
    console.error('  Full URL:', `${error.config?.baseURL || ''}${error.config?.url || ''}`)
    
    if (error.response) {
      console.error('  Response Status:', error.response.status)
      console.error('  Response Headers:', error.response.headers)
      console.error('  Response Data:', error.response.data)
    } else {
      console.error('  No response received - possible network issue')
      console.error('  Network Error Details:', {
        timeout: error.config?.timeout,
        withCredentials: error.config?.withCredentials,
        headers: error.config?.headers
      })
    }
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      console.warn('⚠️ Unauthorized request - clearing auth data')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete api.defaults.headers.common['Authorization']
      
      // Only redirect if not already on auth page
      if (!window.location.pathname.startsWith('/auth/')) {
        window.location.href = '/auth/login'
      }
    }
    
    // Handle 404 Not Found specifically for project resources
    if (error.response?.status === 404 && error.config?.url?.includes('/projects/')) {
      console.warn(`⚠️ Project resource not found: ${error.config.url}`)
      // Don't log the full error for project 404s as they're often expected
      // (e.g., when a project is deleted or user navigates to non-existent project)
    }
    
    // Handle network errors with more specific messaging
    if (!error.response) {
      console.error('🌐 Network error - no response received')
      const isProduction = import.meta.env.PROD
      const backendUrl = import.meta.env.VITE_BACKEND_URL
      
      if (isProduction) {
        console.error('🚂 Railway environment debug info:')
        console.error('  VITE_BACKEND_URL:', backendUrl)
        console.error('  Expected backend:', 'http://backend.railway.internal:8000')
      }
      
      return Promise.reject(new Error('Network error: Unable to connect to server'))
    }
    
    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ Request timeout:', error.config?.url)
      return Promise.reject(new Error('Request timeout'))
    }
    
    return Promise.reject(error)
  }
)

// Export the configured API client
export default api

// Helper function to build API URLs consistently for Railway
export function buildApiUrl(path: string): string {
  // Ensure path starts with /api/ for consistent routing
  if (!path.startsWith('/api/')) {
    path = path.startsWith('/') ? `/api${path}` : `/api/${path}`
  }
  
  const isProduction = import.meta.env.PROD
  const backendUrl = import.meta.env.VITE_BACKEND_URL
  
  console.log('🔗 Building API URL:')
  console.log('  Input path:', path)
  console.log('  Environment:', isProduction ? 'production' : 'development')
  console.log('  Backend URL:', backendUrl)
  
  if (isProduction && backendUrl) {
    // Production with backend URL: Use absolute URL for Railway internal networking
    const fullUrl = `${backendUrl}${path}`
    console.log('  🚂 Railway absolute URL:', fullUrl)
    return fullUrl
  } else {
    // Development or production with nginx proxy: Use relative URLs
    console.log('  📍 Relative URL:', path)
    return path
  }
} 