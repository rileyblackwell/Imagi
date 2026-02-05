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
          :selected-app="selectedApp"
          :on-prompt-submit="handlePrompt"
          :on-model-select="handleModelSelect"
          :on-mode-switch="handleModeSwitch"
          :on-example-prompt="handleExamplePrompt"
          :is-collapsed="collapsed"
        />
      </template>
      
      <!-- Account balance display in navbar right -->
      <template #navbar-right>
        <AccountBalanceDisplay />
      </template>

      <!-- Clean Main Content Area - Matching Homepage -->
      <div class="flex flex-col h-screen max-h-screen w-full overflow-x-hidden overflow-y-hidden bg-white dark:bg-[#0a0a0a] relative transition-colors duration-500">
        <!-- Enhanced Error State Display -->
        <WorkspaceError v-if="store.error" :error="store.error" @retry="retryProjectLoad" />
        
        <!-- Main Layout: Navigation -->
        <div v-else class="flex-1 flex flex-col h-full min-h-0 overflow-hidden relative">
          <!-- Navigation Area (scrollable) -->
          <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
            <!-- Navigation Views -->
            <div class="flex-1 min-h-0 overflow-hidden">
              <!-- Split Screen Layout: Apps List + Detail View -->
              <div class="h-full p-4 sm:p-6 lg:p-8 flex gap-4">
                <!-- Left Side: Apps List (1/3 width) -->
                <div class="w-1/3 flex flex-col min-h-0">
                  <div class="relative flex-1 min-h-0">
                    <div class="relative h-full rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] shadow-sm overflow-hidden flex flex-col transition-all duration-300">
                      <AppsList
                        :files="store.files || []"
                        :preview-loading="isPreviewLoading"
                        @select-app="handleSelectApp"
                        @create-app="handleCreateAppFromGallery"
                        @preview-app="handlePreview"
                        class="flex-1 min-h-0"
                      />
                    </div>
                  </div>
                </div>

                <!-- Right Side: App Detail View (2/3 width) -->
                <div class="w-2/3 flex flex-col min-h-0">
                  <div class="relative flex-1 min-h-0">
                    <div class="relative h-full rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] shadow-sm overflow-hidden flex flex-col transition-all duration-300">
                      <!-- App Detail View (when app selected) -->
                      <AppDetailView
                        v-if="selectedApp"
                        :app="selectedApp"
                        @back="handleBackToList"
                        @select-file="handleFileSelectFromDetail"
                        @create-file="handleFileCreate"
                        @category-change="handleCategoryChange"
                        class="flex-1 min-h-0"
                      />
                      
                      <!-- Empty State (when no app selected) -->
                      <div v-else class="flex-1 flex items-center justify-center p-8">
                        <div class="text-center max-w-md">
                          <div class="inline-flex items-center justify-center w-20 h-20 rounded-xl bg-gray-100 dark:bg-white/[0.05] border border-gray-200 dark:border-white/[0.08] mb-6">
                            <i class="fas fa-arrow-left text-gray-700 dark:text-white/70 text-3xl"></i>
                          </div>
                          <h3 class="text-2xl font-semibold text-gray-900 dark:text-white/90 mb-3">Select an App</h3>
                          <p class="text-gray-600 dark:text-white/60 leading-relaxed">
                            Choose an app from the left to view its pages, blocks, and other files. You can then edit them or create new ones.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </BuilderLayout>
    <!-- New App Modal -->
    <NewAppModal
      v-model="showNewAppModal"
      :submitting="isCreatingApp"
      @submit="handleCreateAppSubmit"
    />
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
import { PreviewService } from '../services/previewService'
import { BuilderCreationService } from '../services/builderCreationService'
import { VersionControlService } from '../services/versionControlService'
import { RouterUpdateService } from '../services/routerUpdateService'
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useBalanceStore } from '@/shared/stores/balance'
import { useNotification } from '@/shared/composables/useNotification'

// Builder Components
import { BuilderLayout } from '@/apps/products/imagi/layouts'
import { AccountBalanceDisplay } from '../components/molecules'

