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
          @undo="handleUndo"
          @preview="handlePreview"
        />
      </template>

      <!-- Main Content Area -->
      <div class="flex flex-col h-screen max-h-screen w-full overflow-hidden bg-dark-950 relative">
        <!-- Modern Chat UI using WorkspaceChat component -->
        <div class="flex-1 flex flex-col h-full overflow-hidden">
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
            @apply-code="handleApplyCode"
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
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentsStore } from '@/apps/payments/store'
import { useBalanceStore } from '@/shared/stores/balance'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import BuilderSidebar from '../components/organisms/sidebar/BuilderSidebar.vue'
import { AccountBalanceDisplay } from '../components/molecules'

// Atomic Components
import { WorkspaceChat } from '../components/organisms/workspace'

// Utils
import { notify } from '@/shared/utils'
import type { ProjectFile, EditorMode, BuilderMode } from '../types/components'
import type { AIMessage } from '../types/index'

// Debounce utility function for balance refresh
const debounce = (fn: Function, delay: number) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: any[]) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
};

const route = useRoute()
const store = useAgentStore()
const projectStore = useProjectStore()
const projectId = ref<string>('')
const { 
  generateCodeFromPrompt, 
  createFile, 
  loadModels,
  applyCode 
} = useBuilderMode()
const { sendMessage } = useChatMode()

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

