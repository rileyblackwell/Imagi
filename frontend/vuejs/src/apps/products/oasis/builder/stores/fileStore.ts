import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { FileService } from '../services/fileService'
import { useAuthStore } from '@/shared/stores/auth'
import type { ProjectFile } from '../types/builder'

/**
 * File Store
 * 
 * This store handles all file management operations:
 * 1. Fetching project files
 * 2. Getting file details
 * 3. Creating files
 * 4. Updating files
 * 5. Deleting files
 * 
 * It's designed to be used by the workspace components for file operations
 */
export const useFileStore = defineStore('file', () => {
  // State
  const files = ref<ProjectFile[]>([])
  const filesMap = ref<Map<string, ProjectFile>>(new Map())
  const currentFile = ref<ProjectFile | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isInitialized = ref(false)
  
  // Get global auth store for authentication state
  const authStore = useAuthStore()
  
  // Getters
  const getFileByPath = (projectId: string, filePath: string) => {
    // Generate a consistent key
    const key = `${projectId}:${filePath}`
    return filesMap.value.get(key)
  }
  
  const sortedFiles = computed(() => {
    // Sort files - directories first, then by name
    return [...files.value].sort((a, b) => {
      // Use path to determine if it's a directory (ends with slash)
      const aIsDir = a.path.endsWith('/') || !a.path.includes('.')
      const bIsDir = b.path.endsWith('/') || !b.path.includes('.')
      
      if (aIsDir && !bIsDir) return -1
      if (!aIsDir && bIsDir) return 1
      
      // If both are directories or both are files, sort by path
      // Extract filename from path as fallback
      const aFilename = a.path.split('/').pop() || ''
      const bFilename = b.path.split('/').pop() || ''
      return aFilename.localeCompare(bFilename)
    })
  })
  
  // Actions
  
  /**
   * Fetch all files for a project
   */
  async function fetchProjectFiles(projectId: string, force = false): Promise<ProjectFile[]> {
    if (!authStore.isAuthenticated) {
      throw new Error('You must be logged in to view project files')
    }
    
    if (!force && isInitialized.value && files.value.length > 0) {
      return files.value
    }
    
    loading.value = true
    error.value = null
    
    try {
      const projectFiles = await FileService.getProjectFiles(projectId)
      
      // Update local state
      files.value = projectFiles
      
      // Update map for quick lookups
      filesMap.value.clear()
      files.value.forEach(file => {
        const key = `${projectId}:${file.path}`
        filesMap.value.set(key, file)
      })
      
      isInitialized.value = true
      return files.value
    } catch (err: any) {
      handleError(err, 'Failed to fetch project files')
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Get a single file by path
   */
  async function fetchFile(projectId: string, filePath: string): Promise<ProjectFile> {
    if (!authStore.isAuthenticated) {
      throw new Error('You must be logged in to view this file')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const file = await FileService.getFile(projectId, filePath)
      
      // Update local state - add/update in map
      const key = `${projectId}:${filePath}`
      filesMap.value.set(key, file)
      
      // Update current file
      currentFile.value = file
      
      return file
    } catch (err: any) {
      handleError(err, 'Failed to fetch file')
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Create a new file
   */
  async function createFile(projectId: string, filePath: string, content: string): Promise<ProjectFile> {
    if (!authStore.isAuthenticated) {
      throw new Error('You must be logged in to create files')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const newFile = await FileService.createFile(projectId, filePath, content)
      
      // Update local state
      const key = `${projectId}:${filePath}`
      filesMap.value.set(key, newFile)
      
      // Refresh files list to include the new file
      await fetchProjectFiles(projectId, true)
      
      return newFile
    } catch (err: any) {
      handleError(err, 'Failed to create file')
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Create a directory
   */
  async function createDirectory(projectId: string, directoryPath: string): Promise<void> {
    if (!authStore.isAuthenticated) {
      throw new Error('You must be logged in to create directories')
    }
    
    loading.value = true
    error.value = null
    
    try {
      await FileService.createDirectory(projectId, directoryPath)
      
      // Refresh files list to include the new directory
      await fetchProjectFiles(projectId, true)
    } catch (err: any) {
      // Directory might already exist, which is fine
      if (err.response?.status !== 409) {
        handleError(err, 'Failed to create directory')
        throw err
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Update file content
   */
  async function updateFileContent(projectId: string, filePath: string, content: string): Promise<ProjectFile> {
    if (!authStore.isAuthenticated) {
      throw new Error('You must be logged in to update files')
    }
    
    loading.value = true
    error.value = null
    
    try {
      const updatedFile = await FileService.updateFileContent(projectId, filePath, content)
      
      // Update local state
      const key = `${projectId}:${filePath}`
      filesMap.value.set(key, updatedFile)
      
      // If this is the current file, update it
      if (currentFile.value && currentFile.value.path === filePath) {
        currentFile.value = updatedFile
      }
      
      return updatedFile
    } catch (err: any) {
      handleError(err, 'Failed to update file')
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Delete a file
   */
  async function deleteFile(projectId: string, filePath: string): Promise<void> {
    if (!authStore.isAuthenticated) {
      throw new Error('You must be logged in to delete files')
    }
    
    loading.value = true
    error.value = null
    
    try {
      await FileService.deleteFile(projectId, filePath)
      
      // Update local state - remove from map
      const key = `${projectId}:${filePath}`
      filesMap.value.delete(key)
      
      // Update files array
      files.value = files.value.filter(file => file.path !== filePath)
      
      // If this was the current file, clear it
      if (currentFile.value && currentFile.value.path === filePath) {
        currentFile.value = null
      }
    } catch (err: any) {
      // If file not found (404), it's already deleted, so no need to throw
      if (err.response?.status !== 404) {
        handleError(err, 'Failed to delete file')
        throw err
      }
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Set the current active file
   */
  function setCurrentFile(file: ProjectFile | null) {
    currentFile.value = file
  }
  
  /**
   * Clear all files
   * Used when changing projects or logging out
   */
  function clearFiles() {
    files.value = []
    filesMap.value.clear()
    currentFile.value = null
    isInitialized.value = false
  }
  
  // Utility functions
  function handleError(err: any, defaultMessage: string) {
    console.error(`${defaultMessage}:`, err)
    
    if (err.response?.status === 401) {
      error.value = 'Please log in to continue'
    } else if (err.response?.data?.error) {
      error.value = err.response.data.error
    } else if (err.message) {
      error.value = err.message
    } else {
      error.value = defaultMessage
    }
  }
  
  function clearError() {
    error.value = null
  }
  
  function setLoading(isLoading: boolean) {
    loading.value = isLoading
  }
  
  return {
    // State
    files,
    filesMap,
    currentFile,
    loading,
    error,
    isInitialized,
    
    // Getters
    getFileByPath,
    sortedFiles,
    
    // Actions
    fetchProjectFiles,
    fetchFile,
    createFile,
    createDirectory,
    updateFileContent,
    deleteFile,
    setCurrentFile,
    clearFiles,
    
    // Utilities
    handleError,
    clearError,
    setLoading
  }
})

export default useFileStore 