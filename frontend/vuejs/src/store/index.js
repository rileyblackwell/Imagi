import { createStore } from 'vuex'
import auth from './modules/auth'
import projects from './modules/projects'
import payments from './modules/payments'

export default createStore({
  modules: {
    auth,
    projects,
    payments
  },
  
  state: {
    loading: false,
    error: null
  },
  
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  
  actions: {
    setLoading({ commit }, loading) {
      commit('SET_LOADING', loading)
    },
    setError({ commit }, error) {
      commit('SET_ERROR', error)
    }
  },
  
  getters: {
    isLoading: state => state.loading,
    error: state => state.error
  }
}) 