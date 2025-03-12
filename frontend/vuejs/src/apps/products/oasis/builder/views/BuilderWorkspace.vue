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
import { ref, onMounted, computed, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useBuilderStore } from '../stores/builderStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import { useChatMode } from '../composables/useChatMode'
import { useFileManager } from '../composables/useFileManager'
import { useProjectStore } from '../stores/projectStore'
import { AI_MODELS } from '../types/builder'
import { ModelService, BuilderService, ProjectService } from '../services'

// Shared Components
import ErrorBoundary from '../components/atoms/utility/ErrorBoundary.vue'
import AppShortcuts from '@/shared/components/molecules/feedback/AppShortcuts.vue'
import { SessionTimeoutWarning } from '@/apps/auth/components/molecules'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import LoadingOverlay from '../components/atoms/feedback/LoadingOverlay.vue'
import BuilderSidebar from '../components/organisms/sidebar/BuilderSidebar.vue'
import BuilderEditor from '../components/organisms/editor/BuilderEditor.vue'
import AIPromptInput from '../components/molecules/inputs/AIPromptInput.vue'
import ChatConversation from '../components/molecules/chat/ChatConversation.vue'

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
  console.log('handleModelSelect called in BuilderWorkspace', { modelId, currentModelId: store.selectedModelId })
  
  // Verify the model exists in available models or default models
  const modelExists = store.availableModels.some(model => model.id === modelId) || 
                     AI_MODELS.some(model => model.id === modelId)
  
  if (modelId && modelExists) {
    try {
      console.log('Model exists, updating store', { modelId })
      
      // Direct update to the store state - use reactive update
      store.selectedModelId = modelId
      
      // Also use patch to ensure reactivity
      store.$patch({ selectedModelId: modelId })
      
      // Force a store update to ensure reactivity
      store.$patch({})
      
      console.log('Store updated', { storeModelId: store.selectedModelId })
      
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
        console.log('Window resize event dispatched')
      }, 50)
      
      // Also dispatch a custom event to ensure other components are updated
      const event = new CustomEvent('model-changed', { 
        detail: modelId,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
      console.log('Custom model-changed event dispatched via window', { 
        modelId,
        eventType: event.type,
        eventDetail: event.detail
      })
      
      console.log('Model selection complete', { 
        modelId, 
        storeModelId: store.selectedModelId 
      })
      
      // Log store state after update
      logStoreState()
    } catch (error) {
      console.error('Error selecting model', error)
      notify({
        type: 'error',
        message: 'Failed to select model. Please try again.'
      })
    }
  } else {
    console.warn('Model does not exist', { modelId })
    notify({
      type: 'warning',
      message: 'Selected model is not available'
    })
  }
}

