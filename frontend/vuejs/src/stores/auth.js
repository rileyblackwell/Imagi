import { defineStore } from 'pinia'
import AuthService from '@/apps/auth/services/auth.service'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },

  actions: {
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },

    setUser(user) {
      this.user = user
    },

    setLoading(loading) {
      this.loading = loading
    },

    setError(error) {
      this.error = error
    },

    async login(credentials) {
      this.loading = true
      this.error = null
      
      try {
        const { token, user } = await AuthService.login(credentials)
        this.setToken(token)
        this.setUser(user)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async register(userData) {
      this.loading = true
      this.error = null
      
      try {
        const { token, user } = await AuthService.register(userData)
        this.setToken(token)
        this.setUser(user)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.loading = true
      this.error = null
      
      try {
        await AuthService.logout()
        this.setToken(null)
        this.setUser(null)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getCurrentUser() {
      this.loading = true
      this.error = null
      
      try {
        const user = await AuthService.getCurrentUser()
        this.setUser(user)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 