<template>
  <ErrorBoundary>
    <BuilderLayout 
      storage-key="builderWorkspaceSidebarCollapsed"
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
          @update:model-id="handleModelSelect"
          @update:mode="handleModeSwitch"
          @select-file="handleFileSelect"
          @create-file="handleFileCreate"
          @undo="handleUndo"
          @preview="handlePreview"
        />
      </template>

      <template #default="{ collapsed }">
        <!-- Main Content -->
        <div class="relative h-full bg-dark-950">
          <!-- Loading Overlay -->
          <LoadingOverlay 
            v-if="store.isProcessing"
            :message="loadingMessage"
            transparent
          />

          <div class="h-[calc(100vh-4rem)] flex flex-col">
            <!-- Main Content Area -->
            <Transition
              mode="out-in"
              enter-active-class="transition-opacity duration-300"
              enter-from-class="opacity-0"
              enter-to-class="opacity-100"
              leave-active-class="transition-opacity duration-300"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
            >
              <div v-if="store.mode === 'chat'" class="flex-1 overflow-auto">
                <ChatConversation 
                  :messages="store.conversation || []" 
                  @use-example="handleExamplePrompt"
                />
              </div>
              <div v-else class="flex-1 flex flex-col overflow-hidden">
                <!-- Show chat feed at the top in build mode -->
                <div class="flex-1 overflow-auto">
                  <ChatConversation 
                    :messages="store.conversation || []" 
                    @use-example="handleExamplePrompt"
                  />
                </div>
                
                <!-- Show editor below chat feed when a file is selected -->
                <div v-if="store.selectedFile" class="h-1/2 border-t border-dark-800">
                  <BuilderEditor
                    v-model="editorContent"
                    :file="store.selectedFile"
                    :editor-mode="currentEditorMode"
                    @change="handleEditorChange"
                    @save="handleSave"
                  />
                </div>
              </div>
            </Transition>

            <!-- AI Input Area -->
            <div 
              class="shrink-0 p-4 border-t border-dark-800 bg-dark-900/50 backdrop-blur-sm"
              :class="{'opacity-50 pointer-events-none': store.isProcessing}"
            >
              <AIPromptInput
                v-model="prompt"
                :loading="store.isProcessing"
                :mode="store.mode || 'chat'"
                :placeholder="promptPlaceholder"
                @submit="handlePrompt"
              />
              
              <!-- Error Message -->
              <TransitionGroup
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 transform -translate-y-2"
                enter-to-class="opacity-100 transform translate-y-0"
                leave-active-class="transition-all duration-300 ease-in"
                leave-from-class="opacity-100 transform translate-y-0"
                leave-to-class="opacity-0 transform -translate-y-2"
              >
                <div 
                  v-if="store.error"
                  class="mt-2 px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm"
                >
                  {{ store.error }}
                </div>
              </TransitionGroup>
            </div>
          </div>

          <!-- Add keyboard shortcuts -->
          <AppShortcuts
            :shortcuts="[
              { key: 'mod+s', handler: handleSave, description: 'Save changes' },
              { key: 'mod+enter', handler: handlePrompt, description: 'Submit prompt' },
              { key: 'esc', handler: () => store.setError(null), description: 'Clear error' }
            ]"
          />

          <!-- Add session timeout warning -->
          <SessionTimeoutWarning 
            v-if="sessionTimeoutWarning"
            @refresh="refreshSession"
          />
        </div>
      </template>
    </BuilderLayout>
  </ErrorBoundary>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useBuilderStore } from '../stores/builderStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import { useChatMode } from '../composables/useChatMode'
import { useFileManager } from '../composables/useFileManager'
import { useProjectStore } from '../stores/projectStore'
import { AI_MODELS } from '../types/builder'
import { ModelService } from '../services/modelService'

// Shared Components
import ErrorBoundary from '../components/atoms/ErrorBoundary.vue'
import AppShortcuts from '@/shared/components/molecules/feedback/AppShortcuts.vue'
import { SessionTimeoutWarning } from '@/apps/auth/components/molecules'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import LoadingOverlay from '../components/atoms/LoadingOverlay.vue'
import BuilderSidebar from '../components/organisms/sidebar/BuilderSidebar.vue'
import BuilderEditor from '../components/organisms/editor/BuilderEditor.vue'
import AIPromptInput from '../components/molecules/inputs/AIPromptInput.vue'
import ChatConversation from '../components/organisms/chat/ChatConversation.vue'

