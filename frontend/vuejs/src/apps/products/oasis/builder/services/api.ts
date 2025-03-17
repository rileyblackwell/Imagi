import axios from 'axios'
import { handleAPIError } from '../utils/errors'
import type { 
  AxiosInstance, 
  InternalAxiosRequestConfig 
} from 'axios'

// Constants for API configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  DEFAULT_HEADERS: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// Debug function for token retrieval
function getAuthToken() {
  try {
    const tokenData = localStorage.getItem('token')
    if (!tokenData) {
      console.debug('No token in localStorage')
      return null
    }
    
    const parsedToken = JSON.parse(tokenData)
    if (!parsedToken || !parsedToken.value) {
      console.debug('Invalid token format in localStorage')
      return null
    }
    
    const token = parsedToken.value
    const expires = parsedToken.expires
    
    // Check if token is expired
    if (expires && Date.now() > expires) {
      console.debug('Token is expired')
      localStorage.removeItem('token')
      return null
    }
    
    console.debug('Valid token found in localStorage')
    return token
  } catch (error) {
    console.error('Error parsing token:', error)
    return null
  }
}

// Alternate token retrieval from session cookie
function getAuthTokenFromCookie() {
  try {
    // Try to get a token from cookie
    const tokenCookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('authToken='))
      ?.split('=')[1]
    
    if (tokenCookie) {
      console.debug('Found auth token in cookie')
      return decodeURIComponent(tokenCookie)
    }
    return null
  } catch (error) {
    console.error('Error retrieving token from cookie:', error)
    return null
  }
}

// Create the API client with proper base URL
const api: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  withCredentials: true,
  headers: API_CONFIG.DEFAULT_HEADERS,
  timeout: API_CONFIG.TIMEOUT
})

// Immediately initialize API with token
const initializeApi = () => {
  // Set auth token from localStorage on initialization if available
  const token = getAuthToken() || getAuthTokenFromCookie()
  if (token) {
    api.defaults.headers.common['Authorization'] = `Token ${token}`
    console.debug('Set Authorization header on API client initialization')
  } else {
    console.debug('No valid token found during API initialization')
  }
};

// Call initialization immediately
initializeApi();

// Re-initialize API when the window gains focus to ensure token is fresh
window.addEventListener('focus', () => {
  console.debug('Window gained focus, refreshing API token')
  initializeApi();
});

// Update token on storage change (listen for auth state changes)
window.addEventListener('storage', (event) => {
  if (event.key === 'token') {
    if (event.newValue) {
      try {
        const tokenData = JSON.parse(event.newValue);
        if (tokenData && tokenData.value) {
          api.defaults.headers.common['Authorization'] = `Token ${tokenData.value}`;
          console.debug('Updated Authorization header from storage event');
        }
      } catch (error) {
        console.error('Error handling storage event:', error);
      }
    } else {
      // Token was removed
      delete api.defaults.headers.common['Authorization'];
      console.debug('Removed Authorization header due to token removal');
    }
  }
});

// Log all request configurations for debugging
const logRequestConfig = (config: InternalAxiosRequestConfig) => {
  console.debug('API Request Configuration:', {
    url: config.url,
    method: config.method,
    baseURL: config.baseURL,
    headers: config.headers,
    withCredentials: config.withCredentials,
    timeout: config.timeout
  })
}

// Update interceptor to handle authentication and CSRF token properly
api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  // Log the request configuration
  logRequestConfig(config)
  
  // Add authentication token if available
  try {
    // Check if Authorization header is already set
    if (!config.headers['Authorization']) {
      const token = getAuthToken() || getAuthTokenFromCookie()
      if (token) {
        config.headers['Authorization'] = `Token ${token}`
        console.debug('Added Authorization header from storage')
      } else {
        console.debug('No valid auth token found for request')
      }
    }
  } catch (error) {
    console.error('Error setting auth token:', error)
  }
  
  // Only fetch CSRF token for mutation requests
  if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
    if (!document.cookie.includes('csrftoken')) {
      console.debug('Fetching CSRF token')
      try {
        await axios.get(`${API_CONFIG.BASE_URL}/api/v1/csrf/`)
      } catch (error) {
        console.error('Error fetching CSRF token:', error)
      }
    }
    
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1]

    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken
      console.debug('Added X-CSRFToken header')
    } else {
      console.debug('No CSRF token found in cookies')
    }
  }
  
  return config
}, (error) => Promise.reject(handleAPIError(error)))

// Add response interceptor
api.interceptors.response.use(
  response => {
    // Check if response is HTML instead of expected JSON
    const contentType = response.headers['content-type'] || '';
    if ((contentType.includes('text/html') || contentType.includes('text/plain')) && 
        !contentType.includes('application/json')) {
      
      // If response data is a string and starts with DOCTYPE, it's likely an HTML error page
      if (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE')) {
        console.error('Received HTML response instead of JSON:', {
          url: response.config?.url,
          method: response.config?.method,
          status: response.status,
          contentType,
          dataPreview: response.data.substring(0, 100) + '...'
        });
        
        // Create a standardized error response
        return Promise.reject({
          response: {
            status: response.status,
            statusText: 'Invalid Response Format',
            data: {
              detail: 'The server returned HTML instead of JSON. This usually indicates a server error or authentication issue.'
            }
          },
          message: 'Received HTML response instead of JSON',
          isHtmlResponse: true
        });
      }
    }
    
    // Log successful responses
    console.debug('API Response:', {
      url: response.config?.url,
      method: response.config?.method,
      status: response.status,
      statusText: response.statusText,
      dataSize: response.data ? JSON.stringify(response.data).length : 0,
      dataType: typeof response.data,
      isArray: Array.isArray(response.data),
      headers: response.headers
    })
    return response
  },
  async error => {
    // Check if this is an HTML error that was caught by our interceptor
    if (error.isHtmlResponse) {
      console.error('HTML response error (intercepted):', error.message);
      return Promise.reject(error);
    }
    
    console.debug('API error intercepted:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
      stack: error.stack?.split('\n').slice(0, 3).join('\n') // Show first 3 lines of stack
    })
    
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
      console.debug(`Retrying request (attempt ${originalRequest._retry}/${API_CONFIG.RETRY_ATTEMPTS}) after ${delay}ms`)
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return api(originalRequest)
    }

    if (error.response?.status === 401) {
      // Handle authentication errors
      console.error('Authentication error:', error.response.data)
      
      // Check if the request already had an Authorization header
      if (originalRequest.headers['Authorization']) {
        console.debug('Request had Authorization header but still got 401')
      }
      
      // Try to refresh the token or redirect if needed
      const token = getAuthToken()
      if (!token) {
        console.debug('No valid token for unauthorized request')
      }
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