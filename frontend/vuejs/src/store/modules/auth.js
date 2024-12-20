import axios from 'axios'

const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
  isAuthenticated: !!localStorage.getItem('token'),
  loading: false,
  error: null
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    state.isAuthenticated = !!token
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
  },
  
  SET_USER(state, user) {
    state.user = user
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  }
}

const actions = {
  async login({ commit }, credentials) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.post('/api/auth/login/', credentials)
      const { token, user } = response.data
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      
      // Set axios default headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      return response.data
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
      
      const response = await axios.post('/api/auth/register/', userData)
      const { token, user } = response.data
      
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      
      // Set axios default headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Registration failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async logout({ commit }) {
    try {
      commit('SET_LOADING', true)
      
      await axios.post('/api/auth/logout/')
      
      // Clear auth state
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
      
      // Remove axios default headers
      delete axios.defaults.headers.common['Authorization']
      
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async forgotPassword({ commit }, email) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      await axios.post('/api/auth/password-reset/', { email })
      
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Password reset request failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async resetPassword({ commit }, { token, password }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      await axios.post(`/api/auth/password-reset/${token}/`, { password })
      
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Password reset failed')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchUser({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.get('/api/auth/user/')
      commit('SET_USER', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch user data')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  isAuthenticated: state => state.isAuthenticated,
  user: state => state.user,
  token: state => state.token,
  loading: state => state.loading,
  error: state => state.error
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 