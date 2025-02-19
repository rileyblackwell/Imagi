<template>
  <ErrorBoundary>
    <BuilderLayout 
      storage-key="builderWorkspaceSidebarCollapsed"
    >
      <!-- Sidebar Content -->
      <template #sidebar-content="{ collapsed }">
        <BuilderSidebar
          :current-project="currentProject"
          :models="store.availableModels"
          :model-id="store.selectedModelId"
          :selected-file="store.selectedFile"
          :is-loading="store.isProcessing"
          :mode="store.mode"
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
        <div class="relative h-full">
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
                <ChatConversation :messages="store.conversation" />
              </div>
              <div v-else class="flex-1 flex overflow-hidden">
                <BuilderEditor
                  v-model="editorContent"
                  :file="store.selectedFile"
                  :editor-mode="currentEditorMode"
                  @change="handleEditorChange"
                  @save="handleSave"
                />
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
                :mode="store.mode"
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
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useBuilderStore } from '../stores/builderStore'
import { useBuilder } from '../composables/useBuilder'
import { useChat } from '../composables/useChat'
import { useAI } from '../composables/useAI'
import { useFileManager } from '../composables/useFileManager'
import { useProjectStore } from '../stores/projectStore'
import ErrorBoundary from '@/shared/components/atoms/ErrorBoundary.vue'
import AppShortcuts from '@/shared/components/atoms/AppShortcuts.vue'
import SessionTimeoutWarning from '@/shared/components/molecules/SessionTimeoutWarning.vue'
import LoadingOverlay from '../components/atoms/LoadingOverlay.vue'
import { notify } from '@/shared/utils'
import type { Project } from '../types'
import type { EditorMode } from '../types/builder'

const route = useRoute()
const store = useBuilderStore()
const projectStore = useProjectStore()
const { generateCodeFromPrompt, updateFile, createFile } = useBuilder()
const { sendMessage } = useChat()
const { loadModels } = useAI()
const { autosaveContent, saveFile, checkUnsavedChanges } = useFileManager()

// Local state
const currentEditorMode = ref<EditorMode>('split')
const prompt = ref('')
const editorContent = ref('')
const sidebarCollapsed = ref(false)
const sessionTimeoutWarning = ref(false)
const sessionCheckInterval = ref<number>()

// Computed properties
const currentProject = computed(() => projectStore.currentProject)

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
  store.selectModel(modelId)
}

const handleModeSwitch = (mode: 'chat' | 'build') => {
  store.setMode(mode)
}

const handleFileSelect = (file: any) => {
  store.selectFile(file)
}

const handleFileCreate = async (name: string, type: string) => {
  try {
    await createFile(name, type)
    notify({ type: 'success', message: 'File created successfully' })
  } catch (err: any) {
    notify({ type: 'error', message: err.message || 'Failed to create file' })
  }
}

const handleUndo = async () => {
  // Implement undo functionality
}

const handlePreview = () => {
  // Implement preview functionality
}

// Handle prompt submission
const handlePrompt = async () => {
  if (!prompt.value.trim() || store.isProcessing) return
  
  const originalPrompt = prompt.value
  prompt.value = '' // Clear prompt immediately for better UX
  
  try {
    if (store.mode === 'chat') {
      await sendMessage(originalPrompt)
    } else {
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
  try {
    const response = await fetch('/api/v1/auth/session-status/')
    const data = await response.json()
    sessionTimeoutWarning.value = data.expiresIn < 300 // Show warning when less than 5 minutes remain
  } catch (err) {
    console.error('Failed to check session status:', err)
  }
}

const refreshSession = async () => {
  try {
    await fetch('/api/v1/auth/refresh-session/', { method: 'POST' })
    sessionTimeoutWarning.value = false
    notify({ type: 'success', message: 'Session refreshed successfully' })
  } catch (err) {
    notify({ type: 'error', message: 'Failed to refresh session' })
  }
}

// Initialize workspace
onMounted(async () => {
  window.addEventListener('beforeunload', handleBeforeUnload)
  try {
    await loadModels()
  } catch (err: any) {
    notify({ 
      type: 'error', 
      message: err.message || 'Failed to load AI models' 
    })
  }

  // Start session check interval
  sessionCheckInterval.value = window.setInterval(checkSession, 60000) // Check every minute
})

onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', handleBeforeUnload)
  if (sessionCheckInterval.value) {
    clearInterval(sessionCheckInterval.value)
  }
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