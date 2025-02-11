import { defineStore } from 'pinia';
import { BuilderAPI } from '../services/api';

export const useProjectStore = defineStore('builder', {
  state: () => ({
    projects: [],
    currentProject: null,
    availableModels: [],
    selectedModel: null,
    loading: false,
    error: null,
    initialized: false
  }),

  getters: {
    // Project getters
    activeProjects: (state) => state.projects.filter(p => p.is_active),
    getProjectById: (state) => (id) => state.projects.find(p => p.id === id),
    hasProjects: (state) => state.initialized && state.projects.length > 0,
    hasError: (state) => !!state.error,
    sortedProjects: (state) => [...state.projects].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at)),
    
    // Model getters
    hasModels: (state) => state.availableModels.length > 0,
    currentModel: (state) => state.selectedModel || state.availableModels[0],
  },

  actions: {
    // Project actions
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
      this.loading = true;
      this.error = null;
      
      try {
        const data = await BuilderAPI.getProject(projectId);
        this.currentProject = data;
        return data;
      } catch (err) {
        console.error('Failed to fetch project:', err);
        if (err.response?.status === 404) {
          this.error = 'Project not found.';
        } else if (err.response?.status === 401) {
          this.error = 'Please log in to view this project.';
        } else {
          this.error = err.response?.data?.error || err.message || 'Failed to fetch project';
        }
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async createProject(projectData) {
      if (this.loading) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        const response = await BuilderAPI.createProject(projectData);
        console.log('Project creation response:', response);
        
        if (!response || (!response.id && response.id !== 0)) {
          throw new Error('Server returned invalid project data');
        }

        const project = {
          id: Number(response.id),
          name: response.name || projectData.name,
          created_at: response.created_at || new Date().toISOString(),
          updated_at: response.updated_at || new Date().toISOString(),
          is_active: response.is_active !== undefined ? response.is_active : true,
          description: response.description || projectData.description || ''
        };
        
        this.projects.unshift(project);
        return project;
      } catch (err) {
        this.handleError(err, 'Failed to create project');
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async updateProject({ projectId, projectData }) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedProject = await BuilderAPI.updateProject(projectId, projectData);
        const index = this.projects.findIndex(p => p.id === projectId);
        if (index !== -1) {
          this.projects.splice(index, 1, updatedProject);
        }
        if (this.currentProject?.id === projectId) {
          this.currentProject = updatedProject;
        }
        return updatedProject;
      } catch (err) {
        this.handleError(err, 'Failed to update project');
        throw err;
      } finally {
        this.loading = false;
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

    // Model actions
    async fetchAvailableModels() {
      if (this.loading) return;
      
      this.loading = true;
      this.error = null;

      try {
        const models = await BuilderAPI.getAvailableModels();
        this.availableModels = models;
        
        // Set default model if none selected
        if (!this.selectedModel && models.length > 0) {
          this.selectedModel = models[0].id;
        }
      } catch (err) {
        this.handleError(err, 'Failed to fetch AI models');
        throw err;
      } finally {
        this.loading = false;
      }
    },

    setSelectedModel(modelId) {
      if (this.availableModels.some(m => m.id === modelId)) {
        this.selectedModel = modelId;
      } else {
        console.warn('Invalid model ID:', modelId);
      }
    },

    // Shared actions
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