// Atomic Components
import { 
  WorkspaceError,
} from '../components/organisms/workspace'
import AppsList from '../components/organisms/workspace/AppsList.vue'
import AppDetailView from '../components/organisms/workspace/AppDetailView.vue'
import NewAppModal from '../components/organisms/workspace/NewAppModal.vue'
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
  applyCode 
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

// Simple creation flows for non-technical users via AppGallery
// New App modal state
const showNewAppModal = ref(false)
const isCreatingApp = ref(false)

// Preview loading state to prevent multiple tabs
const isPreviewLoading = ref(false)

// Open the styled New App modal
async function handleCreateAppFromGallery() {
  showNewAppModal.value = true
}

// Submit handler for New App modal
async function handleCreateAppSubmit(payload: { name: string; description: string }) {
  try {
    if (!projectId.value) return
    isCreatingApp.value = true

    const result = await BuilderCreationService.createAppFromGallery(
      projectId.value,
      payload.name,
      payload.description || ''
    )

    if (result.success) {
      // Close modal and refresh files to show the new app
      showNewAppModal.value = false
      await loadProjectFiles(true)
      const { showNotification } = useNotification()
      showNotification({
        type: 'success',
        message: result.message || 'App created successfully',
        duration: 3000
      })
    } else {
      console.error('Failed to create app:', result.error)
      const { showNotification } = useNotification()
      showNotification({
        type: 'error',
        message: result.error || 'Failed to create app',
        duration: 5000
      })
    }
  } catch (e) {
    console.error('Error creating app from gallery:', e)
    const { showNotification } = useNotification()
    showNotification({
      type: 'error',
      message: 'Unexpected error creating app',
      duration: 5000
    })
  } finally {
    isCreatingApp.value = false
  }
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
const showAppsInMain = ref(true)
const selectedApp = ref<any>(null)
const selectedCategory = ref<{ key: string; label: string } | null>(null)


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
  return parts[parts.length - 1]
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
    
    // For build mode, file selection is required
    if (store.mode === 'build' && !store.selectedFile) {
      return
    }
    
    // Get user auth status before making request
    const isUserAuthenticated = await useAuthStore().validateAuth()
    if (!isUserAuthenticated) {
      return
    }
    
    if (store.mode === 'build') {
      // Check for missing required values
      if (!projectId.value) {
        return
      }
      
      if (!store.selectedFile) {
        return
      }
      
      // Determine file type for specialized handling
      const fileExtension = store.selectedFile.path.split('.').pop()?.toLowerCase() || ''
      const isCSS = fileExtension === 'css' || store.selectedFile.type === 'css'
      const isHTML = fileExtension === 'html' || store.selectedFile.type === 'html'
      
      if (isCSS) {
        try {
          // For CSS files, use specialized stylesheet generator function
          const response = await AgentService.generateStylesheet({
            prompt: promptText,
            projectId: projectId.value,
            filePath: store.selectedFile.path,
            model: store.selectedModelId,
            onProgress: (progress) => {
              // Update UI with progress - no notification needed
            }
          });
          
          // Ensure we got a valid response
          if (response && (response.response || response.code)) {
            // Get the content from either response or code field
            const cssContent = response.response || response.code || '';
            
            if (!cssContent.trim()) {
              store.addMessage({
                role: 'assistant',
                content: 'No stylesheet changes were generated. Please try a different prompt.',
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              });
              return;
            }
            
            // Apply the generated code
            try {
              await applyCode({
                code: cssContent,
                file: store.selectedFile,
                projectId: projectId.value
              });
              
              const simpleSummary = `Changes successfully applied to ${store.selectedFile.path}`;
              
              // Add assistant message to conversation
              store.addMessage({
                role: 'assistant',
                content: simpleSummary,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              });
              
              // Create a git commit for the CSS changes
              createCommitFromPrompt(store.selectedFile.path, promptText);
            } catch (applyError) {
              console.error('Error applying stylesheet changes:', applyError);
              store.addMessage({
                role: 'assistant',
                content: `Failed to apply stylesheet changes to ${store.selectedFile.path}: ${applyError instanceof Error ? applyError.message : 'Unknown error'}`,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              });
            }
          } else {
            store.addMessage({
              role: 'assistant',
              content: 'No stylesheet changes were generated. Please try a different prompt.',
              timestamp: new Date().toISOString(),
              id: `assistant-response-${Date.now()}`
            });
          }
        } catch (cssError) {
          console.error('Error generating stylesheet:', cssError);
          
          store.addMessage({
            role: 'assistant',
            content: `Error generating stylesheet: ${cssError instanceof Error ? cssError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          });
        }
      } else if (isHTML) {
        try {
          // Ensure the file path is correctly formatted for HTML files
          let formattedPath = store.selectedFile.path;
          if (!formattedPath.includes('/templates/') && !formattedPath.startsWith('templates/')) {
            formattedPath = `templates/${formattedPath.replace(/^\//, '')}`;
          }
          
          // Call the AI service to generate code - will use template endpoint in agentService
          const response = await AgentService.generateCode(
            projectId.value,
            {
              prompt: promptText,
              model: store.selectedModelId,
              mode: 'build',
              file_path: formattedPath
            }
          )
          
          // Apply the generated code automatically if available
          if (response && response.code) {
            try {
              await applyCode({
                code: response.code,
                file: store.selectedFile,
                projectId: projectId.value
              })
              
              const simpleSummary = `Changes successfully applied to ${store.selectedFile.path}`;
              
              store.addMessage({
                role: 'assistant',
                content: simpleSummary,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
              
              // Create a git commit for the HTML changes
              createCommitFromPrompt(store.selectedFile.path, promptText);
            } catch (applyError) {
              console.error('Error applying HTML template:', applyError)
              
              store.addMessage({
                role: 'assistant',
                content: `Failed to apply changes to ${store.selectedFile.path}: ${applyError instanceof Error ? applyError.message : 'Unknown error'}`,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
            }
          } else {
            store.addMessage({
              role: 'assistant',
              content: 'No HTML template was generated. Please try a different prompt.',
              timestamp: new Date().toISOString(),
              id: `assistant-response-${Date.now()}`
            })
          }
        } catch (htmlError) {
          console.error('Error generating HTML template:', htmlError)
          
          store.addMessage({
            role: 'assistant',
            content: `Error generating HTML template: ${htmlError instanceof Error ? htmlError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
        }
      } else {
        try {
          // Call the AI service to generate code
          const response = await AgentService.generateCode(
            projectId.value,
            {
              prompt: promptText,
              model: store.selectedModelId,
              mode: 'build',
              file_path: store.selectedFile.path
            }
          )
          
          // Apply the generated code automatically
          if (response && response.code) {
            try {
              // Apply the generated code automatically
              await applyCode({
                code: response.code,
                file: store.selectedFile,
                projectId: projectId.value
              })
              
              // Add only a single success message instead of two
              const simpleSummary = `Changes successfully applied to ${store.selectedFile.path}`;
              
              store.addMessage({
                role: 'assistant',
                content: simpleSummary,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
              
              // Create a git commit for the applied changes
              createCommitFromPrompt(store.selectedFile.path, promptText);
            } catch (applyError) {
              console.error('Error applying generated code:', applyError)
              
              // Just add a single error message
              store.addMessage({
                role: 'assistant',
                content: `Failed to apply changes to ${store.selectedFile.path}: ${applyError instanceof Error ? applyError.message : 'Unknown error'}`,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
            }
          } else {
            // No code was generated, just show the response
            store.addMessage({
              role: 'assistant',
              content: 'No code changes were generated. Please try a different prompt.',
              timestamp: new Date().toISOString(),
              id: `assistant-response-${Date.now()}`
            })
          }
        } catch (buildError) {
          console.error('Error in build mode:', buildError)
          
          // Add error message to conversation
          store.addMessage({
            role: 'assistant',
            content: `Error generating code: ${buildError instanceof Error ? buildError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
        }
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
  if (mode !== 'chat') {
    store.setMode('chat')
    return
  }
  
  // Update the mode in the store
  if (previousMode === 'chat') {
    return
  }
  store.setMode('chat')
  
  // Only add system messages about mode changes if the new mode is chat mode
  // This prevents system messages from appearing in build mode
  if (store.conversation.length > 0) {
    // Add system message about mode change
    // Use a special ID format that can be detected in the ChatConversation component
    const modeChangeId = `system-mode-change-${Date.now()}`;
    
    store.conversation.push({
      role: 'system',
      content: `Switched to chat mode${store.selectedFile ? ` for file: ${store.selectedFile.path}` : ''}`,
      timestamp: new Date().toISOString(),
      id: modeChangeId
    })
    
    // Brief delay to allow UI to settle after mode change
    await nextTick();
  }
}

function handleSelectApp(app: any) {
  selectedApp.value = app
}

function handleBackToList() {
  selectedApp.value = null
  selectedCategory.value = null
  store.setSelectedFile(null)
}

function handleCategoryChange(category: { key: string; label: string } | null) {
  selectedCategory.value = category
}

function handleBackToApps() {
  selectedApp.value = null
  selectedCategory.value = null
  store.setSelectedFile(null)
}

function handleBackToApp() {
  selectedCategory.value = null
  store.setSelectedFile(null)
}

function handleBackToCategory() {
  store.setSelectedFile(null)
}

function handleBackFromChat() {
  store.setSelectedFile(null)
}

async function handleFileSelectFromDetail(file: ProjectFile) {
  // Set the selected file in store (for context in chat input)
  store.selectFile(file)
  
  // Force UI update
  await nextTick()
}

async function handleFileSelect(file: ProjectFile) {
  // Ensure selected file is set
  store.selectFile(file)
  showAppsInMain.value = false

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
    const viewInAppRegex = /(?:^|\/)(?:frontend\/vuejs\/)?src\/apps\/[^\/]+\/views\/[^\/]+\.vue$/i
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

    // Stay in detail view if an app is selected
    if (appMatch?.[1] && !selectedApp.value) {
      // Find the app and show detail view
      const appFiles = store.files?.filter((f: any) => 
        (f.path || '').toLowerCase().includes(`/src/apps/${appMatch[1]}/`)
      ) || []
      if (appFiles.length > 0) {
        // Build app object
        const appKey = appMatch[1]
        const appName = appKey.charAt(0).toUpperCase() + appKey.slice(1)
        selectedApp.value = {
          key: appKey,
          name: appKey,
          displayName: appName,
          files: appFiles,
          icon: 'fas fa-cube',
          color: { bg: 'bg-violet-600/15', border: 'border-violet-400/30', text: 'text-violet-300' },
          hint: 'App files'
        }
      }
    }
    
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

async function handlePreview() {
  // CRITICAL: Set loading state IMMEDIATELY to prevent duplicate tabs
  // This must be the very first check, before any other code runs
  if (isPreviewLoading.value) {
    console.debug('Preview already loading, ignoring duplicate request')
    return
  }
  
  // Set the flag synchronously BEFORE any async operations
  isPreviewLoading.value = true
  
  const { showNotification } = useNotification()
  
  try {
    if (!projectId.value) {
      showNotification({
        type: 'error',
        message: 'No project selected for preview',
        duration: 3000
      })
      return
    }

    const response = await PreviewService.generatePreview(projectId.value)
    
    if (response && response.previewUrl) {
      // Open the preview URL in a new tab
      window.open(response.previewUrl, '_blank')
      showNotification({
        type: 'success',
        message: 'Preview opened in new tab',
        duration: 3000
      })
    } else {
      showNotification({
        type: 'error',
        message: 'Failed to start preview server',
        duration: 4000
      })
    }
  } catch (error) {
    console.error('Error starting preview server:', error)
    showNotification({
      type: 'error',
      message: `Preview failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      duration: 5000
    })
  } finally {
    // Reset loading state after a short delay to prevent rapid re-clicks
    setTimeout(() => {
      isPreviewLoading.value = false
    }, 1000)
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
      const defaultModel = store.availableModels.find(m => m.id === 'gpt-5.2') 
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
          const defaultModel = store.availableModels.find(m => m.id === 'gpt-5.2') 
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