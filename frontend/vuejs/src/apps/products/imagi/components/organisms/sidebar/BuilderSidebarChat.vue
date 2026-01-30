<template>
  <div class="flex flex-col h-full bg-[#0a0a0f]/80 backdrop-blur-xl border-r border-white/[0.08]">
    <!-- Conversation Area (scrollable) -->
    <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <ChatConversation
        :messages="ensureValidMessages(store.conversation || [])"
        :is-processing="store.isProcessing"
        @use-example="handleExamplePrompt"
        class="flex-1"
      />
    </div>
    
    <!-- Chat Input Section (fixed at bottom) -->
    <div class="shrink-0 border-t border-white/[0.08] bg-[#0a0a0f]/90 backdrop-blur-xl">
      <div class="p-4 space-y-3">
        <!-- Controls Row -->
        <div class="flex items-center gap-2">
          <!-- File Context Picker -->
          <div class="relative flex-1" ref="filePickerRef">
            <button
              @click="toggleFilePicker"
              class="w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-xs font-medium"
              :class="selectedContextFiles.length > 0
                ? 'bg-white/[0.08] text-white/90 hover:bg-white/[0.12] border border-white/[0.08]' 
                : 'bg-white/[0.02] text-white/40 hover:bg-white/[0.04] hover:text-white/60 border border-white/[0.04]'"
            >
              <i :class="selectedContextFiles.length > 0 ? 'fas fa-file-code' : 'fas fa-plus'" class="text-[10px]"></i>
              <span v-if="selectedContextFiles.length === 1" class="truncate flex-1 text-left">{{ getDisplayName(selectedContextFiles[0].path) }}</span>
              <span v-else-if="selectedContextFiles.length > 1" class="truncate flex-1 text-left">{{ selectedContextFiles.length }} files</span>
              <span v-else class="flex-1 text-left">Add context</span>
              <i class="fas fa-chevron-down text-[8px] opacity-50 transition-transform duration-200" :class="{ 'rotate-180': isFilePickerOpen }"></i>
            </button>
            
            <!-- File Picker Dropdown -->
            <div
              v-if="isFilePickerOpen"
              class="absolute bottom-full left-0 mb-2 w-full max-h-80 flex flex-col bg-[#0a0a0f]/98 backdrop-blur-xl border border-white/[0.06] rounded-xl shadow-2xl shadow-black/60 z-50 overflow-hidden"
            >
              <div class="flex-1 overflow-y-auto p-2">
                <!-- Clear all button -->
                <button
                  v-if="selectedContextFiles.length > 0"
                  @click="clearAllFileSelections"
                  class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs text-white/50 hover:bg-white/[0.04] hover:text-white/80 transition-colors mb-2 border-b border-white/[0.04] pb-3"
                >
                  <i class="fas fa-times text-[10px]"></i>
                  <span>Clear all ({{ selectedContextFiles.length }})</span>
                </button>
                
                <!-- Files grouped by category -->
                <div v-if="selectedApp" class="space-y-1">
                  <!-- Pages -->
                  <div v-if="appPages.length > 0">
                    <div class="px-3 py-1.5 text-[10px] font-semibold text-white/25 uppercase tracking-wider">Pages</div>
                    <button
                      v-for="file in appPages"
                      :key="file.path"
                      @click="toggleFileContext(file)"
                      class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-all"
                      :class="isFileSelected(file.path)
                        ? 'bg-white/[0.08] text-white/90 border border-white/[0.10]' 
                        : 'text-white/50 hover:bg-white/[0.03] hover:text-white/70 border border-transparent'"
                    >
                      <div class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                        :class="isFileSelected(file.path)
                          ? 'bg-white/[0.15] border-white/[0.25]'
                          : 'bg-white/[0.02] border-white/[0.10]'"
                      >
                        <i v-if="isFileSelected(file.path)" class="fas fa-check text-[8px] text-white"></i>
                      </div>
                      <i class="fas fa-window-maximize text-[10px] text-white/40"></i>
                      <span class="truncate flex-1">{{ getDisplayName(file.path) }}</span>
                    </button>
                  </div>
                  
                  <!-- Blocks -->
                  <div v-if="appBlocks.length > 0">
                    <div class="px-3 py-1.5 text-[10px] font-semibold text-white/25 uppercase tracking-wider mt-2">Blocks</div>
                    <button
                      v-for="file in appBlocks"
                      :key="file.path"
                      @click="toggleFileContext(file)"
                      class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-all"
                      :class="isFileSelected(file.path)
                        ? 'bg-white/[0.08] text-white/90 border border-white/[0.10]' 
                        : 'text-white/50 hover:bg-white/[0.03] hover:text-white/70 border border-transparent'"
                    >
                      <div class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                        :class="isFileSelected(file.path)
                          ? 'bg-white/[0.15] border-white/[0.25]'
                          : 'bg-white/[0.02] border-white/[0.10]'"
                      >
                        <i v-if="isFileSelected(file.path)" class="fas fa-check text-[8px] text-white"></i>
                      </div>
                      <i class="fas fa-puzzle-piece text-[10px] text-white/40"></i>
                      <span class="truncate flex-1">{{ getDisplayName(file.path) }}</span>
                    </button>
                  </div>
                  
                  <!-- Data -->
                  <div v-if="appStores.length > 0">
                    <div class="px-3 py-1.5 text-[10px] font-semibold text-white/25 uppercase tracking-wider mt-2">Data</div>
                    <button
                      v-for="file in appStores"
                      :key="file.path"
                      @click="toggleFileContext(file)"
                      class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-all"
                      :class="isFileSelected(file.path)
                        ? 'bg-white/[0.08] text-white/90 border border-white/[0.10]' 
                        : 'text-white/50 hover:bg-white/[0.03] hover:text-white/70 border border-transparent'"
                    >
                      <div class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                        :class="isFileSelected(file.path)
                          ? 'bg-white/[0.15] border-white/[0.25]'
                          : 'bg-white/[0.02] border-white/[0.10]'"
                      >
                        <i v-if="isFileSelected(file.path)" class="fas fa-check text-[8px] text-white"></i>
                      </div>
                      <i class="fas fa-database text-[10px] text-white/40"></i>
                      <span class="truncate flex-1">{{ getDisplayName(file.path) }}</span>
                    </button>
                  </div>
                  
                  <!-- Empty state -->
                  <div v-if="appPages.length === 0 && appBlocks.length === 0 && appStores.length === 0" class="px-3 py-4 text-center text-xs text-white/30">
                    No files in this app yet
                  </div>
                </div>
                
                <!-- No app selected -->
                <div v-else class="px-3 py-4 text-center text-xs text-white/30">
                  Select an app first
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Model Selector and Mode Toggle Row -->
        <div class="flex items-center gap-2">
          <!-- Model Selector -->
          <div class="flex-1">
            <ModelSelector 
              :models="store.availableModels || []"
              :model-id="store.selectedModelId"
              :mode="store.mode || 'chat'"
              @update:model-id="handleModelSelect"
              compact
            />
          </div>
          
          <!-- Mode Toggle -->
          <div class="flex items-center bg-white/[0.02] rounded-lg p-0.5 border border-white/[0.04]">
            <button
              @click="handleModeSwitch('chat')"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
              :class="store.mode === 'chat' 
                ? 'bg-white/[0.08] text-white/90 shadow-sm' 
                : 'text-white/40 hover:text-white/60 hover:bg-white/[0.03]'"
            >
              <i class="fas fa-comments text-[10px]"></i>
              <span>Ask</span>
            </button>
            <button
              @click="handleModeSwitch('build')"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
              :class="store.mode === 'build' 
                ? 'bg-white/[0.08] text-white/90 shadow-sm' 
                : 'text-white/40 hover:text-white/60 hover:bg-white/[0.03]'"
            >
              <i class="fas fa-magic text-[10px]"></i>
              <span>Build</span>
            </button>
          </div>
        </div>
        
        <!-- Text Input Area -->
        <div class="relative">
          <textarea
            ref="promptTextarea"
            v-model="prompt"
            :placeholder="promptPlaceholder"
            @keydown.enter.exact.prevent="handlePrompt"
            @keydown.enter.shift.exact="() => {}"
            @input="autoResizeTextarea"
            :disabled="store.isProcessing"
            rows="1"
            class="w-full bg-white/[0.03] border border-white/[0.06] text-white/90 placeholder-white/30 text-sm px-3 pr-12 py-2.5 resize-none focus:outline-none focus:border-white/[0.12] rounded-lg leading-relaxed transition-all duration-200"
            style="min-height: 42px; max-height: 120px;"
          ></textarea>
          
          <!-- Send Button -->
          <div class="absolute right-2 bottom-2">
            <button
              @click="handlePrompt"
              :disabled="!prompt.trim() || store.isProcessing"
              class="flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-200"
              :class="prompt.trim() && !store.isProcessing
                ? 'bg-white/[0.12] text-white hover:bg-white/[0.18] active:bg-white/[0.15]'
                : 'bg-white/[0.03] text-white/15 cursor-not-allowed'"
            >
              <i v-if="store.isProcessing" class="fas fa-circle-notch fa-spin text-xs"></i>
              <i v-else class="fas fa-arrow-up text-xs"></i>
            </button>
          </div>
        </div>
        
        <!-- Context Info -->
        <div v-if="selectedContextFiles.length > 0" class="flex items-center gap-2 text-[10px] text-white/30">
          <i class="fas fa-file-code text-[8px]"></i>
          <span v-if="selectedContextFiles.length === 1">{{ getDisplayName(selectedContextFiles[0].path) }}</span>
          <span v-else>{{ selectedContextFiles.length }} files selected</span>
        </div>
        
        <!-- Hint -->
        <div v-else-if="store.mode === 'build'" class="flex items-center gap-2 text-[10px] text-white/25">
          <i class="fas fa-info-circle text-[8px]"></i>
          <span>Select a file to make changes</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { ChatConversation } from '../../organisms/chat'
