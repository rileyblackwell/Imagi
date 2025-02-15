<template>
  <BuilderLayout 
    storage-key="builderWorkspaceSidebarCollapsed"
  >
    <!-- Sidebar Content -->
    <template #sidebar-content="{ collapsed }">
      <BuilderSidebar
        :current-project="currentProject"
        :models="typedModels"
        :model-id="selectedModel"
        :files="typedFiles"
        :selected-file="typedSelectedFile"
        :file-types="FILE_TYPES"
        :is-loading="isLoading"
        :mode="builderMode"
        :current-editor-mode="currentEditorMode"
        :is-collapsed="collapsed"
        @update:model-id="selectedModel = $event"
        @update:mode="switchMode"
        @select-file="selectFile"
        @create-file="handleCreateFile"
        @undo="undoLastAction"
        @preview="handlePreview"
      />
    </template>

    <template #default="{ collapsed }">
      <!-- Main Content -->
      <div class="h-[calc(100vh-4rem)] flex flex-col"> <!-- Adjust height to account for navbar -->
        <!-- Split View -->
        <div v-if="typedSelectedFile" class="flex-1 flex overflow-hidden"> <!-- Add overflow-hidden -->
          <!-- Editor Section -->
          <div class="flex flex-col overflow-hidden h-full" :class="{
            'w-1/2': currentEditorMode === 'split',
            'w-full': currentEditorMode === 'editor',
            'hidden': currentEditorMode === 'preview'
          }">
            <WorkspaceToolbar
              :title="typedSelectedFile.path"
              :subtitle="`Project: ${currentProject?.name}`"
              :has-unsaved-changes="hasUnsavedChanges"
              :loading="isLoading"
              :show-save="true"
              :current-mode="currentEditorMode"
              class="flex-shrink-0"
              @save="saveChanges"
              @mode-change="setMode"
            />
            
            <div class="flex-1 overflow-hidden p-4">
              <WorkspaceEditor
                v-model="editorContent"
                placeholder="Enter code here..."
                wrap="off"
                class="h-full overflow-auto rounded-lg bg-dark-900/50"
              />
            </div>
          </div>

          <!-- Preview Section -->
          <div class="flex flex-col overflow-hidden h-full" :class="{
            'w-1/2': currentEditorMode === 'split',
            'w-full': currentEditorMode === 'preview',
            'hidden': currentEditorMode === 'editor'
          }">
            <WorkspacePreview
              v-if="previewUrl && projectId"
              :project-id="projectId"
              :preview-url="previewUrl"
              class="flex-1 overflow-auto"
              @load="handlePreviewLoad"
            />
          </div>
        </div>

        <!-- Welcome Screen -->
        <div v-else class="flex-1 flex items-center justify-center p-8 overflow-auto">
          <div class="max-w-lg w-full">
            <div class="text-center space-y-6">
              <div class="w-20 h-20 bg-primary-500/10 rounded-full flex items-center justify-center mx-auto">
                <i class="fas fa-code text-3xl text-primary-400"></i>
              </div>
              <div>
                <h2 class="text-2xl font-semibold text-white mb-3">Welcome to Imagi Builder</h2>
                <p class="text-gray-400 text-lg leading-relaxed mb-8">
                  Choose a file from the sidebar to start editing, or describe what you want to build using natural language.
                </p>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <button
                  @click="showNewFileForm = true"
                  class="flex items-center justify-center px-6 py-4 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors group"
                >
                  <i class="fas fa-plus mr-3 text-primary-400 group-hover:text-primary-300"></i>
                  Create New File
                </button>
                <button
                  @click="focusPrompt"
                  class="flex items-center justify-center px-6 py-4 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors group"
                >
                  <i class="fas fa-magic mr-3 group-hover:text-white/90"></i>
                  Start Building
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Chat Input -->
        <div class="shrink-0 p-4 border-t border-dark-800 bg-dark-900/50 backdrop-blur-sm">
          <AIPromptInput
            v-model="prompt"
            :loading="isLoading"
            @submit="handlePrompt"
          />
        </div>
      </div>
    </template>
  </BuilderLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Ref } from 'vue'
import { useRoute } from 'vue-router'
import { BuilderLayout } from '../layouts'
import { WorkspaceEditor, WorkspaceToolbar, WorkspacePreview, BuilderSidebar } from '../components/organisms'
import { AIPromptInput } from '../components/molecules'
import { useBuilder } from '../composables/useBuilder'
import { useAI } from '../composables/useAI'
import type { EditorLanguage } from '@/shared/types/editor'
import type { AIModel, ProjectFile, BuilderMode, EditorMode } from '../types/builder'

