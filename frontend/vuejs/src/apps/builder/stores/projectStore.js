import { defineStore } from 'pinia'
import axios from 'axios'

// Update API base URL to match Django's URL configuration
const API_BASE_URL = '/api/projectmanager/api'

export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: [],
    loading: false,
    error: null,
    currentProject: null,
    initialized: false
  }),

  getters: {
    activeProjects: (state) => state.projects.filter(p => p.is_active),
    getProjectById: (state) => (id) => state.projects.find(p => p.id === id),
    hasProjects: (state) => state.initialized && state.projects.length > 0,
    hasError: (state) => !!state.error
  },

  actions: {
    async fetchProjects() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE_URL}/projects/`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        this.projects = Array.isArray(response.data) ? response.data : []
        this.initialized = true
      } catch (err) {
        console.error('Failed to fetch projects:', err)
        if (err.response?.status === 404) {
          this.error = 'Unable to connect to project service. Please try again later.'
        } else if (err.response?.status === 401) {
          this.error = 'Please log in to view your projects.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to fetch projects'
        }
        this.projects = []
      } finally {
        this.loading = false
      }
    },

    async createProject(projectData) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.post(`${API_BASE_URL}/projects/`, {
          name: projectData.name,
          description: projectData.description || `Web application project: ${projectData.name}`
        }, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })

        const newProject = response.data
        this.projects.push(newProject)
        return newProject
      } catch (err) {
        console.error('Failed to create project:', err)
        if (err.response?.status === 401) {
          this.error = 'Please log in to create a project.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to create project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteProject(projectId) {
      this.loading = true
      this.error = null
      try {
        await axios.delete(`${API_BASE_URL}/projects/${projectId}/`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json'
          }
        })
        this.projects = this.projects.filter(p => p.id !== projectId)
      } catch (err) {
        console.error('Failed to delete project:', err)
        if (err.response?.status === 401) {
          this.error = 'Please log in to delete projects.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to delete project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    setCurrentProject(project) {
      this.currentProject = project
    },

    clearError() {
      this.error = null
    }
  }
}) 