<!--
  Workspace.vue - Project Editing Interface
  
  This component is responsible for:
  1. Loading an existing project's files and data
  2. Supporting chat mode for AI interaction
  3. Editing project files through AI assistance
-->
<template>
  <div class="relative">
    <BuilderLayout 
      storage-key="builderWorkspaceSidebarCollapsed"
      :navigation-items="navigationItems"
    >
      <!-- Sidebar Content: Chat Interface -->
      <template #sidebar-content="{ collapsed }">
        <BuilderSidebarChat
          :selected-app="null"
          :on-prompt-submit="handlePrompt"
          :on-model-select="handleModelSelect"
          :on-mode-switch="handleModeSwitch"
          :on-example-prompt="handleExamplePrompt"
          :is-collapsed="collapsed"
        />
      </template>
      
      <!-- Preview button and account balance display in navbar right -->
      <template #navbar-right>
        <div class="flex items-center gap-3">
          <PreviewButton :project-id="projectId" />
          <AccountBalanceDisplay />
        </div>
      </template>

      <!-- Clean Main Content Area - Matching Homepage -->
      <div class="flex flex-col h-screen max-h-screen w-full overflow-x-hidden overflow-y-hidden bg-white dark:bg-[#0a0a0a] relative transition-colors duration-500">
        <!-- Enhanced Error State Display -->
        <WorkspaceError v-if="store.error" :error="store.error" @retry="retryProjectLoad" />
        
        <!-- Main Layout -->
        <div v-else class="flex-1 flex flex-col h-full min-h-0 overflow-hidden relative">
        </div>
      </div>
    </BuilderLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import useChatMode from '../composables/useChatMode'
import { useProjectStore } from '../stores/projectStore'
import { AgentService } from '../services/agentService'
import { FileService } from '../services/fileService'
import { BuilderCreationService } from '../services/builderCreationService'
import { VersionControlService } from '../services/versionControlService'
import { RouterUpdateService } from '../services/routerUpdateService'
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useBalanceStore } from '@/shared/stores/balance'
import { useNotification } from '@/shared/composables/useNotification'

// Builder Components
import { BuilderLayout } from '@/apps/products/imagi/layouts'
import { AccountBalanceDisplay, PreviewButton } from '../components/molecules'

// Atomic Components
import { 
  WorkspaceError,
} from '../components/organisms/workspace'
import BuilderSidebarChat from '../components/organisms/sidebar/BuilderSidebarChat.vue'
// Set component name
defineOptions({ name: 'Workspace' })

// Types
import type { ProjectFile, BuilderMode } from '../types/components'
import type { AIMessage } from '../types/index'
import { matchesSlug, toSlug } from '../utils/slug'

// Ensure all services use the shared API client with proper timeout configurations
const AI_TIMEOUT = 90000 // 90 seconds for AI processing

const route = useRoute()
const router = useRouter()
const store = useAgentStore()
const projectStore = useProjectStore()
const projectId = ref<string>('')
const {
  createFile,
  loadModels,
} = useBuilderMode()
const {} = useChatMode()

// Constants
const fileTypes = {
  'vue': 'Vue Component',
  'ts': 'TypeScript',
  'js': 'JavaScript',
  'css': 'CSS',
  'html': 'HTML',
  'json': 'JSON',
  'md': 'Markdown'
}

// Version history state and actions
const versionHistory = ref<Array<Record<string, any>>>([])
const selectedVersionHash = ref<string>('')
const isLoadingVersions = ref<boolean>(false)

async function loadVersionHistory() {
  if (!projectId.value) return
  try {
    isLoadingVersions.value = true
    const res = await AgentService.getVersionHistory(projectId.value)
    // Support either versions or commits shapes
    const list = (res && (res as any).versions) || (res as any).commits || []
    versionHistory.value = Array.isArray(list) ? list : []
  } catch (e) {
    console.error('Failed to load version history:', e)
  } finally {
    isLoadingVersions.value = false
  }
}

