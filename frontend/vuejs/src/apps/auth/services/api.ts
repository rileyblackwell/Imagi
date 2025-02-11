import axios, { AxiosHeaders } from 'axios'
import type { 
  InternalAxiosRequestConfig,
  AxiosResponse 
} from 'axios'
import type { User } from '../types/auth'

const BASE_URL = '/api/v1/auth'

interface AuthResponse {
  token: string;
  user: User;
}

interface LoginCredentials {
  username: string;  // Changed from email to username
  password: string;
}

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
      const token = localStorage.getItem('token')
      if (token) {
        headers.set('Authorization', `Token ${token}`)
      }
      
      config.headers = headers
      return config
    },
    error => Promise.reject(error)
  )

  // Add response interceptor
  axios.interceptors.response.use(
    response => response,
    async error => {
      // Handle 403 (CSRF) errors
      if (error.response?.status === 403 && !error.config._retry) {
        error.config._retry = true
        try {
          await AuthAPI.getCSRFToken()
          const newToken = getCookie('csrftoken')
          if (newToken) {
            error.config.headers['X-CSRFToken'] = newToken
          }
          return axios(error.config)
        } catch (retryError) {
          return Promise.reject(retryError)
        }
      }
      
      // Handle 401 (Unauthorized) errors
      if (error.response?.status === 401) {
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        window.location.href = '/' // Redirect to home
      }
      
      return Promise.reject(error)
    }
  )
}

// Initialize interceptors
setupAxiosInterceptors()

let logoutPromise: Promise<any> | null = null
let loginPromise: Promise<any> | null = null

export const AuthAPI = {
  async getCSRFToken() {
    try {
      const response = await axios.get(`${BASE_URL}/csrf/`, {
        withCredentials: true
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
      await this.getCSRFToken()
    }
    return getCookie('csrftoken')
  },

  async init(): Promise<{ data: { isAuthenticated: boolean; user: User } }> {
    const response = await axios.get(`${BASE_URL}/init/`)
    return response
  },

  async login(credentials: LoginCredentials): Promise<{ data: AuthResponse }> {
    try {
      // Simple validation
      if (!credentials?.username || !credentials?.password) {
        throw new Error('Username and password are required')
      }

      // Send login request
      const response = await axios.post(`${BASE_URL}/login/`, credentials, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        withCredentials: true
      })

      // Validate response
      if (!response?.data?.token) {
        throw new Error('Invalid server response')
      }

      return response
    } catch (error: any) {
      // Handle specific error cases
      if (error.response?.status === 401) {
        throw new Error('Invalid username or password')
      }
      if (error.response?.status === 400) {
        const errorData = error.response.data
        throw new Error(errorData.detail || errorData.non_field_errors?.[0] || 'Invalid credentials')
      }
      throw error
    }
  },

  async register(userData: { name: string; email: string; password: string }): Promise<{ data: AuthResponse }> {
    try {
      await this.ensureCSRFToken()
      const response = await axios.post(`${BASE_URL}/register/`, userData, {
        withCredentials: true
      })
      return response
    } catch (error) {
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
