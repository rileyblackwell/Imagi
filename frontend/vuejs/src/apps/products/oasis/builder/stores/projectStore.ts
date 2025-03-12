import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { ProjectService, BuilderService } from '../services'
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
      console.log('Global auth state changed in project store watcher:', newValue)
      setAuthenticated(newValue)
    },
    { immediate: true }
  )

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
    console.debug('Setting authenticated state:', {
      oldState: isAuthenticated.value,
      newState: status,
      globalAuthState: globalAuthStore.isAuthenticated
    })
    
    if (isAuthenticated.value === status) {
      console.debug('Auth state unchanged, skipping update')
      return
    }
    
    isAuthenticated.value = status
    
    if (status) {
      // When authenticated, sync the auth token from global store to API
      const token = globalAuthStore.token
      if (token) {
        console.debug('Setting API token from global auth store')
        api.defaults.headers.common['Authorization'] = `Token ${token}`
      } else {
        console.warn('Global auth store has isAuthenticated=true but no token')
      }
    } else {
      // Clear projects when user is not authenticated
      console.debug('User not authenticated, clearing projects')
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
      // Verify token before making API calls
      const isTokenValid = await verifyToken()
      if (!isTokenValid) {
        console.error('Token validation failed, cannot fetch projects')
        error.value = 'Authentication error. Please log in again.'
        return []
      }
      
      console.debug('Making API call to fetch projects')
      
      // Implement retry logic
      let projectsData = null;
      let attempts = 0;
      const maxAttempts = 3;
      
      while (attempts < maxAttempts) {
        try {
          console.debug(`Project fetch attempt ${attempts + 1}/${maxAttempts}`);
          projectsData = await ProjectService.getProjects();
          
          // If we got here, request succeeded
          break;
        } catch (fetchError: any) {
          attempts++;
          console.error(`Project fetch attempt ${attempts} failed:`, {
            error: fetchError,
            message: fetchError.message,
            status: fetchError.response?.status,
            data: fetchError.response?.data
          });
          
          // If this is auth error, don't retry
          if (fetchError.response?.status === 401 || fetchError.response?.status === 403) {
            setAuthenticated(false)
            error.value = 'Authentication error. Please log in again.'
            throw fetchError;
          }
          
          // If this is the last attempt, let the error propagate
          if (attempts >= maxAttempts) {
            throw fetchError;
          }
          
          // Otherwise wait and retry
          const delay = 1000 * Math.pow(2, attempts - 1); // Exponential backoff
          console.debug(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
      
      console.debug('Received projects from API:', {
        count: Array.isArray(projectsData) ? projectsData.length : 0,
        dataType: typeof projectsData,
        isArray: Array.isArray(projectsData),
        data: projectsData
      })
      
      // If we received null, convert to empty array for consistency
      if (projectsData === null) {
        projectsData = [];
      }
      
      if (!Array.isArray(projectsData)) {
        console.warn('Expected array of projects but got:', projectsData)
        console.warn('Converting to empty array to avoid errors')
        updateProjects([])
        initialized.value = true
        lastFetch.value = new Date()
        return []
      }
      
      // Check if we have a valid array but it's empty - this might be legitimate
      if (Array.isArray(projectsData) && projectsData.length === 0) {
        console.debug('API returned empty projects array')
      }
      
      updateProjects(projectsData)
      initialized.value = true
      lastFetch.value = new Date()
      return projects.value
    } catch (err: any) {
      console.error('Error in fetchProjects:', {
        error: err,
        message: err.message,
        status: err.response?.status,
        data: err.response?.data,
        stack: err.stack,
        name: err.name
      })
      
      // Handle network errors specifically
      if (err.message && err.message.includes('Network Error')) {
        error.value = 'Network error. Please check your internet connection and try again.';
        console.error('Network error detected when fetching projects');
      } else if (err.response?.status === 401) {
        setAuthenticated(false)
        error.value = 'Please log in to view your projects'
      } else if (err.response?.status === 404) {
        // API endpoint might be incorrect
        error.value = 'Project listing API not found. Please check the API configuration.'
        console.error('API endpoint not found. Check if the path is correct: /api/v1/builder/projects/')
      } else {
        handleError(err, 'Failed to fetch projects')
      }
      
      // Return empty array to avoid breaking UI
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
      console.warn('Failed to fetch stats:', error)
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
    console.log(`ProjectStore: Fetching project ${projectId}${isNewProject ? ' (NEW PROJECT)' : ''}`)
    
    if (!projectId) {
      console.error('ProjectStore: Cannot fetch project, no projectId provided')
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
