import axios, { AxiosHeaders } from 'axios'
import type { 
  InternalAxiosRequestConfig,
} from 'axios'
import type { 
  User, 
  LoginCredentials, 
  AuthResponse, 
  UserRegistrationData 
} from '@/apps/auth/types/auth'

const BASE_URL = '/api/v1/auth'

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

// Setup axios interceptors for auth
const setupAxiosInterceptors = () => {
  // Add request interceptor
  axios.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      // Create proper AxiosHeaders instance
      const headers = new AxiosHeaders({
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      })
      
      // Add CSRF token if not already present
      const csrfToken = getCookie('csrftoken')
      if (csrfToken) {
        headers.set('X-CSRFToken', csrfToken)
      }
      
      // Add Authorization header if token exists
      const tokenData = localStorage.getItem('token')
      if (tokenData) {
        try {
          const parsedToken = JSON.parse(tokenData)
          if (parsedToken?.value && Date.now() < parsedToken.expires) {
            headers.set('Authorization', `Token ${parsedToken.value}`)
          } else {
            // Token expired, remove it
            localStorage.removeItem('token')
          }
        } catch (e) {
          console.error('Failed to parse token data:', e)
          localStorage.removeItem('token')
        }
      }
      
      config.headers = headers
      
      // Set reasonable timeout
      if (!config.timeout) {
        config.timeout = 30000 // 30 seconds default timeout
      }
      
      return config
    },
    error => Promise.reject(error)
  )

  // Add response interceptor
  axios.interceptors.response.use(
    response => {
      // Add CORS debugging - log successful responses
      // console.log('API Response:', {
      //   url: response.config.url,
      //   status: response.status,
      //   headers: response.headers,
      //   data: response.data
      // });
      return response;
    },
    async error => {
      // Enhanced CORS debugging - log detailed error information
      // if (error.response) {
      //   console.error('API Error Response:', {
      //     url: error.config?.url,
      //     status: error.response.status,
      //     statusText: error.response.statusText,
      //     headers: error.response.headers,
      //     data: error.response.data,
      //     method: error.config?.method,
      //     requestHeaders: error.config?.headers
      //   });
      // } else {
      //   console.error('Network Error (No Response):', {
      //     url: error.config?.url,
      //     method: error.config?.method,
      //     message: error.message,
      //     code: error.code,
      //     requestHeaders: error.config?.headers
      //   });
      // }
      
      // Handle request timeout
      if (error.code === 'ECONNABORTED') {
        console.error('Request timed out:', error.config?.url)
        return Promise.reject(new Error('Network Error: Request timed out'))
      }
      
      // Handle network errors
      if (!error.response) {
        console.error('Network error:', error)
        return Promise.reject(new Error('Network Error: Unable to connect to server'))
      }
      
      // Handle 403 (CSRF) errors
      if (error.response?.status === 403 && !error.config._retry) {
        error.config._retry = true
        try {
          console.log('Getting new CSRF token due to 403 error')
          await AuthAPI.getCSRFToken()
          const newToken = getCookie('csrftoken')
          if (newToken) {
            error.config.headers['X-CSRFToken'] = newToken
          }
          return axios(error.config)
        } catch (retryError) {
          console.error('Failed to retry with new CSRF token:', retryError)
          return Promise.reject(retryError)
        }
      }
      
      // Handle 401 (Unauthorized) errors
      if (error.response?.status === 401) {
        console.log('Unauthorized request. Clearing auth data')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        delete axios.defaults.headers.common['Authorization']
        
        // Only redirect to home if not already on an auth page
        const currentPath = window.location.pathname
        if (!currentPath.startsWith('/auth/')) {
          console.log('Redirecting to home from', currentPath)
          window.location.href = '/'
        }
      }
      
      return Promise.reject(error)
    }
  )
}

// Initialize interceptors
setupAxiosInterceptors()

let logoutPromise: Promise<any> | null = null

