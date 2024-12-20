import { projectAPI } from '@/services/api'

const state = {
  projects: [],
  currentProject: null,
  loading: false,
  error: null
}

const getters = {
  allProjects: state => state.projects,
  currentProject: state => state.currentProject,
  isLoading: state => state.loading,
  error: state => state.error
}

const actions = {
  async fetchProjects({ commit }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await projectAPI.getProjects()
      commit('SET_PROJECTS', response.data)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch projects')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchProject({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await projectAPI.getProject(id)
      commit('SET_CURRENT_PROJECT', response.data)
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async createProject({ commit, dispatch }, data) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await projectAPI.createProject(data)
      await dispatch('fetchProjects')
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to create project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateProject({ commit, dispatch }, { id, data }) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      const response = await projectAPI.updateProject(id, data)
      commit('SET_CURRENT_PROJECT', response.data)
      await dispatch('fetchProjects')
      return response
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to update project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async deleteProject({ commit }, id) {
    commit('SET_LOADING', true)
    commit('SET_ERROR', null)
    
    try {
      await projectAPI.deleteProject(id)
      commit('REMOVE_PROJECT', id)
      commit('CLEAR_CURRENT_PROJECT')
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to delete project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const mutations = {
  SET_PROJECTS(state, projects) {
    state.projects = projects
  },
  
  SET_CURRENT_PROJECT(state, project) {
    state.currentProject = project
  },
  
  CLEAR_CURRENT_PROJECT(state) {
    state.currentProject = null
  },
  
  REMOVE_PROJECT(state, id) {
    state.projects = state.projects.filter(project => project.id !== id)
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
} 