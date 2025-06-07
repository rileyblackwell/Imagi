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
      // Use the shared API client and build proper URL
      return await api.get(buildApiUrl(`${API_PATH}/csrf/`), {
        timeout: 10000 // 10 seconds timeout
      })
    } catch (error) {
      console.error('🔑 Failed to get CSRF token:', error)
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    // Check if we're in a production environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    const environment = isProd ? 'production' : 'development'
    
    // In production environment, bypass CSRF token requirement - handled by Nginx
    console.log('🔑 Environment:', environment)
    if (isProd) {
      console.log('🔑 AuthAPI: Production environment - bypassing CSRF token')
      return 'bypass'
    }
    
    // In development, check if CSRF token exists
    let csrfToken = getCookie('csrftoken')
    if (!csrfToken) {
      console.log('🔑 AuthAPI: No CSRF token found, fetching...')
      try {
        await this.getCSRFToken()
        csrfToken = getCookie('csrftoken')
        if (csrfToken) {
          console.log('🔑 AuthAPI: CSRF token obtained successfully')
        } else {
          console.error('🔑 AuthAPI: Failed to obtain CSRF token after fetch')
        }
      } catch (error) {
        console.error('🔑 AuthAPI: Error fetching CSRF token:', error)
        return null
      }
    } else {
      console.log('🔑 AuthAPI: CSRF token found in cookies')
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

      // Make sure we have a CSRF token before attempting login
      const csrfToken = await this.ensureCSRFToken();
      if (!csrfToken) {
        console.error('Could not obtain CSRF token');
        throw new Error('Authentication error: Could not obtain security token');
      }
      
      console.log('🔑 AuthAPI: Sending login request to:', buildApiUrl(`${API_PATH}/login/`));
      
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
    // Check if we're in production Railway environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    try {
      console.log('🔄 AuthAPI: Starting registration request')
      console.log('🌐 API Environment:', {
        apiPath: API_PATH,
        viteBackendEnv: import.meta.env.VITE_BACKEND_URL || 'Not defined',
        environment: import.meta.env.MODE,
        isProd
      })
      
      // Ensure CSRF token is available
      console.log('🔑 AuthAPI: Getting CSRF token')
      const csrfToken = await this.ensureCSRFToken()
      console.log('🔑 AuthAPI: CSRF token obtained:', csrfToken ? 'Yes' : 'No')
      if (!csrfToken && !isProd) {
        console.error('Could not obtain CSRF token')
        throw new Error('Registration error: Could not obtain security token');
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
      
      const startTime = performance.now();
      const fullRequestUrl = buildApiUrl(`${API_PATH}/register/`);
      
      console.log('🔄 AuthAPI: Making registration request to:', fullRequestUrl);
      
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      };
      
      if (csrfToken && csrfToken !== 'bypass') {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      try {
        // Use the shared API client
        const response = await api.post(fullRequestUrl, userData, {
          headers,
          timeout: 30000 // 30 seconds timeout
        })
        
        const duration = Math.round(performance.now() - startTime);
        console.log(`⏰ AuthAPI: Request completed in ${duration}ms`);
        
        // Log response status and structure (without sensitive data)
        console.log('✅ AuthAPI: Registration API response successful', {
          status: response.status,
          hasData: !!response.data,
          hasToken: !!(response.data?.token || response.data?.key),
          hasUser: !!response.data?.user
        })

        // Validate response format
        if (!response.data) {
          console.error('❌ AuthAPI: Empty response data')
          throw new Error('Invalid server response: Empty response')
        }
        
        if (!response.data.token && !response.data.key) {
          console.error('❌ AuthAPI: Missing token in response', response.data)
          throw new Error('Invalid server response: Missing token')
        }
        
        console.log('🔐 AuthAPI: Token received successfully')

        return { 
          data: {
            token: response.data.token || response.data.key,
            user: response.data.user || {}
          }
        }
      } catch (error) {
        // Connection issues during the request
        console.error('❌ AuthAPI: Error during API call', error)
        throw error
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
