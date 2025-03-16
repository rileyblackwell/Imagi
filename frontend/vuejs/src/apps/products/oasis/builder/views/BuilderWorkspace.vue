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

      <!-- Main Content Area -->
      <template #main-content>
        <div class="h-full relative flex flex-col">
          <!-- Background decorative elements -->
          <div class="absolute inset-0 overflow-hidden pointer-events-none">
            <!-- Gradient effect -->
            <div class="absolute inset-0 bg-gradient-to-br from-dark-900 to-dark-950"></div>
            
            <!-- Animated orbs -->
            <div class="absolute top-[10%] right-[5%] w-96 h-96 bg-primary-600/10 rounded-full filter blur-3xl opacity-30 animate-float-slow"></div>
            <div class="absolute bottom-[20%] left-[10%] w-64 h-64 bg-violet-600/10 rounded-full filter blur-2xl opacity-20 animate-float-slow-reverse"></div>
            
            <!-- Grid pattern overlay -->
            <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
          </div>

          <!-- Loading Overlay -->
          <div 
            v-if="store.isProcessing"
            class="absolute inset-0 bg-dark-950/70 backdrop-blur-sm flex items-center justify-center z-50"
          >
            <div class="text-center">
              <div class="inline-block w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mb-4"></div>
              <p class="text-lg text-white font-medium">Processing...</p>
              <p class="text-sm text-gray-400 mt-1">The AI is working on your request</p>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 flex flex-col overflow-hidden relative">
            <Transition
              name="fade"
              mode="out-in"
              appear
            >
              <div v-if="store.mode === 'chat'" class="flex-1 overflow-auto px-4 py-2">
                <div class="max-w-4xl mx-auto">
                  <ChatConversation 
                    :messages="ensureValidMessages(store.conversation || [])" 
                    @use-example="handleExamplePrompt"
                  />
                </div>
              </div>
              <div v-else class="flex-1 flex flex-col overflow-hidden">
                <!-- Show chat feed at the top in build mode -->
                <div class="flex-1 overflow-auto px-4 py-2">
                  <div class="max-w-4xl mx-auto">
                    <ChatConversation 
                      :messages="ensureValidMessages(store.conversation || [])" 
                      @use-example="handleExamplePrompt"
                    />
                  </div>
                </div>
                
                <!-- Show editor below chat feed when a file is selected -->
                <div v-if="store.selectedFile" class="h-1/2 border-t border-dark-700/50 shadow-lg">
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
              class="shrink-0 p-4 border-t border-dark-700/50 bg-dark-900/80 backdrop-blur-md shadow-lg relative"
              :class="{'opacity-50 pointer-events-none': store.isProcessing}"
            >
              <!-- Gradient header line -->
              <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-500/30 to-transparent"></div>
              
              <div class="max-w-4xl mx-auto">
                <ChatInputArea
                  v-model="prompt"
                  :placeholder="promptPlaceholder"
                  :focused="false"
                  :is-processing="store.isProcessing"
                  :show-examples="store.conversation.length === 0"
                  @submit="handlePrompt"
                  @examples="() => {}"
                >
                  <template #examples v-if="promptExamplesComputed && promptExamplesComputed.length > 0">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
                      <button
                        v-for="example in promptExamplesComputed"
                        :key="example.text"
                        class="text-left p-3 bg-dark-800/60 hover:bg-dark-800/90 rounded-md border border-dark-700/50 hover:border-primary-500/40 text-gray-300 transition-all duration-200 backdrop-blur-sm hover:shadow-md"
                        @click="prompt = example.text; handlePrompt()"
                      >
                        <p class="font-medium text-white">{{ example.title }}</p>
                        <p class="text-sm text-gray-400 mt-1 line-clamp-2">{{ example.text }}</p>
                      </button>
                    </div>
                  </template>
                </ChatInputArea>
              </div>
            </div>
          </div>
        </div>
      </template>
    </BuilderLayout>
  </ErrorBoundary>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import { useChatMode } from '../composables/useChatMode'
import { useFileManager } from '../composables/useFileManager'
import { useProjectStore } from '../stores/projectStore'
import { AI_MODELS } from '../types/builder'
import { AgentService, ModelService } from '../services/agentService'
import { ProjectService } from '../services/projectService'
import { FileService } from '../services/fileService'
import api from '../services/api'
import axios from 'axios'
import { useAuthStore } from '@/shared/stores/auth'
import { useNotification } from '@/shared/composables/useNotification'

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
import ChatInputArea from '../components/molecules/inputs/ChatInputArea.vue'

// Utils
import { notify } from '@/shared/utils'
import type { ProjectFile, EditorMode } from '../types/builder'
import type { AIMessage } from '../types/index'

const route = useRoute()
const router = useRouter()
const store = useAgentStore()
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

// Add a ref to store the interval ID
const refreshInterval = ref<number | null>(null)

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