async function onVersionSelect() {
  try {
    const hash = selectedVersionHash.value
    if (!hash || !projectId.value) return
    const res = await AgentService.resetToVersion(projectId.value, hash)
    if ((res as any)?.success !== false) {
      await handleVersionReset({ hash })
      await loadVersionHistory()
      // Clear selection after reset
      selectedVersionHash.value = ''
    }
  } catch (e) {
    console.error('Failed to reset to selected version:', e)
  }
}

// Local state


// Navigation items for sidebar
const navigationItems: any[] = [] // Empty array to remove sidebar navigation buttons

// Computed properties
const currentProject = computed(() => {
  return projectStore.currentProject || null
})

const promptExamplesComputed = computed(() => {
  return [] // Return empty array for examples
})

// Display name for the Project Web App title
const projectTitle = computed(() => {
  const name = currentProject.value && (currentProject.value as any).name
  return name && String(name).trim() ? String(name) : ''
})

// Sanitized project title for display (remove 'spacex')
const sanitizedProjectTitle = computed(() => {
  const title = projectTitle.value || ''
  const cleaned = title.replace(/spacex/ig, '').trim()
  return cleaned || ''
})

// Sanitized navbar project name and description (remove 'spacex')
const navbarNameSanitized = computed(() => {
  const raw = currentProject.value && (currentProject.value as any).name
    ? String((currentProject.value as any).name)
    : ''
  return raw.trim()
})

const navbarDescSanitized = computed(() => {
  const raw = currentProject.value && (currentProject.value as any).description
    ? String((currentProject.value as any).description)
    : ''
  return raw.trim()
})

// Refresh files and clear any selection on version reset
async function handleVersionReset(version: Record<string, any>) {
  try {
    console.debug('Version reset to:', version)
    await loadProjectFiles(true)
    // Optionally clear selected file to avoid stale content
    if (typeof store.setSelectedFile === 'function') {
      store.setSelectedFile(null)
    }
  } catch (e) {
    console.error('Error handling version reset:', e)
  }
}

// Helper function to get just the filename
function getFileName(path: string): string {
  if (!path) return 'this file'
  const parts = path.split('/')
  return parts[parts.length - 1] ?? 'this file'
}


// Create a git commit after successful code changes
function createCommitFromPrompt(filePath: string, prompt: string) {
  if (!projectId.value || !filePath) return;
  
  // Use the version control service to handle commits in the background
  VersionControlService.commitAfterFileOperation(
    projectId.value,
    filePath,
    prompt
  );
}

