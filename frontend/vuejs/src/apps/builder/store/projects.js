import axios from 'axios'

const state = {
  projects: [],
  currentProject: null,
  loading: false,
  error: null
}

const mutations = {
  SET_PROJECTS(state, projects) {
    state.projects = projects
  },
  
  SET_CURRENT_PROJECT(state, project) {
    state.currentProject = project
  },
  
  ADD_PROJECT(state, project) {
    state.projects.unshift(project)
  },
  
  UPDATE_PROJECT(state, updatedProject) {
    const index = state.projects.findIndex(p => p.id === updatedProject.id)
    if (index !== -1) {
      state.projects.splice(index, 1, updatedProject)
    }
    if (state.currentProject?.id === updatedProject.id) {
      state.currentProject = updatedProject
    }
  },
  
  DELETE_PROJECT(state, projectId) {
    state.projects = state.projects.filter(p => p.id !== projectId)
    if (state.currentProject?.id === projectId) {
      state.currentProject = null
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
  async fetchProjects({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.get('/api/projects/')
      commit('SET_PROJECTS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch projects')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchProject({ commit }, projectId) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.get(`/api/projects/${projectId}/`)
      commit('SET_CURRENT_PROJECT', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async createProject({ commit }, projectData) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.post('/api/projects/', projectData)
      commit('ADD_PROJECT', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to create project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async updateProject({ commit }, { projectId, projectData }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.patch(`/api/projects/${projectId}/`, projectData)
      commit('UPDATE_PROJECT', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to update project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async deleteProject({ commit }, projectId) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      await axios.delete(`/api/projects/${projectId}/`)
      commit('DELETE_PROJECT', projectId)
      
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to delete project')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  allProjects: state => state.projects,
  currentProject: state => state.currentProject,
  loading: state => state.loading,
  error: state => state.error,
  
  projectById: state => id => {
    return state.projects.find(project => project.id === id)
  },
  
  sortedProjects: state => {
    return [...state.projects].sort((a, b) => {
      return new Date(b.updated_at) - new Date(a.updated_at)
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 