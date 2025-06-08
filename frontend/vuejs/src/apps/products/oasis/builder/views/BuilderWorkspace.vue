<!--
  BuilderWorkspace.vue - Project Editing Interface
  
  This component is responsible for:
  1. Loading an existing project's files and data
  2. Supporting chat & build modes for AI interaction
  3. Editing project files through AI assistance
-->
<template>
  <div>
    <!-- Fixed position account balance display -->
    <AccountBalanceDisplay />
    
    <BuilderLayout 
      storage-key="builderWorkspaceSidebarCollapsed"
      :navigation-items="navigationItems"
    >
      <!-- Sidebar Content -->
      <template #sidebar-content="{ collapsed }">
        <BuilderSidebar
          :current-project="currentProject"
          :models="store.availableModels || []"
          :model-id="store.selectedModelId || null"
          :selected-file="store.selectedFile || null"
          :files="store.files || []"
          :file-types="fileTypes"
          :is-loading="store.isProcessing || false"
          :mode="store.mode || 'chat'"
          :current-editor-mode="currentEditorMode"
          :is-collapsed="collapsed"
          :project-id="projectId || ''"
          @update:model-id="handleModelSelect"
          @update:mode="handleModeSwitch"
          @select-file="handleFileSelect"
          @create-file="handleFileCreate"
          @delete-file="handleFileDelete"
          @preview="handlePreview"
        />
      </template>

      <!-- Main Content Area -->
      <div class="flex flex-col h-screen max-h-screen w-full overflow-hidden bg-dark-950 relative">
        <!-- Error State Display -->
        <div v-if="store.error" class="flex-1 flex flex-col h-full overflow-hidden">
          <div class="flex flex-col items-center justify-center h-full p-8 text-center">
            <div class="w-20 h-20 bg-gradient-to-br from-red-500/15 to-orange-500/15 rounded-full flex items-center justify-center mb-6 border border-red-500/20 shadow-lg shadow-red-500/10">
              <i class="fas fa-exclamation-triangle text-3xl text-red-400"></i>
            </div>
            <h2 class="text-2xl font-semibold text-white mb-4">Workspace Error</h2>
            <p class="text-gray-300 mb-8 max-w-md">{{ store.error }}</p>
            <div class="flex gap-4">
              <router-link
                to="/products/oasis/builder/dashboard"
                class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:-translate-y-1 transition-all duration-300 inline-flex items-center"
              >
                <i class="fas fa-arrow-left mr-2"></i>
                Go to Dashboard
              </router-link>
              <button
                @click="retryProjectLoad"
                class="px-6 py-3 bg-dark-800/60 hover:bg-dark-700/60 border border-dark-800/60 hover:border-indigo-500/30 text-gray-300 hover:text-white rounded-xl shadow-md hover:shadow-lg shadow-dark-900/10 hover:shadow-indigo-500/20 transition-all duration-300 inline-flex items-center"
              >
                <i class="fas fa-sync-alt mr-2"></i>
                Retry
              </button>
            </div>
          </div>
        </div>
        
        <!-- Normal Chat UI when no error -->
        <div v-else class="flex-1 flex flex-col h-full overflow-hidden">
          <WorkspaceChat
            :messages="ensureValidMessages(store.conversation || [])"
            :is-processing="store.isProcessing"
            :mode="store.mode || 'chat'"
            :selected-file="store.selectedFile"
            :selected-model-id="store.selectedModelId"
            :available-models="store.availableModels || []"
            :prompt-placeholder="promptPlaceholder"
            :show-examples="false"
            :prompt-examples="promptExamplesComputed"
            v-model="prompt"
            @submit="handlePrompt"
            @use-example="handleExamplePrompt"
            style="height: 100%; overflow: hidden; display: flex; flex-direction: column;"
          />
        </div>
      </div>
    </BuilderLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import useChatMode from '../composables/useChatMode'
import { useProjectStore } from '../stores/projectStore'
import { AgentService } from '../services/agentService'
import { FileService } from '../services/fileService'
import { PreviewService } from '../services/previewService'
import { VersionControlService } from '../services/versionControlService'
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useBalanceStore } from '@/shared/stores/balance'
import { useNotification } from '@/shared/composables/useNotification'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import BuilderSidebar from '../components/organisms/sidebar/BuilderSidebar.vue'
import { AccountBalanceDisplay } from '../components/molecules'

// Atomic Components
import { WorkspaceChat } from '../components/organisms/workspace'

