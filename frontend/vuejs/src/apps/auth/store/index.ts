import { defineStore } from 'pinia'
import axios from 'axios'
import { AuthAPI } from '../services/api'
import type { AuthState, User } from '../types/auth'
import type { LoginCredentials, AuthResponse, UserRegistrationData } from '../services/types'

// Helper to safely get token
const getStoredToken = (): string | null => localStorage.getItem('token')

// Single store definition
export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: getStoredToken(),
    isAuthenticated: false,
    loading: false,
    error: null,
    isLoggingOut: false,
    isLoginPending: false // Add this to prevent multiple requests
  }),

  getters: {
    currentUser: (state): User | null => state.user,
    userBalance: (state): number => state.user?.balance || 0
  },

  actions: {
    async initAuth() {
      if (!this.token) return

      try {
        this.loading = true
        const response = await AuthAPI.init()
        if (response.data.isAuthenticated) {
          this.user = response.data.user
          this.isAuthenticated = true
        } else {
          await this.logout()
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        await this.logout()
      } finally {
        this.loading = false
      }
    },

    async login(credentials: LoginCredentials): Promise<AuthResponse> {
      try {
        this.loading = true
        this.error = null
        const response = await AuthAPI.login(credentials)
        
        // Handle successful login
        if (response?.data?.token) {
          this.token = response.data.token
          this.user = response.data.user
          this.isAuthenticated = true
          localStorage.setItem('token', response.data.token)
          
          // Set axios default header
          axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`
          
          return response.data
        }
        throw new Error('Invalid response from server')
      } catch (error: any) {
        this.isAuthenticated = false
        this.user = null
        this.token = null
        localStorage.removeItem('token')
        delete axios.defaults.headers.common['Authorization']
        
        this.error = error.message || 'Login failed'
        throw error
      } finally {
        this.loading = false
      }
    },

    async register(userData: UserRegistrationData): Promise<AuthResponse> {
      try {
        this.loading = true
        const response = await AuthAPI.register(userData)
        const token = response.data.token
        
        if (token) {
          this.token = token
          this.user = response.data.user
          this.isAuthenticated = true
          localStorage.setItem('token', token)
        }
        
        return response.data
      } catch (error) {
        console.error('Registration failed:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout(): Promise<void> {
      if (this.isLoggingOut) return

      try {
        this.isLoggingOut = true
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
        this.isLoggingOut = false
        window.location.href = '/'
      }
    },

    async updateUser(userData: Partial<User>): Promise<User> {
      try {
        this.loading = true
        const response = await AuthAPI.updateUser(userData)
        this.user = response.data
        return response.data
      } catch (error) {
        console.error('Failed to update user:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})

// Remove default export
export type { AuthState, User }