// Computed prompt examples
const promptExamplesComputed = computed(() => {
  // Return basic examples if not available from another source
  return [
    {
      title: 'Create a landing page',
      text: 'Please create a landing page with a hero section, features, and a contact form.'
    },
    {
      title: 'Build an ecommerce product page',
      text: 'I need a product details page with image gallery, pricing, and add to cart functionality.'
    },
    {
      title: 'Generate a dashboard',
      text: 'Create a dashboard with stats, charts, and a recent activity feed.'
    },
    {
      title: 'Make a blog layout',
      text: 'Design a blog page with articles, sidebar, and newsletter signup.'
    }
  ];
});

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

const handleFileSelect = (file: any) => {
  // Ensure we're using the correct ProjectFile type
  const projectFile: ProjectFile = {
    path: file.path,
    type: file.type,
    content: file.content || '',
    lastModified: file.lastModified || new Date().toISOString()
  };
  
  store.selectFile(projectFile);
}

const handleFileCreate = async (data: { name: string; type: string; content?: string }) => {
  try {
    // Get project ID from various sources
    let projectId = store.projectId
    
    // Check if project ID is set
    if (!projectId) {
      // Check for projectId in route params
      const routeProjectId = route.params.projectId || route.params.id
      
      console.debug('Route parameters:', {
        params: route.params,
        projectId: routeProjectId
      })
      
      if (routeProjectId) {
        // Ensure it's a string
        const projectIdStr = String(routeProjectId)
        console.debug(`Setting project ID from route: ${projectIdStr}`)
        
        // Set directly on the store state for immediate effect
        store.projectId = projectIdStr
        store.$patch({ projectId: projectIdStr })
        projectId = projectIdStr
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
    const newFile = await createFile(data.name, data.type, data.content || '', projectId || '')
    notify({ type: 'success', message: 'File created successfully' })
    
    // If we just created one of the template files, check if others are needed
    if (data.name === 'templates/base.html' || data.name === 'templates/index.html' || data.name === 'static/css/styles.css') {
      // Reload project files to see what we have
      const updatedFiles = await FileService.getProjectFiles(projectId || '')
      const fileNames = updatedFiles.map(f => f.path)
      
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
          projectId || ''
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
          projectId || ''
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
          projectId || ''
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
    const response = await AgentService.generatePreview(store.projectId || '')
    
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

// Ensure conversation messages have the correct timestamp type
const ensureValidMessages = (messages: any[]): AIMessage[] => {
  return messages.map(msg => ({
    role: msg.role,
    content: msg.content,
    code: msg.code,
    // Convert string timestamp to number if needed
    timestamp: typeof msg.timestamp === 'string' ? Date.parse(msg.timestamp) : (msg.timestamp || Date.now()),
    // Ensure id exists
    id: msg.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
  }));
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

// Properly place the onBeforeUnmount hook at the top level
onBeforeUnmount(() => {
  // Clean up event listeners
  window.removeEventListener('model-changed', handleModelSelectionUpdated)
  window.removeEventListener('mode-changed', handleModeSelectionUpdated)
  
  // Clean up the project refresh interval if it exists
  if (refreshInterval.value !== null) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
  
  // Clean up session check interval
  if (sessionCheckInterval.value) {
    clearInterval(sessionCheckInterval.value)
  }
  
  // Remove beforeunload event listener
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

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
    
    // Refresh all projects before initializing workspace to ensure fresh data
    try {
      const authStore = useAuthStore()
      if (authStore.isAuthenticated && projectStore.fetchProjects) {
        await projectStore.fetchProjects(true)
      }
    } catch (refreshError) {
      console.warn('Failed to refresh projects before workspace initialization:', refreshError)
      // Continue with initialization even if refresh fails
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
  
  // Add event listeners for model and mode changes
  window.addEventListener('model-changed', handleModelSelectionUpdated)
  window.addEventListener('mode-changed', handleModeSelectionUpdated)
  
  // Set up periodic refresh of project data to ensure it stays up to date
  refreshInterval.value = window.setInterval(() => {
    try {
      const authStore = useAuthStore()
      if (authStore.isAuthenticated && projectStore.fetchProjects) {
        // Only perform background refresh when the document is visible
        if (document.visibilityState === 'visible') {
          projectStore.fetchProjects(true).catch(error => {
            console.warn('Background project refresh failed:', error)
          })
        }
      }
    } catch (error) {
      console.warn('Error during background project refresh:', error)
    }
  }, 60000) // Refresh every minute in the background
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
    const mode = (event as CustomEvent).detail as 'chat' | 'build'
    
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
      // Check for projectId in route params
      const routeProjectId = route.params.projectId || route.params.id
      
      console.debug('Route parameters:', {
        params: route.params,
        projectId: routeProjectId
      })
      
      if (routeProjectId) {
        // Ensure it's a string
        const projectIdStr = String(routeProjectId)
        console.debug(`Setting project ID from route: ${projectIdStr}`)
        
        // Set directly on the store state for immediate effect
        store.projectId = projectIdStr
        store.$patch({ projectId: projectIdStr })
        projectId = projectIdStr
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
          // First refresh all projects to avoid stale data
          if (projectStore.fetchProjects) {
            await projectStore.fetchProjects(true)
          }
          
          // Then fetch the specific project
          await projectStore.fetchProject(projectId, isNewProject)
          projectFetched = true;
        } catch (projectErr: any) {
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
          const filesResponse = await FileService.getProjectFiles(projectId)
          if (filesResponse && Array.isArray(filesResponse)) {
            store.$patch({ files: filesResponse })
            
            // Check if project has files, if not ensure project is initialized
            if (filesResponse.length === 0) {
              try {
                // First try to check project status via ProjectService
                let initialized = false;
                try {
                  const statusResponse = await ProjectService.initializeProject(projectId);
                  initialized = statusResponse?.success || statusResponse?.is_initialized;
                  console.debug('Project initialization check:', { statusResponse, initialized });
                } catch (statusErr) {
                  console.warn('Failed to check project status via ProjectService:', statusErr);
                  
                  // Fallback to AgentService
                  try {
                    const initResult = await AgentService.initializeProject(projectId);
                    initialized = initResult?.success;
                    console.debug('Project initialization via AgentService:', { initResult, initialized });
                  } catch (agentErr) {
                    console.warn('Failed to initialize project via AgentService:', agentErr);
                  }
                }
                
                if (initialized) {
                  // Wait a moment for files to be created
                  await new Promise(resolve => setTimeout(resolve, 1000));
                  
                  // Reload project files after backend initialization
                  const updatedFiles = await FileService.getProjectFiles(projectId);
                  
                  if (updatedFiles && Array.isArray(updatedFiles)) {
                    store.$patch({ files: updatedFiles });
                    
                    if (updatedFiles.length > 0) {
                      notify({ 
                        type: 'success', 
                        message: 'Project initialized successfully' 
                      });
                    } else {
                      notify({ 
                        type: 'warning', 
                        message: 'Project initialization did not create any files' 
                      });
                    }
                  }
                }
              } catch (err) {
                console.error('Project initialization failed:', err);
                notify({ 
                  type: 'warning', 
                  message: 'Project initialization failed' 
                });
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
              const initResult = await AgentService.initializeProject(projectId)
              if (initResult && initResult.success) {
                notify({ 
                  type: 'info', 
                  message: 'Project initialization in progress. Files will appear shortly.' 
                })
                
                // Wait a moment for files to be created
                await new Promise(resolve => setTimeout(resolve, 1000))
                
                // Reload project files
                const updatedFiles = await FileService.getProjectFiles(projectId)
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
      } catch (err: any) {
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
  } catch (err: any) {
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

/**
 * Load project details and files
 */
async function loadProject(projectId: string) {
  try {
    // First, load the project details
    const project = await projectStore.fetchProject(projectId)
    
    if (!project) {
      notify({
        type: 'error',
        message: 'Project not found'
      })
      return false
    }
    
    // Then load the project files
    const files = await projectStore.fetchProjectFiles(projectId)
    
    console.debug(`Loaded project ${project.name} with ${files.length} files`)
    return true
  } catch (error: any) {
    notify({
      type: 'error',
      message: error?.message || 'Failed to load project'
    })
    return false
  }
}

/**
 * Save file content
 */
async function updateFileContent(projectId: string, filePath: string, content: string) {
  try {
    await projectStore.updateFileContent(projectId, filePath, content)
    
    notify({
      type: 'success',
      message: `File "${filePath}" saved successfully`
    })
    return true
  } catch (error: any) {
    notify({
      type: 'error',
      message: error?.message || `Failed to save file "${filePath}"`
    })
    return false
  }
}

/**
 * Create a new file
 */
async function createProjectFile(projectId: string, filePath: string, content: string = '') {
  try {
    await projectStore.createFile(projectId, filePath, content)
    
    notify({
      type: 'success',
      message: `File "${filePath}" created successfully`
    })
    return true
  } catch (error: any) {
    notify({
      type: 'error',
      message: error?.message || `Failed to create file "${filePath}"`
    })
    return false
  }
}

/**
 * Delete a file
 */
async function deleteFile(projectId: string, filePath: string) {
  try {
    await projectStore.deleteFile(projectId, filePath)
    
    notify({
      type: 'success',
      message: `File "${filePath}" deleted successfully`
    })
    return true
  } catch (error: any) {
    notify({
      type: 'error',
      message: error?.message || `Failed to delete file "${filePath}"`
    })
    return false
  }
}
</script>

<style scoped>
.bg-grid-pattern {
  background-size: 40px 40px;
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes float-slow {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-10px) translateX(10px);
  }
  50% {
    transform: translateY(0) translateX(20px);
  }
  75% {
    transform: translateY(10px) translateX(10px);
  }
}

@keyframes float-slow-reverse {
  0%, 100% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(10px) translateX(-10px);
  }
  50% {
    transform: translateY(0) translateX(-20px);
  }
  75% {
    transform: translateY(-10px) translateX(-10px);
  }
}

.animate-float-slow {
  animation: float-slow 20s ease-in-out infinite;
}

.animate-float-slow-reverse {
  animation: float-slow-reverse 25s ease-in-out infinite;
}
</style>