async function handlePrompt(promptText: string) {
  if (!promptText.trim()) return
  
  try {
    if (!store.selectedModelId) {
      return
    }
    
    const timestamp = new Date().toISOString()
    
    // Get payments store for updating balance
    const balanceStore = useBalanceStore()
    
    // Mark that a transaction is about to happen to ensure fresh balance data
    balanceStore.beginTransaction()
    
    // Check if we have a project ID
    if (!projectId.value) {
      return
    }
    
    // Set processing flag TRUE at the start
    store.setProcessing(true)
    
    // Add the user message to the conversation immediately
    store.addMessage({
      role: 'user',
      content: promptText,
      timestamp: timestamp,
      id: `user-${Date.now()}`
    })
    
    // Get user auth status before making request
    const isUserAuthenticated = await useAuthStore().validateAuth()
    if (!isUserAuthenticated) {
      return
    }

    if (store.mode === 'agent') {
      // Agent mode: the coding agent decides which files to read/edit via tools
      try {
        const response = await AgentService.processAgent(
          projectId.value,
          {
            prompt: promptText,
            model: store.selectedModelId,
            file: store.selectedFile
          }
        )

        // Add agent's text response as assistant message
        if (response.response) {
          store.addMessage({
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString(),
            id: `assistant-response-${Date.now()}`
          })
        }

        // If files were changed, refresh them in the store and commit
        if (response.files_changed && response.files_changed.length > 0) {
          for (const changedPath of response.files_changed) {
            try {
              const files = await FileService.getProjectFiles(projectId.value)
              store.setFiles(files)
            } catch (refreshError) {
              console.warn('Error refreshing files after agent edit:', refreshError)
            }

            // Create git commits for changed files
            createCommitFromPrompt(changedPath, promptText)
          }
        }
      } catch (agentError) {
        console.error('Error in agent mode:', agentError)
        store.addMessage({
          role: 'assistant',
          content: `Error: ${agentError instanceof Error ? agentError.message : 'Unknown error'}`,
          timestamp: new Date().toISOString(),
          id: `system-error-${Date.now()}`
        })
      }
    } else {
      try {
        // Call the AI service
        const response = await AgentService.processChat(
          projectId.value,
          {
            prompt: promptText,
            model: store.selectedModelId,
            mode: 'chat',
            file: store.selectedFile
          }
        )
        
        // Add the real response message directly (dedupe against last assistant message)
        const normalize = (txt: string | undefined) => (txt || '').trim().replace(/\s+/g, ' ')
        const newContent = normalize(response.response)
        const lastAssistant = [...store.conversation].slice().reverse().find(m => m.role === 'assistant')
        const lastContent = normalize(lastAssistant?.content)
        if (!lastAssistant || newContent !== lastContent) {
          store.addMessage({
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString(),
            id: `assistant-response-${Date.now()}`
            // No code field to prevent displaying code in the UI
          })
        } else {
          console.info('Skipped duplicate assistant message (frontend dedupe)')
        }
      } catch (chatError) {
        throw chatError
      }
    }
    
    // Update balance exactly once after AI operation completes
    try {
      // Get fresh store to avoid stale references
      const balanceStore = useBalanceStore();
      
      // Wait a short delay to ensure backend transaction has completed
      setTimeout(() => {
        balanceStore.fetchBalance(false, true)
          .catch(err => console.warn('Error updating balance after AI operation:', err));
      }, 1000);
    } catch (err) {
      console.warn('Error setting up balance update:', err);
    }
  } catch (error) {
    console.error('Error processing prompt:', error)
  } finally {
    // Ensure processing flag is set to FALSE when everything is complete
    store.setProcessing(false)
  }
}

function handleExamplePrompt(exampleText: string) {
  handlePrompt(exampleText)
}

async function handleModelSelect(modelId: string) {
  store.setSelectedModelId(modelId)
}

async function handleModeSwitch(mode: BuilderMode) {
  const previousMode = store.mode
  if (mode === previousMode) return

  store.setMode(mode)

  if (store.conversation.length > 0) {
    const modeLabel = mode === 'agent' ? 'agent' : 'chat'
    const modeChangeId = `system-mode-change-${Date.now()}`

    store.conversation.push({
      role: 'system',
      content: `Switched to ${modeLabel} mode`,
      timestamp: new Date().toISOString(),
      id: modeChangeId
    })

    await nextTick()
  }
}

async function handleFileSelect(file: ProjectFile) {
  // Ensure selected file is set
  store.selectFile(file)

  // Force UI update to reflect mode/selection changes
  await nextTick()
}

async function handleFileCreate(data: { name: string; type: string; content?: string }) {
  try {
    const created = await createFile({
      projectId: projectId.value,
      ...data
    })

    const createdPath = created?.path || ''
    const requestedPath = data?.name || ''
    const pathForMatch = createdPath || requestedPath
    const appMatch = pathForMatch.match(/src\/apps\/([^/]+)/i)

    // Determine file type for notification message
    const fileName = pathForMatch.split('/').pop() || 'file'
    const isView = data.name.includes('/views/')
    const isComponent = data.name.includes('/components/')
    const fileTypeLabel = isView ? 'View' : isComponent ? 'Component' : 'File'

    // If a view was created under an app, auto-register it in that app's router
    const viewInAppRegex = /(?:^|\/)(?:frontend\/vuejs\/)?src\/apps\/[^/]+\/views\/[^/]+\.vue$/i
    if (pathForMatch && viewInAppRegex.test(pathForMatch)) {
      try {
        await RouterUpdateService.addViewRoute(projectId.value, pathForMatch)
      } catch (e) {
        console.warn('Failed to auto-add route for created view:', pathForMatch, e)
      }
    }
    
    // Force refresh file list after creating a new file to ensure it appears in the explorer
    console.debug('File created, refreshing file list from backend...')
    await loadProjectFiles(true)

    await nextTick()
    
    // Automatically commit the file creation
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      created?.path || data.name,
      `Created ${created?.path || data.name}`
    )
    
    // Show success notification
    const { showNotification } = useNotification()
    showNotification({
      type: 'success',
      message: `${fileTypeLabel} "${fileName}" created successfully`,
      duration: 3000
    })
  } catch (error) {
    console.error('Error creating file:', error)
    
    // Show error notification
    const { showNotification } = useNotification()
    showNotification({
      type: 'error',
      message: `Failed to create file: ${error instanceof Error ? error.message : 'Unknown error'}`,
      duration: 5000
    })
  }
}

