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
        window.location.href = '/' // Redirect to home
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
      
      if (!credentials?.username || !credentials?.password) {
        throw new Error('Missing credentials')
      }
      
      const response = await axios.post(`${BASE_URL}/login/`, {
        username: credentials.username,
        password: credentials.password
      }, {
        withCredentials: true
      })
      
      // Handle successful login
      if (response?.data?.token) {
        localStorage.setItem('token', response.data.token)
        axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      }
      
      return response
    } catch (error) {
      // Only transform error if it's an authentication error
      if (error.response?.status === 401 || error.response?.status === 400) {
        const errorData = error.response.data
        throw new Error(errorData.detail || errorData.non_field_errors?.[0] || 'Invalid credentials')
      }
      throw error
    }
  },

  async register(userData) {
    try {
      await this.ensureCSRFToken()
      
      const response = await axios.post(`${BASE_URL}/register/`, userData, {
        withCredentials: true,
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      return response
    } catch (error) {
      // Let the error handler format the error
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
  }
}