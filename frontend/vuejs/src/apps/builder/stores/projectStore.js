import { defineStore } from 'pinia';
import { BuilderAPI } from '../services/api';

export const useProjectStore = defineStore('builder', {
  state: () => ({
    projects: [],
    projectsMap: new Map(), // For O(1) lookups
    currentProject: null,
    loading: false,
    error: null,
    initialized: false,
    lastFetch: null
  }),

  getters: {
    hasProjects: (state) => state.initialized && state.projects.length > 0,
    getProjectById: (state) => (id) => state.projectsMap.get(id),
    
    // Get projects sorted by last update
    sortedProjects: (state) => {
      return [...state.projects].sort(
        (a, b) => new Date(b.updated_at) - new Date(a.updated_at)
      );
    }
  },

  actions: {
    async fetchProjects(force = false) {
      // Cache projects for 5 minutes unless force refresh
      const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
      if (
        !force && 
        this.initialized && 
        this.lastFetch && 
        (Date.now() - this.lastFetch) < CACHE_DURATION
      ) {
        return this.projects;
      }

      this.loading = true;
      this.error = null;
      
      try {
        const response = await BuilderAPI.getProjects();
        this.updateProjects(response);
        this.initialized = true;
        this.lastFetch = Date.now();
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

    updateProjects(projects) {
      this.projects = projects;
      // Update lookup map
      this.projectsMap.clear();
      projects.forEach(project => {
        this.projectsMap.set(project.id, project);
      });
    },

    clearError() {
      this.error = null;
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

    async fetchAvailableModels() {
      if (this.loading) return;
      
      this.loading = true;
      this.error = null;

      try {
        const models = await BuilderAPI.getAvailableModels();
        this.availableModels = models;
        
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

    setCurrentProject(project) {
      this.currentProject = project
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