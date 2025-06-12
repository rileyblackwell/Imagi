<template>
  <div class="flex-1 overflow-y-auto">
    <!-- Vue.js Files Tree with Enhanced Modern Styling -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-200 flex items-center">
          <i class="fab fa-vuejs text-green-400 mr-1.5"></i>
          <span>Vue.js Files</span>
        </h3>
        <!-- Enhanced Add file button with modern styling -->
        <div class="flex space-x-1">
          <button 
            @click="toggleNewViewForm" 
            class="group relative text-xs rounded-lg px-2 py-1.5 bg-green-600/80 hover:bg-green-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
            title="Create new Vue view"
          >
            <!-- Subtle glow effect on hover -->
            <div class="absolute -inset-0.5 bg-green-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
            <div class="relative flex items-center">
              <i class="fas fa-plus mr-1"></i> 
              <span>View</span>
            </div>
          </button>
          <button 
            @click="toggleNewComponentForm" 
            class="group relative text-xs rounded-lg px-2 py-1.5 bg-blue-600/80 hover:bg-blue-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
            title="Create new Vue component"
          >
            <!-- Subtle glow effect on hover -->
            <div class="absolute -inset-0.5 bg-blue-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
            <div class="relative flex items-center">
              <i class="fas fa-puzzle-piece mr-1"></i> 
              <span>Component</span>
            </div>
          </button>
        </div>
      </div>

      <!-- New Vue View Form - Enhanced with modern styling -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewViewForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-green-700/50 space-y-2">
          <h3 class="text-xs font-medium text-green-300">Create New Vue View</h3>
          
          <input
            v-model="newViewName"
            type="text"
            placeholder="e.g., AboutPage, ContactForm"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-green-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(34,197,94,0.25)] transition-all duration-200"
            @keydown.enter="createVueView"
          />
          
          <input
            v-model="newViewRoute"
            type="text"
            placeholder="Route path: e.g., /about, /contact"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-green-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(34,197,94,0.25)] transition-all duration-200"
            @keydown.enter="createVueView"
          />
          
          <p class="text-xxs text-gray-500">
            View will be created in src/views/ and automatically added to router
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewViewForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 hover:text-white transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <button
              @click="createVueView"
              :disabled="!isValidViewName"
              class="group relative text-xs rounded-md px-2 py-1 bg-green-600/80 disabled:bg-gray-700 disabled:text-gray-500 hover:bg-green-600 text-white transition-all duration-200 focus:outline-none"
            >
              <!-- Subtle glow effect on hover (only when enabled) -->
              <div v-if="isValidViewName" class="absolute -inset-0.5 bg-green-500/30 rounded-md blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <span class="relative">Create View</span>
            </button>
          </div>
        </div>
      </Transition>

      <!-- New Vue Component Form - Enhanced with modern styling -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewComponentForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-blue-700/50 space-y-2">
          <h3 class="text-xs font-medium text-blue-300">Create New Vue Component</h3>
          
          <select
            v-model="newComponentType"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-blue-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(59,130,246,0.25)] transition-all duration-200"
          >
            <option value="atoms">Atom (Basic UI element)</option>
            <option value="molecules">Molecule (Simple combination)</option>
            <option value="organisms">Organism (Complex component)</option>
          </select>
          
          <input
            v-model="newComponentName"
            type="text"
            placeholder="e.g., UserCard, SearchInput"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-blue-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(59,130,246,0.25)] transition-all duration-200"
            @keydown.enter="createVueComponent"
          />
          
          <p class="text-xxs text-gray-500">
            Component will be created in src/components/{{ newComponentType }}/
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewComponentForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 hover:text-white transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <button
              @click="createVueComponent"
              :disabled="!isValidComponentName"
              class="group relative text-xs rounded-md px-2 py-1 bg-blue-600/80 disabled:bg-gray-700 disabled:text-gray-500 hover:bg-blue-600 text-white transition-all duration-200 focus:outline-none"
            >
              <!-- Subtle glow effect on hover (only when enabled) -->
              <div v-if="isValidComponentName" class="absolute -inset-0.5 bg-blue-500/30 rounded-md blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <span class="relative">Create Component</span>
            </button>
          </div>
        </div>
      </Transition>

      <!-- Vue.js Directory Structure - Enhanced with modern styling -->
      <div class="space-y-2">
        <!-- Group Vue.js files by directory -->
        <div 
          v-for="(dirFiles, dirName) in vueFilesByDirectory"
          :key="dirName"
          class="p-2 bg-dark-850/60 backdrop-blur-sm rounded-lg border border-dark-700/40 transition-all duration-200"
          :class="{'border-green-500/30 bg-green-900/10 shadow-[0_0_10px_rgba(34,197,94,0.1)]': currentDirectory === dirName}"
        >
          <div 
            class="group flex items-center text-xs py-1.5 px-2.5 rounded-md transition-all duration-200 cursor-pointer mb-2"
            :class="[
              currentDirectory === dirName 
                ? 'bg-gradient-to-r from-green-500/20 to-blue-500/10 text-white border border-green-500/30' 
                : 'text-green-300 hover:bg-dark-800/80 border border-transparent hover:border-green-500/20'
            ]"
            @click="selectDirectory(dirName)"
          >
            <i 
              class="fas fa-folder-open mr-2 w-4 text-center transition-colors duration-200"
              :class="getVueDirectoryIconClass(dirName)"
            ></i>
            <span class="font-medium">{{ formatVueDirectoryName(dirName) }}</span>
            <span class="ml-auto text-xxs bg-dark-700/80 text-green-300 py-0.5 px-1.5 rounded-full">
              {{ dirFiles.length }}
            </span>
          </div>
          
          <!-- Vue Files List with enhanced styling -->
          <div v-if="currentDirectory === dirName" class="space-y-1.5 pl-2">
            <FileTreeItem
              v-for="file in dirFiles"
              :key="file.path"
              :file="file"
              :is-selected="selectedFile?.path === file.path"
              @select="handleFileSelect"
              @delete="handleFileDelete"
            />
            <div v-if="dirFiles.length === 0" class="text-center text-xxs text-gray-500 py-2">
              <div><i class="fas fa-info-circle"></i> No Vue files in this directory</div>
            </div>
          </div>
        </div>
        
        <!-- No Vue files message - Enhanced with modern styling -->
        <div v-if="Object.keys(vueFilesByDirectory).length === 0" class="text-center text-sm text-gray-500 py-6 px-3 bg-dark-850/60 backdrop-blur-sm rounded-lg border border-dark-700/40">
          <div><i class="fab fa-vuejs text-green-400 mb-2 text-xl opacity-80"></i></div>
          <div>No Vue.js files found</div>
          <div class="text-xs mt-1 mb-3">Create your first Vue view or component</div>
          <div class="flex justify-center space-x-2">
            <button
              @click="toggleNewViewForm"
              class="group relative text-xs rounded-lg px-3 py-1.5 bg-green-600/80 hover:bg-green-600 text-white transition-all duration-200 transform hover:scale-[1.02] inline-flex items-center"
            >
              <!-- Subtle glow effect on hover -->
              <div class="absolute -inset-0.5 bg-green-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <div class="relative flex items-center">
                <i class="fas fa-plus mr-1.5"></i> 
                <span>Create View</span>
              </div>
            </button>
            <button
              @click="toggleNewComponentForm"
              class="group relative text-xs rounded-lg px-3 py-1.5 bg-blue-600/80 hover:bg-blue-600 text-white transition-all duration-200 transform hover:scale-[1.02] inline-flex items-center"
            >
              <!-- Subtle glow effect on hover -->
              <div class="absolute -inset-0.5 bg-blue-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <div class="relative flex items-center">
                <i class="fas fa-puzzle-piece mr-1.5"></i> 
                <span>Create Component</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ProjectFile } from '../../../types/components'
