import api from '@/shared/services/api'
import type { 
  User, 
  LoginCredentials, 
  AuthResponse, 
  UserRegistrationData 
} from '@/apps/auth/types/auth'
import axios from 'axios'

// API Configuration
const API_PATH = '/v1/auth'

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
      const response = await axios.get(`http://backend.railway.internal:8000/${API_PATH}/csrf/`, {
        timeout: 30000,
        headers: {
          'X-Request-Type': 'csrf-token',
          'X-Frontend-Service': 'vue-frontend'
        }
      })
      return response
    } catch (error: any) {
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
        throw error
      }
    }
    
    return csrfToken
  },

  async init(): Promise<{ data: { isAuthenticated: boolean; user: User } }> {
    return await api.get(`${API_PATH}/init/`)
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
      
      const response = await api.post(`${API_PATH}/login/`, credentials, {
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

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!userData.email || !emailRegex.test(userData.email)) {
        throw new Error('Please enter a valid email address')
      }
      
      const fullRequestUrl = `${API_PATH}/register/`;
      
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      };
      
      if (csrfToken && csrfToken !== 'bypass') {
        headers['X-CSRFToken'] = csrfToken;
      }
      
      // Only send fields that backend expects
      const registrationData = {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        password_confirmation: userData.password_confirmation
      }
      
      const response = await api.post(fullRequestUrl, registrationData, {
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
          const usernameError = Array.isArray(errorData.username) ? errorData.username[0] : errorData.username
          throw new Error(`Username: ${usernameError}`)
        }
        if (errorData.email) {
          const emailError = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email
          throw new Error(`Email: ${emailError}`)
        }
        if (errorData.password) {
          const passwordError = Array.isArray(errorData.password) ? errorData.password[0] : errorData.password
          throw new Error(`Password: ${passwordError}`)
        }
        if (errorData.password_confirmation) {
          const confirmError = Array.isArray(errorData.password_confirmation) ? errorData.password_confirmation[0] : errorData.password_confirmation
          throw new Error(`${confirmError}`)
        }
        if (errorData.non_field_errors) {
          const nonFieldError = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors
          throw new Error(nonFieldError)
        }
        if (errorData.error) {
          throw new Error(errorData.error)
        }
        if (errorData.detail) {
          const detail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
          throw new Error(detail)
        }
        
        // If we have any error data, show it
        if (Object.keys(errorData).length > 0) {
          const firstKey = Object.keys(errorData)[0]
          const firstError = errorData[firstKey]
          const errorMsg = Array.isArray(firstError) ? firstError[0] : firstError
          throw new Error(`${firstKey}: ${errorMsg}`)
        }
        
        // Generic validation error
        throw new Error('Registration failed. Please check your input and try again.')
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
      logoutPromise = api.post(`${API_PATH}/logout/`, {})
      await logoutPromise
      
      localStorage.removeItem('token')
      // The shared API client will handle removing the Authorization header
    } catch (error) {
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async updateUser(userData: Partial<User>): Promise<{ data: User }> {
    const response = await api.patch(`${API_PATH}/user/`, userData)
    return response
  },

  async healthCheck(): Promise<{ data: { status: string; service: string; database: string } }> {
    try {
      const response = await api.get(`${API_PATH}/health/`, {
        timeout: 5000
      })
      return response
    } catch (error: any) {
      throw error
    }
  }
}
