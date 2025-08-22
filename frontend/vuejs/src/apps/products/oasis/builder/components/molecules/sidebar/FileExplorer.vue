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
        <div v-if="Object.keys(vueFilesByDirectory).length > 0">
          <ActionButton
            :text="'Create New App'"
            icon="plus"
            :fullWidth="true"
            size="sm"
            @click="toggleNewAppForm"
          />
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
            class="w-full text-xs bg-dark-950/90 border border-dark-700/60 rounded-md p-2 text-white placeholder-gray-500 outline-none focus:outline-none focus:ring-0 focus:border-transparent shadow-none focus:shadow-none transition-all duration-200"
            @keydown.enter="createNewApp"
          />
          
          <input
            v-model="newAppDescription"
            type="text"
            placeholder="App description (optional)"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/60 rounded-md p-2 text-white placeholder-gray-500 outline-none focus:outline-none focus:ring-0 focus:border-transparent shadow-none focus:shadow-none transition-all duration-200"
            @keydown.enter="createNewApp"
          />
          
          <p class="text-xxs text-gray-500">
            App will be created with Vue.js best practices structure (views, components, stores, router)
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewAppForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <ActionButton
              :text="'Create App'"
              icon="plus"
              :disabled="!isValidAppName"
              size="sm"
              @click="createNewApp"
            />
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
        <div v-if="showNewViewForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-primary-700/50 space-y-2">
          <h3 class="text-xs font-medium text-primary-300">Create New View</h3>
          
          <select
            v-model="newViewSelectedApp"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(139,92,246,0.25)] transition-all duration-200"
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
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(139,92,246,0.25)] transition-all duration-200"
            @keydown.enter="createVueView"
          />
          
          <input
            v-model="newViewRoute"
            type="text"
            placeholder="Route path: e.g., /about, /contact, /services"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(139,92,246,0.25)] transition-all duration-200"
            @keydown.enter="createVueView"
          />
          
          <p class="text-xxs text-gray-500">
            View will be created in {{ newViewSelectedApp || '[selected app]' }}/views/ directory
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewViewForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <button
              @click="createVueView"
              :disabled="!isValidViewName"
              class="group relative text-xs rounded-md px-2 py-1 border bg-gradient-to-r from-primary-600/85 to-violet-600/85 border-primary-400/40 disabled:bg-gray-700 disabled:text-gray-500 disabled:border-transparent text-white transition-all duration-200 focus:outline-none"
            >
              <!-- Subtle glow effect on hover (only when enabled) -->
              <!-- hover glow removed -->
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
        <div v-if="showNewComponentForm" class="mb-4 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg border border-primary-700/50 space-y-2">
          <h3 class="text-xs font-medium text-primary-300">Create New Component</h3>
          
          <select
            v-model="newComponentSelectedApp"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(139,92,246,0.25)] transition-all duration-200"
          >
            <option value="">Select an app...</option>
            <option v-for="app in availableApps" :key="app" :value="app">
              {{ app.charAt(0).toUpperCase() + app.slice(1) }} App
            </option>
          </select>
          
          <select
            v-model="newComponentType"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(139,92,246,0.25)] transition-all duration-200"
          >
            <option value="atoms">Atom (Basic UI element)</option>
            <option value="molecules">Molecule (Simple combination)</option>
            <option value="organisms">Organism (Complex component)</option>
          </select>
          
          <div class="p-2 bg-violet-950/20 rounded-md border border-primary-700/30">
            <p class="text-xxs text-primary-300 mb-1">{{ getComponentTypeDescription(newComponentType).title }}</p>
            <p class="text-xxs text-gray-400">{{ getComponentTypeDescription(newComponentType).description }}</p>
          </div>
          
          <input
            v-model="newComponentName"
            type="text"
            placeholder="e.g., PrimaryButton, SearchInput, UserAvatar"
            class="w-full text-xs bg-dark-950/90 border border-dark-700/80 rounded-md p-2 text-white placeholder-gray-500 focus:outline-none focus:ring-[1.5px] focus:ring-offset-0 focus:ring-primary-500/60 focus:border-transparent shadow-sm focus:shadow-[0_0_8px_rgba(139,92,246,0.25)] transition-all duration-200"
            @keydown.enter="createVueComponent"
          />
          
          <p class="text-xxs text-gray-500">
            Component will be created in {{ newComponentSelectedApp || '[selected app]' }}/components/{{ newComponentType }}/
          </p>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="toggleNewComponentForm"
              class="text-xs rounded-md px-2 py-1 text-gray-400 transition-colors focus:outline-none"
            >
              Cancel
            </button>
            <button
              @click="createVueComponent"
              :disabled="!isValidComponentName"
              class="group relative text-xs rounded-md px-2 py-1 border bg-gradient-to-r from-primary-600/85 to-violet-600/85 border-primary-400/40 disabled:bg-gray-700 disabled:text-gray-500 disabled:border-transparent text-white transition-all duration-200 focus:outline-none"
            >
              <!-- Subtle glow effect on hover (only when enabled) -->
              <!-- hover glow removed -->
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
          :class="{'border-primary-500/30 bg-violet-900/10 shadow-[0_0_10px_rgba(139,92,246,0.12)]': currentDirectory === dirName}"
        >
          <div 
            class="group flex items-center text-xs py-1.5 px-2.5 rounded-md transition-all duration-200 cursor-pointer mb-2"
            :class="[
              currentDirectory === dirName 
                ? 'bg-gradient-to-r from-primary-500/20 to-violet-500/10 text-white border border-primary-500/30' 
                : 'text-primary-300 border border-transparent'
            ]"
            @click="selectDirectory(dirName)"
          >
            <i 
              class="fas fa-folder-open mr-2 w-4 text-center transition-colors duration-200"
              :class="getVueDirectoryIconClass(dirName)"
            ></i>
            <span class="font-medium">{{ formatVueDirectoryName(dirName) }}</span>
            <span class="ml-auto text-xxs bg-dark-700/80 text-primary-300 py-0.5 px-1.5 rounded-full">
              {{ dirFiles.length }}
            </span>
          </div>
          
          <!-- App Files Tree with enhanced styling -->
          <div v-if="currentDirectory === dirName" class="space-y-1.5 pl-2">
            <!-- Add View/Component buttons for current app -->
            <div class="mb-3 grid grid-cols-2 gap-1.5">
              <button 
                @click="openCreateViewForApp(dirName)" 
                class="group relative text-xxs rounded-md px-2 py-1.5 border border-white/10 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white shadow-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
                :title="`Create view in ${dirName}`"
              >
                <div class="relative flex items-center justify-center">
                  <i class="fas fa-file-alt mr-1 text-xxs"></i> 
                  <span>Add View</span>
                </div>
              </button>
              <button 
                @click="openCreateComponentForApp(dirName)" 
                class="group relative text-xxs rounded-md px-2 py-1.5 border border-white/10 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white shadow-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
                :title="`Create component in ${dirName}`"
              >
                <div class="relative flex items-center justify-center">
                  <i class="fas fa-puzzle-piece mr-1 text-xxs"></i> 
                  <span>Add Component</span>
                </div>
              </button>
            </div>
            
            <!-- File tree structure -->
            <div class="space-y-1">
              <!-- Render directory structure recursively -->
              <template v-for="(dirData, dirName) in fileStructure" :key="String(dirName)">
                <!-- Root level files -->
                <template v-if="String(dirName) === 'root' && dirData.files">
                  <FileTreeItem
                    v-for="file in dirData.files"
                    :key="file.path"
                    :file="file"
                    :is-selected="selectedFile?.path === file.path"
                    @select="handleFileSelect"
                    @delete="handleFileDelete"
                  />
                </template>
                
                <!-- Directory with potential subdirectories -->
                <div v-else-if="dirData.name" class="mb-1">
                  <!-- Directory header -->
                  <div 
                    @click="toggleDirectory(String(dirName))"
                    class="flex items-center py-1.5 px-2 rounded-md cursor-pointer transition-colors duration-200"
                  >
                    <i 
                      :class="expandedDirs.has(String(dirName)) ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"
                      class="text-xxs text-gray-500 mr-2 w-2"
                    ></i>
                    <i :class="getDirectoryIcon(String(dirName))" class="text-xs mr-2"></i>
                    <span class="text-xs text-gray-300 font-medium">{{ dirName }}</span>
                    <span class="ml-auto text-xxs text-gray-500">
                      {{ dirData.files.length + Object.keys(dirData.subdirectories || {}).length }}
                    </span>
                  </div>
                  
                  <!-- Directory contents when expanded -->
                  <div v-if="expandedDirs.has(String(dirName))" class="ml-4 space-y-1">
                    <!-- Files in this directory -->
                    <FileTreeItem
                      v-for="file in dirData.files"
                      :key="file.path"
                      :file="file"
                      :is-selected="selectedFile?.path === file.path"
                      @select="handleFileSelect"
                      @delete="handleFileDelete"
                    />
                    
                    <!-- Subdirectories (like atoms, molecules, organisms) -->
                    <template v-for="(subDirData, subDirName) in dirData.subdirectories" :key="String(subDirName)">
                      <div class="mb-1">
                        <!-- Subdirectory header -->
                        <div 
                          @click="toggleDirectory(`${String(dirName)}/${String(subDirName)}`)"
                          class="flex items-center py-1 px-2 rounded-md cursor-pointer transition-colors duration-200"
                        >
                          <i 
                            :class="expandedDirs.has(`${String(dirName)}/${String(subDirName)}`) ? 'fas fa-chevron-down' : 'fas fa-chevron-right'"
                            class="text-xxs text-gray-500 mr-2 w-2"
                          ></i>
                          <i :class="getDirectoryIcon(String(subDirName))" class="text-xs mr-2"></i>
                          <span class="text-xs text-gray-300 font-medium">{{ subDirName }}</span>
                          <span class="ml-auto text-xxs text-gray-500">{{ subDirData.files.length }}</span>
                        </div>
                        
                        <!-- Subdirectory files when expanded -->
                        <div v-if="expandedDirs.has(`${String(dirName)}/${String(subDirName)}`)" class="ml-4 space-y-1">
                          <FileTreeItem
                            v-for="file in subDirData.files"
                            :key="file.path"
                            :file="file"
                            :is-selected="selectedFile?.path === file.path"
                            @select="handleFileSelect"
                            @delete="handleFileDelete"
                          />
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
              </template>
            </div>
            
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
            <ActionButton
              :text="'Create New App'"
              icon="plus"
              :fullWidth="true"
              size="sm"
              @click="toggleNewAppForm"
            />
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
import ActionButton from '../../atoms/buttons/ActionButton.vue'

