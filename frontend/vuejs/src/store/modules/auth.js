import { authAPI } from '@/services/api'

const state = {
  user: null,
  accessToken: localStorage.getItem('accessToken') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  loading: false,
  error: null,
  preferences: {
    notifications: {
      projectUpdates: true,
      securityAlerts: true,
      newsletter: false
    },
    timezone: 'UTC'
  }
}

const getters = {
  isAuthenticated: state => !!state.accessToken,
  currentUser: state => state.user,
  authError: state => state.error,
  isLoading: state => state.loading,
  userPreferences: state => state.preferences
}

const actions = {
  async login({ commit }, credentials) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await authAPI.login(credentials)
      const { access, refresh } = response.data
      
      commit('SET_TOKENS', { access, refresh })
      
      // Get user profile
      const userResponse = await authAPI.getMe()
      commit('SET_USER', userResponse.data)
      
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Login failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async register({ commit }, userData) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await authAPI.register(userData)
      
      // After registration, log the user in
      const { username, password } = userData
      await this.dispatch('auth/login', { username, password })
      
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || 'Registration failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async refreshToken({ commit, state }) {
    try {
      const response = await authAPI.refreshToken(state.refreshToken)
      const { access } = response.data
      
      commit('SET_ACCESS_TOKEN', access)
      return response
    } catch (error) {
      commit('CLEAR_AUTH')
      throw error
    }
  },
  
  async fetchUser({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await authAPI.getMe()
      commit('SET_USER', response.data)
      
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || 'Failed to fetch user')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateProfile({ commit }, profileData) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await authAPI.updateProfile(profileData)
      commit('SET_USER', response.data)
      
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || 'Failed to update profile')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updatePassword({ commit }, passwordData) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await authAPI.updatePassword(passwordData)
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || 'Failed to update password')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updatePreferences({ commit }, preferences) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await authAPI.updatePreferences(preferences)
      commit('SET_PREFERENCES', preferences)
      
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data || 'Failed to update preferences')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  logout({ commit }) {
    commit('CLEAR_AUTH')
  }
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
  },
  
  SET_ACCESS_TOKEN(state, token) {
    state.accessToken = token
    localStorage.setItem('accessToken', token)
  },
  
  SET_REFRESH_TOKEN(state, token) {
    state.refreshToken = token
    localStorage.setItem('refreshToken', token)
  },
  
  SET_TOKENS(state, { access, refresh }) {
    state.accessToken = access
    state.refreshToken = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  },
  
  SET_PREFERENCES(state, preferences) {
    state.preferences = preferences
  },
  
  CLEAR_AUTH(state) {
    state.user = null
    state.accessToken = null
    state.refreshToken = null
    state.error = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 