import FileTreeItem from '../../atoms/navigation/FileTreeItem.vue'
import { FileService } from '../../../services/fileService'

const props = defineProps<{
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
  showNewForm?: boolean
  projectId?: string
}>()

const emit = defineEmits<{
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string; content?: string }): void
  (e: 'deleteFile', file: ProjectFile): void
}>()

// Local state
const showNewViewForm = ref(false)
const showNewComponentForm = ref(false)
const newViewName = ref('')
const newViewRoute = ref('')
const newComponentName = ref('')
const newComponentType = ref<'atoms' | 'molecules' | 'organisms'>('atoms')
const currentDirectory = ref<string>('')

// Filter files to only show Vue.js related files
const vueFiles = computed(() => {
  return props.files.filter(file => {
    const path = file.path.toLowerCase()
    const normalizedPath = path.replace(/\\/g, '/') // Handle Windows paths
    
    // Include ALL Vue files (.vue extension)
    if (normalizedPath.endsWith('.vue')) return true
    
    // Include TypeScript/JavaScript files in ANY Vue.js src directories
    if ((normalizedPath.endsWith('.ts') || normalizedPath.endsWith('.js') || normalizedPath.endsWith('.jsx') || normalizedPath.endsWith('.tsx')) && 
        (normalizedPath.includes('/src/views/') || 
         normalizedPath.includes('/src/components/') || 
         normalizedPath.includes('/src/router/') ||
         normalizedPath.includes('/src/stores/') ||
         normalizedPath.includes('/src/services/') ||
         normalizedPath.includes('/src/types/') ||
         normalizedPath.includes('/src/composables/') ||
         normalizedPath.includes('/src/utils/') ||
         normalizedPath.includes('/src/plugins/') ||
         normalizedPath.includes('/src/directives/') ||
         normalizedPath.includes('/src/layouts/'))) {
      return true
    }
    
    // Include main Vue.js files and configuration files
    if (normalizedPath.includes('/frontend/vuejs/') || normalizedPath.includes('/vuejs/')) {
      if (normalizedPath.endsWith('main.ts') || 
          normalizedPath.endsWith('main.js') ||
          normalizedPath.endsWith('app.vue') ||
          normalizedPath.endsWith('index.html') ||
          normalizedPath.includes('vite.config') ||
          normalizedPath.includes('vue.config') ||
          normalizedPath.includes('tsconfig') ||
          normalizedPath.includes('tailwind.config')) {
        return true
      }
    }
    
    // Include any file that appears to be a Vue component based on naming convention
    if (normalizedPath.endsWith('.vue') || 
        (normalizedPath.includes('component') && (normalizedPath.endsWith('.ts') || normalizedPath.endsWith('.js')))) {
      return true
    }
    
    return false
  })
})

