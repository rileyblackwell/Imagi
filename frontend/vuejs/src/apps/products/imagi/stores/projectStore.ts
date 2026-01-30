import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { ProjectService } from '../services/projectService'
import type { Project } from '../types/components'
import { normalizeProject } from '../types/components'
import type { Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { AIModel } from '../types/services'
import { useAuthStore } from '@/shared/stores/auth'

// Constants
const DEBOUNCE_DURATION = 1000 // 1 second
const CACHE_EXPIRY_TIME = 5 * 60 * 1000 // 5 minutes (was 30 seconds)

// Create static request tracker outside the store to prevent duplicate calls across component instances
let globalProjectListRequest: Promise<Project[]> | null = null;
let globalProjectListRequestExpiry = 0;
const PROJECT_LIST_CACHE_DURATION = 60000; // 1 minute

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
  
  // Track project fetch caching to prevent duplicate calls
  const projectFetchPromises = ref<Map<string, Promise<Project | null>>>(new Map())
  const lastProjectFetch = ref<Map<string, number>>(new Map())
  const PROJECT_CACHE_DURATION = 5000 // 5 seconds
  
  // Use for tracking global fetch operations
  const currentFetchPromise = ref<Promise<any> | null>(null)
  
  // Get global auth store
  const globalAuthStore = useAuthStore()
  
  // Watch for changes in global auth state
  watch(
    () => globalAuthStore.isAuthenticated,
    (newValue) => {
      setAuthenticated(newValue)
      
      // Clean up old deleted projects when auth state changes
      if (newValue) {
        cleanupDeletedProjects()
      }
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
    
    if (!status) {
      // Clear projects when user is not authenticated
      projects.value = []
      projectsMap.value.clear()
      initialized.value = false
      lastFetch.value = null
    }
  }

  /**
   * Verify that the token is valid and update authentication state if needed
   */
  async function verifyToken(): Promise<boolean> {
    try {
      console.debug('Verifying authentication token...')
      
      // Use the global auth store for token validation - it's the source of truth
      if (globalAuthStore.isAuthenticated && globalAuthStore.token) {
        console.debug('Token verified via global auth store')
        setAuthenticated(true)
        return true
      }
      
      // If global auth store says we're not authenticated, but we need to check if there's a valid token
      if (!globalAuthStore.isAuthenticated) {
        try {
          // Try to validate auth through the auth store
          await globalAuthStore.validateAuth()
          if (globalAuthStore.isAuthenticated) {
            setAuthenticated(true)
            return true
          }
        } catch (error) {
          console.debug('Auth validation failed:', error)
        }
        
        console.debug('Global auth store says not authenticated')
        setAuthenticated(false)
        return false
      }
      
      // Fallback - should not reach here normally
      setAuthenticated(globalAuthStore.isAuthenticated)
      return globalAuthStore.isAuthenticated
    } catch (error) {
      console.error('Error verifying token:', error)
      setAuthenticated(false)
      return false
    }
  }

  /**
   * Fetch projects from API
   * May hit cache if data is fresh
   * @param force Force fetch even if cache is fresh
   */
  async function fetchProjects(force = false) {
    // Skip if not authenticated
    if (!isAuthenticated.value) {
      console.debug('Not authenticated, skipping project fetch')
      return []
    }
    
    // Check if we have cached data and force is false
    if (!force && 
        initialized.value && 
        lastFetch.value && 
        projects.value.length > 0 && 
        (new Date().getTime() - lastFetch.value.getTime() < CACHE_EXPIRY_TIME)) {
      console.debug('Using cached projects:', projects.value.length)
      return projects.value
    }
    
    // If there's already a fetch in progress, return that promise
    if (currentFetchPromise.value) {
      console.debug('Request already in progress, using existing promise')
      return currentFetchPromise.value
    }
    
    // Check if there's a global request that's still recent
    if (globalProjectListRequest && (Date.now() < globalProjectListRequestExpiry)) {
      console.debug('Using recent global projects request')
      return globalProjectListRequest
    }
    
    // Start loading
    setLoading(true)
    
    // Create fetch promise
    const fetchPromise = (async () => {
      error.value = null
      
      try {
        // Verify token before making API calls
        const isValid = await verifyToken()
        if (!isValid) {
          throw new Error('Authentication token is invalid or expired')
        }

        console.debug('Fetching projects from API')
        const projectsData = await ProjectService.getProjects(force)
        
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
        
        return filteredProjects
      } catch (err: any) {
        handleError(err, 'Failed to fetch projects')
        return []
      } finally {
        setLoading(false)
        
        // Clear the current fetch promise after a short delay
        // This prevents multiple simultaneous requests but allows new requests after a delay
        setTimeout(() => {
          if (currentFetchPromise.value === fetchPromise) {
            currentFetchPromise.value = null
          }
          
          // Also clear the global request reference if it matches this one
          if (globalProjectListRequest === fetchPromise) {
            globalProjectListRequest = null
          }
        }, DEBOUNCE_DURATION)
      }
    })()
    
    // Store the promise for deduplication (both locally and globally)
    currentFetchPromise.value = fetchPromise
    globalProjectListRequest = fetchPromise
    globalProjectListRequestExpiry = Date.now() + 2000 // Set expiry for 2 seconds
    
    return fetchPromise
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
      
      // Don't automatically refresh here - let the calling component decide
      // The ProjectService already clears the cache, and the component will refresh
      
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

      const deletedProjectId = String(projectId)
      
      // Store deleted project IDs in localStorage FIRST to prevent any race conditions
      // This ensures no other part of the app tries to fetch this project during deletion
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
      
      // Remove from local state IMMEDIATELY to update the UI
      projects.value = projects.value.filter(p => String(p.id) !== deletedProjectId)
      projectsMap.value.delete(deletedProjectId)
      
      // Clear current project if it's the one being deleted
      if (currentProject.value && String(currentProject.value.id) === deletedProjectId) {
        currentProject.value = null
      }
      
      // Clear any cached fetch promises for this project
      projectFetchPromises.value.delete(deletedProjectId)
      lastProjectFetch.value.delete(deletedProjectId)
      
      console.debug('Project removed from local state:', {
        remainingProjects: projects.value.length,
        deletedId: deletedProjectId
      })
      
      // Now delete the project on the server (this will also clear the cache)
      await ProjectService.deleteProject(projectId)
      
      console.debug('Project deleted from server successfully')
      
      // Do NOT immediately refresh projects to avoid race conditions
      // Let the calling component decide when to refresh if needed
      // This prevents 404 errors during the deletion process
      
    } catch (err: any) {
      console.error('Project deletion error in store:', {
        error: err,
        message: err.message,
        status: err.response?.status,
        data: err.response?.data,
        projectId
      })
      
      // If we get a 404, the project was already deleted - treat as success
      if (err.response?.status === 404) {
        console.debug('Project already deleted (404), treating as success')
        
        // Local state cleanup was already done above, so just return success
        // Don't throw error for 404 - project is gone which is what we wanted
        return
      }
      
      // For other errors, restore the project to local state since deletion failed
      // and remove it from the deleted projects list
      const deletedProjectId = String(projectId)
      
      try {
        // Remove from deleted projects list since deletion failed
        const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
        const updatedDeletedProjects = deletedProjects.filter((id: string) => id !== deletedProjectId)
        localStorage.setItem('deletedProjects', JSON.stringify(updatedDeletedProjects))
        
        // Also remove timestamp
        const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
        delete deletedProjectsTimestamp[deletedProjectId]
        localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
        
        console.debug('Removed project from deleted list due to deletion failure')
      } catch (e) {
        console.warn('Failed to remove project from deleted list after error:', e)
      }
      
      // We don't need to restore to projects array since we need to refresh from API anyway
      // The calling component will handle refreshing the project list
      
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
    
    // Check if project is in the deleted projects list - fail fast
    try {
      const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
      if (deletedProjects.includes(String(projectId))) {
        console.debug(`ProjectStore: Project ${projectId} is in deleted list, not fetching`)
        error.value = 'Project not found'
        throw new Error('Project not found')
      }
    } catch (parseError) {
      if (parseError instanceof Error && parseError.message === 'Project not found') {
        throw parseError
      }
      // Handle JSON parsing errors silently and continue
    }
    
    // Check if there's an existing in-progress fetch for this project
    if (projectFetchPromises.value.has(projectId)) {
      console.debug(`ProjectStore: Reusing existing fetch promise for project ${projectId}`)
      return projectFetchPromises.value.get(projectId)!
    }
    
    // Check cache for recent fetches to avoid duplicate calls
    const now = Date.now()
    const lastFetchTime = lastProjectFetch.value.get(projectId) || 0
    const shouldUseCache = 
      !isNewProject && 
      now - lastFetchTime < PROJECT_CACHE_DURATION && 
      currentProject.value?.id === projectId
    
    if (shouldUseCache) {
      console.debug(`ProjectStore: Using cached project data for ${projectId}`)
      return currentProject.value
    }
    
    // Check if project is already in the projectsMap - this prevents unnecessary API calls
    // when a project was already fetched as part of the projects list
    const existingProject = projectsMap.value.get(projectId)
    if (existingProject && !isNewProject) {
      console.debug(`ProjectStore: Using project from projectsMap for ${projectId}`)
      currentProject.value = existingProject
      // Update cache timestamp for future reference
      lastProjectFetch.value.set(projectId, now)
      return existingProject
    }
    
    loading.value = true
    
    // Create a new promise for this fetch operation
    const fetchPromise = (async () => {
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
          const normalizedProject = normalizeProject(project)
          currentProject.value = normalizedProject
          
          // Also update the project in projectsMap for future reference
          projectsMap.value.set(projectId, normalizedProject)
          
          error = null
          
          // Update cache timestamp
          lastProjectFetch.value.set(projectId, now)
        }
      } catch (err: any) {
        console.error('ProjectStore: Error fetching project', err)
        
        // If project not found (404), add it to deleted projects list to prevent future attempts
        if (err.response?.status === 404 || err.message?.includes('Project not found')) {
          console.debug(`ProjectStore: Project ${projectId} not found, adding to deleted list`)
          try {
            const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
            if (!deletedProjects.includes(String(projectId))) {
              deletedProjects.push(String(projectId))
              localStorage.setItem('deletedProjects', JSON.stringify(deletedProjects))
            }
          } catch (e) {
            // Handle localStorage errors silently
          }
        }
        
        error = err
        throw err
      } finally {
        loading.value = false
        // Remove the promise from the cache when it completes
        setTimeout(() => {
          projectFetchPromises.value.delete(projectId)
        }, 0)
      }
      
      return currentProject.value
    })()
    
    // Store the promise in the cache
    projectFetchPromises.value.set(projectId, fetchPromise)
    
    return fetchPromise
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
      // TODO: Implement getAvailableModels in AgentService or update logic here
      // const models = await AgentService.getAvailableModels()
      const models: any[] = []; // TODO: Type this properly when AgentService.getAvailableModels is implemented
      availableModels.value = models // Will be empty until implemented
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

  /**
   * Update an existing project
   * Used to update project details like name and description
   */
  async function updateProject(projectId: string, projectData: { description?: string; name?: string }) {
    if (!isAuthenticated.value) {
      throw new Error('You must be logged in to update projects')
    }

    if (!projectId) {
      throw new Error('Project ID is required')
    }

    loading.value = true
    error.value = null
    
    try {
      console.debug('Updating project:', { projectId, projectData })
      const updatedProject = await ProjectService.updateProject(projectId, projectData)
      
      console.debug('Project updated:', updatedProject)
      
      if (!updatedProject || typeof updatedProject !== 'object') {
        throw new Error('Invalid project data received')
      }

      const normalizedProject = normalizeProject(updatedProject)
      
      // Update project in local state
      const existingProjectIndex = projects.value.findIndex(p => String(p.id) === String(projectId))
      if (existingProjectIndex !== -1) {
        projects.value[existingProjectIndex] = {
          ...projects.value[existingProjectIndex],
          ...normalizedProject
        }
      }
      
      // Update in projects map
      projectsMap.value.set(String(projectId), normalizedProject)
      
      console.debug('Store updated with modified project:', {
        projectId,
        updatedProject: normalizedProject
      })
      
      // Immediately refresh projects to ensure we have the most current data
      fetchProjects(true).catch(error => {
        console.error('Failed to refresh projects after update:', error)
      })
      
      return normalizedProject
    } catch (err: any) {
      console.error('Project update error in store:', {
        error: err,
        message: err.message,
        status: err.response?.status,
        data: err.response?.data
      })
      handleError(err, 'Failed to update project')
      throw err
    } finally {
      loading.value = false
    }
  }

  // Utility function to clean up old deleted project IDs
  function cleanupDeletedProjects() {
    try {
      const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
      const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
      const now = Date.now()
      const maxAge = 24 * 60 * 60 * 1000 // 24 hours
      
      // Remove projects that were deleted more than 24 hours ago
      const recentlyDeleted = deletedProjects.filter((projectId: string) => {
        const deleteTime = deletedProjectsTimestamp[projectId]
        return deleteTime && (now - deleteTime) < maxAge
      })
      
      // Update localStorage if there were changes
      if (recentlyDeleted.length !== deletedProjects.length) {
        localStorage.setItem('deletedProjects', JSON.stringify(recentlyDeleted))
        
        // Also clean up timestamps
        const cleanedTimestamps: Record<string, number> = {}
        recentlyDeleted.forEach((projectId: string) => {
          if (deletedProjectsTimestamp[projectId]) {
            cleanedTimestamps[projectId] = deletedProjectsTimestamp[projectId]
          }
        })
        localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(cleanedTimestamps))
        
        console.debug(`Cleaned up ${deletedProjects.length - recentlyDeleted.length} old deleted project IDs`)
      }
    } catch (e) {
      console.debug('Error cleaning up deleted projects:', e)
    }
  }

  /**
   * Clear the projects cache
   * Used when immediate cache invalidation is needed
   */
  function clearProjectsCache() {
    ProjectService.clearProjectsCache()
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
    refreshProjectData,
    updateProject,
    clearProjectsCache
  }
})
