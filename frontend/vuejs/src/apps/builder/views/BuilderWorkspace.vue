<template>
  <BuilderLayout storage-key="builderWorkspaceSidebarCollapsed">
    <template #sidebar-content>
      <!-- Project Header -->
      <div class="p-4 border-b border-dark-700">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-white truncate">{{ currentProject?.name }}</h2>
          <router-link
            :to="{ name: 'builder-dashboard' }"
            class="text-gray-400 hover:text-white"
            title="Back to projects"
          >
            <i class="fas fa-times"></i>
          </router-link>
        </div>
      </div>

      <!-- Model Selection -->
      <div class="p-4 border-b border-dark-700">
        <label class="block text-sm font-medium text-gray-400 mb-2">AI Model</label>
        <select
          v-model="selectedModel"
          class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2"
        >
          <option
            v-for="model in availableModels"
            :key="model.id"
            :value="model.id"
          >
            {{ model.name }}
          </option>
        </select>
      </div>

      <!-- Mode Toggle -->
      <div class="p-4 border-b border-dark-700">
        <label class="block text-sm font-medium text-gray-400 mb-2">Mode</label>
        <div class="flex bg-dark-900 rounded-lg p-1">
          <button
            @click="switchMode('chat')"
            class="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            :class="[
              currentMode === 'chat'
                ? 'bg-primary-500 text-white'
                : 'text-gray-400 hover:text-white'
            ]"
          >
            <i class="fas fa-comments mr-2"></i>
            Chat
          </button>
          <button
            @click="switchMode('build')"
            class="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors"
            :class="[
              currentMode === 'build'
                ? 'bg-primary-500 text-white'
                : 'text-gray-400 hover:text-white'
            ]"
          >
            <i class="fas fa-code mr-2"></i>
            Build
          </button>
        </div>
      </div>

      <!-- File Explorer -->
      <div class="flex-1 overflow-y-auto">
        <div class="p-4 border-b border-dark-700">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-sm font-medium text-gray-400">Project Files</h3>
            <button
              @click="showNewFileForm = !showNewFileForm"
              class="text-gray-400 hover:text-white transition-colors"
              :title="showNewFileForm ? 'Cancel' : 'New File'"
            >
              <i :class="['fas', showNewFileForm ? 'fa-times' : 'fa-plus']"></i>
            </button>
          </div>

          <!-- New File Form -->
          <div v-if="showNewFileForm" class="mb-4 space-y-3">
            <input
              v-model="newFileName"
              type="text"
              placeholder="File name"
              class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
            />
            <select
              v-model="newFileType"
              class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm focus:outline-none focus:border-primary-500"
            >
              <option value="" disabled>Select file type</option>
              <option v-for="(type, key) in FILE_TYPES" :key="key" :value="type">
                {{ key.toLowerCase() }}
              </option>
            </select>
            <div class="flex justify-end space-x-2">
              <button
                @click="showNewFileForm = false"
                class="px-3 py-1 text-sm text-gray-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                @click="handleCreateFile"
                :disabled="!canCreateFile"
                class="px-3 py-1 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Create
              </button>
            </div>
          </div>
          
          <div v-show="isFileExplorerExpanded" class="space-y-1">
            <button
              v-for="file in files"
              :key="file.path"
              @click="selectFile(file)"
              class="w-full text-left px-3 py-2 rounded-lg text-sm flex items-center group transition-colors"
              :class="[
                selectedFile?.path === file.path
                  ? 'bg-primary-500/20 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              ]"
            >
              <i :class="[getFileIcon(file.type), 'mr-2']"></i>
              <span class="truncate">{{ file.path }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="p-4 border-t border-dark-700">
        <button
          @click="undoLastAction"
          class="w-full flex items-center justify-center px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="isLoading"
        >
          <i class="fas fa-undo mr-2"></i>
          Undo
        </button>
      </div>
    </template>

    <!-- File Explorer Toggle Button -->
    <template #sidebar-bottom>
      <div class="p-4">
        <button
          @click="isFileExplorerExpanded = !isFileExplorerExpanded"
          class="w-full flex items-center justify-center px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg"
        >
          <i :class="[
            'fas',
            isFileExplorerExpanded ? 'fa-chevron-down' : 'fa-chevron-right'
          ]"></i>
          <span class="ml-2">{{ isFileExplorerExpanded ? 'Collapse' : 'Expand' }} Files</span>
        </button>
      </div>
    </template>

    <div class="min-h-screen flex">
      <!-- Main Content -->
      <main class="flex-1 flex flex-col">
        <!-- File Content -->
        <div v-if="selectedFile" class="flex-1 p-4">
          <WorkspaceToolbar
            :title="selectedFile.path"
            :subtitle="`Project: ${currentProject?.name}`"
            :unsaved-changes="hasUnsavedChanges"
            :loading="isLoading"
            :show-save="true"
            @save="saveChanges"
          />
          
          <WorkspaceEditor
            v-model="editorContent"
            placeholder="Enter code here..."
            wrap="off"
            class="mt-4"
          />
        </div>

        <!-- Welcome Screen -->
        <div v-else class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <i class="fas fa-code text-2xl text-primary-400"></i>
            </div>
            <h2 class="text-xl font-semibold text-white mb-2">Select a File</h2>
            <p class="text-gray-400">Choose a file from the sidebar to start editing</p>
          </div>
        </div>

        <!-- AI Chat Input -->
        <div class="p-4 border-t border-dark-700">
          <div class="flex items-center space-x-4">
            <input
              v-model="prompt"
              type="text"
              placeholder="Describe what you want to build..."
              class="flex-1 bg-dark-900 border border-dark-600 rounded-lg text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              @keyup.enter="handlePrompt"
            >
            <button
              @click="handlePrompt"
              class="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isLoading || !prompt.trim()"
            >
              <i class="fas fa-magic mr-2"></i>
              Generate
            </button>
          </div>
        </div>
      </main>
    </div>
  </BuilderLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Ref } from 'vue'
