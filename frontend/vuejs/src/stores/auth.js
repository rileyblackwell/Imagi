import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import config from '@/shared/config'

// Configure axios defaults
axios.defaults.baseURL = config.apiUrl
axios.defaults.withCredentials = true // Important for CSRF
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

// Function to get CSRF token from cookies
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

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)

  // Actions
  async function ensureCsrfToken() {
    if (!getCookie('csrftoken')) {
      await axios.get('/api/auth/csrf/')
    }
  }

  async function initAuth() {
    const token = localStorage.getItem(config.auth.tokenKey)
    if (token) {
      try {
        // Set the auth header
        axios.defaults.headers.common['Authorization'] = `Token ${token}`
        
        // Fetch user data
        const response = await axios.get('/api/auth/user/')
        user.value = response.data
      } catch (err) {
        console.error('Failed to initialize auth:', err)
        // Clear invalid token
        localStorage.removeItem(config.auth.tokenKey)
        user.value = null
      }
    }
  }

  async function login(credentials) {
    loading.value = true
    error.value = null

    try {
      // Ensure CSRF token is set
      await ensureCsrfToken()

      const response = await axios.post('/api/auth/login/', {
        username: credentials.username,
        password: credentials.password
      })

      const { token, user: userData } = response.data

      // Store token
      localStorage.setItem(config.auth.tokenKey, token)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`

      // Set user
      user.value = userData
      return response.data
    } catch (err) {
      console.error('Login failed:', err)
      error.value = err.response?.data?.error || 'Login failed. Please try again.'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null

    try {
      // Ensure CSRF token is set
      await ensureCsrfToken()

      const response = await axios.post('/api/auth/register/', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        first_name: userData.firstName,
        last_name: userData.lastName
      })

      const { token, user: newUser } = response.data

      // Store token
      localStorage.setItem(config.auth.tokenKey, token)
      axios.defaults.headers.common['Authorization'] = `Token ${token}`

      // Set user
      user.value = newUser
      return response.data
    } catch (err) {
      console.error('Registration failed:', err)
      error.value = err.response?.data?.errors || err.response?.data?.error || 'Registration failed. Please try again.'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      // Ensure CSRF token is set
      await ensureCsrfToken()
      await axios.post('/api/auth/logout/')
    } catch (err) {
      console.error('Logout failed:', err)
    } finally {
      // Clear auth state regardless of API call success
      localStorage.removeItem(config.auth.tokenKey)
      delete axios.defaults.headers.common['Authorization']
      user.value = null
    }
  }

  return {
    // State
    user,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    
    // Actions
    initAuth,
    login,
    logout,
    register
  }
}) 