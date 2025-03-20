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
const navigationItems: any[] = [] // Empty array to remove sidebar navigation buttons

// Project examples for different modes
interface PromptExample {
  title: string;
  text: string;
}

const chatExamples: PromptExample[] = []
const buildExamples: PromptExample[] = []

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
  // console.log('BuilderWorkspace: Ensuring valid messages, received:', messages)
  
  if (!messages || !Array.isArray(messages)) {
    // console.log('BuilderWorkspace: No valid messages array received')
    return []
  }
  
  const validMessages = messages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => {
      // Ensure content is a valid string
      let content = m.content || '';
      
      // If content ends with ellipsis from console.log truncation, use the original
      if (typeof content === 'string' && content.includes('…')) {
        // console.log('BuilderWorkspace: Found truncated content in message, working with full content');
      }
      
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
  
  // console.log('BuilderWorkspace: Processed valid messages:', validMessages)
  return validMessages
}

async function handlePrompt() {
  if (!prompt.value.trim()) return
  
  try {
    if (store.mode === 'build') {
      if (!store.selectedFile) {
        notify({ type: 'warning', message: 'Please select a file to modify' })
        return
      }
      
      if (!store.selectedModelId) {
        notify({ type: 'warning', message: 'Please select an AI model' })
        return
      }
      
      await generateCodeFromPrompt({
        prompt: prompt.value,
        file: store.selectedFile,
        projectId: projectId.value,
        modelId: store.selectedModelId
      })
    } else {
      if (!store.selectedModelId) {
        notify({ type: 'warning', message: 'Please select an AI model' })
        return
      }
      
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
    notify({ type: 'error', message: 'Error processing your request. Please try again.' })
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
  // Implement undo functionality
  notify({ type: 'info', message: 'Undo feature coming soon' })
}

async function handlePreview() {
  // Implement preview functionality
  notify({ type: 'info', message: 'Preview feature coming soon' })
}

// Helper function to load project files
async function loadProjectFiles() {
  try {
    const files = await FileService.getProjectFiles(projectId.value)
    if (Array.isArray(files)) {
      // Use the setFiles method to avoid type issues with $patch
      if (typeof store.setFiles === 'function') {
        // Cast the files to the expected type if needed
        store.setFiles(files as any)
      } else {
        console.error('setFiles method not available on store')
      }
    } else {
      console.error('Project files data is not an array:', files)
    }
  } catch (error) {
    console.error('Error loading project files:', error)
    notify({ type: 'error', message: 'Error loading project files' })
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
    notify({ type: 'error', message: 'Error loading project. Please try again.' })
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