// Utils
import { notify } from '@/shared/utils'
import type { ProjectFile, EditorMode } from '../types/builder'

const route = useRoute()
const store = useBuilderStore()
const projectStore = useProjectStore()
const { 
  generateCodeFromPrompt, 
  createFile, 
  undoLastAction,
  loadModels
} = useBuilderMode()
const { sendMessage } = useChatMode()
const { autosaveContent, saveFile, checkUnsavedChanges } = useFileManager()

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
const editorContent = ref('')
const sidebarCollapsed = ref(false)
const sessionTimeoutWarning = ref(false)
const sessionCheckInterval = ref<number>()
const sessionCheckEnabled = ref(true)
const sessionCheckFailCount = ref(0)
const MAX_SESSION_CHECK_FAILS = 3

// Computed properties
const currentProject = computed(() => {
  // Ensure we always return a valid value (object or null, never undefined)
  return projectStore.currentProject || null
})

const loadingMessage = computed(() => {
  if (store.mode === 'chat') {
    return 'Processing your message...'
  }
  return store.selectedFile 
    ? 'Generating code changes...'
    : 'Processing your request...'
})

const promptPlaceholder = computed(() => 
  store.mode === 'chat'
    ? 'Ask a question about your project...'
    : store.selectedFile
      ? 'Describe the changes you want to make...'
      : 'Select a file to start making changes...'
)

// Event handlers
const handleModelSelect = (modelId: string) => {
  // Verify the model exists in available models or default models
  const modelExists = store.availableModels.some(model => model.id === modelId) || 
                     AI_MODELS.some(model => model.id === modelId)
  
  if (modelId && modelExists) {
    try {
      // Try to use the store action if available
      if (typeof store.selectModel === 'function') {
        store.selectModel(modelId)
      } else {
        // Fallback: directly update the store state if the action is not available
        store.$patch({ selectedModelId: modelId })
      }
      
      // Force a store update to ensure reactivity
      store.$patch({})
      
      // Optionally notify the user about the model change
      const modelName = store.availableModels.find(m => m.id === modelId)?.name || 
                        AI_MODELS.find(m => m.id === modelId)?.name || 
                        modelId
      notify({ 
        type: 'info', 
        message: `Switched to ${modelName}` 
      })
      
      // Force a UI update by triggering a window resize event
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'))
      }, 50)
    } catch (error) {
      notify({
        type: 'error',
        message: 'Failed to select model. Please try again.'
      })
    }
  } else {
    notify({
      type: 'warning',
      message: 'Selected model is not available'
    })
  }
}

const handleModeSwitch = (mode: 'chat' | 'build') => {
  if (store.mode !== mode) {
    // Use the store action if available
    if (typeof store.setMode === 'function') {
      store.setMode(mode)
    } else {
      // Fallback: directly update the store state
      store.$patch({ mode })
    }
    
    // Force a store update to ensure reactivity
    store.$patch({})
    
    // Notify the user about the mode change
    notify({ 
      type: 'info', 
      message: `Switched to ${mode} mode` 
    })
    
    // Force a UI update by triggering a window resize event
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'))
    }, 50)
  }
}

const handleFileSelect = (file: ProjectFile) => {
  store.selectFile(file)
}

const handleFileCreate = async (data: { name: string; type: string }) => {
  try {
    const newFile = await createFile(data.name, data.type)
    notify({ type: 'success', message: 'File created successfully' })
    return newFile
  } catch (err: any) {
    notify({ type: 'error', message: err.message || 'Failed to create file' })
    throw err
  }
}

const handleUndo = async () => {
  try {
    store.setProcessing(true)
    await undoLastAction()
    notify({ type: 'success', message: 'Last action undone successfully' })
  } catch (err: any) {
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to undo last action' 
    })
  } finally {
    store.setProcessing(false)
  }
}

const handlePreview = () => {
  // Implement preview functionality
}