async function handleFileDelete(file: ProjectFile) {
  try {
    await FileService.deleteFile(projectId.value, file.path)
    
    // Force refresh file list after deleting a file to ensure it's removed from the explorer
    console.debug('File deleted, refreshing file list from backend...')
    await loadProjectFiles(true)
    
    // If the deleted file was selected, clear selection
    if (store.selectedFile && store.selectedFile.path === file.path) {
      store.setSelectedFile(null)
    }
    
    // Automatically commit the file deletion
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      file.path,
      `Deleted ${file.path}`
    )
  } catch (error) {
    console.error('Error deleting file:', error)
  }
}

// Ensure default apps exist for every new project
async function ensureDefaultApps() {
  try {
    // Call the backend API to ensure default apps exist
    const result = await BuilderCreationService.ensureDefaultApps(projectId.value)

    if (result.success) {
      
      // Reload project files to show any newly created default apps
      await loadProjectFiles(true)
      
      const { showNotification } = useNotification()
      if (result.created_apps && result.created_apps.length > 0) {
        showNotification({
          type: 'success',
          message: `Created ${result.created_apps.length} default app(s): ${result.created_apps.join(', ')}`,
          duration: 3000
        })
      }
    } else {
      console.error('[Workspace] Failed to ensure default apps:', result.error)
      const { showNotification } = useNotification()
      showNotification({
        type: 'warning',
        message: 'Some default apps may not have been created. Check console for details.',
        duration: 4000
      })
    }
  } catch (e) {
    console.error('[Workspace] Error ensuring default apps:', e)
    const { showNotification } = useNotification()
    showNotification({
      type: 'error',
      message: 'Error creating default apps. Please try refreshing.',
      duration: 5000
    })
  }
}

// Retry loading the project when user clicks retry button
async function retryProjectLoad() {
  // Clear any existing error state
  store.setError(null)
  
  try {
    // Retry loading the project
    await projectStore.fetchProject(projectId.value)
    
    // If successful, reload the workspace data
    await loadModels()
    // Force refresh files when retrying to ensure we get the latest state
    await loadProjectFiles(true)
    // Ensure default apps exist after retry load
    await ensureDefaultApps()
    // Refresh version history after retry
    await loadVersionHistory()
    
    // Set default model if needed
    if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
      const defaultModel = store.availableModels.find(m => m.id === 'gpt-5.4') 
        || store.availableModels[0];
      if (defaultModel) {
        store.setSelectedModelId(defaultModel.id);
      }
    }
    
    // Ensure chat-only mode for now
    if (store.mode !== 'chat') {
      store.setMode('chat');
    }
  } catch (error: any) {
    console.error('Error retrying project load:', error)
    store.setError(`Failed to load project: ${error.message || 'Unknown error'}`)
  }
}

