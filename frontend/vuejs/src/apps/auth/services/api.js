import axios from 'axios'

const BASE_URL = '/api/v1/auth'

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

// Setup axios interceptors for auth
const setupAxiosInterceptors = () => {
  // Add request interceptor
  axios.interceptors.request.use(
    async config => {
      // Add default headers
      config.headers = {
        ...config.headers,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
      
      // Add CSRF token if not already present
      const csrfToken = getCookie('csrftoken')
      if (!config.headers['X-CSRFToken'] && csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken
      }
      
      // Add Authorization header if token exists
      const token = localStorage.getItem('token')
      if (token) {
        config.headers['Authorization'] = `Token ${token}`
      }
      
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
        window.location.href = '/login'
      }
      
      return Promise.reject(error)
    }
  )
}

// Initialize interceptors
setupAxiosInterceptors()

let logoutPromise = null

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

  async ensureCSRFToken() {
    const token = getCookie('csrftoken')
    if (!token) {
      await this.getCSRFToken()
    }
    return getCookie('csrftoken')
  },

  async login(credentials) {
    try {
      await this.ensureCSRFToken()
      
      const response = await axios.post(`${BASE_URL}/login/`, credentials, {
        withCredentials: true
      })
      
      if (response.data.token) {
        localStorage.setItem('token', response.data.token)
        axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      }
      
      return response
    } catch (error) {
      console.error('Login error:', error.response?.data || error)
      throw error
    }
  },

  async register(userData) {
    try {
      await this.ensureCSRFToken()
      
      const response = await axios.post(`${BASE_URL}/register/`, {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        password_confirmation: userData.password_confirmation
      }, {
        withCredentials: true
      })
      
      if (response.data.token) {
        localStorage.setItem('token', response.data.token)
        axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      }
      
      return response
    } catch (error) {
      console.error('Registration error:', error.response?.data || error)
      throw error
    }
  },

  async logout() {
    if (logoutPromise) {
      return logoutPromise
    }

    try {
      logoutPromise = axios.post(`${BASE_URL}/logout/`, {}, {
        withCredentials: true
      })
      const response = await logoutPromise
      
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      
      return response
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async getCurrentUser() {
    try {
      const response = await axios.get(`${BASE_URL}/me/`, {
        withCredentials: true
      })
      return response
    } catch (error) {
      console.error('Get user error:', error)
      throw error
    }
  }
}