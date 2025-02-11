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
    hasProjects: (state) => state.initialized && state.projects.length > 0,
    getProjectById: (state) => (id: string) => state.projectsMap.get(id),
    
    sortedProjects: (state) => {
      return [...state.projects].sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      )
    }
  },

  actions: {
    updateProjects(projects: Project[]) {
      this.projects = projects
      // Update lookup map
      this.projectsMap.clear()
      projects.forEach(project => {
        this.projectsMap.set(project.id, project)
      })
    },

    async fetchProjects(force = false) {
      const CACHE_DURATION = 5 * 60 * 1000
      if (
        !force && 
        this.initialized && 
        this.lastFetch && 
        (Date.now() - this.lastFetch.getTime()) < CACHE_DURATION
      ) {
        return this.projects
      }

      this.loading = true
      this.error = null
      
      try {
        const response = await BuilderAPI.getProjects()
        this.updateProjects(response)
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
    }
  }
})
