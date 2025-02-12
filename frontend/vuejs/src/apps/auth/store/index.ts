import { defineStore } from 'pinia'
import axios from 'axios'
import { AuthAPI } from '../services/api'
import type { AuthState, User, LoginCredentials, AuthResponse, UserRegistrationData } from '../types/auth'

// Helper Functions
const getCookie = (name: string): string | null => {
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

const securelyStoreToken = (token: string): boolean => {
  try {
    const tokenData = {
      value: token,
      expires: Date.now() + (24 * 60 * 60 * 1000)
    }
    localStorage.setItem('token', JSON.stringify(tokenData))
    return true
  } catch (error) {
    console.error('Error storing token:', error)
    return false
  }
}

const getStoredToken = (): string | null => {
  try {
    const tokenData = JSON.parse(localStorage.getItem('token') || '{}')
    if (!tokenData?.value) return null
    if (Date.now() > tokenData.expires) {
      localStorage.removeItem('token')
      return null
    }
    return tokenData.value
  } catch {
    return null
  }
}

// Axios Configuration
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// CSRF Token Management
const getCSRFToken = async (): Promise<string> => {
  try {
    const response = await axios.get('/api/v1/auth/init/')
    if (response.data.csrfToken) {
      axios.defaults.headers['X-CSRFToken'] = response.data.csrfToken
      return response.data.csrfToken
    }
    throw new Error('No CSRF token in response')
  } catch (error) {
    console.error('Failed to get CSRF token:', error)
    throw error
  }
}

// Axios Interceptors
axios.interceptors.request.use(async config => {
  if (!config.url?.endsWith('/csrf/')) {
    const csrfToken = getCookie('csrftoken')
    if (!csrfToken) {
      await getCSRFToken()
      const newToken = getCookie('csrftoken')
      if (newToken) {
        config.headers['X-CSRFToken'] = newToken
      }
    } else {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }

  config.headers['Accept'] = 'application/json'
  config.headers['Content-Type'] = 'application/json'
  config.withCredentials = true

  return config
})

axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 403 && !error.config._retry) {
      error.config._retry = true
      try {
        await getCSRFToken()
        error.config.headers['X-CSRFToken'] = getCookie('csrftoken')
        return axios(error.config)
      } catch (retryError) {
        console.error('Failed to retry request:', retryError)
        throw retryError
      }
    }
    throw error
  }
)

// Single store definition
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: getStoredToken(),
    isAuthenticated: false,
    loading: false,
    error: null,
    isLoggingOut: false,
    isLoginPending: false,
    initialized: false
  }),

  getters: {
    currentUser: (state): User | null => state.user,
    userBalance: (state): number => state.user?.balance || 0
  },

  actions: {
    async initAuth() {
      if (!this.token) {
        this.initialized = true
        return
      }

      try {
        this.loading = true
        const response = await AuthAPI.init()
        if (response.data.isAuthenticated) {
          this.user = response.data.user
          this.isAuthenticated = true
        } else {
          await this.logout()
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        await this.logout()
      } finally {
        this.loading = false
        this.initialized = true
      }
    },

    async login(credentials: LoginCredentials): Promise<AuthResponse> {
      try {
        this.loading = true
        this.error = null
        const response = await AuthAPI.login(credentials)
        
        // Handle successful login
        if (response?.data?.token) {
          this.token = response.data.token
          this.user = response.data.user
          this.isAuthenticated = true
          localStorage.setItem('token', response.data.token)
          
          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
          
          return response.data
        }
        throw new Error('Invalid response from server')
      } catch (error: any) {
        this.isAuthenticated = false
        this.user = null
        this.token = null
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        
        this.error = error.message || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async register(userData: UserRegistrationData): Promise<AuthResponse> {
      try {
        this.loading = true
        this.error = null
        const response = await AuthAPI.register(userData)
        
        // Handle successful registration same as login
        if (response?.data?.token) {
          this.token = response.data.token
          this.user = response.data.user
          this.isAuthenticated = true
          localStorage.setItem('token', response.data.token)
          
          // Set axios default header for subsequent requests
          axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
          
          return response.data
        }
        throw new Error('Invalid response from server')
      } catch (error: any) {
        this.isAuthenticated = false
        this.user = null
        this.token = null
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        
        this.error = error.message || 'Registration failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout(): Promise<void> {
      if (this.isLoggingOut) return

      try {
        this.isLoggingOut = true
        if (this.isAuthenticated) {
          await AuthAPI.logout()
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.token = null
        this.user = null
        this.isAuthenticated = false
        localStorage.removeItem('token')
        this.isLoggingOut = false
        window.location.href = '/'
      }
    },

    async updateUser(userData: Partial<User>): Promise<User> {
      try {
        this.loading = true
        const response = await AuthAPI.updateUser(userData)
        this.user = response.data
        return response.data
      } catch (error) {
        console.error('Failed to update user:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

export type { AuthState, User }
