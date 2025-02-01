<template>
  <BuilderLayout>
    <div v-if="isLoading" class="flex items-center justify-center h-full">
      <i class="fas fa-spinner fa-spin text-2xl text-primary-500"></i>
      <span class="ml-2 text-gray-400">Loading project...</span>
    </div>

    <div v-else-if="error" class="flex flex-col items-center justify-center h-full">
      <i class="fas fa-exclamation-circle text-4xl text-red-500 mb-4"></i>
      <h2 class="text-xl font-semibold text-white mb-2">Error Loading Project</h2>
      <p class="text-gray-400 mb-4">{{ error }}</p>
      <router-link
        to="/builder/projects"
        class="text-primary-500 hover:text-primary-400 font-medium flex items-center"
      >
        <i class="fas fa-arrow-left mr-2"></i>
        Back to Projects
      </router-link>
    </div>

    <div v-else class="h-full">
      <!-- Project workspace content goes here -->
      <div class="flex flex-col h-full">
        <!-- File tabs -->
        <div class="flex items-center bg-dark-900 border-b border-dark-700 px-4 py-2">
          <div
            v-for="file in projectFiles"
            :key="file.name"
            @click="selectFile(file)"
            class="px-4 py-2 mr-2 rounded cursor-pointer"
            :class="[
              currentFile?.name === file.name
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:bg-dark-800'
            ]"
          >
            <i :class="getFileIcon(file.type)" class="mr-2"></i>
            {{ file.name }}
          </div>
        </div>

        <!-- Editor area -->
        <div class="flex-grow p-4">
          <!-- Add your code editor component here -->
          <div class="bg-dark-800 rounded-lg h-full p-4">
            <p class="text-gray-400">Editor content for {{ currentFile?.name }}</p>
          </div>
        </div>
      </div>
    </div>
  </BuilderLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BuilderLayout from '../layouts/BuilderLayout.vue'
import { useProjects } from '@/apps/builder/composables/useProjects'

export default {
  name: 'ProjectDetail',
  components: {
    BuilderLayout
  },
  setup() {
    const route = useRoute()
    const { fetchProject } = useProjects()
    const isLoading = ref(true)
    const error = ref(null)
    const currentFile = ref(null)

    // Mock project files - replace with actual project files from your backend
    const projectFiles = ref([
      { name: 'index.html', type: 'html' },
      { name: 'styles.css', type: 'css' },
      { name: 'about.html', type: 'html' }
    ])

    const loadProject = async () => {
      try {
        const projectId = route.params.id
        await fetchProject(projectId)
        isLoading.value = false
      } catch (err) {
        console.error('Failed to load project:', err)
        error.value = 'Failed to load project. Please try again.'
        isLoading.value = false
      }
    }

    const selectFile = (file) => {
      currentFile.value = file
    }

    const getFileIcon = (type) => {
      switch (type) {
        case 'html':
          return 'fas fa-code'
        case 'css':
          return 'fas fa-paint-brush'
        default:
          return 'fas fa-file'
      }
    }

    onMounted(() => {
      loadProject()
      // Select first file by default
      if (projectFiles.value.length) {
        currentFile.value = projectFiles.value[0]
      }
    })

    return {
      isLoading,
      error,
      projectFiles,
      currentFile,
      selectFile,
      getFileIcon
    }
  }
}
</script> 