// Create hierarchical file structure for current app
const fileStructure = computed(() => {
  const currentFiles = vueFilesByDirectory.value[currentDirectory.value] || []
  
  const createDirectoryStructure = () => {
    const structure: any = {}
    
    currentFiles.forEach(file => {
      const relativePath = file.path.includes('/src/apps/') 
        ? file.path.split('/src/apps/')[1].split('/').slice(1).join('/') // Remove app name
        : file.path
      
      const pathParts = relativePath.split('/')
      const fileName = pathParts.pop() // Remove filename
      
      if (pathParts.length === 0) {
        // Root level file
        if (!structure.root) {
          structure.root = { files: [], subdirectories: {} }
        }
        structure.root.files.push(file)
      } else {
        // File in subdirectory - build nested structure
        let currentLevel = structure
        let currentPath = ''
        
        pathParts.forEach((part, index) => {
          currentPath = currentPath ? `${currentPath}/${part}` : part
          
          if (!currentLevel[part]) {
            currentLevel[part] = {
              name: part,
              path: currentPath,
              files: [],
              subdirectories: {}
            }
          }
          
          if (index === pathParts.length - 1) {
            // Last directory - add the file here
            currentLevel[part].files.push(file)
          } else {
            // Navigate deeper into subdirectories
            currentLevel = currentLevel[part].subdirectories
          }
        })
      }
    })
    
    return structure
  }
  
  return createDirectoryStructure()
})

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