// Types
import type { ProjectFile, EditorMode, BuilderMode } from '../types/components'
import type { AIMessage } from '../types/index'

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

// Local state
const currentEditorMode = ref<EditorMode>('split')
const prompt = ref('')

// Navigation items for sidebar
const navigationItems: any[] = [] // Empty array to remove sidebar navigation buttons

// Computed properties
const currentProject = computed(() => {
  return projectStore.currentProject || null
})

const promptExamplesComputed = computed(() => {
  return [] // Return empty array for examples
})

const promptPlaceholder = computed(() => 
  store.mode === 'chat'
    ? 'Ask a question about your project...'
    : store.selectedFile
      ? 'Describe the changes you want to make to this file...'
      : 'Select a file to start making changes...'
)

// Methods
function ensureValidMessages(messages: any[]): AIMessage[] {
  if (!messages || !Array.isArray(messages)) {
    return []
  }
  
  // Filter out system messages related to file switching in all modes
  const filteredMessages = messages.filter(m => {
    // Remove all system messages related to file switching
    if (m && m.role === 'system') {
      // Filter out messages about file switching, mode switching or file availability
      if (m.content && (
        m.content.includes('Switched to file:') || 
        m.content.includes('Switched to build mode') ||
        m.content.includes('previously selected file')
      )) {
        return false;
      }
    }
    return true;
  });
  
  const validMessages = filteredMessages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => {
      // Ensure content is a valid string
      let content = m.content || '';
      
      // Generate a new id if not present to force proper rendering
      const messageId = m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      
      return {
        role: m.role,
        content: content,
        code: m.code || '',
        timestamp: m.timestamp || new Date().toISOString(),
        id: messageId
      };
    }) as AIMessage[];
  
  return validMessages
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

async function handlePrompt(eventData?: { timestamp: string }) {
  if (!prompt.value.trim()) return
  
  try {
    if (!store.selectedModelId) {
      return
    }
    
    const timestamp = eventData?.timestamp || new Date().toISOString()
    
    // Get payments store for updating balance
    const paymentsStore = usePaymentStore()
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
      content: prompt.value,
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
            prompt: prompt.value,
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
              createCommitFromPrompt(store.selectedFile.path, prompt.value);
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
              prompt: prompt.value,
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
              createCommitFromPrompt(store.selectedFile.path, prompt.value);
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
              prompt: prompt.value,
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
              createCommitFromPrompt(store.selectedFile.path, prompt.value);
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
            prompt: prompt.value,
            model: store.selectedModelId,
            mode: 'chat',
            file: store.selectedFile
          }
        )
        
        // Add the real response message directly, but without showing code in the UI
        store.addMessage({
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString(),
          id: `assistant-response-${Date.now()}`
          // No code field to prevent displaying code in the UI
        })
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
    
    // Clear prompt after sending
    prompt.value = ''
  } catch (error) {
    console.error('Error processing prompt:', error)
  } finally {
    // Ensure processing flag is set to FALSE when everything is complete
    store.setProcessing(false)
  }
}

function handleExamplePrompt(exampleText: string) {
  prompt.value = exampleText
  handlePrompt()
}

async function handleModelSelect(modelId: string) {
  store.setSelectedModelId(modelId)
}

async function handleModeSwitch(mode: BuilderMode) {
  const previousMode = store.mode
  
  // Update the mode in the store
  store.setMode(mode)
  
  // If switching from chat to build and no file is selected
  if (previousMode === 'chat' && mode === 'build' && !store.selectedFile && store.files.length > 0) {
    // Auto-select the first file when switching to build mode
    store.selectFile(store.files[0])
  }
  
  // Only add system messages about mode changes if the new mode is chat mode
  // This prevents system messages from appearing in build mode
  if (mode === 'chat' && previousMode !== mode && store.conversation.length > 0) {
    // Add system message about mode change
    // Use a special ID format that can be detected in the ChatConversation component
    const modeChangeId = `system-mode-change-${Date.now()}`;
    
    store.conversation.push({
      role: 'system',
      content: `Switched to ${mode} mode${store.selectedFile ? ` for file: ${store.selectedFile.path}` : ''}`,
      timestamp: new Date().toISOString(),
      id: modeChangeId
    })
    
    // Brief delay to allow UI to settle after mode change
    await nextTick();
  }
}