// Group Vue files by directory with Vue.js specific logic
const vueFilesByDirectory = computed(() => {
  const result: Record<string, ProjectFile[]> = {}
  
  vueFiles.value.forEach(file => {
    const normalizedPath = file.path.toLowerCase().replace(/\\/g, '/')
    let dir = ''
    
    // Prioritize Views directory
    if (normalizedPath.includes('/src/views/') || normalizedPath.includes('/views/')) {
      dir = 'Views'
    }
    // Organize components by atomic design structure
    else if (normalizedPath.includes('/src/components/atoms/') || normalizedPath.includes('/components/atoms/')) {
      dir = 'Components/Atoms'
    } else if (normalizedPath.includes('/src/components/molecules/') || normalizedPath.includes('/components/molecules/')) {
      dir = 'Components/Molecules'
    } else if (normalizedPath.includes('/src/components/organisms/') || normalizedPath.includes('/components/organisms/')) {
      dir = 'Components/Organisms'
    } else if (normalizedPath.includes('/src/components/') || normalizedPath.includes('/components/')) {
      dir = 'Components'
    }
    // Other Vue.js directories
    else if (normalizedPath.includes('/src/layouts/') || normalizedPath.includes('/layouts/')) {
      dir = 'Layouts'
    } else if (normalizedPath.includes('/src/router/') || normalizedPath.includes('/router/')) {
      dir = 'Router'
    } else if (normalizedPath.includes('/src/stores/') || normalizedPath.includes('/stores/')) {
      dir = 'Stores'
    } else if (normalizedPath.includes('/src/services/') || normalizedPath.includes('/services/')) {
      dir = 'Services'
    } else if (normalizedPath.includes('/src/composables/') || normalizedPath.includes('/composables/')) {
      dir = 'Composables'
    } else if (normalizedPath.includes('/src/utils/') || normalizedPath.includes('/utils/')) {
      dir = 'Utils'
    } else if (normalizedPath.includes('/src/plugins/') || normalizedPath.includes('/plugins/')) {
      dir = 'Plugins'
    } else if (normalizedPath.includes('/src/directives/') || normalizedPath.includes('/directives/')) {
      dir = 'Directives'
    } else if (normalizedPath.includes('/src/types/') || normalizedPath.includes('/types/')) {
      dir = 'Types'
    }
    // Configuration files
    else if (normalizedPath.includes('vite.config') || normalizedPath.includes('vue.config') || 
             normalizedPath.includes('tsconfig') || normalizedPath.includes('tailwind.config')) {
      dir = 'Config'
    }
    // Core files (main.ts, App.vue, index.html)
    else if (normalizedPath.includes('/src/') || normalizedPath.endsWith('index.html')) {
      dir = 'Core'
    }
    // Fallback for any other files
    else {
      dir = 'Other'
    }
    
    if (!result[dir]) {
      result[dir] = []
    }
    
    result[dir].push(file)
  })
  
  // Sort files within each directory alphabetically
  Object.keys(result).forEach(dir => {
    result[dir].sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  })
  
  // Set current directory to Views first, then Components, then first available
  if (!currentDirectory.value && Object.keys(result).length > 0) {
    const priorityOrder = ['Views', 'Components', 'Components/Atoms', 'Components/Molecules', 'Components/Organisms', 'Layouts', 'Core']
    for (const priority of priorityOrder) {
      if (result[priority]) {
        currentDirectory.value = priority
        break
      }
    }
    // If no priority directory found, use first available
    if (!currentDirectory.value) {
      currentDirectory.value = Object.keys(result)[0]
    }
  }
  
  return result
})

