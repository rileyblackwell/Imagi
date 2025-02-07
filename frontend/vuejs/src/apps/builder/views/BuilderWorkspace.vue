<template>
  <DashboardLayout 
    :navigation-items="navigationItems" 
    storage-key="builderWorkspaceSidebarCollapsed"
  >
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
            <div class="flex items-center space-x-2">
              <button
                @click="showNewFileForm = !showNewFileForm"
                class="text-gray-400 hover:text-white transition-colors"
                :title="showNewFileForm ? 'Cancel' : 'New File'"
              >
                <i :class="['fas', showNewFileForm ? 'fa-times' : 'fa-plus']"></i>
              </button>
              <button
                @click="isFileExplorerExpanded = !isFileExplorerExpanded"
                class="text-gray-400 hover:text-white transition-colors"
              >
                <i :class="[
                  'fas',
                  isFileExplorerExpanded ? 'fa-chevron-down' : 'fa-chevron-right'
                ]"></i>
              </button>
            </div>
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
      <div class="p-4 border-t border-dark-700 space-y-2">
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

    <div class="min-h-screen flex">
      <!-- Main Content -->
      <main class="flex-1 flex flex-col">
        <!-- File Content -->
        <div v-if="selectedFile" class="flex-1 p-4">
          <div class="mb-4 flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <h2 class="text-lg font-semibold text-white">
                {{ selectedFile.path }}
              </h2>
              <span class="text-sm text-gray-400">
                Project: {{ currentProject?.name }}
              </span>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="hasUnsavedChanges" class="text-yellow-500 text-sm">
                Unsaved changes
              </span>
              <button
                @click="saveChanges"
                class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg"
                :disabled="!hasUnsavedChanges || isLoading"
              >
                Save Changes
              </button>
            </div>
          </div>
          
          <!-- Code Editor -->
          <div class="h-[calc(100vh-12rem)] rounded-lg border border-dark-700 bg-dark-900">
            <textarea
              v-model="editorContent"
              :placeholder="'Enter code here...'"
              class="w-full h-full bg-dark-900 text-white p-4 font-mono resize-none focus:outline-none"
              @input="(e) => onEditorChange(e.target.value)"
              spellcheck="false"
              wrap="off"
            ></textarea>
          </div>
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
  </DashboardLayout>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import { useBuilder } from '../composables/useBuilder'

export default {
  name: 'BuilderWorkspace',
  components: {
    DashboardLayout
  },
  setup() {
    const route = useRoute()
    const prompt = ref('')
    const editorContent = ref('')
    const isFileExplorerExpanded = ref(true)
    const showNewFileForm = ref(false)
    const newFileName = ref('')
    const newFileType = ref('')

    // Define workspace navigation items
    const navigationItems = [] // Empty array since we don't want any navigation items

    const {
      currentProject,
      files,
      selectedFile,
      fileContent,
      availableModels,
      selectedModel,
      isLoading,
      error,
      hasUnsavedChanges,
      currentMode,
      loadProject,
      loadFiles,
      selectFile,
      updateFile,
      generateCode,
      undoLastAction,
      loadAvailableModels,
      switchMode,
      createFile,
      FILE_TYPES
    } = useBuilder()

    // Computed
    const canCreateFile = computed(() => {
      return newFileName.value.trim() && newFileType.value;
    })

    // Load project and models on mount
    onMounted(async () => {
      await loadProject(route.params.projectId)
      await loadAvailableModels()
    })

    // Watch for file content changes
    watch(fileContent, (newContent) => {
      if (newContent !== editorContent.value) {
        editorContent.value = newContent || ''
      }
    })

    // Handle editor content changes
    const onEditorChange = (content) => {
      if (content !== fileContent.value) {
        hasUnsavedChanges.value = true
      }
    }

    // Save changes
    const saveChanges = async () => {
      if (hasUnsavedChanges.value) {
        await updateFile(editorContent.value)
        hasUnsavedChanges.value = false
      }
    }

    // Handle AI prompt
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

    // Get file icon based on type
    const getFileIcon = (type) => {
      const icons = {
        html: 'fas fa-code',
        css: 'fab fa-css3',
        javascript: 'fab fa-js',
        python: 'fab fa-python',
        markdown: 'fas fa-file-alt',
        text: 'fas fa-file-alt',
        unknown: 'fas fa-file'
      }
      return icons[type] || icons.unknown
    }

    // Methods
    const handleCreateFile = async () => {
      if (!canCreateFile.value) return;

      try {
        await createFile(newFileName.value.trim(), newFileType.value);
        // Reset form
        newFileName.value = '';
        newFileType.value = '';
        showNewFileForm.value = false;
      } catch (err) {
        console.error('Error creating file:', err);
      }
    }

    return {
      navigationItems,
      currentProject,
      files,
      selectedFile,
      availableModels,
      selectedModel,
      isLoading,
      error,
      hasUnsavedChanges,
      prompt,
      editorContent,
      currentMode,
      isFileExplorerExpanded,
      showNewFileForm,
      newFileName,
      newFileType,
      canCreateFile,
      FILE_TYPES,
      selectFile,
      undoLastAction,
      saveChanges,
      handlePrompt,
      onEditorChange,
      getFileIcon,
      handleCreateFile,
      switchMode
    }
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