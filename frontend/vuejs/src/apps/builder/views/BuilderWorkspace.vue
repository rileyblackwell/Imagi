<template>
  <DashboardLayout>
    <div class="min-h-screen flex">
      <!-- Sidebar -->
      <aside class="w-64 bg-dark-800 border-r border-dark-700 flex flex-col">
        <!-- Project Info -->
        <div class="p-4 border-b border-dark-700">
          <h2 class="text-lg font-semibold text-white truncate">{{ currentProject?.name }}</h2>
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

        <!-- File Explorer -->
        <div class="flex-1 overflow-y-auto p-4">
          <h3 class="text-sm font-medium text-gray-400 mb-2">Project Files</h3>
          <div class="space-y-1">
            <button
              v-for="file in files"
              :key="file.path"
              @click="selectFile(file)"
              class="w-full text-left px-3 py-2 rounded-lg text-sm"
              :class="[
                selectedFile?.path === file.path
                  ? 'bg-primary-500/20 text-white'
                  : 'text-gray-400 hover:bg-dark-700 hover:text-white'
              ]"
            >
              <i :class="getFileIcon(file.type)" class="mr-2"></i>
              {{ file.path }}
            </button>
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
      </aside>

      <!-- Main Content -->
      <main class="flex-1 flex flex-col">
        <!-- File Content -->
        <div v-if="selectedFile" class="flex-1 p-4">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-white">
              {{ selectedFile.path }}
            </h2>
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
            <MonacoEditor
              v-model="editorContent"
              :language="getFileLanguage(selectedFile.type)"
              theme="vs-dark"
              @change="onEditorChange"
            />
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
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import { MonacoEditor } from '@/shared/components'
import { useBuilder } from '../composables/useBuilder'

export default {
  name: 'BuilderWorkspace',
  components: {
    DashboardLayout,
    MonacoEditor
  },
  setup() {
    const route = useRoute()
    const prompt = ref('')
    const editorContent = ref('')

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
      loadProject,
      loadFiles,
      selectFile,
      updateFile,
      generateCode,
      undoLastAction,
      loadAvailableModels
    } = useBuilder()

    // Load project and models on mount
    onMounted(async () => {
      await loadProject(route.params.projectId)
      await loadAvailableModels()
    })

    // Watch for file content changes
    watch(fileContent, (newContent) => {
      editorContent.value = newContent
    })

    // Handle editor content changes
    const onEditorChange = (content) => {
      hasUnsavedChanges.value = content !== fileContent.value
    }

    // Save changes
    const saveChanges = async () => {
      await updateFile(editorContent.value)
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

    // Get Monaco editor language
    const getFileLanguage = (type) => {
      const languages = {
        html: 'html',
        css: 'css',
        javascript: 'javascript',
        python: 'python',
        markdown: 'markdown',
        text: 'plaintext'
      }
      return languages[type] || 'plaintext'
    }

    return {
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
      selectFile,
      undoLastAction,
      saveChanges,
      handlePrompt,
      onEditorChange,
      getFileIcon,
      getFileLanguage
    }
  }
}
</script>

<style>
@import '../assets/styles/builder_styles.css';
</style> 