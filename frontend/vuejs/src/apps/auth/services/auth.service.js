import axios from 'axios'
import config from '@/shared/config'

const API_URL = `${config.apiUrl}/auth`

class AuthService {
  async login(credentials) {
    try {
      const response = await axios.post(`${API_URL}/login/`, credentials)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Login failed')
    }
  }

  async register(userData) {
    try {
      const response = await axios.post(`${API_URL}/register/`, userData)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Registration failed')
    }
  }

  async logout() {
    try {
      await axios.post(`${API_URL}/logout/`)
      localStorage.removeItem('token')
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Logout failed')
    }
  }

  async getCurrentUser() {
    try {
      const response = await axios.get(`${API_URL}/user/`)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to get user data')
    }
  }

  async requestPasswordReset(email) {
    try {
      const response = await axios.post(`${API_URL}/password-reset/`, { email })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to request password reset')
    }
  }

  async resetPassword(token, newPassword) {
    try {
      const response = await axios.post(`${API_URL}/password-reset/confirm/`, {
        token,
        new_password: newPassword
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to reset password')
    }
  }
}

export default new AuthService() 