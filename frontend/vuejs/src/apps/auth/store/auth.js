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

// Configure axios defaults
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)

  // Set axios default authorization header when token exists
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
  }

  const isAuthenticated = computed(() => !!token.value)
  const isLoading = computed(() => loading.value)
  const authError = computed(() => error.value)

  function setUser(userData) {
    user.value = userData
  }

  function setToken(tokenValue) {
    token.value = tokenValue
    if (tokenValue) {
      localStorage.setItem('token', tokenValue)
      axios.defaults.headers.common['Authorization'] = `Token ${tokenValue}`
    } else {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }

  async function ensureCSRFToken() {
    if (!getCookie('csrftoken')) {
      // Fetch CSRF token by making a GET request to the server
      await axios.get('/api/auth/csrf/')
    }
  }

  async function initAuth() {
    loading.value = true
    error.value = null

    try {
      await ensureCSRFToken()
      // Only attempt to fetch user if we have a token
      if (token.value) {
        const response = await axios.get('/api/auth/user/')
        setUser(response.data)
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to initialize auth'
      // Clear invalid token
      setToken(null)
      setUser(null)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(credentials) {
    loading.value = true
    error.value = null

    try {
      await ensureCSRFToken()
      const response = await axios.post('/api/auth/login/', {
        username: credentials.username,
        password: credentials.password
      })
      
      if (response.data.token) {
        setToken(response.data.token)
        setUser(response.data.user)
        return response.data
      }
      throw new Error('No token received from server')
    } catch (err) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function register(userData) {
    loading.value = true
    error.value = null

    try {
      const response = await axios.post('/api/auth/register/', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        first_name: userData.firstName,
        last_name: userData.lastName
      })
      
      if (response.data.token) {
        setToken(response.data.token)
        setUser(response.data.user)
        return response.data
      }
      throw new Error('No token received from server')
    } catch (err) {
      console.error('Registration error:', err)
      if (err.response?.data?.errors) {
        error.value = err.response.data.errors
      } else if (err.response?.data?.error) {
        error.value = { general: err.response.data.error }
      } else {
        error.value = { general: err.message || 'An error occurred during registration' }
      }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    error.value = null

    try {
      await axios.post('/api/auth/logout/')
      setToken(null)
      setUser(null)
      return true
    } catch (err) {
      console.error('Logout error:', err)
      error.value = { general: err.response?.data?.error || 'An error occurred during logout' }
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function checkAuth() {
    if (!token.value) return false

    try {
      const response = await axios.get('/api/auth/user/')
      setUser(response.data)
      return true
    } catch (err) {
      console.error('Auth check error:', err)
      setToken(null)
      setUser(null)
      return false
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    isLoading,
    authError,
    login,
    register,
    logout,
    checkAuth,
    setUser,
    setToken,
    initAuth,
  }
}) 