async function handlePrompt(eventData?: { timestamp: string }) {
  if (!prompt.value.trim()) return
  
  try {
    if (!store.selectedModelId) {
      notify({ type: 'warning', message: 'Please select an AI model' })
      return
    }
    
    const timestamp = eventData?.timestamp || new Date().toISOString()
    
    // Get payments store for updating balance
    const paymentsStore = usePaymentsStore()
    const balanceStore = useBalanceStore()
    
    // Mark that a transaction is about to happen to ensure fresh balance data
    balanceStore.beginTransaction()
    
    // Check if we have a project ID
    if (!projectId.value) {
      notify({ type: 'warning', message: 'Invalid project ID' })
      return
    }
    
    // Add the user message to the conversation immediately
    store.conversation.push({
      role: 'user' as const,
      content: prompt.value,
      timestamp: timestamp,
      id: `user-${Date.now()}`
    })
    
    // For build mode, file selection is required
    if (store.mode === 'build' && !store.selectedFile) {
      notify({ type: 'warning', message: 'Please select a file to modify' })
      return
    }
    
    // Get user auth status before making request
    const isUserAuthenticated = await useAuthStore().validateAuth()
    if (!isUserAuthenticated) {
      notify({ 
        type: 'error', 
        message: 'Authentication error. Please log in again.' 
      })
      return
    }
    
    if (store.mode === 'build') {
      // Check for missing required values
      if (!projectId.value) {
        notify({ type: 'error', message: 'No project selected. Please select or create a project first.' })
        return
      }
      
      if (!store.selectedFile) {
        notify({ type: 'warning', message: 'Please select a file to modify' })
        return
      }
      
      // Determine file type for specialized handling
      const fileExtension = store.selectedFile.path.split('.').pop()?.toLowerCase() || ''
      const isCSS = fileExtension === 'css' || store.selectedFile.type === 'css'
      
      // Show loading notification
      notify({ type: 'info', message: isCSS ? 'Generating stylesheet...' : 'Generating code...' })
      
      await generateCodeFromPrompt({
        prompt: prompt.value,
        file: store.selectedFile,
        projectId: projectId.value, // This is guaranteed to be non-null at this point
        modelId: store.selectedModelId as string, // Type assertion since we checked it's not null above
        mode: 'build'
      })
      
      // Show success notification
      notify({ type: 'success', message: isCSS ? 'Stylesheet generated successfully' : 'Code generated successfully' })
    } else {
      // Show loading notification for chat
      notify({ type: 'info', message: 'Connecting with AI...' })
      
      // Add temporary assistant message to show typing
      const assistantMessageId = `assistant-${Date.now()}`
      const assistantMessage = {
        role: 'assistant' as const,
        content: '',
        timestamp: new Date().toISOString(),
        id: assistantMessageId,
        isStreaming: true
      }
      
      // Add temporary message to show loading
      store.conversation.push(assistantMessage)
      
      try {
        // Call the AI service
        const response = await AgentService.processChat(
          projectId.value as string, // Type assertion since we checked it's not null above
          {
            prompt: prompt.value,
            model: store.selectedModelId,
            mode: 'chat',
            file: store.selectedFile
          }
        )
        
        // Find and update the temporary message with the actual response
        const messageIndex = store.conversation.findIndex(msg => msg.id === assistantMessageId)
        
        if (messageIndex !== -1) {
          // Update the message in place
          store.conversation[messageIndex] = {
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString(),
            id: assistantMessageId,
            code: response.messages[1]?.code || null
          }
        } else {
          // If temporary message wasn't found, add the response as a new message
          store.conversation.push({
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString(),
            id: `assistant-response-${Date.now()}`,
            code: response.messages[1]?.code || null
          })
        }

        // Aggressively update balance - Try multiple approaches to ensure balance updates
        const updateBalancePromises = [];
        
        // 1. Get new stores to avoid stale references
        const freshPaymentsStore = usePaymentsStore();
        const freshBalanceStore = useBalanceStore();
        
        // 2. Force balance update using both stores (belt and suspenders approach)
        updateBalancePromises.push(freshPaymentsStore.fetchBalance(false, true));
        updateBalancePromises.push(freshBalanceStore.fetchBalance(true, true));
        
        // Wait for balance updates without blocking UI
        Promise.allSettled(updateBalancePromises)
          .then(results => {
            // Check if any balance fetches failed and retry once more if needed
            const allFailed = results.every(r => r.status === 'rejected');
            if (allFailed) {
              console.warn('Both balance update attempts failed, retrying once more');
              // Try one more time after a short delay
              setTimeout(() => {
                freshBalanceStore.fetchBalance(true, true)
                  .catch(e => console.error('Final balance update attempt failed:', e));
              }, 1000);
            }
          })
          .catch(err => console.warn('Error checking balance update results:', err));
          
      } catch (chatError) {
        // Remove the temporary message if there was an error
        store.conversation = store.conversation.filter(msg => msg.id !== assistantMessageId)
        
        // Even on error, try to update the balance since credits might have been charged
        try {
          const freshBalanceStore = useBalanceStore();
          freshBalanceStore.fetchBalance(false, true)
            .catch(err => console.warn('Failed to refresh balance after chat error:', err));
        } catch (balanceError) {
          console.warn('Failed to initialize balance store after chat error:', balanceError);
        }
        
        throw chatError
      }
    }
    
    // Fetch the updated balance immediately after AI usage
    // This ensures the credits display shows the correct amount
    try {
      // Force update of balance after AI model usage
      const freshPaymentsStore = usePaymentsStore();
      await freshPaymentsStore.fetchBalance(false, true);
    } catch (err) {
      console.warn('Failed to refresh balance after AI usage:', err)
      
      // Try alternative balance update as fallback
      try {
        const freshBalanceStore = useBalanceStore();
        await freshBalanceStore.fetchBalance(false, true);
      } catch (balanceError) {
        console.error('All balance update attempts failed:', balanceError);
      }
    }
    
    // Clear prompt after sending
    prompt.value = ''
  } catch (error) {
    console.error('Error processing prompt:', error)
    
    // Show specific error message if available
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'Error processing your request. Please try again.';
      
    notify({ type: 'error', message: errorMessage })
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
    notify({ type: 'info', message: `Auto-selected file: ${store.files[0].path}` })
  }
  
  // Only add system messages about mode changes if the new mode is chat mode
  // This prevents system messages from appearing in build mode
  if (mode === 'chat' && previousMode !== mode && store.conversation.length > 0) {
    store.conversation.push({
      role: 'system',
      content: `Switched to ${mode} mode${store.selectedFile ? ` for file: ${store.selectedFile.path}` : ''}`,
      timestamp: new Date().toISOString(),
      id: `system-${Date.now()}`
    })
  }
}