const handleModeSwitch = (mode: 'chat' | 'build') => {
  console.log('handleModeSwitch called in BuilderWorkspace', { mode, currentMode: store.mode })
  
  if (store.mode !== mode) {
    try {
      console.log('Mode differs, updating store', { mode })
      
      // Direct update to the store state - use reactive update
      store.mode = mode
      
      // Also use patch to ensure reactivity
      store.$patch({ mode })
      
      // Force a store update to ensure reactivity
      store.$patch({})
      
      console.log('Store updated', { storeMode: store.mode })
      
      // Clear conversation when switching to build mode
      if (mode === 'build') {
        store.$patch({ conversation: [] })
        console.log('Conversation cleared for build mode')
      }
      
      // Notify the user about the mode change
      notify({ 
        type: 'info', 
        message: `Switched to ${mode} mode` 
      })
      
      // Force a UI update by triggering a window resize event
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'))
        console.log('Window resize event dispatched')
      }, 50)
      
      // Also dispatch a custom event to ensure other components are updated
      const event = new CustomEvent('mode-changed', { 
        detail: mode,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
      console.log('Custom mode-changed event dispatched via window', { 
        mode,
        eventType: event.type,
        eventDetail: event.detail
      })
      
      console.log('Mode switch complete', { 
        mode, 
        storeMode: store.mode 
      })
      
      // Log store state after update
      logStoreState()
    } catch (error) {
      console.error('Error switching mode', error)
      notify({
        type: 'error',
        message: 'Failed to switch mode. Please try again.'
      })
    }
  } else {
    console.log('Mode is already set to', mode)
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

const handlePreview = async () => {
  try {
    store.setProcessing(true)
    
    // Call the backend to generate a preview URL
    const response = await BuilderService.generatePreview(store.projectId || '')
    
    if (response && response.previewUrl) {
      // Open the preview URL in a new tab
      window.open(response.previewUrl, '_blank')
      notify({ type: 'success', message: 'Preview launched successfully' })
    } else {
      throw new Error('Failed to generate preview URL')
    }
  } catch (err: any) {
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to launch preview' 
    })
  } finally {
    store.setProcessing(false)
  }
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
      // For build mode, ensure a file is selected when in build mode
      if (!store.selectedFile) {
        notify({
          type: 'warning',
          message: 'Please select a file first'
        })
        prompt.value = originalPrompt // Restore prompt
        return
      }
      
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

// Debugging function to log store state
const logStoreState = () => {
  console.log('Current store state:', {
    mode: store.mode,
    selectedModelId: store.selectedModelId,
    availableModels: store.availableModels?.length || 0,
    files: store.files?.length || 0,
    conversation: store.conversation?.length || 0,
    isProcessing: store.isProcessing,
    unsavedChanges: store.unsavedChanges,
    error: store.error
  })
}

// Initialize workspace
onMounted(async () => {
  try {
    console.log('Component mounted, initializing workspace')
    
    // Log initial store state
    logStoreState()
    
    // Force direct initialization of store with default values
    if (!store.mode) {
      store.$patch({ mode: 'chat' })
      console.log('Set default mode: chat')
    }
    
    // Make sure AI_MODELS is defined and has elements before accessing
    if (AI_MODELS && Array.isArray(AI_MODELS) && AI_MODELS.length > 0 && !store.selectedModelId) {
      store.$patch({ selectedModelId: AI_MODELS[0].id })
      console.log('Set default model:', AI_MODELS[0].id)
    }
    
    // Log store state after defaults
    logStoreState()
    
    // Initialize the workspace
    await initializeWorkspace()
    
    // Log store state after initialization
    logStoreState()
    
    // Remove any existing event listeners to prevent duplicates
    window.removeEventListener('model-changed', handleModelSelectionUpdated)
    window.removeEventListener('mode-changed', handleModeSelectionUpdated)
    
    // Add event listeners for model and mode changes
    window.addEventListener('model-changed', handleModelSelectionUpdated)
    window.addEventListener('mode-changed', handleModeSelectionUpdated)
    
    console.log('Event listeners set up for model-changed and mode-changed events on window')
    
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
    
    // Log final state after initialization
    console.log('Component initialization complete', {
      selectedModelId: store.selectedModelId,
      mode: store.mode,
      files: store.files?.length || 0
    })
    
    // Final store state log
    logStoreState()
  } catch (err: any) {
    console.error('Error in onMounted', err)
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to initialize workspace' 
    })
  }
})