// Setup route and state
const route = useRoute()
const currentEditorMode = ref<EditorMode>('split')
const builderMode = ref<BuilderMode>('chat')
const previewUrl = ref<string>('')

// Add sidebarCollapsed state
const sidebarCollapsed = ref(false)

// Initialize composables
const {
  currentProject,
  availableModels,
  selectedModel,
  isLoading,
  error,
  files,
  selectedFile,
  fileContent,
  hasUnsavedChanges,
  componentTree,
  loadProject,
  loadFiles,
  selectFile,
  updateFile,
  createFile,
  generateCode,
  loadAvailableModels,
  loadComponentTree,
  undoLastAction,
  FILE_TYPES
} = useBuilder()

const { sendPrompt, fetchConversationHistory } = useAI()

// Local state
const prompt = ref('')
const showNewFileForm = ref(false)
const newFileName = ref('')
const newFileType = ref<EditorLanguage | undefined>()
const isFileExplorerExpanded = ref(true)
const editorContent = ref('')

// Type assertions for reactive refs
const typedFiles = files as Ref<ProjectFile[]>
const typedSelectedFile = selectedFile as Ref<ProjectFile | null>
const typedModels = availableModels as Ref<AIModel[]>

// Computed properties
const projectId = computed(() => currentProject.value?.id?.toString() || '')
const canCreateFile = computed(() => newFileName.value.trim() && newFileType.value)

// Methods
const handlePrompt = async () => {
  if (!prompt.value.trim() || isLoading.value) return

  try {
    const response = await sendPrompt({
      prompt: prompt.value,
      mode: builderMode.value,
      context: selectedFile.value?.path || ''
    })

    if (response.code) {
      editorContent.value = response.code
    }
    prompt.value = ''
  } catch (err) {
    console.error('Error handling prompt:', err)
  }
}

// Add return type for file icon mapping
const getFileIcon = (type: EditorLanguage): string => {
  const icons: Record<EditorLanguage, string> = {
    html: 'fas fa-code',
    css: 'fab fa-css3',
    javascript: 'fab fa-js',
    typescript: 'fab fa-ts',
    python: 'fab fa-python',
    markdown: 'fas fa-file-alt',
    text: 'fas fa-file-alt'
  }
  return icons[type] || 'fas fa-file'
}

// Watch for file content changes
watch(fileContent, (newContent: string) => {
  if (newContent !== editorContent.value) {
    editorContent.value = newContent
  }
})

// Load initial data
watch(() => route.params.projectId, async (newId) => {
  const projectId = Array.isArray(newId) ? newId[0] : newId
  if (projectId) {
    await loadProject(projectId)
    await Promise.all([
      loadComponentTree(),
      loadAvailableModels(),
      fetchConversationHistory(projectId)
    ])
  }
}, { immediate: true })

const onEditorChange = (content: string) => {
  if (content !== fileContent.value) {
    hasUnsavedChanges.value = true
  }
}

const saveChanges = async () => {
  if (hasUnsavedChanges.value) {
    await updateFile(editorContent.value)
    hasUnsavedChanges.value = false
  }
}

const handleCreateFile = async () => {
  if (!canCreateFile.value || !newFileType.value) return

  try {
    await createFile(newFileName.value.trim(), newFileType.value)
    // Reset form
    newFileName.value = ''
    newFileType.value = undefined
    showNewFileForm.value = false
  } catch (err) {
    console.error('Error creating file:', err)
  }
}

// Mode management methods
const setMode = (mode: EditorMode) => {
  currentEditorMode.value = mode
}

const switchMode = (mode: BuilderMode) => {
  builderMode.value = mode
}

const handlePreviewLoad = () => {
  console.log('Preview loaded')
}

const focusPrompt = () => {
  const promptInput = document.querySelector('#user-input')
  if (promptInput instanceof HTMLElement) {
    promptInput.focus()
  }
}

const handlePreview = () => {
  if (currentEditorMode.value === 'preview') {
    currentEditorMode.value = 'split'
  } else {
    currentEditorMode.value = 'preview'
  }
}

onMounted(async () => {
  const projectId = Array.isArray(route.params.projectId) 
    ? route.params.projectId[0] 
    : route.params.projectId
  if (projectId) {
    await loadProject(projectId)
    await loadComponentTree()
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