// Utility functions for Vue.js directories
const formatVueDirectoryName = (dirName: string) => {
  return dirName
}

const getVueDirectoryIconClass = (dirName: string) => {
  if (dirName === 'Views') return 'text-green-400'
  if (dirName.startsWith('Components')) return 'text-blue-400'
  if (dirName === 'Layouts') return 'text-cyan-400'
  if (dirName === 'Router') return 'text-purple-400'
  if (dirName === 'Stores') return 'text-orange-400'
  if (dirName === 'Services') return 'text-yellow-400'
  if (dirName === 'Composables') return 'text-emerald-400'
  if (dirName === 'Utils') return 'text-teal-400'
  if (dirName === 'Plugins') return 'text-pink-400'
  if (dirName === 'Directives') return 'text-lime-400'
  if (dirName === 'Types') return 'text-red-400'
  if (dirName === 'Config') return 'text-slate-400'
  if (dirName === 'Core') return 'text-indigo-400'
  return 'text-gray-400'
}

// Validation computed properties
const isValidViewName = computed(() => {
  return newViewName.value.trim().length > 0 && /^[A-Za-z][A-Za-z0-9]*$/.test(newViewName.value.trim())
})

const isValidComponentName = computed(() => {
  return newComponentName.value.trim().length > 0 && /^[A-Za-z][A-Za-z0-9]*$/.test(newComponentName.value.trim())
})

// Methods
const toggleNewViewForm = () => {
  showNewViewForm.value = !showNewViewForm.value
  if (!showNewViewForm.value) {
    newViewName.value = ''
    newViewRoute.value = ''
  }
  if (showNewViewForm.value) {
    showNewComponentForm.value = false
  }
}

const toggleNewComponentForm = () => {
  showNewComponentForm.value = !showNewComponentForm.value
  if (!showNewComponentForm.value) {
    newComponentName.value = ''
    newComponentType.value = 'atoms'
  }
  if (showNewComponentForm.value) {
    showNewViewForm.value = false
  }
}

const selectDirectory = (dirName: string) => {
  currentDirectory.value = dirName
}

const handleFileSelect = (file: ProjectFile) => {
  emit('selectFile', file)
}