onBeforeUnmount(() => {
  // Clean up event listeners
  window.removeEventListener('model-changed', handleModelSelectionUpdated)
  window.removeEventListener('mode-changed', handleModeSelectionUpdated)
  
  // Clean up interval
  if (sessionCheckInterval.value) {
    clearInterval(sessionCheckInterval.value)
  }
  
  // Remove beforeunload event listener
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

// Handle model selection updates
const handleModelSelectionUpdated = (event: Event) => {
  // Log the current state for debugging
  console.log('Model selection updated event received', {
    event,
    currentModelId: store.selectedModelId,
    availableModels: store.availableModels
  })

  // Force UI update by triggering a window resize event
  window.dispatchEvent(new Event('resize'))
  
  // Notify user of model change
  const customEvent = event as CustomEvent
  if (customEvent.detail) {
    const modelId = customEvent.detail
    
    console.log('Updating store with new model ID from event', { modelId })
    
    // Ensure the store is updated with the new model ID
    store.$patch({ selectedModelId: modelId })
    
    console.log('Store updated from event', { storeModelId: store.selectedModelId })
    
    const modelName = store.availableModels.find(m => m.id === modelId)?.name || 
                     AI_MODELS.find(m => m.id === modelId)?.name || 
                     'new model'
    
    notify({
      type: 'info',
      message: `Model changed to ${modelName}`
    })
    
    // Log the updated state
    console.log('After model selection update', {
      modelId,
      currentModelId: store.selectedModelId
    })
    
    // Log store state after update
    logStoreState()
  }
}

// Handle mode selection updates
const handleModeSelectionUpdated = (event: Event) => {
  // Log the current state for debugging
  console.log('Mode selection updated event received', {
    event,
    currentMode: store.mode
  })

  // Force UI update by triggering a window resize event
  window.dispatchEvent(new Event('resize'))
  
  // Notify user of mode change
  const customEvent = event as CustomEvent
  if (customEvent.detail) {
    const mode = customEvent.detail
    
    console.log('Updating store with new mode from event', { mode })
    
    // Ensure the store is updated - use direct patch instead of method call
    store.$patch({ mode })
    
    console.log('Store updated from event', { storeMode: store.mode })
    
    // Clear conversation when switching to build mode
    if (mode === 'build') {
      store.$patch({ conversation: [] })
      console.log('Conversation cleared for build mode from event')
    }
    
    notify({
      type: 'info',
      message: `Switched to ${mode} mode`
    })
    
    // Log the updated state
    console.log('After mode selection update', {
      mode,
      currentMode: store.mode
    })
    
    // Log store state after update
    logStoreState()
  }
}

// Add this function to initialize the builder
const initializeWorkspace = async () => {
  try {
    console.log('Initializing workspace')
    
    // Set default models directly
    const defaultModels = ModelService.getDefaultModels()
    console.log('Default models', defaultModels)
    
    // Ensure we're using the store correctly
    if (defaultModels && Array.isArray(defaultModels)) {
      try {
        // Set models directly in the store state instead of using setModels
        store.$patch({ availableModels: defaultModels })
        console.log('Models set in store', store.availableModels)
        
        // If no model is selected, select the first one
        if (!store.selectedModelId && defaultModels.length > 0) {
          const defaultModelId = defaultModels[0].id
          console.log('Setting default model', defaultModelId)
          
          // Direct update to the store state
          store.$patch({ selectedModelId: defaultModelId })
          
          console.log('Default model set', store.selectedModelId)
        }
      } catch (err) {
        console.error('Error initializing models', err)
        notify({ 
          type: 'warning', 
          message: 'Failed to initialize AI models. Some features may be limited.' 
        })
      }
    }
    
    // Try to load models from API as well
    try {
      await loadModels()
      console.log('Models loaded from API', store.availableModels)
    } catch (err) {
      console.warn('Failed to load models from API, using defaults', err)
      // Silently fall back to default models
    }
    
    // Initialize mode if needed
    if (!store.mode) {
      const defaultMode = 'chat'
      console.log('Setting default mode', defaultMode)
      
      // Direct update to the store state
      store.$patch({ mode: defaultMode })
      
      console.log('Default mode set', store.mode)
    }
    
    // Load project data if we have a project ID
    const projectId = route.params.id as string
    if (projectId) {
      try {
        await projectStore.fetchProject(projectId)
        console.log('Project fetched', projectStore.currentProject)
        
        // Load project files
        const filesResponse = await ProjectService.getProjectFiles(projectId)
        if (filesResponse && Array.isArray(filesResponse)) {
          store.$patch({ files: filesResponse })
          console.log('Project files loaded', store.files?.length || 0)
        }
      } catch (err: any) {
        console.error('Error loading project data', err)
        notify({ 
          type: 'error', 
          message: err.message || 'Failed to load project data' 
        })
      }
    }
    
    console.log('Workspace initialization complete', {
      selectedModelId: store.selectedModelId,
      mode: store.mode,
      files: store.files?.length || 0
    })
  } catch (err: any) {
    console.error('Error initializing workspace', err)
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to initialize workspace' 
    })
  }
}

// Watch for changes to the store's selectedModelId
watch(() => store.selectedModelId, (newModelId, oldModelId) => {
  console.log('Store selectedModelId changed', { newModelId, oldModelId })
})

// Watch for changes to the store's mode
watch(() => store.mode, (newMode, oldMode) => {
  console.log('Store mode changed', { newMode, oldMode })
})
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