// Filter files to show all app-based structure
const vueFiles = computed(() => {
  return props.files.filter(file => {
    const path = file.path.toLowerCase()
    const normalizedPath = path.replace(/\\/g, '/') // Handle Windows paths
    
    // Include all files from any app directory
    if (normalizedPath.includes('/src/apps/')) {
      // Include all relevant file types for Vue.js apps
      const relevantExtensions = ['.vue', '.ts', '.js', '.jsx', '.tsx', '.json', '.css', '.scss', '.sass', '.less', '.md', '.html']
      const hasRelevantExtension = relevantExtensions.some(ext => normalizedPath.endsWith(ext))
      
      // Also include files without extensions (like index files, config files)
      const fileName = normalizedPath.split('/').pop() || ''
      const hasNoExtension = !fileName.includes('.')
      const isConfigFile = ['index', 'main', 'app'].some(name => fileName.startsWith(name))
      
      // Include if it has a relevant extension or is a config file
      if (hasRelevantExtension || (hasNoExtension && isConfigFile)) {
        return true
      }
    }
    
    return false
  })
})

// Group files by app with hierarchical directory structure
const vueFilesByDirectory = computed(() => {
  const result: Record<string, any> = {}
  
  vueFiles.value.forEach(file => {
    const normalizedPath = file.path.toLowerCase().replace(/\\/g, '/')
    
    // Extract app name from path like: frontend/vuejs/src/apps/{appname}/
    const appMatch = normalizedPath.match(/\/src\/apps\/([^\/]+)\/(.*)/)
    if (appMatch) {
      const appName = appMatch[1]
      const appDisplayName = appName.charAt(0).toUpperCase() + appName.slice(1)
      const relativePath = appMatch[2] // Path within the app
      
      const dirKey = `${appDisplayName} App`
      
      if (!result[dirKey]) {
        result[dirKey] = {
          files: [],
          subdirectories: {}
        }
      }
      
      // Parse the relative path to create directory structure
      const pathParts = relativePath.split('/')
      const fileName = pathParts.pop() // Remove the filename
      
      if (pathParts.length === 0) {
        // File is in app root
        result[dirKey].files.push(file)
      } else {
        // File is in a subdirectory - create nested structure
        let currentLevel = result[dirKey].subdirectories
        let currentPath = ''
        
        pathParts.forEach((part, index) => {
          currentPath = currentPath ? `${currentPath}/${part}` : part
          
          if (!currentLevel[part]) {
            currentLevel[part] = {
              name: part,
              path: currentPath,
              files: [],
              subdirectories: {}
            }
          }
          
          if (index === pathParts.length - 1) {
            // Last directory - add the file here
            currentLevel[part].files.push(file)
          } else {
            // Navigate deeper
            currentLevel = currentLevel[part].subdirectories
          }
        })
      }
    }
  })
  
  // Convert to flat structure for the current UI (we'll enhance this later for tree view)
  const flatResult: Record<string, ProjectFile[]> = {}
  
  Object.keys(result).forEach(appKey => {
    const appData = result[appKey]
    let allFiles: ProjectFile[] = [...appData.files]
    
    // Flatten subdirectories for now
    const flattenDirectory = (dir: any) => {
      allFiles = allFiles.concat(dir.files)
      Object.values(dir.subdirectories).forEach((subDir: any) => {
        flattenDirectory(subDir)
      })
    }
    
    Object.values(appData.subdirectories).forEach((dir: any) => {
      flattenDirectory(dir)
    })
    
    // Sort files by path for better organization
    allFiles.sort((a, b) => (a.path || '').localeCompare(b.path || ''))
    
    flatResult[appKey] = allFiles
  })
  
  // Set current directory to first available app
  if (!currentDirectory.value && Object.keys(flatResult).length > 0) {
    // Try to find auth app first, then home, then first available
    const priorityOrder = ['Auth App', 'Home App', 'Products App']
    for (const priority of priorityOrder) {
      if (flatResult[priority]) {
        currentDirectory.value = priority
        break
      }
    }
    // If no priority directory found, use first available
    if (!currentDirectory.value) {
      currentDirectory.value = Object.keys(flatResult)[0]
    }
  }
  
  return flatResult
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

// Directory expansion state - auto-expand common directories including atomic design structure
const expandedDirs = ref<Set<string>>(new Set([
  'views', 
  'components', 
  'components/atoms', 
  'components/molecules', 
  'components/organisms'
]))

const toggleDirectory = (dirName: string) => {
  if (expandedDirs.value.has(dirName)) {
    expandedDirs.value.delete(dirName)
  } else {
    expandedDirs.value.add(dirName)
  }
}

const getDirectoryIcon = (dirName: string) => {
  const iconMap: Record<string, string> = {
    // Main directories
    views: 'fas fa-eye text-green-400',
    components: 'fas fa-puzzle-piece text-blue-400',
    stores: 'fas fa-database text-orange-400',
    router: 'fas fa-route text-purple-400',
    services: 'fas fa-cogs text-yellow-400',
    types: 'fas fa-code text-red-400',
    layouts: 'fas fa-columns text-cyan-400',
    composables: 'fas fa-magic text-emerald-400',
    
    // Atomic Design Structure
    atoms: 'fas fa-atom text-blue-300',
    molecules: 'fas fa-share-alt text-blue-400', 
    organisms: 'fas fa-sitemap text-blue-500',
    
    // Component subdirectories
    buttons: 'fas fa-hand-pointer text-indigo-400',
    forms: 'fas fa-edit text-green-400',
    inputs: 'fas fa-keyboard text-gray-400',
    cards: 'fas fa-id-card text-yellow-400',
    modals: 'fas fa-window-restore text-purple-400',
    navigation: 'fas fa-compass text-cyan-400',
    headers: 'fas fa-heading text-orange-400',
    footers: 'fas fa-grip-lines text-gray-400',
    sidebar: 'fas fa-columns text-blue-300',
    
    // Other common directories
    utils: 'fas fa-tools text-gray-400',
    helpers: 'fas fa-hand-holding-heart text-pink-400',
    constants: 'fas fa-lock text-red-300',
    assets: 'fas fa-file-image text-green-300',
    styles: 'fas fa-palette text-purple-300'
  }
  return iconMap[dirName.toLowerCase()] || 'fas fa-folder text-gray-400'
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

/* Directory tree styles */
.directory-item {
  transition: all 0.2s ease;
}

.file-tree-indent {
  border-left: 1px solid rgba(75, 85, 99, 0.3);
  margin-left: 0.5rem;
}
</style> 