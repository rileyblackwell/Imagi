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
      />
    </template>

    <!-- Main Content Area -->
    <template #main-content>
      <div class="flex flex-col h-full w-full bg-gray-50 dark:bg-gray-900">
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
        />
      </div>
    </template>
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
  loadModels
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

const buildExamples = [
  {
    title: 'Add Feature',
    text: 'Add a toggle switch component that can be used to enable/disable features'
  },
  {
    title: 'Fix Layout',
    text: 'Fix the responsive layout so it works better on mobile devices'
  },
  {
    title: 'Improve Style',
    text: 'Make this component look more modern and professional'
  },
  {
    title: 'Add Functionality',
    text: 'Add form validation to this component'
  }
]

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
  // Filter out invalid messages and ensure they have all required properties
  return messages
    .filter(m => m && (m.role === 'user' || m.role === 'assistant') && m.content)
    .map(m => ({
      role: m.role,
      content: m.content,
      code: m.code || '',
      timestamp: m.timestamp || new Date().toISOString()
    }))
}

// Event handlers
async function handlePrompt() {
  if (!prompt.value || store.isProcessing) return
  
  try {
    const promptText = prompt.value
    prompt.value = '' // Clear input field immediately
    
    if (store.mode === 'chat') {
      // Handle chat mode
      await sendMessage(promptText)
    } else {
      // Handle build mode
      if (!store.selectedFile) {
        notify({ 
          type: 'error', 
          message: 'Please select a file to edit' 
        })
        return
      }
      
      await generateCodeFromPrompt(promptText)
    }
  } catch (error: any) {
    notify({ 
      type: 'error', 
      message: error.message || 'Failed to process your request' 
    })
  }
}

function handleExamplePrompt(examplePrompt: string) {
  prompt.value = examplePrompt
  handlePrompt()
}

function handleModelSelect(modelId: string) {
  store.selectModel(modelId)
}

function handleModeSwitch(mode: BuilderMode) {
  store.setMode(mode)
}

async function handleFileSelect(file: ProjectFile) {
  try {
    store.selectFile(file)
  } catch (error: any) {
    notify({ 
      type: 'error', 
      message: error.message || 'Failed to select file'
    })
  }
}

async function handleFileCreate(data: { name: string, type: string, content?: string }) {
  try {
    const newFile = await createFile(data.name, data.type, data.content || '')
    
    if (newFile) {
      // Select the newly created file
      store.selectFile(newFile)
    }
  } catch (error: any) {
    notify({ 
      type: 'error', 
      message: error.message || 'Failed to create file'
    })
  }
}

async function handleFileDelete(file: ProjectFile) {
  try {
    await FileService.deleteFile(projectId.value, file.path)
    
    // Refresh files
    const files = await FileService.getProjectFiles(projectId.value)
    // Fix the type issue by using the functional update pattern
    store.$patch((state) => {
      state.files = files as any // Type assertion for compatibility
    })
    
    // Deselect file if it was selected
    if (store.selectedFile?.path === file.path) {
      store.selectFile(null)
    }
    
    notify({ 
      type: 'success', 
      message: `File ${file.path} deleted successfully`
    })
  } catch (error: any) {
    notify({ 
      type: 'error', 
      message: error.message || 'Failed to delete file'
    })
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Get project ID from route params
  projectId.value = route.params.projectId as string
  
  if (!projectId.value) {
    notify({ 
      type: 'error', 
      message: 'No project ID provided'
    })
    return
  }
  
  // Set project ID in store
  store.setProjectId(projectId.value)
  
  try {
    // Load models
    await loadModels()
    
    // Load project data
    await projectStore.fetchProject(projectId.value)
    
    // Load project files
    const files = await FileService.getProjectFiles(projectId.value)
    // Fix the type issue by using the functional update pattern
    store.$patch((state) => {
      state.files = files as any // Type assertion for compatibility
    })
    
    // Initialize with default mode
    if (!store.mode) {
      store.setMode('chat')
    }
  } catch (error: any) {
    notify({ 
      type: 'error', 
      message: error.message || 'Failed to load project data'
    })
  }
})

// Clean up when component is destroyed
onBeforeUnmount(() => {
  // No cleanup needed since we removed the editor
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