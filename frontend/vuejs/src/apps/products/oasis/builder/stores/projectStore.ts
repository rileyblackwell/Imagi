import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ProjectService, BuilderService } from '../services'
import type { Project } from '../types/project'
import { normalizeProject } from '../types/project'
import type { Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { AIModel } from '../types/builder'

export const useProjectStore = defineStore('builder', () => {
  // State
  const projects = ref<Project[]>([])
  const projectsMap = ref<Map<string, Project>>(new Map())
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const initialized = ref(false)
  const lastFetch = ref<Date | null>(null)
  const activities = ref<Activity[]>([])
  const stats = ref<DashboardStats | null>(null)
  const availableModels = ref<AIModel[]>([])
  const selectedModel = ref<string | null>(null)
  const isLoading = ref(false)
  const isAuthenticated = ref(false)

  // Getters
  const hasProjects = computed(() => {
    const hasValidProjects = projects.value.length > 0
    console.debug('Store hasProjects:', { 
      initialized: initialized.value,
      projectCount: projects.value.length,
      result: hasValidProjects
    })
    return hasValidProjects
  })

  const getProjectById = (id: string) => projectsMap.value.get(id)
  
  const sortedProjects = computed(() => {
    return [...projects.value].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  // Actions
  function updateProjects(projectsData: unknown[]) {
    console.debug('Updating projects:', {
      rawProjects: projectsData,
      isArray: Array.isArray(projectsData)
    })
    
    if (!Array.isArray(projectsData)) {
      console.error('Invalid projects data:', projectsData)
      return
    }
    
    projects.value = projectsData
      .filter(p => p && typeof p === 'object')
      .map(p => normalizeProject(p))

    projectsMap.value.clear()
    projects.value.forEach(project => {
      if (project.id) {
        projectsMap.value.set(String(project.id), project)
      }
    })
    
    console.debug('Updated store state:', {
      projectCount: projects.value.length,
      mapSize: projectsMap.value.size,
      projects: projects.value
    })
  }

  function setAuthenticated(status: boolean) {
    console.debug('Setting authenticated state:', {
      oldState: isAuthenticated.value,
      newState: status
    })
    
    isAuthenticated.value = status
    if (!status) {
      // Clear projects when user is not authenticated
      projects.value = []
      projectsMap.value.clear()
      initialized.value = false
      lastFetch.value = null
    }
  }

  async function fetchProjects(force = false) {
    const CACHE_DURATION = 5 * 60 * 1000
    
    console.debug('Fetching projects:', {
      force,
      initialized: initialized.value,
      lastFetch: lastFetch.value,
      projectCount: projects.value.length,
      isAuthenticated: isAuthenticated.value,
      cacheValid: lastFetch.value && (Date.now() - lastFetch.value.getTime()) < CACHE_DURATION
    })

    if (!isAuthenticated.value) {
      console.debug('User not authenticated, skipping project fetch')
      projects.value = []
      projectsMap.value.clear()
      return []
    }

    if (
      !force && 
      initialized.value && 
      lastFetch.value && 
      (Date.now() - lastFetch.value.getTime()) < CACHE_DURATION &&
      projects.value.length > 0
    ) {
      console.debug('Using cached projects')
      return projects.value
    }

    setLoading(true)
    error.value = null
    
    try {
      console.debug('Making API call to fetch projects')
      const projectsData = await ProjectService.getProjects()
      console.debug('Received projects from API:', {
        count: projectsData.length,
        projects: projectsData
      })
      
      updateProjects(projectsData)
      initialized.value = true
      lastFetch.value = new Date()
      return projects.value
    } catch (err: any) {
      console.error('Error in fetchProjects:', {
        error: err,
        status: err.response?.status,
        data: err.response?.data
      })
      
      if (err.response?.status === 401) {
        setAuthenticated(false)
        error.value = 'Please log in to view your projects'
      } else {
        handleError(err, 'Failed to fetch projects')
      }
      throw err
    } finally {
      setLoading(false)
    }
  }

  async function createProject(projectData: { name: string; description: string }) {
    if (!isAuthenticated.value) {
      throw new Error('You must be logged in to create projects')
    }

    loading.value = true
    error.value = null
    
    try {
      console.debug('Creating project:', projectData)
      const newProject = await ProjectService.createProject(projectData)
      
      console.debug('Project created:', newProject)
      
      if (!newProject || typeof newProject !== 'object') {
        throw new Error('Invalid project data received')
      }

      const normalizedProject = normalizeProject(newProject)
      
      // Update local state
      projects.value = [...projects.value, normalizedProject]
      projectsMap.value.set(String(normalizedProject.id), normalizedProject)
      
      console.debug('Store updated with new project:', {
        projectId: normalizedProject.id,
        totalProjects: projects.value.length,
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
      handleError(err, 'Failed to create project')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteProject(projectId: string) {
    if (!isAuthenticated.value) {
      throw new Error('You must be logged in to delete projects')
    }

    if (!projectId) {
      throw new Error('Project ID is required')
    }

    loading.value = true
    error.value = null
    
    try {
      console.debug('Deleting project:', {
        projectId,
        existingProject: projectsMap.value.get(String(projectId))
      })

      await ProjectService.deleteProject(projectId)
      
      // Remove from projects array
      projects.value = projects.value.filter(p => String(p.id) !== String(projectId))
      // Remove from map
      projectsMap.value.delete(String(projectId))
      
      console.debug('Project deleted, store updated:', {
        remainingProjects: projects.value.length,
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
      handleError(err, 'Failed to delete project')
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchActivities() {
    try {
      const activitiesData = await ProjectService.getActivities()
      activities.value = activitiesData
      return activitiesData
    } catch (error) {
      console.warn('Failed to fetch activities:', error)
      return [] // Return empty array as fallback
    }
  }

  async function fetchStats() {
    try {
      const statsData = await ProjectService.getStats()
      stats.value = statsData
      return statsData
    } catch (error) {
      console.warn('Failed to fetch stats:', error)
      return {
        activeBuildCount: 0,
        apiCallCount: 0,
        creditsUsed: 0
      }
    }
  }

  function handleError(err: any, defaultMessage: string) {
    console.error(defaultMessage + ':', err)
    if (err.response?.status === 401) {
      error.value = 'Please log in to continue'
    } else if (err.response?.data?.error) {
      error.value = err.response.data.error
    } else {
      error.value = defaultMessage
    }
  }

  function clearError() {
    error.value = null
  }

  function setLoading(isLoadingState: boolean) {
    loading.value = isLoadingState
    isLoading.value = isLoadingState // Update both for compatibility
  }

  async function fetchProject(id: string): Promise<Project> {
    loading.value = true
    try {
      const data = await ProjectService.getProject(id)
      const project = normalizeProject(data)
      currentProject.value = project
      return project
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch project'
      throw err
    } finally {
      loading.value = false
    }
  }

  function setSelectedModel(model: string | null) {
    selectedModel.value = model
  }

  async function fetchAvailableModels() {
    loading.value = true
    try {
      const models = await BuilderService.getAvailableModels()
      availableModels.value = models
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch models'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    projects,
    projectsMap,
    currentProject,
    loading,
    error,
    initialized,
    lastFetch,
    activities,
    stats,
    availableModels,
    selectedModel,
    isLoading,
    isAuthenticated,
    
    // Getters
    hasProjects,
    getProjectById,
    sortedProjects,
    
    // Actions
    updateProjects,
    setAuthenticated,
    fetchProjects,
    createProject,
    deleteProject,
    fetchActivities,
    fetchStats,
    handleError,
    clearError,
    setLoading,
    fetchProject,
    setSelectedModel,
    fetchAvailableModels
  }
})
