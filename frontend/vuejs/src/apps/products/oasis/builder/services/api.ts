import api, { getAuthToken } from '@/shared/services/api'
import { handleAPIError } from '../utils/errors'
import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosError } from 'axios'

// DEPRECATED: This builder-specific API client is no longer used
// All services should use the shared API client from '@/shared/services/api'
// This file is kept for backward compatibility but will be removed in future versions

// Constants for API configuration - keeping timeout separate for longer AI processing
export const API_CONFIG = {
  TIMEOUT: 60000, // 60 seconds (increased from 30 to handle longer AI model processing)
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// Create a custom API instance with longer timeout for AI operations
// This extends the shared API client with builder-specific configurations
const createBuilderApi = (): AxiosInstance => {
  // Use axios.create instead of api.create
  const builderApi = axios.create({
    ...api.defaults,
    timeout: API_CONFIG.TIMEOUT
  })
  
  // Add builder-specific request interceptor for debugging
  builderApi.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // Log request configuration for debugging
      console.debug('Builder API Request Configuration:', {
        url: config.url,
        method: config.method,
        headers: config.headers,
        timeout: config.timeout
      })
      return config
    },
    (error: AxiosError) => Promise.reject(handleAPIError(error))
  )

  // Add builder-specific response interceptor with retry logic
  builderApi.interceptors.response.use(
    (response: any) => {
      // Check if response is HTML instead of expected JSON
      const contentType = response.headers['content-type'] || '';
      if ((contentType.includes('text/html') || contentType.includes('text/plain')) && 
          !contentType.includes('application/json')) {
        
        // If response data is a string and starts with DOCTYPE, it's likely an HTML error page
        if (typeof response.data === 'string' && 
            (response.data.trim().startsWith('<!DOCTYPE') || 
             response.data.trim().startsWith('<html'))) {
          console.error('Received HTML response instead of JSON:', {
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
    async (error: AxiosError) => {
      const originalRequest = error.config as any
      
      // Implement retry logic for network errors or 5xx responses
      if (
        originalRequest && 
        (error.message.includes('Network Error') || 
         (error.response && error.response.status >= 500 && error.response.status <= 599)) &&
        originalRequest._retry !== API_CONFIG.RETRY_ATTEMPTS
      ) {
        originalRequest._retry = (originalRequest._retry || 0) + 1
        
        // Exponential backoff
        const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, originalRequest._retry - 1)
        console.debug(`Retrying request (attempt ${originalRequest._retry}/${API_CONFIG.RETRY_ATTEMPTS}) after ${delay}ms`)
        await new Promise(resolve => setTimeout(resolve, delay))
        
        // Ensure the request config is valid before retrying
        if (originalRequest) {
          return builderApi(originalRequest)
        }
      }

      if (error.response && error.response.status === 401) {
        // Handle authentication errors
        console.error('Authentication error:', error.response.data)
        
        // Check if the request already had an Authorization header
        if (originalRequest && originalRequest.headers && originalRequest.headers['Authorization']) {
          console.debug('Request had Authorization header but still got 401')
        }
        
        // Try to refresh the token or redirect if needed
        const token = getAuthToken()
        if (!token) {
          console.debug('No valid token for unauthorized request')
        }
        
        // Trigger auth refresh event that other components can listen for
        window.dispatchEvent(new CustomEvent('auth:refresh-needed'));
      } else if (error.response && error.response.status === 403) {
        console.error('Permission denied:', error.response.data)
      } else if (error.response && error.response.status === 404) {
        console.error('Resource not found:', error.response.data)
      } else if (error.response && error.response.status >= 500) {
        console.error('Server error:', {
          status: error.response.status,
          url: error.config?.url,
          method: error.config?.method,
          data: error.response.data
        })
      }
      return Promise.reject(handleAPIError(error))
    }
  )
  
  return builderApi
}

// Create the builder API instance
const builderApi = createBuilderApi()

// Export the builder API instance as the default export
export default builderApi

// Helper function to check if a value is a string
export function isString(value: any): value is string {
  return typeof value === 'string'
}