// Handle prompt submission
const handlePrompt = async () => {
  if (!prompt.value.trim() || store.isProcessing) return
  
  // Ensure we have a selected model
  if (!store.selectedModelId) {
    notify({
      type: 'warning',
      message: 'Please select an AI model first'
    })
    return
  }
  
  const originalPrompt = prompt.value
  prompt.value = '' // Clear prompt immediately for better UX
  
  try {
    if (store.mode === 'chat') {
      // For chat mode, use the chat service with the selected model
      await sendMessage(originalPrompt)
    } else {
      // For build mode, use the code generation service with the selected model and file
      const response = await generateCodeFromPrompt(originalPrompt)
      if (response.success) {
        notify({ type: 'success', message: 'Code generated successfully' })
      }
    }
  } catch (err: any) {
    prompt.value = originalPrompt // Restore prompt on error
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to process prompt' 
    })
  }
}

// Handle example prompt selection
const handleExamplePrompt = (example: string) => {
  prompt.value = example
  // Focus the input field
  setTimeout(() => {
    const inputElement = document.getElementById('user-input')
    if (inputElement) {
      inputElement.focus()
    }
  }, 100)
}

// Watch for editor content changes
const handleEditorChange = (content: string) => {
  if (store.selectedFile) {
    editorContent.value = content
    checkUnsavedChanges(content)
    autosaveContent(content)
  }
}

// Save file changes
const handleSave = async () => {
  try {
    await saveFile(editorContent.value)
    notify({ type: 'success', message: 'Changes saved successfully' })
  } catch (err: any) {
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to save changes' 
    })
  }
}

// Handle window close
const handleBeforeUnload = (e: BeforeUnloadEvent) => {
  if (store.unsavedChanges) {
    e.preventDefault()
    e.returnValue = ''
  }
}

// Session management
const checkSession = async () => {
  if (!sessionCheckEnabled.value) return;
  
  try {
    const response = await fetch('/api/v1/auth/session-status/')
    if (!response.ok) {
      throw new Error('Session check failed')
    }
    
    // Check if the response is JSON
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      sessionCheckFailCount.value++;
      
      // Disable session checks after multiple failures
      if (sessionCheckFailCount.value >= MAX_SESSION_CHECK_FAILS) {
        sessionCheckEnabled.value = false;
        if (sessionCheckInterval.value) {
          clearInterval(sessionCheckInterval.value);
          sessionCheckInterval.value = undefined;
        }
      }
      return;
    }
    
    // Reset fail count on success
    sessionCheckFailCount.value = 0;
    
    const data = await response.json()
    sessionTimeoutWarning.value = data.expiresIn < 300 // Show warning when less than 5 minutes remain
  } catch (err) {
    // Don't show warning on error to avoid false positives
    sessionTimeoutWarning.value = false
    
    // Increment fail count
    sessionCheckFailCount.value++;
    
    // Disable session checks after multiple failures
    if (sessionCheckFailCount.value >= MAX_SESSION_CHECK_FAILS) {
      sessionCheckEnabled.value = false;
      if (sessionCheckInterval.value) {
        clearInterval(sessionCheckInterval.value);
        sessionCheckInterval.value = undefined;
      }
    }
  }
}

const refreshSession = async () => {
  try {
    const response = await fetch('/api/v1/auth/refresh-session/', { method: 'POST' })
    if (!response.ok) {
      throw new Error('Failed to refresh session')
    }
    
    // Check if the response is JSON
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      notify({ type: 'warning', message: 'Session refresh may not have worked properly' })
      return;
    }
    
    sessionTimeoutWarning.value = false
    sessionCheckFailCount.value = 0
    sessionCheckEnabled.value = true
    
    // Restart session check interval if it was disabled
    if (!sessionCheckInterval.value) {
      sessionCheckInterval.value = window.setInterval(checkSession, 60000)
    }
    
    notify({ type: 'success', message: 'Session refreshed successfully' })
  } catch (err) {
    // If the session refresh fails, disable session checks to prevent further warnings
    sessionCheckEnabled.value = false
    if (sessionCheckInterval.value) {
      clearInterval(sessionCheckInterval.value)
      sessionCheckInterval.value = undefined
    }
    
    // Only show error notification if session checks were previously enabled
    if (sessionTimeoutWarning.value) {
      notify({ type: 'error', message: 'Failed to refresh session' })
      sessionTimeoutWarning.value = false
    }
  }
}

