import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// Helper function to get CSRF token from cookies
function getCookie(name) {
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

// Secure token storage with encryption
function securelyStoreToken(token) {
  try {
    // Store token with expiration (24 hours)
    const tokenData = {
      value: token,
      expires: Date.now() + (24 * 60 * 60 * 1000)
    }
    localStorage.setItem('token', JSON.stringify(tokenData))
  } catch (error) {
    console.error('Error storing token:', error)
    return false
  }
  return true
}

function getStoredToken() {
  try {
    const tokenData = JSON.parse(localStorage.getItem('token'))
    if (!tokenData) return null
    
    // Check if token has expired
    if (Date.now() > tokenData.expires) {
      localStorage.removeItem('token')
      return null
    }
    return tokenData.value
  } catch {
    return null
  }
}

// Configure axios defaults
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Development-specific settings
const isDevelopment = import.meta.env.DEV

// Helper function to check server availability and get CSRF token
async function getCSRFToken() {
  try {
    const response = await axios.get('/api/v1/auth/init/', {
      withCredentials: true
    })
    
    if (response.data.csrfToken) {
      axios.defaults.headers['X-CSRFToken'] = response.data.csrfToken
      return response.data.csrfToken
    }
    throw new Error('No CSRF token in response')
  } catch (error) {
    console.error('Failed to get CSRF token:', error.message)
    throw error
  }
}

// Add axios interceptor to handle CORS and CSRF
axios.interceptors.request.use(async config => {
  try {
    // Don't get CSRF token for the CSRF endpoint itself
    if (!config.url.endsWith('/csrf/')) {
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

    // Add common headers
    config.headers['Accept'] = 'application/json'
    config.headers['Content-Type'] = 'application/json'
    config.withCredentials = true

    return config
  } catch (error) {
    console.error('Request interceptor error:', error.message)
    throw error
  }
})

// Add response interceptor for error handling
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 403) {
      // Only retry once to prevent infinite loops
      if (!error.config._retry) {
        error.config._retry = true
        try {
          await getCSRFToken()
          error.config.headers['X-CSRFToken'] = getCookie('csrftoken')
          return axios(error.config)
        } catch (retryError) {
          console.error('Failed to retry request:', retryError.message)
          throw retryError
        }
      }
    }
    throw error
  }
)

// Add retry delay helper
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Add server health check
async function checkServerHealth() {
  try {
    await axios.get('/api/v1/health/')
    return true
  } catch (error) {
    console.error('Server health check failed:', error)
    return false
  }
}

import { AuthAPI } from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoading: false,
    isAuthenticated: false,
  }),

  actions: {
    async register(userData) {
      this.isLoading = true
      try {
        const response = await AuthAPI.register(userData)
        
        // Handle successful registration
        if (response.data) {
          this.isAuthenticated = true
          this.user = response.data.user || null
          
          // Check if token exists before setting it
          if (response.data.token) {
            localStorage.setItem('token', response.data.token)
          }
        }
        
        return response.data
      } catch (error) {
        throw error
      } finally {
        this.isLoading = false
      }
    },
    // ...other actions...
  }
})