// Helper function to load project files
async function loadProjectFiles(force = false) {
  try {
    // Always reload files when force is true, or when files haven't been loaded yet
    if (!force && store.files && store.files.length > 0) {
      console.debug('Using existing files from store, skipping API call')
      return store.files
    }
    
    console.debug('Loading project files from backend API...')
    const files = await FileService.getProjectFiles(projectId.value)
    if (Array.isArray(files)) {
      // Use the setFiles method to avoid type issues with $patch
      if (typeof store.setFiles === 'function') {
        // Cast the files to the expected type if needed
        store.setFiles(files as any)
        console.debug(`Loaded ${files.length} files from backend`)
      } else {
        console.error('setFiles method not available on store')
      }
      return files
    } else {
      console.error('Project files data is not an array:', files)
      return []
    }
  } catch (error) {
    console.error('Error loading project files:', error)
    return []
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Get project name from route params (URL slug)
  const projectNameSlug = String(route.params.projectName)
  
  try {
    // Get stores for easier access
    const paymentsStore = usePaymentStore();
    const authStore = useAuthStore();
    
    // Create a shared request cache to prevent duplicate calls
    const requestCache = new Map<string, Promise<any>>();
    
    // Helper function to deduplicate API calls
    const executeOnce = async (key: string, apiCall: () => Promise<any>) => {
      // Check if this API call is already in progress
      if (requestCache.has(key)) {
        console.debug(`Using existing API call promise for: ${key}`);
        return requestCache.get(key);
      }
      
      // Start a new API call and track it
      const promise = apiCall();
      requestCache.set(key, promise);
      
      try {
        // Execute the API call and return its result
        return await promise;
      } finally {
        // Remove the API call from tracking after completion
        setTimeout(() => {
          requestCache.delete(key);
        }, 100); // Short delay to prevent race conditions
      }
    };
    
    // First, verify authentication only once
    await executeOnce('verifyAuth', () => authStore.validateAuth());
    
    // Load projects list to find the project by slug
    await executeOnce('fetchProjects', () => projectStore.fetchProjects());
    
    // Find the project by slug
    const foundProject = projectStore.getProjectBySlug(projectNameSlug);
    
    if (!foundProject) {
      console.error('Project not found for slug:', projectNameSlug);
      const { showNotification } = useNotification();
      showNotification({
        type: 'error',
        message: `Project "${projectNameSlug}" not found.`,
        duration: 3000
      });
      router.replace({ name: 'projects' });
      return;
    }
    
    // Set the project ID from the found project
    projectId.value = String(foundProject.id);
    
    // IMPORTANT: Check if project is in deleted list BEFORE doing anything else
    // This prevents any API calls or initialization for deleted projects
    try {
      const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
      if (deletedProjects.includes(projectId.value)) {
        // Show notification and redirect immediately
        const { showNotification } = useNotification();
        showNotification({
          type: 'error',
          message: `Project "${foundProject.name}" has been deleted.`,
          duration: 3000
        });
        
        // Immediate redirect without waiting
        router.replace({ name: 'projects' });
        return; // Exit early to prevent any further initialization
      }
    } catch (e) {
      // Handle localStorage errors silently and continue
      console.warn('Error checking deleted projects list:', e)
    }
    
    // Critical request - project must be loaded first and only once
    try {
      const project = await executeOnce('fetchProject', () => {
        // Directly return the API call result, don't wrap in another promise
        return projectStore.fetchProject(projectId.value);
      });
      
      // Set project ID in store only after project data is loaded
      if (project && typeof store.setProjectId === 'function') {
        store.setProjectId(projectId.value);
        
        // Now load models and files in sequence - files depend on project data
        // IMPORTANT: We DON'T use Promise.all here to prevent race conditions
        // between file fetching and the project data
        await executeOnce('loadModels', loadModels);
        // Force fresh file load on initial page load to always get latest files including initial home view
        await executeOnce('loadProjectFiles', () => loadProjectFiles(true));
        // Ensure default apps are present for new/empty projects
        await ensureDefaultApps()
        // Load version history for header dropdown
        await loadVersionHistory()
        
        // Only fetch balance once at startup, with no auto-refresh
        // Make sure it doesn't block the UI
        executeOnce('fetchBalance', () => paymentsStore.fetchBalance(false, false))
          .catch(err => console.error('Error fetching balance:', err));
        
        // Set default model if not already set
        if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
          const defaultModel = store.availableModels.find(m => m.id === 'gpt-5.4') 
            || store.availableModels[0];
          if (defaultModel) {
            store.setSelectedModelId(defaultModel.id);
          }
        }
        
        // Ensure chat-only mode for now
        if (store.mode !== 'chat') {
          store.setMode('chat');
        }
      } else {
        console.error('Failed to load project or set project ID');
        // Don't redirect - let the workspace show an error state
      }
    } catch (projectError: any) {
      console.error('Error loading project:', projectError);
      
      // Handle specific cases for missing projects
      if (projectError.message?.includes('Project not found') || 
          projectError.response?.status === 404) {
        console.log('Project not found - redirecting to dashboard');
        
        // Add project to deleted list if it resulted in 404
        try {
          const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
          if (!deletedProjects.includes(projectId.value)) {
            deletedProjects.push(projectId.value)
            localStorage.setItem('deletedProjects', JSON.stringify(deletedProjects))
            
            const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
            deletedProjectsTimestamp[projectId.value] = Date.now()
            localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
          }
        } catch (e) {
          console.warn('Failed to add project to deleted list:', e)
        }
        
        // Show a notification but redirect to dashboard to prevent further errors
        const { showNotification } = useNotification();
        showNotification({
          type: 'warning',
          message: 'Project not found. This project may have been deleted. Redirecting to dashboard...',
          duration: 4000
        });
        
        // Redirect to dashboard to prevent further 404 errors
        setTimeout(() => {
          router.push({ name: 'projects' });
        }, 1500); // Give user time to read the notification
        
        // Set the workspace to an error state
        store.setError('Project not found. Redirecting to dashboard...');
      } else {
        // For other errors, stay on the page and show an error state
        console.error('Unexpected error during project initialization:', projectError);
        store.setError(`Error loading project: ${projectError.message || 'Unknown error'}`);
        
        // Show notification for other errors
        const { showNotification } = useNotification();
        showNotification({
          type: 'error',
          message: `Failed to load project: ${projectError.message || 'Unknown error'}`,
          duration: 5000
        });
      }
    }
  } catch (error) {
    console.error('Error initializing workspace:', error);
  }
})

