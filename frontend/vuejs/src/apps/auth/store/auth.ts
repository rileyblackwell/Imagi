import { defineStore } from 'pinia'
import axios from 'axios'
import { AuthAPI } from '../services/api'
import type { AuthState, UserRegistrationData } from '../types/auth'

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

// Auth Store
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

  actions: {
    async initAuth() {
      if (!this.token) return

      try {
        this.loading = true
        const response = await axios.get('/api/v1/auth/init/')
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

    async register(userData: Partial<UserRegistrationData>): Promise<void> {
      this.loading = true
      try {
        // Validate and transform the partial data into complete data
        if (!userData.username || !userData.email || !userData.password || 
            !userData.password_confirmation || userData.terms_accepted === undefined) {
          throw new Error('All registration fields are required')
        }

        const registrationData: UserRegistrationData = {
          username: userData.username,
          email: userData.email,
          password: userData.password,
          password_confirmation: userData.password_confirmation,
          terms_accepted: userData.terms_accepted
        }

        const response = await AuthAPI.register(registrationData)

        if (!response?.data?.token) {
          throw new Error('Registration failed: No token received')
        }

        // Set auth state
        securelyStoreToken(response.data.token)
        this.token = response.data.token
        this.user = response.data.user
        this.isAuthenticated = true
        this.error = null

      } catch (error) {
        this.isAuthenticated = false
        this.user = null
        this.token = null
        this.error = error instanceof Error ? error.message : 'Registration failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async login(credentials: { username: string; password: string }): Promise<void> {
      this.loading = true
      try {
        const response = await AuthAPI.login(credentials)

        if (!response?.data?.token) {
          throw new Error('Login failed: No token received')
        }

        // Set auth state
        securelyStoreToken(response.data.token)
        this.token = response.data.token
        this.user = response.data.user
        this.isAuthenticated = true
        this.error = null

      } catch (error) {
        this.isAuthenticated = false
        this.user = null
        this.token = null
        this.error = error instanceof Error ? error.message : 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.isLoggingOut = true
      try {
        await AuthAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.token = null
        this.isAuthenticated = false
        this.isLoggingOut = false
        localStorage.removeItem('token')
      }
    }
  }
})
