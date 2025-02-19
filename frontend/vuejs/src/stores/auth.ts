import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const sessionTimeout = ref<number | null>(null)
  const user = ref<any | null>(null)

  const login = async (credentials: { email: string; password: string }) => {
    try {
      const response = await axios.post('/api/v1/auth/login/', credentials)
      token.value = response.data.token
      user.value = response.data.user
      sessionTimeout.value = 30 * 60 * 1000 // 30 minutes
      return response.data
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await axios.post('/api/v1/auth/logout/')
      }
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      token.value = null
      user.value = null
      sessionTimeout.value = null
    }
  }

  const refreshToken = async () => {
    try {
      const response = await axios.post('/api/v1/auth/refresh/')
      token.value = response.data.token
      sessionTimeout.value = 30 * 60 * 1000 // Reset timeout to 30 minutes
      return response.data
    } catch (error) {
      console.error('Token refresh failed:', error)
      throw error
    }
  }

  return {
    token,
    user,
    sessionTimeout,
    login,
    logout,
    refreshToken
  }
}) 