// Watch for route parameter changes (e.g., if user navigates to different project)
watch(
  () => route.params.projectName,
  async (newProjectName, oldProjectName) => {
    if (newProjectName && newProjectName !== oldProjectName) {
      console.debug('Workspace: Project name changed in route:', { oldProjectName, newProjectName })
      
      // Find the new project by slug
      const foundProject = projectStore.getProjectBySlug(String(newProjectName));
      
      if (!foundProject) {
        // Try to load projects and search again
        await projectStore.fetchProjects();
        const retryProject = projectStore.getProjectBySlug(String(newProjectName));
        
        if (!retryProject) {
          const { showNotification } = useNotification();
          showNotification({
            type: 'error',
            message: `Project "${newProjectName}" not found.`,
            duration: 3000
          });
          router.replace({ name: 'projects' });
          return;
        }
        
        projectId.value = String(retryProject.id);
        return;
      }
      
      const newProjectId = String(foundProject.id);
      
      // Check if the new project is in the deleted list
      try {
        const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
        if (deletedProjects.includes(newProjectId)) {
          // Show notification and redirect immediately
          const { showNotification } = useNotification();
          showNotification({
            type: 'error',
            message: `Project "${foundProject.name}" has been deleted.`,
            duration: 3000
          });
          
          // Immediate redirect without waiting
          router.replace({ name: 'projects' });
          return;
        }
      } catch (e) {
        console.warn('Error checking deleted projects list during route change:', e)
      }
      
      // If not deleted, update the project ID and reload
      projectId.value = newProjectId
      // Could add logic here to reload the project if needed
    }
  },
  { immediate: false } // Don't run immediately since onMounted handles the initial load
)

onBeforeUnmount(() => {
  // Clean up resources
  store.clearConversation()
  store.setSelectedFile(null)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Refined minimal scrollbar - Matching Homepage */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}

/* Safe area padding for mobile */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>