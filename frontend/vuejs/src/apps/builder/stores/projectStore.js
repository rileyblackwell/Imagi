import { defineStore } from 'pinia';
import { BuilderAPI } from '../services/api';

export const useProjectStore = defineStore('projects', {
  state: () => ({
    projects: [],
    loading: false,
    error: null,
    currentProject: null,
    initialized: false
  }),

  getters: {
    activeProjects: (state) => {
      // Return only active projects, ensuring no duplicates
      return state.projects.filter(p => p.is_active)
    },
    getProjectById: (state) => (id) => state.projects.find(p => p.id === id),
    hasProjects: (state) => state.initialized && state.projects.length > 0,
    hasError: (state) => !!state.error,
    sortedProjects: (state) => {
      return [...state.projects].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    }
  },

  actions: {
    async fetchProjects() {
      if (this.loading) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const data = await BuilderAPI.getProjects();
        if (Array.isArray(data)) {
          this.projects = data;
        } else {
          console.warn('Expected array of projects but got:', data);
          this.projects = [];
        }
        this.initialized = true;
      } catch (err) {
        console.error('Failed to fetch projects:', err);
        this.error = err.response?.data?.detail || 
                    err.response?.data?.error ||
                    'Failed to fetch projects';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchProject(projectId) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get(`${API_BASE_URL}/projects/${projectId}/`, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        this.currentProject = response.data
        return response.data
      } catch (err) {
        console.error('Failed to fetch project:', err)
        if (err.response?.status === 404) {
          this.error = 'Project not found.'
        } else if (err.response?.status === 401) {
          this.error = 'Please log in to view this project.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to fetch project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async createProject(projectData) {
      if (this.loading) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const newProject = await BuilderAPI.createProject(projectData);
        this.projects.unshift(newProject);
        return newProject;
      } catch (err) {
        this.handleError(err, 'Failed to create project');
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async updateProject({ projectId, projectData }) {
      this.loading = true
      this.error = null
      try {
        const response = await axios.patch(`${API_BASE_URL}/projects/${projectId}/`, projectData, {
          withCredentials: true,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })

        const updatedProject = response.data
        const index = this.projects.findIndex(p => p.id === projectId)
        if (index !== -1) {
          this.projects.splice(index, 1, updatedProject)
        }
        if (this.currentProject?.id === projectId) {
          this.currentProject = updatedProject
        }
        return updatedProject
      } catch (err) {
        console.error('Failed to update project:', err)
        if (err.response?.status === 401) {
          this.error = 'Please log in to update this project.'
        } else if (err.response?.status === 404) {
          this.error = 'Project not found.'
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to update project'
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteProject(projectId) {
      if (this.loading) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        await BuilderAPI.deleteProject(projectId);
        this.projects = this.projects.filter(p => p.id !== projectId);
        if (this.currentProject?.id === projectId) {
          this.currentProject = null;
        }
      } catch (err) {
        this.handleError(err, 'Failed to delete project');
        throw err;
      } finally {
        this.loading = false;
      }
    },

    setCurrentProject(project) {
      this.currentProject = project
    },

    clearError() {
      this.error = null
    },

    handleError(err, defaultMessage) {
      console.error(defaultMessage + ':', err);
      if (err.response?.status === 401) {
        this.error = 'Please log in to continue';
      } else if (err.response?.data?.error) {
        this.error = err.response.data.error;
      } else {
        this.error = defaultMessage;
      }
    }
  }
});