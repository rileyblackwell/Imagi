import { ref, computed } from 'vue'
import { useProjectStore } from '../stores/projectStore'
import { useBuilderMode } from './useBuilderMode'
import { useAgentStore } from '../stores/agentStore'

export const useProjects = () => {
  const store = useProjectStore()
  const agentStore = useAgentStore()
  const builderMode = useBuilderMode()

  // Handle file changes with proper error handling and optimistic updates
  const handleFileUpdate = async (content: string) => {
    if (!agentStore.selectedFile || !store.currentProject?.id) return

    try {
      await builderMode.updateFile(String(store.currentProject.id), agentStore.selectedFile.path, content)
    } catch (err) {
      throw err
    }
  }

  // Create new file with proper validation
  const handleFileCreate = async (name: string, type: string) => {
    if (!store.currentProject?.id) {
      throw new Error('No project selected')
    }

    // Validate file name
    if (!/^[\w-]+([./][\w-]+)*$/.test(name)) {
      throw new Error('Invalid file name. Use only letters, numbers, dashes, and dots.')
    }

    try {
      const newFile = await builderMode.createFile(name, type)
      return newFile
    } catch (err) {
      console.error('File creation failed:', err)
      throw err
    }
  }

  return {
    // Original store properties
    ...store,
    // Computed properties from JS version
    projects: computed(() => store.projects),
    currentProject: computed(() => store.currentProject),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    // File handling methods
    handleFileUpdate,
    handleFileCreate,
    // Project management methods
    fetchProjects: store.fetchProjects,
    fetchProject: store.fetchProject,
    createProject: store.createProject,
    updateProjects: store.updateProjects,
    deleteProject: store.deleteProject,
    clearError: store.clearError
  }
}