import ModelSelector from '../../molecules/sidebar/ModelSelector.vue'
import type { ProjectFile, BuilderMode } from '../../../types/components'
import type { AIMessage } from '../../../types/index'

// Props
const props = defineProps<{
  selectedApp: any
  onPromptSubmit: (prompt: string) => Promise<void>
  onModelSelect: (modelId: string) => Promise<void>
  onModeSwitch: (mode: BuilderMode) => Promise<void>
  onExamplePrompt: (example: string) => void
}>()

const store = useAgentStore()
const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)
const filePickerRef = ref<HTMLElement | null>(null)
const isFilePickerOpen = ref(false)
const selectedContextFiles = ref<ProjectFile[]>([])

// Helper to check if file is a barrel file
function isBarrelFile(path: string): boolean {
  const filename = path.split('/').pop()?.toLowerCase() || ''
  return filename === 'index.ts' || filename === 'index.js' || filename === 'index.vue'
}

// Computed: files in the selected app categorized
const appPages = computed(() => {
  if (!props.selectedApp?.files) return []
  return props.selectedApp.files.filter((f: ProjectFile) => 
    /\/views\//i.test(f.path) && !isBarrelFile(f.path)
  )
})

const appBlocks = computed(() => {
  if (!props.selectedApp?.files) return []
  return props.selectedApp.files.filter((f: ProjectFile) => 
    /\/components\//i.test(f.path) && !isBarrelFile(f.path)
  )
})

