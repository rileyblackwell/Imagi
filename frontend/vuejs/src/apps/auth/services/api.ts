import api, { buildApiUrl } from '@/shared/services/api'
import type { 
  User, 
  LoginCredentials, 
  AuthResponse, 
  UserRegistrationData 
} from '@/apps/auth/types/auth'

// API Configuration
const API_PATH = '/api/v1/auth'

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

let logoutPromise: Promise<any> | null = null

export const AuthAPI = {
  async healthCheck() {
    const startTime = Date.now()
    const fullUrl = buildApiUrl(`${API_PATH}/health/`)
    
    try {
      // Detailed diagnostic information
      const diagnostics = {
        timestamp: new Date().toISOString(),
        environment: import.meta.env.PROD ? 'production' : 'development',
        url: {
          requested: fullUrl,
          apiPath: API_PATH,
          isRelative: !fullUrl.startsWith('http'),
          protocol: fullUrl.startsWith('http') ? new URL(fullUrl).protocol : 'relative'
        },
        config: {
          baseURL: api.defaults.baseURL || 'not set',
          backendUrl: import.meta.env.BACKEND_URL || 'not set',
          viteBackendUrl: import.meta.env.VITE_BACKEND_URL || 'not set',
          timeout: 10000,
          withCredentials: api.defaults.withCredentials
        },
        browser: {
          userAgent: navigator.userAgent,
          online: navigator.onLine,
          location: window.location.href,
          origin: window.location.origin
        }
      }
      
      console.log('🏥 Auth Health Check - Starting:', diagnostics)
      
      const response = await api.get(fullUrl, {
        timeout: 10000,
        headers: {
          'X-Request-Type': 'health-check',
          'X-Frontend-Service': 'vue-frontend'
        }
      })
      
      const duration = Date.now() - startTime
      
      console.log('✅ Auth API health check passed:', {
        status: response.status,
        duration: `${duration}ms`,
        data: response.data,
        headers: {
          contentType: response.headers['content-type'],
          server: response.headers['server'],
          date: response.headers['date']
        }
      })
      
      return response
    } catch (error: any) {
      const duration = Date.now() - startTime
      
      // Enhanced error diagnostics
      const errorDetails = {
        timestamp: new Date().toISOString(),
        duration: `${duration}ms`,
        errorType: error.name || 'Unknown',
        message: error.message,
        
        // Request details
        request: {
          url: fullUrl,
          method: 'GET',
          baseURL: error.config?.baseURL || api.defaults.baseURL || 'not set',
          fullRequestUrl: error.config?.url ? `${error.config.baseURL || ''}${error.config.url}` : fullUrl,
          headers: error.config?.headers || {}
        },
        
        // Response details (if any)
        response: error.response ? {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: {
            contentType: error.response.headers['content-type'],
            server: error.response.headers['server'],
            date: error.response.headers['date']
          }
        } : null,
        
        // Network error details
        network: {
          code: error.code,
          isNetworkError: !error.response,
          isTimeout: error.code === 'ECONNABORTED',
          browserOnline: navigator.onLine
        },
        
        // Environment context
        environment: {
          isProd: import.meta.env.PROD,
          mode: import.meta.env.MODE,
          baseURL: api.defaults.baseURL,
          backendUrl: import.meta.env.BACKEND_URL || 'not set',
          viteBackendUrl: import.meta.env.VITE_BACKEND_URL || 'not set'
        },
        
        // Axios error details
        axios: {
          isAxiosError: error.isAxiosError,
          code: error.code,
          stack: error.stack?.split('\n').slice(0, 3).join('\n')
        }
      }
      
      console.error('❌ Auth API health check failed:', errorDetails)
      
      // Provide user-friendly error message based on failure type
      let userMessage = error.message
      
      if (!error.response && !navigator.onLine) {
        userMessage = 'No internet connection detected. Please check your network.'
      } else if (!error.response) {
        userMessage = `Network error: Unable to reach backend server at ${fullUrl}. The server may be down or unreachable.`
      } else if (error.response.status >= 500) {
        userMessage = `Server error (${error.response.status}): The backend server encountered an error.`
      } else if (error.response.status === 404) {
        userMessage = `Health check endpoint not found (404) at ${fullUrl}. The API route may not be configured.`
      } else if (error.code === 'ECONNABORTED') {
        userMessage = `Request timeout after ${duration}ms. The server is taking too long to respond.`
      }
      
      // Attach enhanced error details to the error object
      error.diagnostics = errorDetails
      error.userMessage = userMessage
      
      throw error
    }
  },

  async getCSRFToken() {
    try {
      const fullUrl = buildApiUrl(`${API_PATH}/csrf/`)
      const response = await api.get(fullUrl, {
        timeout: 30000,
        headers: {
          'X-Request-Type': 'csrf-token',
          'X-Frontend-Service': 'vue-frontend'
        }
      })
      return response
    } catch (error: any) {
      console.error('CSRF token request failed:', error.message)
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    let csrfToken = getCookie('csrftoken')
    
    if (!csrfToken) {
      try {
        await this.getCSRFToken()
        csrfToken = getCookie('csrftoken')
        
        if (!csrfToken) {
          throw new Error('Failed to obtain CSRF token')
        }
      } catch (error: any) {
        console.error('Error fetching CSRF token:', error.message)
        throw error
      }
    }
    
    return csrfToken
  },

  async init(): Promise<{ data: { isAuthenticated: boolean; user: User } }> {
    return await api.get(buildApiUrl(`${API_PATH}/init/`))
  },

  async login(credentials: LoginCredentials): Promise<{ data: AuthResponse }> {
    try {
      if (!credentials?.username || !credentials?.password) {
        throw new Error('Username and password are required')
      }

      const csrfToken = await this.ensureCSRFToken();
      if (!csrfToken) {
        throw new Error('Authentication error: Could not obtain security token');
      }
      
      const response = await api.post(buildApiUrl(`${API_PATH}/login/`), credentials, {
        headers: csrfToken !== 'bypass' ? { 'X-CSRFToken': csrfToken } : {},
        timeout: 15000
      });

      if (!response.data) {
        throw new Error('Invalid server response: Empty response')
      }
      
      if (!response.data.token && !response.data.key) {
        throw new Error('Invalid server response: Missing token')
      }

      return { 
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error: any) {
      if (error.response?.status === 400) {
        const errorMessage = error.response.data?.non_field_errors?.[0] || 
                           error.response.data?.detail || 
                           'Invalid username or password'
        throw new Error(errorMessage)
      } else if (error.response?.status === 401) {
        throw new Error('Invalid username or password')
      } else if (error.response?.status === 429) {
        throw new Error('Too many login attempts. Please try again later.')
      } else if (!error.response) {
        throw new Error('Network Error: Unable to connect to server')
      }
      
      throw error
    }
  },

  async register(userData: UserRegistrationData): Promise<{ data: AuthResponse }> {
    try {
      const csrfToken = await this.ensureCSRFToken()
      if (!csrfToken) {
        throw new Error('Registration error: Could not obtain security token')
      }
      
      if (!userData.username || userData.username.trim() === '') {
        throw new Error('Username is required')
      }
      
      if (!userData.password || userData.password.length < 8) {
        throw new Error('Password must be at least 8 characters long')
      }
      
      if (userData.password !== userData.password_confirmation) {
        throw new Error('Passwords do not match')
      }
      
      if (!userData.terms_accepted) {
        throw new Error('You must accept the terms and conditions')
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!userData.email || !emailRegex.test(userData.email)) {
        throw new Error('Please enter a valid email address')
      }
      
      const fullRequestUrl = buildApiUrl(`${API_PATH}/register/`);
      
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      };
      
      if (csrfToken && csrfToken !== 'bypass') {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      const response = await api.post(fullRequestUrl, userData, {
        headers,
        timeout: 30000
      })
      
      return { 
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error: any) {
      // Handle validation errors from server
      if (error.response?.status === 400) {
        const errorData = error.response.data
        
        // Handle field-specific errors
        if (errorData.username) {
          throw new Error(`Username: ${errorData.username[0]}`)
        }
        if (errorData.email) {
          throw new Error(`Email: ${errorData.email[0]}`)
        }
        if (errorData.password) {
          throw new Error(`Password: ${errorData.password[0]}`)
        }
        if (errorData.non_field_errors) {
          throw new Error(errorData.non_field_errors[0])
        }
        
        // Generic validation error
        throw new Error('Please check your input and try again')
      }
      
      // Handle other HTTP errors
      if (error.response?.status === 409) {
        throw new Error('An account with this email or username already exists')
      }
      
      if (error.response?.status === 429) {
        throw new Error('Too many registration attempts. Please try again later.')
      }
      
      // Handle network errors
      if (!error.response) {
        throw new Error('Network Error: Unable to connect to server')
      }
      
      // Re-throw other errors
      throw error
    }
  },

  async logout(): Promise<void> {
    if (logoutPromise) {
      return logoutPromise
    }

    try {
      logoutPromise = api.post(buildApiUrl(`${API_PATH}/logout/`), {})
      await logoutPromise
      
      localStorage.removeItem('token')
      // The shared API client will handle removing the Authorization header
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async updateUser(userData: Partial<User>): Promise<{ data: User }> {
    const response = await api.patch(buildApiUrl(`${API_PATH}/user/`), userData)
    return response
  }
}
