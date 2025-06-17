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
  async getCSRFToken() {
    try {
      // Build the full URL and log it
      const fullUrl = buildApiUrl(`${API_PATH}/csrf/`)
      
      console.log('🔑 CSRF Token Request Details:')
      console.log('  Full URL:', fullUrl)
      console.log('  API_PATH:', API_PATH)
      console.log('  Environment:', import.meta.env.PROD ? 'production' : 'development')
      console.log('  VITE_BACKEND_URL:', import.meta.env.VITE_BACKEND_URL)
      console.log('  Base URL (api client):', api.defaults.baseURL)
      
      // Use the shared API client and build proper URL
      const response = await api.get(fullUrl, {
        timeout: 30000, // 30 seconds timeout for Railway environment
        headers: {
          'X-Request-Type': 'csrf-token',
          'X-Frontend-Service': 'vue-frontend'
        }
      })
      
      console.log('✅ CSRF token request successful')
      console.log('  Response status:', response.status)
      console.log('  Response headers:', response.headers)
      console.log('  Response data:', response.data)
      
      return response
    } catch (error: any) {
      console.error('❌ CSRF Token Request Failed:')
      console.error('  Error message:', error.message)
      console.error('  Error code:', error.code)
      console.error('  Request URL:', error.config?.url)
      console.error('  Request method:', error.config?.method)
      console.error('  Request headers:', error.config?.headers)
      console.error('  Request timeout:', error.config?.timeout)
      
      if (error.response) {
        console.error('  Response status:', error.response.status)
        console.error('  Response headers:', error.response.headers)
        console.error('  Response data:', error.response.data)
      } else {
        console.error('  No response received - network issue')
        
        // Railway-specific debugging
        if (import.meta.env.PROD) {
          console.error('🚂 Railway Environment Debug:')
          console.error('  Expected backend:', 'http://backend.railway.internal:8000')
          console.error('  Actual backend URL:', import.meta.env.VITE_BACKEND_URL)
          console.error('  API base URL:', api.defaults.baseURL)
          console.error('  Full request URL:', `${api.defaults.baseURL || ''}${buildApiUrl(`${API_PATH}/csrf/`)}`)
        }
      }
      
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    // Check if CSRF token exists in cookies first
    let csrfToken = getCookie('csrftoken')
    
    if (!csrfToken) {
      try {
        console.log('🔑 No CSRF token found in cookies, fetching from server...')
        console.log('  Request URL will be:', buildApiUrl(`${API_PATH}/csrf/`))
        
        await this.getCSRFToken()
        csrfToken = getCookie('csrftoken')
        
        if (!csrfToken) {
          console.warn('⚠️ Failed to obtain CSRF token after fetch')
          console.warn('  Cookies after request:', document.cookie)
          throw new Error('Failed to obtain CSRF token')
        } else {
          console.log('✅ CSRF token obtained successfully:', csrfToken.substring(0, 10) + '...')
        }
      } catch (error: any) {
        console.error('❌ Error fetching CSRF token:', error)
        
        // Railway-specific error handling
        if (import.meta.env.PROD && error.message.includes('Network error')) {
          console.error('🚂 Railway Network Error Detected:')
          console.error('  This may indicate a problem with Railway internal networking')
          console.error('  Frontend service cannot reach backend.railway.internal:8000')
          console.error('  Check Railway service configuration and network policies')
        }
        
        throw error
      }
    } else {
      console.log('✅ CSRF token found in cookies:', csrfToken.substring(0, 10) + '...')
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

      // Ensure CSRF token is available for all environments
      const csrfToken = await this.ensureCSRFToken();
      if (!csrfToken) {
        console.error('Could not obtain CSRF token');
        throw new Error('Authentication error: Could not obtain security token');
      }
      

      
      // Use the shared API client
      const response = await api.post(buildApiUrl(`${API_PATH}/login/`), credentials, {
        headers: csrfToken !== 'bypass' ? { 'X-CSRFToken': csrfToken } : {},
        timeout: 15000
      });

      // Validate response format
      if (!response.data) {
        throw new Error('Invalid server response: Empty response')
      }
      
      if (!response.data.token && !response.data.key) {
        console.error('Login response missing token:', response.data);
        throw new Error('Invalid server response: Missing token')
      }

      return { 
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error: any) {
      console.error('🔑 AuthAPI: Login error:', error)
      
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
      // Ensure CSRF token is available for all environments
      const csrfToken = await this.ensureCSRFToken()
      if (!csrfToken) {
        throw new Error('Registration error: Could not obtain security token')
      }
      
      // Validate username (basic check only, server will check uniqueness)
      if (!userData.username || userData.username.trim() === '') {
        throw new Error('Username is required')
      }
      
      // Validate password requirements
      if (!userData.password || userData.password.length < 8) {
        throw new Error('Password must be at least 8 characters long')
      }
      
      // Confirm password matches confirmation
      if (userData.password !== userData.password_confirmation) {
        throw new Error('Passwords do not match')
      }
      
      // Validate terms acceptance
      if (!userData.terms_accepted) {
        throw new Error('You must accept the terms and conditions')
      }

      // Validate email format only (remove uniqueness check)
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
      
      console.log('🔄 Attempting registration with headers:', {
        hasCSRF: !!csrfToken,
        environment: import.meta.env.PROD ? 'production' : 'development',
        url: fullRequestUrl
      });
      
      try {
        // Use the shared API client
        const response = await api.post(fullRequestUrl, userData, {
          headers,
          timeout: 30000 // 30 seconds timeout
        })
        
        console.log('✅ Registration successful');
        return { 
          data: {
            token: response.data.token || response.data.key,
            user: response.data.user || {}
          }
        }
      } catch (registrationError) {
        console.error('❌ Registration request failed:', registrationError);
        throw registrationError;
      }
    } catch (error: any) {
      console.error('❌ AuthAPI: Registration error:', error)
      
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