// Initialize workspace
onMounted(async () => {
  try {
    // Initialize the workspace
    await initializeWorkspace()
    
    // Add event listeners for model and mode changes
    document.addEventListener('model-selection-updated', handleModelSelectionUpdated)
    document.addEventListener('mode-selection-updated', handleModeSelectionUpdated)
    
    // Check session status
    try {
      const response = await fetch('/api/v1/auth/session-status/')
      if (!response.ok) {
        throw new Error('Session status endpoint returned error')
      }
      
      // Check if the response is JSON
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Session status endpoint returned non-JSON response')
      }
      
      // Session management is available, start the interval
      sessionCheckEnabled.value = true
      sessionCheckInterval.value = window.setInterval(checkSession, 60000) // Check every minute
    } catch (err) {
      // Silently disable session checks without console warnings
      sessionCheckEnabled.value = false
    }
    
    // Add beforeunload event listener
    window.addEventListener('beforeunload', handleBeforeUnload)
  } catch (err: any) {
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to initialize workspace' 
    })
  }
})

onBeforeUnmount(() => {
  // Clean up event listeners
  document.removeEventListener('model-selection-updated', handleModelSelectionUpdated)
  document.removeEventListener('mode-selection-updated', handleModeSelectionUpdated)
  
  // Clean up interval
  if (sessionCheckInterval.value) {
    clearInterval(sessionCheckInterval.value)
  }
  
  // Remove beforeunload event listener
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

// Handle model selection updates
const handleModelSelectionUpdated = (event: Event) => {
  // Force UI update by triggering a window resize event
  window.dispatchEvent(new Event('resize'))
  
  // Notify user of model change
  const customEvent = event as CustomEvent
  if (customEvent.detail?.modelId) {
    notify({
      type: 'info',
      message: `Model changed to ${store.selectedModel?.name || 'new model'}`
    })
  }
}

// Handle mode selection updates
const handleModeSelectionUpdated = (event: Event) => {
  // Force UI update by triggering a window resize event
  window.dispatchEvent(new Event('resize'))
  
  // Notify user of mode change
  const customEvent = event as CustomEvent
  if (customEvent.detail?.mode) {
    notify({
      type: 'info',
      message: `Switched to ${customEvent.detail.mode} mode`
    })
  }
}

// Add this function to initialize the builder
const initializeWorkspace = async () => {
  try {
    // Set default models directly
    const defaultModels = ModelService.getDefaultModels()
    
    // Ensure we're using the store correctly
    if (defaultModels && Array.isArray(defaultModels)) {
      try {
        // Set default models in the store
        store.setModels(defaultModels)
        
        // If no model is selected, select the first one
        if (!store.selectedModelId && defaultModels.length > 0) {
          if (typeof store.selectModel === 'function') {
            store.selectModel(defaultModels[0].id)
          } else {
            // Fallback: directly update the store state
            store.$patch({ selectedModelId: defaultModels[0].id })
          }
        }
      } catch (err) {
        notify({ 
          type: 'warning', 
          message: 'Failed to initialize AI models. Some features may be limited.' 
        })
      }
    }
    
    // Try to load models from API as well
    try {
      await loadModels()
    } catch (err) {
      // Silently fall back to default models
    }
    
    // Initialize mode if needed
    if (!store.mode) {
      try {
        store.setMode('chat')
      } catch (modeError) {
        // Fallback: directly update the store state if the action fails
        store.$patch({ mode: 'chat' })
      }
    }
    
    // Load project data if we have a project ID
    const projectId = route.params.id as string
    if (projectId) {
      try {
        await projectStore.fetchProject(projectId)
      } catch (err: any) {
        notify({ 
          type: 'error', 
          message: err.message || 'Failed to load project data' 
        })
      }
    }
  } catch (err: any) {
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to initialize workspace' 
    })
  }
}
</script>

<style scoped>
textarea {
  tab-size: 2;
  -moz-tab-size: 2;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  line-height: 1.5;
  font-size: 0.875rem;
}
</style>