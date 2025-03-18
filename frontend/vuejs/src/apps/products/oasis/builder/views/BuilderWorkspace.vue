<!--
  BuilderWorkspace.vue - Project Editing Interface
  
  This component is responsible for:
  1. Loading an existing project's files and data
  2. Supporting chat & build modes for AI interaction
  3. Editing project files through AI assistance
-->
<template>
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
      <WorkspaceChat
        :messages="ensureValidMessages(store.conversation || [])"
        :is-processing="store.isProcessing"
        :mode="store.mode || 'chat'"
        :selected-file="store.selectedFile"
        :selected-model-id="store.selectedModelId"
        :available-models="store.availableModels || []"
        :prompt-placeholder="promptPlaceholder"
        :show-examples="store.conversation.length === 0"
        :prompt-examples="promptExamplesComputed"
        v-model="prompt"
        @submit="handlePrompt"
        @use-example="handleExamplePrompt"
        @apply-code="handleApplyCode"
      />
    </div>
  </BuilderLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import { useChatMode } from '../composables/useChatMode'
import { useProjectStore } from '../stores/projectStore'
import { AgentService } from '../services/agentService'
import { ProjectService } from '../services/projectService'
import { FileService } from '../services/fileService'
import { useAuthStore } from '@/shared/stores/auth'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import BuilderSidebar from '../components/organisms/sidebar/BuilderSidebar.vue'

// Atomic Components
import { WorkspaceChat } from '../components/organisms/workspace'

// Utils
import { notify } from '@/shared/utils'
import type { ProjectFile, EditorMode, BuilderMode } from '../types/builder'
import type { AIMessage } from '../types/index'

const route = useRoute()
const router = useRouter()
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
const navigationItems = [] // Empty array to remove sidebar navigation buttons

// Project examples for different modes
const chatExamples = [
  {
    title: 'Project Analysis',
    text: 'Can you analyze my current project structure and suggest improvements?'
  },
  {
    title: 'Code Explanation',
    text: 'Can you explain how the routing works in this application?'
  },
  {
    title: 'Feature Ideas',
    text: 'What features would make this application more user-friendly?'
  },
  {
    title: 'Technical Help',
    text: 'I\'m getting an error with Vue reactivity. How can I debug this?'
  }
]

// Empty build examples to remove them from the UI
const buildExamples = []

// Computed properties
const currentProject = computed(() => {
  return projectStore.currentProject || null
})

const promptExamplesComputed = computed(() => {
  if (store.mode === 'chat') {
    return chatExamples
  } else {
    return buildExamples
  }
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
  if (!messages || !Array.isArray(messages)) return []
  
  return messages
    .filter(m => m && typeof m === 'object' && m.role && m.content)
    .map(m => ({
      role: m.role,
      content: m.content,
      code: m.code || '',
      timestamp: m.timestamp || Date.now(),
      id: m.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    })) as AIMessage[]
}

async function handlePrompt() {
  if (!prompt.value.trim()) return
  
  try {
    if (store.mode === 'build') {
      if (!store.selectedFile) {
        notify('Please select a file to modify', 'warning')
        return
      }
      
      if (!store.selectedModelId) {
        notify('Please select an AI model', 'warning')
        return
      }
      
      await generateCodeFromPrompt({
        prompt: prompt.value,
        file: store.selectedFile,
        projectId: projectId.value,
        modelId: store.selectedModelId
      })
    } else {
      await sendMessage({
        prompt: prompt.value,
        projectId: projectId.value,
        file: store.selectedFile,
        modelId: store.selectedModelId
      })
    }
    
    // Clear prompt after sending
    prompt.value = ''
  } catch (error) {
    console.error('Error processing prompt:', error)
    notify('Error processing your request. Please try again.', 'error')
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
  store.setMode(mode)
}

async function handleFileSelect(file: ProjectFile) {
  store.setSelectedFile(file)
}

async function handleFileCreate(data: { name: string; type: string; content?: string }) {
  try {
    await createFile({
      projectId: projectId.value,
      ...data
    })
    
    // Refresh file list after creating a new file
    await loadProjectFiles()
    
    notify(`File ${data.name} created successfully`, 'success')
  } catch (error) {
    console.error('Error creating file:', error)
    notify('Error creating file. Please try again.', 'error')
  }
}

async function handleFileDelete(file: ProjectFile) {
  try {
    await FileService.deleteFile(projectId.value, file.id || file.path)
    
    // Remove file from store
    store.removeFile(file)
    
    // If the deleted file was selected, clear selection
    if (store.selectedFile && store.selectedFile.path === file.path) {
      store.setSelectedFile(null)
    }
    
    notify(`File ${file.path} deleted successfully`, 'success')
  } catch (error) {
    console.error('Error deleting file:', error)
    notify('Error deleting file. Please try again.', 'error')
  }
}

async function handleApplyCode(code: string) {
  if (!store.selectedFile) {
    notify('Please select a file to apply the changes', 'warning')
    return
  }
  
  try {
    await applyCode({
      code,
      file: store.selectedFile,
      projectId: projectId.value
    })
    
    notify('Code changes applied successfully', 'success')
  } catch (error) {
    console.error('Error applying code:', error)
    notify('Error applying code changes. Please try again.', 'error')
  }
}

async function handleUndo() {
  // Implement undo functionality
  notify('Undo feature coming soon', 'info')
}

async function handlePreview() {
  // Implement preview functionality
  notify('Preview feature coming soon', 'info')
}

// Helper function to load project files
async function loadProjectFiles() {
  try {
    const files = await FileService.getProjectFiles(projectId.value)
    if (Array.isArray(files)) {
      // Directly update the store with the files array
      store.$patch({
        files: files
      })
      // Or use setFiles if available
      if (typeof store.setFiles === 'function') {
        store.setFiles(files)
      }
    } else {
      console.error('Project files data is not an array:', files)
    }
  } catch (error) {
    console.error('Error loading project files:', error)
    notify('Error loading project files', 'error')
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Get project ID from route params
  projectId.value = String(route.params.projectId)
  
  try {
    // Load project data
    await projectStore.fetchProject(projectId.value)
    
    // Set project ID in store if needed
    if (typeof store.setProjectId === 'function') {
      store.setProjectId(projectId.value)
    }
    
    // Load project files using dedicated function
    await loadProjectFiles()
    
    // Load available AI models
    await loadModels()
      
    // Set default model if not already set
    if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
      const defaultModel = store.availableModels.find(m => m.id === 'claude-3-5-sonnet-20241022') || store.availableModels[0]
      if (defaultModel) {
        store.setSelectedModelId(defaultModel.id)
      }
    }
    
    // Initialize mode if not set
    if (!store.mode) {
      store.setMode('chat')
    }
  } catch (error) {
    console.error('Error initializing workspace:', error)
    notify('Error loading project. Please try again.', 'error')
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