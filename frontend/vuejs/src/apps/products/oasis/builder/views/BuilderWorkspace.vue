<!--
  BuilderWorkspace.vue - Project Editing Interface
  
  This component is responsible for:
  1. Loading an existing project's files and data
  2. Editing project files (create, update, delete files)
  3. Providing editor, preview, and file management tools
  
  It should NOT be responsible for:
  - Project creation (handled by BuilderDashboard.vue)
  - Project deletion (handled by BuilderDashboard.vue)
  - Project listing (handled by BuilderDashboard.vue)
-->
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
              { key: 'esc', handler: () => store.$patch({ error: null }), description: 'Clear error' }
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
import { useRoute, useRouter } from 'vue-router'
import { useBuilderStore } from '../stores/builderStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import { useChatMode } from '../composables/useChatMode'
import { useFileManager } from '../composables/useFileManager'
import { useProjectStore } from '../stores/projectStore'
import { AI_MODELS } from '../types/builder'
import { ModelService, BuilderService, ProjectService } from '../services'
import api from '../services/api'
import axios from 'axios'

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
const router = useRouter()
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
      // Direct update to the store state - use reactive update
      store.selectedModelId = modelId
      
      // Also use patch to ensure reactivity
      store.$patch({ selectedModelId: modelId })
      
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
      
      // Also dispatch a custom event to ensure other components are updated
      const event = new CustomEvent('model-changed', { 
        detail: modelId,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
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
  if (store.mode !== mode) {
    try {
      // Direct update to the store state - use reactive update
      store.mode = mode
      
      // Also use patch to ensure reactivity
      store.$patch({ mode })
      
      // Force a store update to ensure reactivity
      store.$patch({})
      
      // Clear conversation when switching to build mode
      if (mode === 'build') {
        store.$patch({ conversation: [] })
      }
      
      // Notify the user about the mode change
      notify({ 
        type: 'info', 
        message: `Switched to ${mode} mode` 
      })
      
      // Force a UI update by triggering a window resize event
      setTimeout(() => {
        window.dispatchEvent(new Event('resize'))
      }, 50)
      
      // Also dispatch a custom event to ensure other components are updated
      const event = new CustomEvent('mode-changed', { 
        detail: mode,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
    } catch (error) {
      console.error('Error switching mode', error)
      notify({
        type: 'error',
        message: 'Failed to switch mode. Please try again.'
      })
    }
  }
}

const handleFileSelect = (file: ProjectFile) => {
  store.selectFile(file)
}

const handleFileCreate = async (data: { name: string; type: string; content?: string }) => {
  try {
    // Get project ID from various sources
    let projectId = store.projectId
    
    // Check if project ID is set
    if (!projectId) {
      // Try to get project ID from route params
      projectId = route.params.id || route.params.projectId
      if (projectId) {
        // Set directly on the store state for immediate effect
        store.projectId = projectId
        store.$patch({ projectId })
      } else if (currentProject.value?.id) {
        // Try to get project ID from current project
        projectId = String(currentProject.value.id)
        // Set directly on the store state for immediate effect
        store.projectId = projectId
        store.$patch({ projectId })
      } else {
        throw new Error('No project selected. Please make sure you are in a project workspace.')
      }
    }
    
    // Handle directory creation for nested paths
    if (data.name.includes('/')) {
      // Extract directory and ensure it exists
      const pathParts = data.name.split('/')
      const fileName = pathParts.pop() || ''
      const directory = pathParts.join('/')
      
      try {
        // Try to create directory structure first, but continue if it fails
        // The enhanced ProjectService.createFile will handle this properly
      } catch (dirErr) {
        // Continue with file creation even if directory creation fails
      }
    }
    
    // This is where the actual file is created - this should only happen in the workspace
    const newFile = await createFile(data.name, data.type, data.content || '', projectId)
    notify({ type: 'success', message: 'File created successfully' })
    
    // If we just created one of the template files, check if others are needed
    if (data.name === 'templates/base.html' || data.name === 'templates/index.html' || data.name === 'static/css/styles.css') {
      // Reload project files to see what we have
      const updatedFiles = await ProjectService.getProjectFiles(projectId, false)
      const fileNames = updatedFiles.map(f => f.name)
      
      // Create any missing template files
      if (!fileNames.includes('templates/base.html')) {
        await createFile(
          'templates/base.html', 
          'html',
          `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Django Project{% endblock %}</title>
  {% load static %}
  <link rel="stylesheet" href="{% static 'css/styles.css' %}">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <header>
    <nav>
      <div class="container">
        <h1>My Django Project</h1>
      </div>
    </nav>
  </header>

  <main class="container">
    {% block content %}{% endblock %}
  </main>

  <footer>
    <div class="container">
      <p>&copy; {% now "Y" %} My Django Project</p>
    </div>
  </footer>
  
  {% block extra_js %}{% endblock %}
</body>
</html>`,
          projectId
        )
      }
      
      if (!fileNames.includes('templates/index.html')) {
        await createFile(
          'templates/index.html',
          'html',
          `{% extends "base.html" %}
{% load static %}

{% block title %}Home | Django Project{% endblock %}

{% block content %}
<div class="welcome-section">
  <h2>Welcome to your new Django project</h2>
  <p>This is the homepage of your Django application.</p>
  <p>Edit this template to start building your web application.</p>
</div>
{% endblock %}`,
          projectId
        )
      }
      
      if (!fileNames.includes('static/css/styles.css')) {
        await createFile(
          'static/css/styles.css',
          'css',
          `/* Main stylesheet */

:root {
  --primary-color: #4b6bfb;
  --secondary-color: #2e3856;
  --text-color: #333;
  --light-bg: #f9f9f9;
  --dark-bg: #2d3748;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
    Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  line-height: 1.6;
  margin: 0;
  padding: 0;
  color: var(--text-color);
  background-color: var(--light-bg);
}

.container {
  width: 85%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  font-size: 1.75rem;
}

main {
  padding: 2rem 0;
}

.welcome-section {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  margin-bottom: 2rem;
}

footer {
  background-color: var(--secondary-color);
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: 2rem;
}`,
          projectId
        )
      }
    }
    
    return newFile
  } catch (err: any) {
    console.error('Error creating file:', err)
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

// Save file changes - this should only happen in the workspace
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
      sessionCheckInterval.value = window.setInterval(checkSession, 60000);
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

// Add this function to redirect to the projects page
const redirectToProjectsPage = (message: string) => {
  notify({ 
    type: 'error', 
    message 
  })
  
  // Small delay to ensure notification is seen
  setTimeout(() => {
    router.push({ name: 'builder-projects' })
  }, 100)
}

// Add this function to check if an error is a 404 error
const isProjectNotFoundError = (error: any): boolean => {
  return (
    error?.isProjectNotFound === true ||
    error?.response?.status === 404 ||
    error?.message?.includes('not found') ||
    error?.message?.includes('Not Found') ||
    error?.detail?.includes('not found') ||
    error?.detail?.includes('Not Found') ||
    error?.response?.data?.detail?.includes('not found') ||
    error?.response?.data?.detail?.includes('Not Found') ||
    error?.response?.data?.message?.includes('not found') ||
    error?.response?.data?.message?.includes('Not Found')
  )
}

// Initialize workspace
onMounted(async () => {
  // Extract project ID from route parameters
  const projectId = route.params.id as string || ''
  const isNewProject = route.query.new === 'true'
  
  if (projectId) {
    // Use direct state mutation for immediate effect
    store.projectId = projectId
    store.$patch({ projectId })
    
    // Pre-emptively try to update API headers in case they weren't set
    const token = localStorage.getItem('token')
    if (token) {
      try {
        let tokenValue = token;
        // Try to parse as JSON if it's a JSON string
        if (token.startsWith('{') && token.endsWith('}')) {
          const parsedToken = JSON.parse(token)
          if (parsedToken && parsedToken.value) {
            tokenValue = parsedToken.value
          }
        }
        
        // Ensure the token is set in both API clients
        api.defaults.headers.common['Authorization'] = `Token ${tokenValue}`
        axios.defaults.headers.common['Authorization'] = `Token ${tokenValue}`
      } catch (e) {
        // Handle error silently
      }
    }
  }
  
  // Initialize the workspace
  try {
    await initializeWorkspace(isNewProject)
  } catch (initError) {
    // Show error but don't fail completely - some features might still work
    notify({ 
      type: 'warning', 
      message: 'Workspace initialization encountered issues. Some features may be limited.' 
    })
  }
  
  // Remove any existing event listeners to prevent duplicates
  window.removeEventListener('model-changed', handleModelSelectionUpdated)
  window.removeEventListener('mode-changed', handleModeSelectionUpdated)
  
  // Add event listeners for model and mode changes
  window.addEventListener('model-changed', handleModelSelectionUpdated)
  window.addEventListener('mode-changed', handleModeSelectionUpdated)
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

// Handle model selection updates from events
const handleModelSelectionUpdated = (event: Event) => {
  try {
    // Force UI update
    window.dispatchEvent(new Event('resize'))
    
    // Get the model ID from the event
    const modelId = (event as CustomEvent).detail
    
    // Find the model name for notification
    const model = [...(store.availableModels || []), ...AI_MODELS].find(m => m.id === modelId)
    
    // Notify user of model change
    if (model) {
      notify({ 
        type: 'info', 
        message: `Switched to ${model.name} model` 
      })
    }
    
    // Update store
    store.selectedModelId = modelId
    store.$patch({}) // Force reactive update
  } catch (err: any) {
    console.error('Error handling model selection update', err)
  }
}

// Handle mode selection updates from events
const handleModeSelectionUpdated = (event: Event) => {
  try {
    // Force UI update
    window.dispatchEvent(new Event('resize'))
    
    // Get the mode from the event
    const mode = (event as CustomEvent).detail as BuilderMode
    
    // Notify user of mode change
    notify({ 
      type: 'info', 
      message: `Switched to ${mode} mode` 
    })
    
    // Update store
    store.mode = mode
    store.$patch({}) // Force reactive update
    
    // Clear conversation when switching to build mode
    if (mode === 'build' && store.conversation?.length) {
      store.conversation = []
    }
  } catch (err: any) {
    console.error('Error handling mode selection update', err)
  }
}

// Add this function to initialize the builder
const initializeWorkspace = async (isNewProject = false) => {
  try {
    // Set default models directly
    const defaultModels = ModelService.getDefaultModels()
    
    // Ensure we're using the store correctly
    if (defaultModels && Array.isArray(defaultModels)) {
      try {
        // Set models directly in the store state instead of using setModels
        store.$patch({ availableModels: defaultModels })
        
        // If no model is selected, select the first one
        if (!store.selectedModelId && defaultModels.length > 0) {
          const defaultModelId = defaultModels[0].id
          
          // Direct update to the store state
          store.$patch({ selectedModelId: defaultModelId })
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
      const defaultMode = 'chat'
      
      // Direct update to the store state
      store.$patch({ mode: defaultMode })
    }
    
    // Ensure we have a project ID
    let projectId = store.projectId
    
    if (!projectId) {
      const routeProjectId = route.params.id || route.params.projectId
      if (routeProjectId) {
        // Set directly on the store state for immediate effect
        store.projectId = routeProjectId
        store.$patch({ projectId: routeProjectId })
        projectId = routeProjectId
      }
    }
    
    // Use the project ID from the store after ensuring it's set
    if (projectId) {
      try {
        // Ensure the store has the project ID
        if (!store.projectId) {
          store.projectId = projectId
        }
        
        let projectFetched = false;
        
        try {
          // Try to fetch project, but don't let it block other initialization steps if it fails
          await projectStore.fetchProject(projectId, isNewProject)
          projectFetched = true;
        } catch (projectErr) {
          // Handle 404 (Not Found) errors by redirecting to projects page
          if (isProjectNotFoundError(projectErr) || projectErr?.response?.status === 404) {
            redirectToProjectsPage('Project not found or has been deleted')
            return
          } else if (projectErr?.response?.status === 403) {
            // Handle forbidden errors
            redirectToProjectsPage('You do not have permission to access this project')
            return
          } else {
            // For other errors, continue with initialization but show warning
            notify({ 
              type: 'warning', 
              message: 'Project details could not be loaded, but you can still work with files' 
            })
          }
        }
        
        // Load project files - this can work even if the project details couldn't be fetched
        try {
          const filesResponse = await ProjectService.getProjectFiles(projectId, isNewProject)
          if (filesResponse && Array.isArray(filesResponse)) {
            store.$patch({ files: filesResponse })
            
            // Check if project has files, if not ensure project is initialized
            if (filesResponse.length === 0) {
              try {
                // First, try to initialize the project
                const initResult = await BuilderService.initializeProject(projectId)
                
                if (initResult && initResult.success) {
                  // Wait a moment for files to be created
                  await new Promise(resolve => setTimeout(resolve, 1000))
                  
                  // Reload project files after backend initialization
                  const updatedFiles = await ProjectService.getProjectFiles(projectId, true)
                  
                  if (updatedFiles && Array.isArray(updatedFiles)) {
                    store.$patch({ files: updatedFiles })
                    
                    if (updatedFiles.length > 0) {
                      notify({ 
                        type: 'success', 
                        message: 'Project initialized successfully' 
                      })
                    } else {
                      notify({ 
                        type: 'warning', 
                        message: 'Project initialization did not create any files' 
                      })
                    }
                  }
                }
              } catch (err) {
                notify({ 
                  type: 'warning', 
                  message: 'Project initialization failed' 
                })
              }
            }
          }
        } catch (filesErr) {
          // If this is a 404 error, redirect to projects page
          if (isProjectNotFoundError(filesErr)) {
            redirectToProjectsPage('Project not found or has been deleted')
            return
          }
          
          notify({ 
            type: 'warning', 
            message: 'Could not load project files' 
          })
          // Still keep the workspace usable with empty files array
          store.$patch({ files: [] })

          if (isNewProject) {
            // For new projects, try to initialize directly
            try {
              // Initialize the project and create default files
              const initResult = await BuilderService.initializeProject(projectId)
              if (initResult && initResult.success) {
                notify({ 
                  type: 'info', 
                  message: 'Project initialization in progress. Files will appear shortly.' 
                })
                
                // Wait a moment for files to be created
                await new Promise(resolve => setTimeout(resolve, 1000))
                
                // Reload project files
                const updatedFiles = await ProjectService.getProjectFiles(projectId, true)
                if (updatedFiles && Array.isArray(updatedFiles)) {
                  store.$patch({ files: updatedFiles })
                  
                  if (updatedFiles.length > 0) {
                    notify({ 
                      type: 'success', 
                      message: 'Project initialized successfully' 
                    })
                  }
                }
              }
            } catch (err) {
              // Check if this is a not found error
              if (isProjectNotFoundError(err)) {
                redirectToProjectsPage('Project not found or has been deleted')
                return
              }
            }
          }
        }
        
        // If everything completed without major errors, show success message
        if (!projectFetched) {
          notify({ 
            type: 'info', 
            message: 'Workspace initialized with limited functionality' 
          })
        }
      } catch (err) {
        // Check if this is a not found error
        if (isProjectNotFoundError(err)) {
          redirectToProjectsPage('Project not found or has been deleted')
          return
        }
        
        notify({ 
          type: 'error', 
          message: err.message || 'Failed to load project data' 
        })
      }
    } else {
      redirectToProjectsPage('Failed to initialize workspace: No project ID available')
    }
  } catch (err) {
    // Check if this is a not found error
    if (isProjectNotFoundError(err)) {
      redirectToProjectsPage('Project not found or has been deleted')
      return
    }
    
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