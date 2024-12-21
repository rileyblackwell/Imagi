import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))

  const isAuthenticated = computed(() => !!token.value)

  function setUser(userData) {
    user.value = userData
  }

  function setToken(tokenValue) {
    token.value = tokenValue
    if (tokenValue) {
      localStorage.setItem('token', tokenValue)
    } else {
      localStorage.removeItem('token')
    }
  }

  async function login(credentials) {
    try {
      // TODO: Implement actual login API call
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })
      
      if (!response.ok) {
        throw new Error('Login failed')
      }

      const data = await response.json()
      setToken(data.token)
      setUser(data.user)
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  async function register(userData) {
    try {
      // TODO: Implement actual register API call
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })
      
      if (!response.ok) {
        throw new Error('Registration failed')
      }

      const data = await response.json()
      setToken(data.token)
      setUser(data.user)
      return true
    } catch (error) {
      console.error('Registration error:', error)
      return false
    }
  }

  async function logout() {
    try {
      // TODO: Implement actual logout API call if needed
      setToken(null)
      setUser(null)
      return true
    } catch (error) {
      console.error('Logout error:', error)
      return false
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    setUser,
    setToken,
  }
}) 