const appStores = computed(() => {
  if (!props.selectedApp?.files) return []
  return props.selectedApp.files.filter((f: ProjectFile) => 
    (/\/stores\//i.test(f.path) || /store\.(ts|js)$/i.test(f.path)) && !isBarrelFile(f.path)
  )
})

// Helper to get friendly display name from file path
function getDisplayName(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  const filename = parts[parts.length - 1]
  return filename.replace(/\.(vue|ts|js|tsx|jsx)$/, '')
}

// Helper to determine item kind from path
function getItemKind(path: string): string {
  if (!path) return 'item'
  if (/\/views\//i.test(path)) return 'page'
  if (/\/components\//i.test(path)) return 'block'
  if (/\/stores\//i.test(path)) return 'data store'
  return 'item'
}

const promptPlaceholder = computed(() => {
  if (store.mode === 'chat') {
    if (store.selectedFile) {
      return `Ask me anything about "${getDisplayName(store.selectedFile.path)}"...`
    }
    return 'Ask me anything about your project...'
  } else {
    if (store.selectedFile) {
      return `Describe changes to "${getDisplayName(store.selectedFile.path)}"...`
    }
    return 'Select a file to start making changes...'
  }
})

// Methods
function ensureValidMessages(messages: any[]): AIMessage[] {
  if (!messages || !Array.isArray(messages)) {
    return []
  }
  
  const filteredMessages = messages.filter(m => {
    if (m && m.role === 'system') {
      if (m.content && (
        m.content.includes('Switched to file:') || 
        m.content.includes('Switched to build mode') ||
        m.content.includes('previously selected file')
      )) {
        return false
      }
    }
    return true
  })
  
  const validMessages = filteredMessages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => {
      let content = m.content || ''
      const messageId = m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
      
      return {
        role: m.role,
        content: content,
        code: m.code || '',
        timestamp: m.timestamp || new Date().toISOString(),
        id: messageId
      }
    }) as AIMessage[]
  
  return validMessages
}

function autoResizeTextarea() {
  if (!promptTextarea.value) return
  promptTextarea.value.style.height = 'auto'
  const scrollHeight = promptTextarea.value.scrollHeight
  const maxHeight = 120
  promptTextarea.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

async function handlePrompt() {
  if (!prompt.value.trim() || store.isProcessing) return
  
  const promptText = prompt.value
  prompt.value = '' // Clear immediately
  
  // Reset textarea height
  if (promptTextarea.value) {
    promptTextarea.value.style.height = '42px'
  }
  
  await props.onPromptSubmit(promptText)
}

function handleExamplePrompt(exampleText: string) {
  prompt.value = exampleText
  handlePrompt()
}

async function handleModelSelect(modelId: string) {
  await props.onModelSelect(modelId)
}

async function handleModeSwitch(mode: BuilderMode) {
  await props.onModeSwitch(mode)
}

function toggleFilePicker() {
  isFilePickerOpen.value = !isFilePickerOpen.value
}

function toggleFileContext(file: ProjectFile) {
  const index = selectedContextFiles.value.findIndex(f => f.path === file.path)
  if (index >= 0) {
    selectedContextFiles.value.splice(index, 1)
  } else {
    selectedContextFiles.value.push(file)
  }
  
  if (selectedContextFiles.value.length > 0) {
    store.selectFile(selectedContextFiles.value[0])
  } else {
    store.setSelectedFile(null)
  }
}

function isFileSelected(filePath: string): boolean {
  return selectedContextFiles.value.some(f => f.path === filePath)
}

function clearAllFileSelections() {
  selectedContextFiles.value = []
  store.setSelectedFile(null)
}

function handleClickOutside(event: MouseEvent) {
  if (filePickerRef.value && !filePickerRef.value.contains(event.target as Node)) {
    isFilePickerOpen.value = false
  }
}

// Watch for changes to the selected file in store and sync with selectedContextFiles
watch(() => store.selectedFile, (newFile) => {
  if (newFile && !selectedContextFiles.value.some(f => f.path === newFile.path)) {
    selectedContextFiles.value = [newFile]
  } else if (!newFile) {
    selectedContextFiles.value = []
  }
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Custom scrollbar */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(139, 92, 246, 0.5);
}
</style>
