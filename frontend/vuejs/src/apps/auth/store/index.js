import { defineStore } from 'pinia'
import { AuthAPI } from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false,
    isLoading: false,
    error: null
  }),

  getters: {
    currentUser: (state) => state.user,
    userBalance: (state) => state.user?.balance || 0
  },

  actions: {
    async initAuth() {
      if (!this.token) {
        return
      }

      try {
        this.isLoading = true
        // Use the correct endpoint
        const response = await AuthAPI.getCurrentUser()
        this.user = response.data
        this.isAuthenticated = true
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        this.logout()
      } finally {
        this.isLoading = false
      }
    },

    async login(credentials) {
      try {
        this.isLoading = true
        const response = await AuthAPI.login(credentials)
        this.token = response.data.token
        this.user = response.data.user
        this.isAuthenticated = true
        localStorage.setItem('token', this.token)
        return response
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async register(userData) {
      try {
        this.isLoading = true
        const response = await AuthAPI.register(userData)
        this.token = response.data.token
        this.user = response.data.user
        this.isAuthenticated = true
        localStorage.setItem('token', this.token)
        return response
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
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
      }
    },

    async updateUser(userData) {
      try {
        this.isLoading = true
        const response = await AuthAPI.updateUser(userData)
        this.user = response.data
        return response
      } catch (error) {
        console.error('Failed to update user:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async refreshUser() {
      try {
        this.isLoading = true
        const response = await AuthAPI.getCurrentUser()
        this.user = response.data
        return response
      } catch (error) {
        console.error('Failed to refresh user:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    }
  }
}) 