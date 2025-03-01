import { defineStore } from 'pinia'
import { BuilderAPI } from '../services/api'
import type { Project } from '../types/project'
import { normalizeProject } from '../types/project'
import type { Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { AIModel } from '../types/builder'

interface ProjectState {
  projects: Project[]
  projectsMap: Map<string, Project>
  currentProject: Project | null
  loading: boolean
  error: string | null
  initialized: boolean
  lastFetch: Date | null
  activities: Activity[]
  stats: DashboardStats | null
  availableModels: AIModel[]
  selectedModel: string | null
  isLoading: boolean
  isAuthenticated: boolean
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
    selectedModel: null,
    isLoading: false,
    isAuthenticated: false
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
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    }
  },

  actions: {
    updateProjects(projects: unknown[]) {
      console.debug('Updating projects:', {
        rawProjects: projects,
        isArray: Array.isArray(projects)
      })
      
      if (!Array.isArray(projects)) {
        console.error('Invalid projects data:', projects)
        return
      }
      
      this.projects = projects
        .filter(p => p && typeof p === 'object')
        .map(p => normalizeProject(p))

      this.projectsMap.clear()
      this.projects.forEach(project => {
        if (project.id) {
          this.projectsMap.set(String(project.id), project)
        }
      })
      
      console.debug('Updated store state:', {
        projectCount: this.projects.length,
        mapSize: this.projectsMap.size,
        projects: this.projects
      })
    },

    setAuthenticated(status: boolean) {
      console.debug('Setting authenticated state:', {
        oldState: this.isAuthenticated,
        newState: status
      })
      
      this.isAuthenticated = status
      if (!status) {
        // Clear projects when user is not authenticated
        this.projects = []
        this.projectsMap.clear()
        this.initialized = false
        this.lastFetch = null
      }
    },

    async fetchProjects(force = false) {
      const CACHE_DURATION = 5 * 60 * 1000
      
      console.debug('Fetching projects:', {
        force,
        initialized: this.initialized,
        lastFetch: this.lastFetch,
        projectCount: this.projects.length,
        isAuthenticated: this.isAuthenticated,
        cacheValid: this.lastFetch && (Date.now() - this.lastFetch.getTime()) < CACHE_DURATION
      })

      if (!this.isAuthenticated) {
        console.debug('User not authenticated, skipping project fetch')
        this.projects = []
        this.projectsMap.clear()
        return []
      }

      if (
        !force && 
        this.initialized && 
        this.lastFetch && 
        (Date.now() - this.lastFetch.getTime()) < CACHE_DURATION &&
        this.projects.length > 0
      ) {
        console.debug('Using cached projects')
        return this.projects
      }

      this.setLoading(true)
      this.error = null
      
      try {
        console.debug('Making API call to fetch projects')
        const projects = await BuilderAPI.getProjects()
        console.debug('Received projects from API:', {
          count: projects.length,
          projects
        })
        
        this.updateProjects(projects)
        this.initialized = true
        this.lastFetch = new Date()
        return this.projects
      } catch (err: any) {
        console.error('Error in fetchProjects:', {
          error: err,
          status: err.response?.status,
          data: err.response?.data
        })
        
        if (err.response?.status === 401) {
          this.setAuthenticated(false)
          this.error = 'Please log in to view your projects'
        } else {
          this.handleError(err, 'Failed to fetch projects')
        }
        throw err
      } finally {
        this.setLoading(false)
      }
    },

    async createProject(projectData: { name: string; description: string }) {
      if (!this.isAuthenticated) {
        throw new Error('You must be logged in to create projects')
      }

      this.loading = true
      this.error = null
      
      try {
        console.debug('Creating project:', projectData)
        const newProject = await BuilderAPI.createProject(projectData)
        
        console.debug('Project created:', newProject)
        
        if (!newProject || typeof newProject !== 'object') {
          throw new Error('Invalid project data received')
        }

        const normalizedProject = normalizeProject(newProject)
        
        // Update local state
        this.projects = [...this.projects, normalizedProject]
        this.projectsMap.set(String(normalizedProject.id), normalizedProject)
        
        console.debug('Store updated with new project:', {
          projectId: normalizedProject.id,
          totalProjects: this.projects.length,
          project: normalizedProject
        })
        
        return normalizedProject
      } catch (err: any) {
        console.error('Project creation error in store:', {
          error: err,
          message: err.message,
          status: err.response?.status,
          data: err.response?.data
        })
        this.handleError(err, 'Failed to create project')
        throw err
      } finally {
        this.loading = false
      }
    },

    async deleteProject(projectId: string) {
      if (!this.isAuthenticated) {
        throw new Error('You must be logged in to delete projects')
      }

      if (!projectId) {
        throw new Error('Project ID is required')
      }

      this.loading = true
      this.error = null
      
      try {
        console.debug('Deleting project:', {
          projectId,
          existingProject: this.projectsMap.get(String(projectId))
        })

        await BuilderAPI.deleteProject(projectId)
        
        // Remove from projects array
        this.projects = this.projects.filter(p => String(p.id) !== String(projectId))
        // Remove from map
        this.projectsMap.delete(String(projectId))
        
        console.debug('Project deleted, store updated:', {
          remainingProjects: this.projects.length,
          deletedId: projectId
        })
        
      } catch (err: any) {
        console.error('Project deletion error in store:', {
          error: err,
          message: err.message,
          status: err.response?.status,
          data: err.response?.data,
          projectId
        })
        this.handleError(err, 'Failed to delete project')
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchActivities() {
      try {
        const activities = await BuilderAPI.getActivities()
        this.activities = activities
        return activities
      } catch (error) {
        console.warn('Failed to fetch activities:', error)
        return [] // Return empty array as fallback
      }
    },

    async fetchStats() {
      try {
        const stats = await BuilderAPI.getStats()
        this.stats = stats
        return stats
      } catch (error) {
        console.warn('Failed to fetch stats:', error)
        return {
          activeBuildCount: 0,
          apiCallCount: 0,
          creditsUsed: 0
        }
      }
    },

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
    },

    // Add simplified loading state setters for JS compatibility
    setLoading(loading: boolean) {
      this.loading = loading;
      this.isLoading = loading; // Update both for compatibility
    },

    // New actions
    async fetchProject(id: string): Promise<Project> {
      this.loading = true
      try {
        const data = await BuilderAPI.getProject(id)
        const project = normalizeProject(data)
        this.currentProject = project
        return project
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to fetch project'
        throw err
      } finally {
        this.loading = false
      }
    },

    setSelectedModel(model: string | null) {
      this.selectedModel = model
    },

    async fetchAvailableModels() {
      this.loading = true
      try {
        const models = await BuilderAPI.getAvailableModels()
        this.availableModels = models
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'Failed to fetch models'
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
