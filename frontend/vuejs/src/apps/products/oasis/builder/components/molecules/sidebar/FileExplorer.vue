<template>
  <div class="flex-1 overflow-y-auto">
    <!-- Apps with Enhanced Modern Styling -->
    <div class="p-3">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-medium text-gray-200 flex items-center">
          <i class="fas fa-cubes text-purple-400 mr-1.5"></i>
          <span>Apps</span>
        </h3>
        <!-- Enhanced Add app button -->
        <div>
          <button 
            @click="toggleNewAppForm" 
            class="group relative w-full text-xs rounded-lg px-3 py-2 bg-purple-600/80 hover:bg-purple-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
            title="Create new app"
          >
            <!-- Subtle glow effect on hover -->
            <div class="absolute -inset-0.5 bg-purple-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
            <div class="relative flex items-center justify-center">
              <i class="fas fa-plus mr-2"></i> 
              <span>Create New App</span>
            </div>
          </button>
        </div>
      </div>

      <!-- New App Form - Enhanced with modern styling -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewAppForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-purple-700/50 space-y-2">
          <h3 class="text-xs font-medium text-purple-300">Create New App</h3>
          
          <input
            v-model="newAppName"
            type="text"
            placeholder="e.g., blog, ecommerce, portfolio"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-purple-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(147,51,234,0.25)] transition-all duration-200"
            @keydown.enter="createNewApp"
          />
          
          <input
            v-model="newAppDescription"
            type="text"
            placeholder="App description (optional)"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-purple-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(147,51,234,0.25)] transition-all duration-200"
            @keydown.enter="createNewApp"
          />
          
          <p class="text-xxs text-gray-500">
            App will be created with Vue.js best practices structure (views, components, stores, router)
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewAppForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 hover:text-white transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <button
              @click="createNewApp"
              :disabled="!isValidAppName"
              class="group relative text-xs rounded-md px-2 py-1 bg-purple-600/80 disabled:bg-gray-700 disabled:text-gray-500 hover:bg-purple-600 text-white transition-all duration-200 focus:outline-none"
            >
              <!-- Subtle glow effect on hover (only when enabled) -->
              <div v-if="isValidAppName" class="absolute -inset-0.5 bg-purple-500/30 rounded-md blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <span class="relative">Create App</span>
            </button>
          </div>
        </div>
      </Transition>

      <!-- New View Form for App - Enhanced with modern styling -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewViewForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-green-700/50 space-y-2">
          <h3 class="text-xs font-medium text-green-300">Create New View</h3>
          
          <select
            v-model="newViewSelectedApp"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-green-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(34,197,94,0.25)] transition-all duration-200"
          >
            <option value="">Select an app...</option>
            <option v-for="app in availableApps" :key="app" :value="app">
              {{ app.charAt(0).toUpperCase() + app.slice(1) }} App
            </option>
          </select>
          
          <input
            v-model="newViewName"
            type="text"
            placeholder="e.g., AboutPage, ContactPage, ServicesPage"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-green-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(34,197,94,0.25)] transition-all duration-200"
            @keydown.enter="createVueView"
          />
          
          <input
            v-model="newViewRoute"
            type="text"
            placeholder="Route path: e.g., /about, /contact, /services"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-green-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(34,197,94,0.25)] transition-all duration-200"
            @keydown.enter="createVueView"
          />
          
          <p class="text-xxs text-gray-500">
            View will be created in {{ newViewSelectedApp || '[selected app]' }}/views/ directory
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

      <!-- New UI Component Form - Enhanced with modern styling -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-300 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div v-if="showNewComponentForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-blue-700/50 space-y-2">
          <h3 class="text-xs font-medium text-blue-300">Create New Component</h3>
          
          <select
            v-model="newComponentSelectedApp"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-blue-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(59,130,246,0.25)] transition-all duration-200"
          >
            <option value="">Select an app...</option>
            <option v-for="app in availableApps" :key="app" :value="app">
              {{ app.charAt(0).toUpperCase() + app.slice(1) }} App
            </option>
          </select>
          
          <select
            v-model="newComponentType"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-blue-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(59,130,246,0.25)] transition-all duration-200"
          >
            <option value="atoms">Atom (Basic UI element)</option>
            <option value="molecules">Molecule (Simple combination)</option>
            <option value="organisms">Organism (Complex component)</option>
          </select>
          
          <div class="p-2 bg-blue-950/30 rounded-md border border-blue-700/30">
            <p class="text-xxs text-blue-300 mb-1">{{ getComponentTypeDescription(newComponentType).title }}</p>
            <p class="text-xxs text-gray-400">{{ getComponentTypeDescription(newComponentType).description }}</p>
          </div>
          
          <input
            v-model="newComponentName"
            type="text"
            placeholder="e.g., PrimaryButton, SearchInput, UserAvatar"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-blue-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(59,130,246,0.25)] transition-all duration-200"
            @keydown.enter="createVueComponent"
          />
          
          <p class="text-xxs text-gray-500">
            Component will be created in {{ newComponentSelectedApp || '[selected app]' }}/components/{{ newComponentType }}/
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
              <span class="relative">Create UI Component</span>
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
          
          <!-- App Files List with enhanced styling -->
          <div v-if="currentDirectory === dirName" class="space-y-1.5 pl-2">
            <!-- Add View/Component buttons for current app -->
            <div class="mb-3 grid grid-cols-2 gap-1.5">
              <button 
                @click="openCreateViewForApp(dirName)" 
                class="group relative text-xxs rounded-md px-2 py-1.5 bg-green-600/70 hover:bg-green-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
                :title="`Create view in ${dirName}`"
              >
                <div class="absolute -inset-0.5 bg-green-500/20 rounded-md blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
                <div class="relative flex items-center justify-center">
                  <i class="fas fa-file-alt mr-1 text-xxs"></i> 
                  <span>Add View</span>
                </div>
              </button>
              <button 
                @click="openCreateComponentForApp(dirName)" 
                class="group relative text-xxs rounded-md px-2 py-1.5 bg-blue-600/70 hover:bg-blue-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
                :title="`Create component in ${dirName}`"
              >
                <div class="absolute -inset-0.5 bg-blue-500/20 rounded-md blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
                <div class="relative flex items-center justify-center">
                  <i class="fas fa-puzzle-piece mr-1 text-xxs"></i> 
                  <span>Add Component</span>
                </div>
              </button>
            </div>
            
            <FileTreeItem
              v-for="file in dirFiles"
              :key="file.path"
              :file="file"
              :is-selected="selectedFile?.path === file.path"
              @select="handleFileSelect"
              @delete="handleFileDelete"
            />
            <div v-if="dirFiles.length === 0" class="text-center text-xxs text-gray-500 py-2">
              <div><i class="fas fa-info-circle"></i> No files in this app yet</div>
            </div>
          </div>
        </div>
        
        <!-- No apps message - Enhanced with modern styling -->
        <div v-if="Object.keys(vueFilesByDirectory).length === 0" class="text-center text-sm text-gray-500 py-6 px-3 bg-dark-850/60 backdrop-blur-sm rounded-lg border border-dark-700/40">
          <div><i class="fas fa-cubes text-purple-400 mb-2 text-xl opacity-80"></i></div>
          <div>No apps found</div>
          <div class="text-xs mt-1 mb-4">Create your first modular Vue.js app</div>
          <div class="space-y-2">
            <button
              @click="toggleNewAppForm"
              class="group relative w-full text-xs rounded-lg px-3 py-2 bg-purple-600/80 hover:bg-purple-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
            >
              <!-- Subtle glow effect on hover -->
              <div class="absolute -inset-0.5 bg-purple-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <div class="relative flex items-center justify-center">
                <i class="fas fa-plus mr-1.5"></i> 
                <span>Create New App</span>
              </div>
            </button>
            <button
              @click="toggleNewViewForm"
              class="group relative w-full text-xs rounded-lg px-3 py-2 bg-green-600/80 hover:bg-green-600 text-white transition-all duration-200 transform hover:scale-[1.02]"
            >
              <!-- Subtle glow effect on hover -->
              <div class="absolute -inset-0.5 bg-green-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
              <div class="relative flex items-center justify-center">
                <i class="fas fa-file-alt mr-1.5"></i> 
                <span>Create View in Existing App</span>
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
const showNewAppForm = ref(false)
const showNewViewForm = ref(false)
const showNewComponentForm = ref(false)
const newAppName = ref('')
const newAppDescription = ref('')
const newViewName = ref('')
const newViewRoute = ref('')
const newViewSelectedApp = ref('')
const newComponentName = ref('')
const newComponentSelectedApp = ref('')
const newComponentType = ref<'atoms' | 'molecules' | 'organisms'>('atoms')
const currentApp = ref<string>('')
const currentDirectory = ref<string>('')