async function handleFileSelect(file: ProjectFile) {
  if (store.selectedFile?.path !== file.path) {
    // Remove system messages about file changes completely
    // No longer add file switch notifications to the conversation
    
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
    
    notify({ type: 'success', message: `File ${data.name} created successfully` })
  } catch (error) {
    console.error('Error creating file:', error)
    notify({ type: 'error', message: 'Error creating file. Please try again.' })
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
    
    notify({ type: 'success', message: `File ${file.path} deleted successfully` })
  } catch (error) {
    console.error('Error deleting file:', error)
    notify({ type: 'error', message: 'Error deleting file. Please try again.' })
  }
}

async function handleApplyCode(code: string) {
  if (!store.selectedFile) {
    notify({ type: 'warning', message: 'Please select a file to apply the changes' })
    return
  }
  
  try {
    await applyCode({
      code,
      file: store.selectedFile,
      projectId: projectId.value
    })
    
    notify({ type: 'success', message: 'Code changes applied successfully' })
  } catch (error) {
    console.error('Error applying code:', error)
    notify({ type: 'error', message: 'Error applying code changes. Please try again.' })
  }
}

async function handleUndo() {
  if (!store.selectedFile) {
    notify({ type: 'warning', message: 'Please select a file to undo changes' })
    return
  }
  
  try {
    store.setProcessing(true)
    
    const result = await AgentService.undoAction(
      projectId.value,
      store.selectedFile.path
    )
    
    if (result.success) {
      // Refresh the file content after undo
      const updatedContent = await FileService.getFileContent(
        projectId.value, 
        store.selectedFile.path
      )
      
      // Update the file in the store
      if (store.selectedFile) {
        store.setSelectedFile({
          ...store.selectedFile,
          content: updatedContent
        })
      }
      
      // Remove the last two messages from the conversation (user and assistant)
      if (store.conversation.length >= 2) {
        // Create a new array with all but the last two messages
        const newConversation = store.conversation.slice(0, -2)
        // Use $patch to update the conversation state
        store.$patch({ conversation: newConversation })
      }
      
      notify({ 
        type: 'success', 
        message: result.message || 'Successfully undid the last AI interaction'
      })
    } else {
      notify({ 
        type: 'error', 
        message: result.message || 'Failed to undo the last AI interaction'
      })
    }
  } catch (error) {
    console.error('Error undoing last interaction:', error)
    notify({ 
      type: 'error', 
      message: 'Error undoing the last AI interaction. Please try again.'
    })
  } finally {
    store.setProcessing(false)
  }
}

async function handlePreview() {
  try {
    if (!projectId.value) {
      notify({ type: 'warning', message: 'Project ID is required' })
      return
    }

    notify({ type: 'info', message: 'Starting preview server...' })
    const response = await AgentService.generatePreview(projectId.value)
    
    if (response && response.previewUrl) {
      // Open the preview URL in a new tab
      window.open(response.previewUrl, '_blank')
      notify({ type: 'success', message: 'Preview server started successfully' })
    } else {
      notify({ type: 'error', message: 'Failed to start preview server' })
    }
  } catch (error) {
    console.error('Error starting preview server:', error)
    notify({ type: 'error', message: 'Error starting preview server. Please try again.' })
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
    notify({ type: 'error', message: 'Error loading project files' })
    return []
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Get project ID from route params
  projectId.value = String(route.params.projectId)
  
  try {
    // Get stores for easier access
    const paymentsStore = usePaymentsStore();
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
      notify({ type: 'error', message: 'Error loading project' });
    }
  } catch (error) {
    console.error('Error initializing workspace:', error);
    notify({ type: 'error', message: 'Error loading project. Please try again.' });
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