const handleFileDelete = (file: ProjectFile) => {
  emit('deleteFile', file)
}

const createVueView = async () => {
  if (!isValidViewName.value) return
  
  const viewName = newViewName.value.trim()
  const routePath = newViewRoute.value.trim() || `/${viewName.toLowerCase()}`
  
  const viewContent = `<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-8">
          ${viewName}
        </h1>
        <p class="text-lg text-gray-600">
          Welcome to the ${viewName} page. Start building your content here.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Add your component logic here
console.log('${viewName} component mounted')
<\/script>

<style scoped>
/* Add component-specific styles here */
</style>
`

  emit('createFile', {
    name: `frontend/vuejs/src/views/${viewName}.vue`,
    type: 'vue',
    content: viewContent
  })

  if (routePath && props.projectId) {
    await updateRouterWithNewView(viewName, routePath)
  }

  newViewName.value = ''
  newViewRoute.value = ''
  showNewViewForm.value = false
}

const createVueComponent = () => {
  if (!isValidComponentName.value) return
  
  const componentName = newComponentName.value.trim()
  const componentType = newComponentType.value
  
  const componentContent = `<template>
  <div class="${componentName.toLowerCase()}-component">
    <!-- ${componentName} component content -->
    <p>{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Component props
interface Props {
  // Define your props here
}

const props = withDefaults(defineProps<Props>(), {
  // Default values
})

// Component state
const message = ref('Hello from ${componentName}!')

// Component methods
// Add your methods here
<\/script>

<style scoped>
.${componentName.toLowerCase()}-component {
  /* Add component-specific styles here */
}
</style>
`

  emit('createFile', {
    name: `frontend/vuejs/src/components/${componentType}/${componentName}.vue`,
    type: 'vue',
    content: componentContent
  })

  newComponentName.value = ''
  newComponentType.value = 'atoms'
  showNewComponentForm.value = false
}

const updateRouterWithNewView = async (viewName: string, routePath: string) => {
  if (!props.projectId) return

  try {
    const routerFiles = props.files.filter(f => f.path.includes('src/router/index.'))
    if (routerFiles.length === 0) return

    const routerFile = routerFiles[0]
    const currentContent = await FileService.getFileContent(props.projectId, routerFile.path)
    const updatedContent = addRouteToRouter(currentContent, viewName, routePath)
    
    await FileService.updateFileContent(props.projectId, routerFile.path, updatedContent)
  } catch (error) {
    console.error('Error updating router:', error)
  }
}

const addRouteToRouter = (routerContent: string, viewName: string, routePath: string): string => {
  const importStatement = `import ${viewName} from '@/views/${viewName}.vue'`
  
  let updatedContent = routerContent
  if (!updatedContent.includes(importStatement)) {
    const importMatch = updatedContent.match(/(import .+ from .+\.vue['"])/g)
    if (importMatch && importMatch.length > 0) {
      const lastImport = importMatch[importMatch.length - 1]
      updatedContent = updatedContent.replace(lastImport, `${lastImport}\n${importStatement}`)
    } else {
      const firstImportMatch = updatedContent.match(/(import .+)/)
      if (firstImportMatch) {
        updatedContent = updatedContent.replace(firstImportMatch[0], `${firstImportMatch[0]}\n${importStatement}`)
      }
    }
  }
  
  const routeEntry = `  {
    path: '${routePath}',
    name: '${viewName.toLowerCase()}',
    component: ${viewName},
    meta: {
      title: '${viewName}'
    }
  }`
  
  const routesMatch = updatedContent.match(/const routes[^=]*=\s*\[([\s\S]*?)\]/m)
  if (routesMatch) {
    const routesContent = routesMatch[1]
    const updatedRoutes = routesContent.trim() + (routesContent.trim() ? ',\n' : '') + routeEntry
    updatedContent = updatedContent.replace(routesMatch[0], `const routes = [\n${updatedRoutes}\n]`)
  }
  
  return updatedContent
}
</script>

<style scoped>
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.600') transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.600');
  border-radius: 3px;
}

.text-xxs {
  font-size: 0.65rem;
  line-height: 1rem;
}
</style> 