// Filter files to show app-based structure (views, components, stores, etc.)
const vueFiles = computed(() => {
  return props.files.filter(file => {
    const path = file.path.toLowerCase()
    const normalizedPath = path.replace(/\\/g, '/') // Handle Windows paths
    
    // Include files from any app directory
    if (normalizedPath.includes('/src/apps/')) {
      // Include Vue files (.vue extension)
      if (normalizedPath.endsWith('.vue')) return true
      
      // Include TypeScript/JavaScript files in app directories
      if ((normalizedPath.endsWith('.ts') || normalizedPath.endsWith('.js')) && 
          (normalizedPath.includes('/views/') || 
           normalizedPath.includes('/components/') || 
           normalizedPath.includes('/stores/') ||
           normalizedPath.includes('/router/') ||
           normalizedPath.includes('/services/') ||
           normalizedPath.includes('/types/'))) {
        return true
      }
    }
    
    return false
  })
})

// Group files by app and then by type within each app
const vueFilesByDirectory = computed(() => {
  const result: Record<string, ProjectFile[]> = {}
  
  vueFiles.value.forEach(file => {
    const normalizedPath = file.path.toLowerCase().replace(/\\/g, '/')
    
    // Extract app name from path like: frontend/vuejs/src/apps/{appname}/
    const appMatch = normalizedPath.match(/\/src\/apps\/([^\/]+)\//)
    if (appMatch) {
      const appName = appMatch[1]
      const appDisplayName = appName.charAt(0).toUpperCase() + appName.slice(1)
      
      // Determine the file type within the app
      let fileType = ''
      if (normalizedPath.includes('/views/')) {
        fileType = 'Views'
      } else if (normalizedPath.includes('/components/atoms/')) {
        fileType = 'Components'
      } else if (normalizedPath.includes('/components/molecules/')) {
        fileType = 'Components'
      } else if (normalizedPath.includes('/components/organisms/')) {
        fileType = 'Components'
      } else if (normalizedPath.includes('/components/')) {
        fileType = 'Components'
      } else if (normalizedPath.includes('/stores/')) {
        fileType = 'Stores'
      } else if (normalizedPath.includes('/router/')) {
        fileType = 'Router'
      } else if (normalizedPath.includes('/services/')) {
        fileType = 'Services'
      } else if (normalizedPath.includes('/types/')) {
        fileType = 'Types'
      } else {
        fileType = 'Other'
      }
      
      const dirKey = `${appDisplayName} App`
      
      if (!result[dirKey]) {
        result[dirKey] = []
      }
      
      result[dirKey].push(file)
    }
  })
  
  // Sort files within each app alphabetically
  Object.keys(result).forEach(dir => {
    result[dir].sort((a, b) => (a.name || '').localeCompare(b.name || ''))
  })
  
  // Set current directory to first available app
  if (!currentDirectory.value && Object.keys(result).length > 0) {
    // Try to find auth app first, then home, then first available
    const priorityOrder = ['Auth App', 'Home App', 'Products App']
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

// Get available apps for dropdowns
const availableApps = computed(() => {
  const apps = new Set<string>()
  vueFiles.value.forEach(file => {
    const normalizedPath = file.path.toLowerCase().replace(/\\/g, '/')
    const appMatch = normalizedPath.match(/\/src\/apps\/([^\/]+)\//)
    if (appMatch) {
      apps.add(appMatch[1])
    }
  })
  return Array.from(apps).sort()
})

// Utility functions for app directories
const formatVueDirectoryName = (dirName: string) => {
  return dirName
}

const getVueDirectoryIconClass = (dirName: string) => {
  if (dirName.includes('Auth')) return 'text-purple-400'
  if (dirName.includes('Home')) return 'text-green-400'
  if (dirName.includes('Products')) return 'text-blue-400'
  if (dirName.includes('Payments')) return 'text-yellow-400'
  if (dirName.includes('Docs')) return 'text-cyan-400'
  return 'text-indigo-400' // Default for new apps
}

const getComponentTypeDescription = (type: string) => {
  const descriptions = {
    atoms: {
      title: 'Creating Atomic Component',
      description: 'Basic UI building blocks like buttons, inputs, icons'
    },
    molecules: {
      title: 'Creating Molecule Component', 
      description: 'Simple combinations of atoms like form fields, cards'
    },
    organisms: {
      title: 'Creating Organism Component',
      description: 'Complex combinations of molecules like headers, forms'
    }
  }
  return descriptions[type as keyof typeof descriptions] || descriptions.atoms
}

// Validation computed properties
const isValidAppName = computed(() => {
  return newAppName.value.trim().length > 0 && /^[a-z][a-z0-9]*$/.test(newAppName.value.trim())
})

const isValidViewName = computed(() => {
  return newViewName.value.trim().length > 0 && 
         /^[A-Za-z][A-Za-z0-9]*$/.test(newViewName.value.trim()) &&
         newViewSelectedApp.value.trim().length > 0
})

const isValidComponentName = computed(() => {
  return newComponentName.value.trim().length > 0 && 
         /^[A-Za-z][A-Za-z0-9]*$/.test(newComponentName.value.trim()) &&
         newComponentSelectedApp.value.trim().length > 0
})

// Methods
const toggleNewAppForm = () => {
  showNewAppForm.value = !showNewAppForm.value
  if (!showNewAppForm.value) {
    newAppName.value = ''
    newAppDescription.value = ''
  }
  if (showNewAppForm.value) {
    showNewViewForm.value = false
    showNewComponentForm.value = false
  }
}

const toggleNewViewForm = () => {
  showNewViewForm.value = !showNewViewForm.value
  if (!showNewViewForm.value) {
    newViewName.value = ''
    newViewRoute.value = ''
    newViewSelectedApp.value = ''
  }
  if (showNewViewForm.value) {
    showNewAppForm.value = false
    showNewComponentForm.value = false
  }
}

const toggleNewComponentForm = () => {
  showNewComponentForm.value = !showNewComponentForm.value
  if (!showNewComponentForm.value) {
    newComponentName.value = ''
    newComponentSelectedApp.value = ''
    newComponentType.value = 'atoms'
  }
  if (showNewComponentForm.value) {
    showNewViewForm.value = false
    showNewAppForm.value = false
  }
}

const selectDirectory = (dirName: string) => {
  currentDirectory.value = dirName
}

const openCreateViewForApp = (appDirName: string) => {
  // Extract app name from "App Name App" format
  const appName = appDirName.replace(' App', '').toLowerCase()
  newViewSelectedApp.value = appName
  showNewViewForm.value = true
  showNewAppForm.value = false
  showNewComponentForm.value = false
}

const openCreateComponentForApp = (appDirName: string) => {
  // Extract app name from "App Name App" format  
  const appName = appDirName.replace(' App', '').toLowerCase()
  newComponentSelectedApp.value = appName
  showNewComponentForm.value = true
  showNewAppForm.value = false
  showNewViewForm.value = false
}

const handleFileSelect = (file: ProjectFile) => {
  emit('selectFile', file)
}

const handleFileDelete = (file: ProjectFile) => {
  emit('deleteFile', file)
}

const createNewApp = async () => {
  if (!isValidAppName.value) return
  
  const appName = newAppName.value.trim()
  const appDescription = newAppDescription.value.trim()
  
  // Create the basic app structure files
  const appStructure = [
    // Index file
    {
      name: `frontend/vuejs/src/apps/${appName}/index.ts`,
      type: 'typescript',
      content: `// ${appName} app entry point\nexport * from './router'\nexport * from './stores'\nexport * from './components'\nexport * from './views'\n`
    },
    // Router
    {
      name: `frontend/vuejs/src/apps/${appName}/router/index.ts`,
      type: 'typescript',
      content: `import type { RouteRecordRaw } from 'vue-router'\n\n// Views\nimport ${appName.charAt(0).toUpperCase() + appName.slice(1)}Home from '../views/${appName.charAt(0).toUpperCase() + appName.slice(1)}Home.vue'\n\nconst routes: RouteRecordRaw[] = [\n  {\n    path: '/${appName}',\n    name: '${appName}-home',\n    component: ${appName.charAt(0).toUpperCase() + appName.slice(1)}Home,\n    meta: {\n      requiresAuth: false,\n      title: '${appName.charAt(0).toUpperCase() + appName.slice(1)}'\n    }\n  }\n]\n\nexport { routes }\n`
    },
    // Store
    {
      name: `frontend/vuejs/src/apps/${appName}/stores/index.ts`,
      type: 'typescript',
      content: `// ${appName} stores\nexport * from './${appName}'\n`
    },
    {
      name: `frontend/vuejs/src/apps/${appName}/stores/${appName}.ts`,
      type: 'typescript',
      content: `import { defineStore } from 'pinia'\nimport { ref } from 'vue'\n\nexport const use${appName.charAt(0).toUpperCase() + appName.slice(1)}Store = defineStore('${appName}', () => {\n  // State\n  const loading = ref(false)\n  \n  // Actions\n  const setLoading = (value: boolean) => {\n    loading.value = value\n  }\n  \n  return {\n    loading,\n    setLoading\n  }\n})\n`
    },
    // Components index
    {
      name: `frontend/vuejs/src/apps/${appName}/components/index.ts`,
      type: 'typescript',
      content: `// ${appName} components\nexport * from './atoms'\nexport * from './molecules'\nexport * from './organisms'\n`
    },
    {
      name: `frontend/vuejs/src/apps/${appName}/components/atoms/index.ts`,
      type: 'typescript',
      content: `// ${appName} atomic components\n`
    },
    {
      name: `frontend/vuejs/src/apps/${appName}/components/molecules/index.ts`,
      type: 'typescript',
      content: `// ${appName} molecule components\n`
    },
    {
      name: `frontend/vuejs/src/apps/${appName}/components/organisms/index.ts`,
      type: 'typescript',
      content: `// ${appName} organism components\n`
    },
    // Views
    {
      name: `frontend/vuejs/src/apps/${appName}/views/${appName.charAt(0).toUpperCase() + appName.slice(1)}Home.vue`,
      type: 'vue',
      content: `<template>\n  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">\n    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">\n      <!-- Hero Section -->\n      <div class="text-center mb-16">\n        <h1 class="text-5xl font-bold text-gray-900 mb-6">\n          ${appName.charAt(0).toUpperCase() + appName.slice(1)} App\n        </h1>\n        <p class="text-xl text-gray-600 max-w-3xl mx-auto">\n          ${appDescription || `Welcome to the ${appName} app. This is your new modular Vue.js application.`}\n        </p>\n      </div>\n      \n      <!-- Content Section -->\n      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">\n        <div class="bg-white rounded-lg shadow-lg p-6">\n          <h3 class="text-xl font-semibold text-gray-900 mb-4">Welcome</h3>\n          <p class="text-gray-600">Start building your ${appName} app with modular Vue.js components.</p>\n        </div>\n        <div class="bg-white rounded-lg shadow-lg p-6">\n          <h3 class="text-xl font-semibold text-gray-900 mb-4">Features</h3>\n          <p class="text-gray-600">Add your app-specific features and functionality here.</p>\n        </div>\n        <div class="bg-white rounded-lg shadow-lg p-6">\n          <h3 class="text-xl font-semibold text-gray-900 mb-4">Components</h3>\n          <p class="text-gray-600">Build reusable atomic components for your ${appName} app.</p>\n        </div>\n      </div>\n    </div>\n  </div>\n</template>\n\n<script setup lang="ts">\nimport { ref, onMounted } from 'vue'\nimport { use${appName.charAt(0).toUpperCase() + appName.slice(1)}Store } from '../stores/${appName}'\n\n// Store\nconst ${appName}Store = use${appName.charAt(0).toUpperCase() + appName.slice(1)}Store()\n\n// App state\nconst appTitle = ref('${appName.charAt(0).toUpperCase() + appName.slice(1)} App')\n\n// App lifecycle\nonMounted(() => {\n  console.log('${appName} app mounted')\n  // Add any initialization logic here\n})\n\n// App methods\n// Add your app-specific methods here\n<\/script>\n\n<style scoped>\n/* ${appName} app styles */\n.fade-in {\n  animation: fadeIn 0.5s ease-in;\n}\n\n@keyframes fadeIn {\n  from { opacity: 0; transform: translateY(20px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n</style>\n`
    }
  ]

  // Create all files for the new app
  for (const file of appStructure) {
    emit('createFile', file)
  }

  newAppName.value = ''
  newAppDescription.value = ''
  showNewAppForm.value = false
}

const createVueView = async () => {
  if (!isValidViewName.value) return
  
  const viewName = newViewName.value.trim()
  const routePath = newViewRoute.value.trim() || `/${viewName.toLowerCase()}`
  
  const viewContent = `<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Hero Section -->
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">
          ${viewName}
        </h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">
          Welcome to the ${viewName} page. This is your new web page ready for customization.
        </p>
      </div>
      
      <!-- Content Section -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-4">Section 1</h3>
          <p class="text-gray-600">Add your content here. This web page is ready for you to build upon.</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-4">Section 2</h3>
          <p class="text-gray-600">Customize this section with your own content and components.</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-semibold text-gray-900 mb-4">Section 3</h3>
          <p class="text-gray-600">Use atomic components to build the UI for this web page.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Page state
const pageTitle = ref('${viewName}')

// Page lifecycle
onMounted(() => {
  console.log('${viewName} web page mounted')
  // Add any initialization logic here
})

// Page methods
// Add your page-specific methods here
<\/script>

<style scoped>
/* ${viewName} page styles */
.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
`

  const appPath = newViewSelectedApp.value ? `apps/${newViewSelectedApp.value}` : 'views'
  
  emit('createFile', {
    name: `frontend/vuejs/src/${appPath}/views/${viewName}.vue`,
    type: 'vue',
    content: viewContent
  })

  if (routePath && props.projectId) {
    await updateRouterWithNewView(viewName, routePath)
  }

  newViewName.value = ''
  newViewRoute.value = ''
  newViewSelectedApp.value = ''
  showNewViewForm.value = false
}

const createVueComponent = () => {
  if (!isValidComponentName.value) return
  
  const componentName = newComponentName.value.trim()
  
  const componentContent = `<template>
  <div class="${componentName.toLowerCase()}-component">
    <!-- ${componentName} ${newComponentType.value} component content -->
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

  const appPath = newComponentSelectedApp.value ? `apps/${newComponentSelectedApp.value}` : 'components'
  
  emit('createFile', {
    name: `frontend/vuejs/src/${appPath}/components/${newComponentType.value}/${componentName}.vue`,
    type: 'vue',
    content: componentContent
  })

  newComponentName.value = ''
  newComponentSelectedApp.value = ''
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