export const AuthAPI = {
  async getCSRFToken() {
    try {
      const response = await axios.get(`${BASE_URL}/csrf/`, {
        withCredentials: true,
        timeout: 10000 // 10 second timeout
      })
      return response
    } catch (error) {
      console.error('Failed to get CSRF token:', error)
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    const token = getCookie('csrftoken')
    if (!token) {
      console.log('No CSRF token found, fetching a new one')
      try {
        await this.getCSRFToken()
        const newToken = getCookie('csrftoken')
        if (!newToken) {
          console.error('Failed to get CSRF token after explicit request')
        }
        return newToken
      } catch (error) {
        console.error('Error fetching CSRF token:', error)
        return null
      }
    }
    return token
  },

  async init(): Promise<{ data: { isAuthenticated: boolean; user: User } }> {
    const response = await axios.get(`${BASE_URL}/init/`)
    return response
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
      
      const response = await axios.post(`${BASE_URL}/login/`, credentials, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        withCredentials: true,
        // Add timeout to prevent hanging requests
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
      console.error('Login error details:', error);
      
      // Handle network errors
      if (error.code === 'ECONNABORTED' || !error.response) {
        throw new Error('Network Error')
      }
      
      // Handle specific status codes with clear messages
      if (error.response?.status === 401) {
        throw new Error('Invalid credentials')
      }
      
      if (error.response?.status === 400) {
        const errorData = error.response.data
        
        // Check for error structure from backend
        if (errorData.error) {
          throw new Error(errorData.error)
        }
        
        if (errorData.detail) {
          // Check if detail is an object with field-specific errors
          if (typeof errorData.detail === 'object') {
            throw error // Pass the original error to preserve structure
          }
          throw new Error(errorData.detail)
        }
        
        if (errorData.non_field_errors?.[0]) {
          throw new Error(errorData.non_field_errors[0])
        }
        
        throw new Error('Invalid credentials')
      }
      
      // Fallback for other errors
      throw error
    }
  },

  async register(userData: UserRegistrationData): Promise<{ data: AuthResponse }> {
    try {
      // Make sure we have a CSRF token before attempting registration
      const csrfToken = await this.ensureCSRFToken();
      if (!csrfToken) {
        console.error('Could not obtain CSRF token');
        throw new Error('Registration error: Could not obtain security token');
      }
      
      // Validate required fields
      if (!userData.username || !userData.email || !userData.password || !userData.password_confirmation) {
        throw new Error('All registration fields are required')
      }
      
      // Validate that password and confirmation match
      if (userData.password !== userData.password_confirmation) {
        throw new Error('Passwords do not match')
      }
      
      // Validate terms acceptance
      if (!userData.terms_accepted) {
        throw new Error('You must accept the terms and conditions')
      }

      // Validate email format only (remove uniqueness check)
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(userData.email)) {
        throw new Error('Please enter a valid email address')
      }

      const response = await axios.post(`${BASE_URL}/register/`, userData, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        withCredentials: true,
        // Add timeout to prevent hanging requests
        timeout: 15000
      })

      // Validate response format
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
      // Handle network errors
      if (error.code === 'ECONNABORTED' || !error.response) {
        throw new Error('Network Error')
      }
      
      if (error.response?.status === 400) {
        const errorData = error.response.data
        
        // Check for error structure from backend
        if (errorData.error) {
          throw new Error(errorData.error)
        }
        
        if (errorData.detail) {
          // Check if detail is an object with field-specific errors
          if (typeof errorData.detail === 'object') {
            throw error // Pass the original error to preserve structure
          }
          throw new Error(errorData.detail)
        }
        
        // Handle specific field errors
        if (errorData.username) {
          // Make it clear this is a uniqueness error
          const usernameError = Array.isArray(errorData.username) ? errorData.username[0] : errorData.username;
          if (usernameError.includes('already') || usernameError.includes('taken')) {
            throw new Error('This username is already taken. Please choose another one.')
          }
          throw new Error(usernameError)
        }
        
        if (errorData.email) {
          throw new Error(Array.isArray(errorData.email) ? errorData.email[0] : errorData.email)
        }
        
        if (errorData.password) {
          throw new Error(Array.isArray(errorData.password) ? errorData.password[0] : errorData.password)
        }
        
        if (errorData.non_field_errors?.[0]) {
          throw new Error(errorData.non_field_errors[0])
        }
        
        throw new Error('Registration failed')
      }
      
      // Fallback for other errors
      throw error
    }
  },

  async logout(): Promise<void> {
    if (logoutPromise) {
      return logoutPromise
    }

    try {
      logoutPromise = axios.post(`${BASE_URL}/logout/`, {}, {
        withCredentials: true
      })
      await logoutPromise
      
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async updateUser(userData: Partial<User>): Promise<{ data: User }> {
    const response = await axios.patch(`${BASE_URL}/user/`, userData)
    return response
  }
}
