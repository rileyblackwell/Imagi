import { defineStore } from 'pinia'
import { BuilderAPI } from '../services/api'
import type { Project, Activity, DashboardStats } from '@/apps/home/types/dashboard'

interface ProjectState {
  projects: Project[];
  projectsMap: Map<string, Project>;
  currentProject: Project | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
  lastFetch: Date | null;
  activities: Activity[];
  stats: DashboardStats | null;
  availableModels: Array<{ id: string; name: string }>;
  selectedModel: string | null;
}

export const useProjectStore = defineStore('builder', {
  state: (): ProjectState => ({
    projects: [],
    projectsMap: new Map(),
    currentProject: null,
    loading: false,
    error: null,
    initialized: false,
    lastFetch: null,
    activities: [],
    stats: null,
    availableModels: [],
    selectedModel: null
  }),

  getters: {
    hasProjects: (state) => {
      const hasValidProjects = state.projects.length > 0
      console.debug('Store hasProjects:', { 
        initialized: state.initialized,
        projectCount: state.projects.length,
        result: hasValidProjects
      })
      return hasValidProjects
    },
    getProjectById: (state) => (id: string) => state.projectsMap.get(id),
    
    sortedProjects: (state) => {
      return [...state.projects].sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      )
    }
  },

  actions: {
    updateProjects(projects: Project[]) {
      console.debug('Updating projects:', projects)
      if (!Array.isArray(projects)) {
        console.error('Invalid projects data:', projects)
        return
      }
      
      this.projects = projects.filter(p => p && typeof p === 'object')
      this.projectsMap.clear()
      this.projects.forEach(project => {
        if (project.id) {
          this.projectsMap.set(String(project.id), project)
        }
      })
      
      console.debug('Updated store state:', {
        projectCount: this.projects.length,
        mapSize: this.projectsMap.size
      })
    },

    async fetchProjects(force = false) {
      const CACHE_DURATION = 5 * 60 * 1000
      
      console.debug('Fetching projects:', {
        force,
        initialized: this.initialized,
        lastFetch: this.lastFetch,
        projectCount: this.projects.length
      })

      if (
        !force && 
        this.initialized && 
        this.lastFetch && 
        (Date.now() - this.lastFetch.getTime()) < CACHE_DURATION &&
        this.projects.length > 0
      ) {
        return this.projects
      }

      this.loading = true
      this.error = null
      
      try {
        const projects = await BuilderAPI.getProjects()
        this.updateProjects(projects)
        this.initialized = true
        this.lastFetch = new Date()
        return this.projects
      } catch (err: any) {
        this.handleError(err, 'Failed to fetch projects')
        throw err
      } finally {
        this.loading = false
      }
    },

    async createProject(projectData: { name: string; description: string }) {
      this.loading = true
      this.error = null
      
      try {
        const newProject = await BuilderAPI.createProject(projectData)
        this.projects = [...this.projects, newProject]
        this.projectsMap.set(String(newProject.id), newProject)
        return newProject
      } catch (err: any) {
        this.handleError(err, 'Failed to create project')
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchActivities() {
      try {
        const activities = await BuilderAPI.getActivities()
        this.activities = activities
      } catch (error) {
        console.error('Failed to fetch activities:', error)
        throw error
      }
    },

    async fetchStats() {
      try {
        const stats = await BuilderAPI.getStats()
        this.stats = stats
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        throw error
      }
    },

    // ... rest of existing actions from projectStore.js ...

    handleError(err: any, defaultMessage: string) {
      console.error(defaultMessage + ':', err)
      if (err.response?.status === 401) {
        this.error = 'Please log in to continue'
      } else if (err.response?.data?.error) {
        this.error = err.response.data.error
      } else {
        this.error = defaultMessage
      }
    },

    clearError() {
      this.error = null
    }
  }
})
