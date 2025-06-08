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
      const response = await api.get(buildApiUrl(`${API_PATH}/csrf/`), {
        timeout: 30000 // Increase timeout for production environment
      })
      return response
    } catch (error) {
      console.error('🔑 Failed to get CSRF token:', error)
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    // Check if we're in a production environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    
    // Check if CSRF token exists in cookies first
    let csrfToken = getCookie('csrftoken')
    
    if (!csrfToken) {
      try {
        console.log('🔑 Fetching CSRF token...')
        await this.getCSRFToken()
        csrfToken = getCookie('csrftoken')
        
        if (!csrfToken) {
          console.warn('Failed to obtain CSRF token after fetch')
          // In production, if CSRF fetch fails, we can try to proceed without it
          // as Railway's proxy might handle CSRF differently
          if (isProd) {
            console.warn('Production: Proceeding without CSRF token')
            return null
          } else {
            throw new Error('Failed to obtain CSRF token')
          }
        }
      } catch (error) {
        console.error('Error fetching CSRF token:', error)
        
        // In production, don't fail the entire request if CSRF token can't be fetched
        // This allows the request to proceed and let the backend handle CSRF validation
        if (isProd) {
          console.warn('Production: CSRF token fetch failed, proceeding without it')
          return null
        } else {
          throw error
        }
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

      // Make sure we have a CSRF token before attempting login
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
    // Check if we're in production Railway environment
    const isProd = import.meta.env.PROD || import.meta.env.MODE === 'production'
    try {
      // Ensure CSRF token is available - but don't fail if we can't get it in production
      let csrfToken: string | null = null
      try {
        csrfToken = await this.ensureCSRFToken()
      } catch (error) {
        console.warn('CSRF token fetch failed:', error)
        if (!isProd) {
          throw new Error('Registration error: Could not obtain security token')
        }
        // In production, continue without CSRF token
        console.warn('Production: Continuing registration without CSRF token')
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
        environment: isProd ? 'production' : 'development',
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
        
        // If CSRF token was used and we get a CSRF error, try once more without CSRF in production
        if (isProd && csrfToken && (registrationError as any).response?.status === 403) {
          console.warn('🔄 Retrying registration without CSRF token in production');
          try {
            const retryHeaders = {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            };
            
            const retryResponse = await api.post(fullRequestUrl, userData, {
              headers: retryHeaders,
              timeout: 30000
            });
            
            console.log('✅ Registration successful on retry without CSRF');
            return { 
              data: {
                token: retryResponse.data.token || retryResponse.data.key,
                user: retryResponse.data.user || {}
              }
            }
          } catch (retryError) {
            console.error('❌ Registration retry also failed:', retryError);
            throw retryError;
          }
        }
        
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
