import axios from 'axios'
import config from '@/shared/config'

const API_URL = `${config.apiUrl}/api/auth`

class AuthService {
  async getCsrfToken() {
    try {
      await axios.get(`${API_URL}/csrf/`)
    } catch (error) {
      console.error('Failed to get CSRF token:', error)
    }
  }

  async login(credentials) {
    try {
      // Get CSRF token first
      await this.getCsrfToken()
      
      const response = await axios.post(`${API_URL}/login/`, credentials)
      if (response.data.token) {
        localStorage.setItem('token', response.data.token)
        axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      }
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Login failed')
    }
  }

  async register(userData) {
    try {
      // Get CSRF token first
      await this.getCsrfToken()
      
      const response = await axios.post(`${API_URL}/register/`, userData)
      if (response.data.token) {
        localStorage.setItem('token', response.data.token)
        axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
      }
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Registration failed')
    }
  }

  async logout() {
    try {
      await axios.post(`${API_URL}/logout/`)
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Logout failed')
    }
  }

  async getCurrentUser() {
    try {
      const response = await axios.get(`${API_URL}/me/`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to get user data')
    }
  }

  async requestPasswordReset(email) {
    try {
      // Get CSRF token first
      await this.getCsrfToken()
      
      const response = await axios.post(`${API_URL}/password/reset/`, { email })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to request password reset')
    }
  }

  async resetPassword(uid, token, newPassword) {
    try {
      // Get CSRF token first
      await this.getCsrfToken()
      
      const response = await axios.post(`${API_URL}/password/reset/confirm/`, {
        uid,
        token,
        new_password: newPassword
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to reset password')
    }
  }

  async changePassword(oldPassword, newPassword) {
    try {
      const response = await axios.post(`${API_URL}/change-password/`, {
        old_password: oldPassword,
        new_password: newPassword
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to change password')
    }
  }

  // Setup interceptor for token
  setupAxiosInterceptors() {
    const token = localStorage.getItem('token')
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`
    }
    
    axios.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          this.logout()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }
}

const authService = new AuthService()
authService.setupAxiosInterceptors()

export default authService 