async function handleFileSelect(file: ProjectFile) {
  if (store.selectedFile?.path !== file.path) {
    // Remove system messages about file changes completely
    // No longer add file switch notifications to the conversation
    
    // Determine file type before selecting the file
    const fileExtension = file.path.split('.').pop()?.toLowerCase() || '';
    const isCSS = fileExtension === 'css' || file.type === 'css';
    const isHTML = fileExtension === 'html' || file.type === 'html';
    
    // Use the improved selectFile method to maintain chat context
    store.selectFile(file)
    
    // Update the mode indicator UI by forcing a re-render
    // This is needed because the selectedFile reference might not change
    // if the file content is the same, but we still want the UI to update
    await nextTick()
  }
}

async function handleFileCreate(data: { name: string; type: string; content?: string }) {
  try {
    await createFile({
      projectId: projectId.value,
      ...data
    })
    
    // Refresh file list after creating a new file
    await loadProjectFiles()
    
    // Automatically commit the file creation
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      data.name,
      `Created ${data.name}`
    )
  } catch (error) {
    console.error('Error creating file:', error)
  }
}

async function handleFileDelete(file: ProjectFile) {
  try {
    await FileService.deleteFile(projectId.value, file.path)
    
    // Remove file from store
    store.removeFile(file)
    
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
  try {
    if (!projectId.value) {
      return
    }

    const response = await PreviewService.generatePreview(projectId.value)
    
    if (response && response.previewUrl) {
      // Open the preview URL in a new tab
      window.open(response.previewUrl, '_blank')
    } else {
      // Show notification about preview failure
    }
  } catch (error) {
    console.error('Error starting preview server:', error)
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
    await loadProjectFiles()
    
    // Set default model if needed
    if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
      const defaultModel = store.availableModels.find(m => m.id === 'claude-3-7-sonnet-20250219') 
        || store.availableModels[0];
      if (defaultModel) {
        store.setSelectedModelId(defaultModel.id);
      }
    }
    
    // Initialize mode if not set
    if (!store.mode) {
      store.setMode('chat');
    }
  } catch (error: any) {
    console.error('Error retrying project load:', error)
    store.setError(`Failed to load project: ${error.message || 'Unknown error'}`)
  }
}

// Helper function to load project files
async function loadProjectFiles() {
  try {
    // Avoid duplicate calls by checking if project files are already loaded
    if (store.files && store.files.length > 0) {
      console.debug('Using existing files from store, skipping API call')
      return store.files
    }
    
    const files = await FileService.getProjectFiles(projectId.value)
    if (Array.isArray(files)) {
      // Use the setFiles method to avoid type issues with $patch
      if (typeof store.setFiles === 'function') {
        // Cast the files to the expected type if needed
        store.setFiles(files as any)
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
  // Get project ID from route params
  projectId.value = String(route.params.projectId)
  
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
        await executeOnce('loadProjectFiles', loadProjectFiles);
        
        // Only fetch balance once at startup, with no auto-refresh
        // Make sure it doesn't block the UI
        executeOnce('fetchBalance', () => paymentsStore.fetchBalance(false, false))
          .catch(err => console.error('Error fetching balance:', err));
        
        // Set default model if not already set
        if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
          const defaultModel = store.availableModels.find(m => m.id === 'claude-3-7-sonnet-20250219') 
            || store.availableModels[0];
          if (defaultModel) {
            store.setSelectedModelId(defaultModel.id);
          }
        }
        
        // Initialize mode if not set
        if (!store.mode) {
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
        
        // Show a notification but redirect to dashboard to prevent further errors
        const { showNotification } = useNotification();
        showNotification({
          type: 'warning',
          message: 'Project not found. This project may have been deleted. Redirecting to dashboard...',
          duration: 4000
        });
        
        // Redirect to dashboard to prevent further 404 errors
        setTimeout(() => {
          router.push({ name: 'builder-dashboard' });
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

/* Background grid pattern */
.bg-grid-pattern {
  background-image: linear-gradient(to right, theme('colors.dark.800') 1px, transparent 1px),
                    linear-gradient(to bottom, theme('colors.dark.800') 1px, transparent 1px);
  background-size: 20px 20px;
}

/* Animation for floating orbs */
@keyframes float-slow {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
}

@keyframes float-slow-reverse {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(20px) translateX(-10px); }
}

.animate-float-slow {
  animation: float-slow 20s ease-in-out infinite;
}

.animate-float-slow-reverse {
  animation: float-slow-reverse 25s ease-in-out infinite;
}
</style>

<script lang="ts">
export default {
  name: 'BuilderWorkspace'
}
</script>