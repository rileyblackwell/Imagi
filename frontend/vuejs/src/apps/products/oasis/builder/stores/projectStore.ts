import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { ProjectService } from '../services/projectService'
import { AgentService } from '../services/agentService'
import api from '../services/api'
import type { Project } from '../types/project'
import { normalizeProject } from '../types/project'
import type { Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { AIModel } from '../types/builder'
import { useAuthStore } from '@/shared/stores/auth'

/**
 * Project Store
 * 
 * This store handles all project management operations:
 * 1. Project creation (via dashboard)
 * 2. Project deletion (via dashboard)
 * 3. Project listing and fetching (via dashboard)
 * 4. Project details loading (used by workspace)
 * 
 * Note: Actual file/content editing operations are NOT handled by this store
 * Those are managed by the BuilderStore and related composables
 */
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
  
  // Get global auth store
  const globalAuthStore = useAuthStore()
  
  // Watch for changes in global auth state
  watch(
    () => globalAuthStore.isAuthenticated,
    (newValue) => {
      setAuthenticated(newValue)
    },
    { immediate: true }
  )

  // Getters
  const hasProjects = computed(() => {
    const hasValidProjects = projects.value.length > 0
    return hasValidProjects
  })

  const getProjectById = (id: string) => projectsMap.value.get(id)
  
  const sortedProjects = computed(() => {
    return [...projects.value].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  })

  // Actions - Project Management (Dashboard)
  
  /**
   * Update projects list in store
   * Used internally by the store
   */
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

  /**
   * Set authentication state
   * Called when auth state changes
   */
  function setAuthenticated(status: boolean) {
    if (isAuthenticated.value === status) {
      return
    }
    
    isAuthenticated.value = status
    
    if (status) {
      // When authenticated, sync the auth token from global store to API
      const token = globalAuthStore.token
      if (token) {
        api.defaults.headers.common['Authorization'] = `Token ${token}`
      }
    } else {
      // Clear projects when user is not authenticated
      projects.value = []
      projectsMap.value.clear()
      initialized.value = false
      lastFetch.value = null
      
      // Remove Authorization header
      delete api.defaults.headers.common['Authorization']
    }
  }

  /**
   * Verify that the token is valid and update authentication state if needed
   */
  async function verifyToken(): Promise<boolean> {
    try {
      console.debug('Verifying authentication token...')
      
      // First check global auth store - the source of truth
      if (globalAuthStore.isAuthenticated && globalAuthStore.token) {
        console.debug('Token verified via global auth store')
        // Ensure our local state matches
        setAuthenticated(true)
        // Ensure API headers are set
        api.defaults.headers.common['Authorization'] = `Token ${globalAuthStore.token}`
        return true
      }
      
      // If global auth store says we're not authenticated, respect that
      if (!globalAuthStore.isAuthenticated) {
        console.debug('Global auth store says not authenticated')
        setAuthenticated(false)
        return false
      }
      
      // Fallback: Check if we have a token in localStorage
      const tokenData = localStorage.getItem('token')
      if (!tokenData) {
        console.debug('No token in localStorage')
        setAuthenticated(false)
        return false
      }
      
      try {
        const parsedToken = JSON.parse(tokenData)
        if (!parsedToken || !parsedToken.value) {
          console.debug('Invalid token format in localStorage')
          setAuthenticated(false)
          return false
        }
        
        // Check if token is expired
        if (parsedToken.expires && Date.now() > parsedToken.expires) {
          console.debug('Token is expired')
          localStorage.removeItem('token')
          setAuthenticated(false)
          return false
        }
        
        // Ensure token is set in API headers
        api.defaults.headers.common['Authorization'] = `Token ${parsedToken.value}`
        
        // Try to verify the token with a quick API call
        try {
          await api.get('/auth/user/')
          setAuthenticated(true)
          return true
        } catch (apiError: any) {
          // If we get a 401 error, the token is invalid
          if (apiError.response?.status === 401) {
            console.debug('Token verification failed with 401')
            setAuthenticated(false)
            return false
          }
          
          // For other errors, assume the token is still valid
          console.debug('Token verification API call failed, but continuing', apiError)
          setAuthenticated(true)
          return true
        }
      } catch (parseError) {
        console.error('Error parsing token:', parseError)
        setAuthenticated(false)
        return false
      }
    } catch (error) {
      console.error('Error verifying token:', error)
      setAuthenticated(false)
      return false
    }
  }

  /**
   * Fetch all projects for the current user
   * Used by dashboard components to display project list
   * This should not be called directly from workspace components
   */
  async function fetchProjects(force = false) {
    // Reduced cache duration from 5 minutes to 30 seconds to prevent stale data
    const CACHE_DURATION = 30 * 1000
    
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
      // Verify token before making API calls
      const isValid = await verifyToken()
      if (!isValid) {
        throw new Error('Authentication token is invalid or expired')
      }

      console.debug('Fetching projects from API')
      const projectsData = await ProjectService.getProjects()
      
      if (!projectsData || !Array.isArray(projectsData)) {
        throw new Error('Invalid response from server')
      }
      
      console.debug(`Fetched ${projectsData.length} projects from API`)
      
      // Get list of recently deleted project IDs
      let deletedProjectIds: string[] = []
      try {
        deletedProjectIds = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
      } catch (e) {
        console.warn('Failed to parse deleted projects from localStorage:', e)
      }
      
      // Filter out recently deleted projects from the fetched data
      const filteredProjects = projectsData.filter(project => {
        // Skip projects that are in the deleted list
        if (project && project.id && deletedProjectIds.includes(String(project.id))) {
          console.debug(`Filtering out deleted project: ${project.id}`)
          return false
        }
        return true
      })
      
      console.debug(`After filtering deleted projects: ${filteredProjects.length} projects remaining`)
      
      // Update projects in store
      updateProjects(filteredProjects)
      initialized.value = true
      lastFetch.value = new Date()
      
      // Clean up old deleted project IDs (older than 1 hour)
      try {
        const ONE_HOUR = 60 * 60 * 1000
        const now = Date.now()
        const deletedProjectsWithTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
        
        // Keep track of which projects to remove from the deleted list
        const projectsToRemove: string[] = []
        
        for (const projectId of deletedProjectIds) {
          const timestamp = deletedProjectsWithTimestamp[projectId]
          if (timestamp && (now - timestamp) > ONE_HOUR) {
            projectsToRemove.push(projectId)
          } else if (!timestamp) {
            // Add timestamp for projects that don't have one yet
            deletedProjectsWithTimestamp[projectId] = now
          }
        }
        
        // Remove expired deleted projects
        if (projectsToRemove.length > 0) {
          const updatedDeletedProjects = deletedProjectIds.filter(id => !projectsToRemove.includes(id))
          localStorage.setItem('deletedProjects', JSON.stringify(updatedDeletedProjects))
          
          // Also update the timestamps
          for (const projectId of projectsToRemove) {
            delete deletedProjectsWithTimestamp[projectId]
          }
          
          localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsWithTimestamp))
        } else {
          // Just update the timestamps
          localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsWithTimestamp))
        }
      } catch (e) {
        console.warn('Failed to clean up old deleted project IDs:', e)
      }
      
      return projects.value
    } catch (err: any) {
      handleError(err, 'Failed to fetch projects')
      return []
    } finally {
      setLoading(false)
    }
  }

  /**
   * Create a new project
   * Used by dashboard components for project creation
   * Should not be called from workspace components
   */
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
      
      // Initialize the project right after creation
      try {
        await initializeProject(String(normalizedProject.id))
      } catch (initError: any) {
        console.warn('Project created but initialization failed:', initError)
        // Don't rethrow - we want to return the created project even if initialization fails
      }
      
      // Force refresh projects to ensure we have the most current data
      setTimeout(() => {
        fetchProjects(true).catch(error => {
          console.error('Failed to refresh projects after creation:', error)
        })
      }, 1000)
      
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

  /**
   * Initialize an existing project
   * This sets up the initial project structure
   */
  async function initializeProject(projectId: string) {
    if (!isAuthenticated.value) {
      throw new Error('You must be logged in to initialize projects')
    }

    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      console.debug('Initializing project:', projectId)
      
      // Implement retry logic with exponential backoff for project initialization
      let attempts = 0
      const maxAttempts = 3
      const baseDelay = 1000 // 1 second
      let result = null
      let lastError = null
      
      while (attempts < maxAttempts) {
        try {
          console.debug(`Initialize project attempt ${attempts + 1}/${maxAttempts} for project ${projectId}`)
          result = await ProjectService.initializeProject(projectId)
          
          // If we get here, the request succeeded
          console.debug('Project initialized successfully:', {
            projectId, 
            result
          })
          
          // Update the project in the store if it's present
          const project = projectsMap.value.get(String(projectId))
          if (project) {
            project.is_initialized = true
            projectsMap.value.set(String(projectId), project)
          }
          
          return result
        } catch (err: any) {
          attempts++
          lastError = err
          
          console.error(`Project initialization attempt ${attempts} failed:`, {
            error: err,
            message: err.message
          })
          
          // If this is the last attempt, we'll throw the error below after exiting the loop
          if (attempts >= maxAttempts) {
            break
          }
          
          // If it's a 404 or 403 error, don't retry
          if (err.response?.status === 404 || err.response?.status === 403) {
            console.error('Not retrying due to 404/403 error')
            break
          }
          
          // Wait before the next attempt with exponential backoff
          const delay = baseDelay * Math.pow(2, attempts - 1)
          console.debug(`Retrying initialization in ${delay}ms...`)
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }
      
      // If we got here with no result, throw the last error
      if (!result) {
        console.error('All initialization attempts failed:', lastError)
        
        // Format a more helpful error message
        let errorMessage = 'Failed to initialize project'
        if (lastError?.message) {
          errorMessage = lastError.message
        } else if (lastError?.response?.data?.error) {
          errorMessage = lastError.response.data.error
        }
        
        handleError(lastError, 'Failed to initialize project')
        throw new Error(errorMessage)
      }
      
      return result
    } catch (err: any) {
      console.error('Project initialization error in store:', {
        error: err,
        message: err.message,
        status: err.response?.status,
        data: err.response?.data
      })
      
      // Only throw if it's not already initialized (409 Conflict)
      if (!err.response || err.response.status !== 409) {
        handleError(err, 'Failed to initialize project')
        throw err
      }
      
      // Return success: true for already initialized projects
      return { success: true, already_initialized: true }
    }
  }

  /**
   * Delete an existing project
   * Used by dashboard components for project deletion
   * Should not be called from workspace components
   */
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

      // Keep track of deleted project IDs to prevent them from reappearing on refresh
      const deletedProjectId = String(projectId)
      
      // Delete the project on the server
      await ProjectService.deleteProject(projectId)
      
      // Remove from projects array
      projects.value = projects.value.filter(p => String(p.id) !== deletedProjectId)
      
      // Remove from map
      projectsMap.value.delete(deletedProjectId)
      
      console.debug('Project deleted, store updated:', {
        remainingProjects: projects.value.length,
        deletedId: deletedProjectId
      })
      
      // Store deleted project IDs in localStorage to prevent them from reappearing
      // during periodic refreshes before the server fully processes the deletion
      try {
        const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
        if (!deletedProjects.includes(deletedProjectId)) {
          deletedProjects.push(deletedProjectId)
          localStorage.setItem('deletedProjects', JSON.stringify(deletedProjects))
          
          // Also store timestamp for cleanup purposes
          const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
          deletedProjectsTimestamp[deletedProjectId] = Date.now()
          localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
        }
      } catch (e) {
        console.error('Failed to store deleted project ID in localStorage:', e)
      }
      
      // Force refresh projects after a longer delay to ensure server has processed the deletion
      setTimeout(() => {
        fetchProjects(true).catch(error => {
          console.error('Failed to refresh projects after deletion:', error)
        })
      }, 2000)
      
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

  /**
   * Fetch activities for dashboard
   * Used by dashboard components only
   */
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

  /**
   * Fetch stats for dashboard
   * Used by dashboard components only
   */
  async function fetchStats() {
    try {
      const statsData = await ProjectService.getStats()
      stats.value = statsData
      return statsData
    } catch (error) {
      return {
        activeBuildCount: 0,
        apiCallCount: 0,
        creditsUsed: 0
      }
    }
  }

  // Actions - Project Loading (for Workspace)
  
  /**
   * Fetch a single project by ID
   * Used by workspace to load project details
   * Should not modify the projects list
   */
  async function fetchProject(projectId: string, isNewProject = false): Promise<Project | null> {
    if (!projectId) {
      return null
    }
    
    loading.value = true
    let error = null
    let project = null
    
    try {
      // For new projects, implement a retry strategy with backoff
      if (isNewProject) {
        let attempts = 0
        const maxAttempts = 3
        const baseDelay = 1000 // 1 second
        
        while (attempts < maxAttempts) {
          try {
            console.log(`ProjectStore: Attempt ${attempts + 1}/${maxAttempts} to fetch new project ${projectId}`)
            project = await ProjectService.getProject(projectId, true)
            break // Success, exit the retry loop
          } catch (err) {
            attempts++
            
            if (attempts >= maxAttempts) {
              console.error(`ProjectStore: Failed to fetch new project after ${maxAttempts} attempts`)
              throw err
            }
            
            // Exponential backoff
            const delay = baseDelay * Math.pow(2, attempts - 1)
            console.log(`ProjectStore: Retrying in ${delay}ms...`)
            await new Promise(resolve => setTimeout(resolve, delay))
          }
        }
      } else {
        // Normal fetch for existing projects
        project = await ProjectService.getProject(projectId)
      }
      
      if (project) {
        currentProject.value = normalizeProject(project)
        error = null
      }
    } catch (err) {
      console.error('ProjectStore: Error fetching project', err)
      error = err
      throw err
    } finally {
      loading.value = false
    }
    
    return currentProject.value
  }

  async function fetchProjectFiles(projectId: string) {
    try {
      const files = await ProjectService.getProjectFiles(projectId)
      // Process and store the files
      return files
    } catch (error) {
      // Handle error
      throw error
    }
  }

  async function createFile(projectId: string, filePath: string, content: string) {
    try {
      const file = await ProjectService.createFile(projectId, filePath, content)
      // Process and update store
      return file
    } catch (error) {
      // Handle error
      throw error
    }
  }

  async function updateFileContent(projectId: string, filePath: string, content: string) {
    try {
      const file = await ProjectService.updateFileContent(projectId, filePath, content)
      // Process and update store
      return file
    } catch (error) {
      // Handle error
      throw error
    }
  }

  async function deleteFile(projectId: string, filePath: string) {
    try {
      await ProjectService.deleteFile(projectId, filePath)
      // Update store
      return true
    } catch (error) {
      // Handle error
      throw error
    }
  }

  // Utility functions
  
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

  // AI model functionality
  
  function setSelectedModel(model: string | null) {
    selectedModel.value = model
  }

  async function fetchAvailableModels() {
    loading.value = true
    try {
      const models = await AgentService.getAvailableModels()
      availableModels.value = models
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch models'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Creates a new utility method to ensure fresh project data
   * This can be called from anywhere in the app to ensure we have the latest data
   */
  async function refreshProjectData() {
    // Skip if not authenticated
    if (!isAuthenticated.value) {
      return
    }
    
    console.debug('Forcing project data refresh')
    
    try {
      // Always use force=true to bypass any caching
      return await fetchProjects(true)
    } catch (error) {
      console.error('Failed to refresh project data:', error)
      throw error
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
    fetchAvailableModels,
    fetchProjectFiles,
    createFile,
    updateFileContent,
    deleteFile,
    refreshProjectData
  }
})