import { useRoute } from 'vue-router'
import { BuilderLayout } from '../layouts'
import { WorkspaceEditor, WorkspaceToolbar } from '../components/organisms/workspace'
import { useBuilder } from '../composables/useBuilder'
import type { EditorLanguage } from '@/shared/types/editor'
import type { Project } from '@/shared/types/project'

// Setup route
const route = useRoute()

interface ProjectFile {
  path: string
  type: EditorLanguage
  content: string
}

// Update FILE_TYPES to include all EditorLanguage values
const FILE_TYPES = {
  HTML: 'html' as const,
  CSS: 'css' as const,
  JAVASCRIPT: 'javascript' as const,
  TYPESCRIPT: 'typescript' as const,
  PYTHON: 'python' as const,
  MARKDOWN: 'markdown' as const,
  TEXT: 'text' as const
} as const

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

// Type the builder composable return values
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
  currentMode,
  aiGenerating,
  componentTree,
  selectedComponent,
  loadProject,
  loadFiles,
  selectFile,
  updateFile,
  createFile,
  generateCode,
  undoLastAction,
  loadAvailableModels,
  loadComponentTree,
  switchMode
} = useBuilder() as {
  currentProject: Ref<Project | null>
  availableModels: Ref<Array<{ id: string; name: string }>>
  selectedModel: Ref<string | null>
  isLoading: Ref<boolean>
  error: Ref<string | null>
  files: Ref<ProjectFile[]>
  selectedFile: Ref<ProjectFile | null>
  fileContent: Ref<string>
  hasUnsavedChanges: Ref<boolean>
  currentMode: Ref<'chat' | 'build'>
  aiGenerating: Ref<boolean>
  componentTree: Ref<any> // Replace with proper type
  selectedComponent: Ref<any> // Replace with proper type
  loadProject: (id: string) => Promise<void>
  loadFiles: () => Promise<void>
  selectFile: (file: ProjectFile) => void
  updateFile: (content: string) => Promise<void>
  createFile: (name: string, type: EditorLanguage) => Promise<void>
  generateCode: (prompt: string) => Promise<string>
  undoLastAction: () => Promise<void>
  loadAvailableModels: () => Promise<void>
  loadComponentTree: () => Promise<void>
  switchMode: (mode: 'chat' | 'build') => void
}

// Add type annotations to local state
const prompt = ref('')
const showNewFileForm = ref(false)
const newFileName = ref('')
const newFileType = ref<EditorLanguage | undefined>()
const isFileExplorerExpanded = ref(true)
const editorContent = ref('')

const canCreateFile = computed(() => {
  return newFileName.value.trim() && newFileType.value
})

watch(fileContent, (newContent: string) => {
  if (newContent !== editorContent.value) {
    editorContent.value = newContent
  }
})

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

const handlePrompt = async () => {
  if (!prompt.value.trim() || isLoading.value) return

  try {
    const generatedCode = await generateCode(prompt.value)
    editorContent.value = generatedCode
    prompt.value = ''
  } catch (err) {
    console.error('Error handling prompt:', err)
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

// Load project data when component mounts or route changes
watch(() => route.params.projectId, async (newId) => {
  const projectId = Array.isArray(newId) ? newId[0] : newId
  if (projectId) {
    await loadProject(projectId)
    await loadComponentTree()
  }
}, { immediate: true })

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