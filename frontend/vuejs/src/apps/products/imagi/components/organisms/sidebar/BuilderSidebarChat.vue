<template>
  <div v-if="!isCollapsed" class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] border-r border-gray-200 dark:border-white/[0.08] transition-colors duration-300">
    <!-- Header: manager toggle + instance title -->
    <div class="shrink-0 flex items-center gap-2 px-3 py-2 border-b border-gray-200 dark:border-white/[0.08]">
      <div class="relative group">
        <button
          class="flex items-center justify-center w-8 h-8 rounded-md text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-800/70 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
          @click="$emit('toggleManager')"
        >
          <i :class="['fas text-sm transition-transform duration-300', isManagerOpen ? 'fa-chevron-left' : 'fa-chevron-right']"></i>
        </button>
        <div
          class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-gray-900 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-gray-900 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          {{ isManagerOpen ? 'Hide agent manager' : 'Show agent manager' }}
        </div>
      </div>
      <div class="flex-1 min-w-0 text-xs font-semibold text-gray-700 dark:text-white/80 truncate">
        {{ activeInstance?.title || 'New instance' }}
      </div>
    </div>

    <!-- Conversation Area (scrollable) -->
    <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <ChatConversation
        :messages="ensureValidMessages(activeInstance?.conversation || [])"
        :is-processing="!!activeInstance?.isProcessing"
        @use-example="handleExamplePrompt"
        class="flex-1"
      />
    </div>

    <!-- Chat Input Section (fixed at bottom) -->
    <div class="shrink-0 border-t border-gray-200 dark:border-white/[0.08] bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
      <div class="p-4 space-y-3">
        <!-- Text Input Area -->
        <div class="relative">
          <textarea
            ref="promptTextarea"
            v-model="prompt"
            :placeholder="promptPlaceholder"
            @keydown.enter.exact.prevent="handlePrompt"
            @keydown.enter.shift.exact="() => {}"
            @input="autoResizeTextarea"
            :disabled="!activeInstance || activeInstance.isProcessing"
            rows="5"
            class="w-full bg-gray-50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.06] text-gray-900 dark:text-white/90 placeholder-gray-400 dark:placeholder-white/30 text-sm px-3 pr-12 py-3 pb-10 resize-none rounded-lg leading-relaxed"
            style="min-height: 130px; max-height: 280px;"
          ></textarea>

          <!-- Mode and Model Dropdowns (Bottom Left inside input) -->
          <div class="absolute left-2 bottom-2 flex items-center gap-1.5">
            <!-- Mode Dropdown -->
            <div class="dropdown-wrapper">
              <i :class="['dropdown-icon fas', activeInstance?.mode === 'agent' ? 'fa-robot' : 'fa-comment-dots']"></i>
              <select
                :value="activeInstance?.mode ?? 'chat'"
                :disabled="!activeInstance"
                @change="handleModeSwitch(($event.target as HTMLSelectElement).value as BuilderMode)"
                class="dropdown-select dropdown-select--with-icon text-xs"
              >
                <option value="chat">Chat</option>
                <option value="agent">Agent</option>
              </select>
            </div>

            <!-- Model Dropdown -->
            <div class="dropdown-wrapper">
              <i class="fas fa-microchip dropdown-icon"></i>
              <select
                :value="activeInstance?.selectedModelId ?? ''"
                :disabled="!activeInstance"
                @change="handleModelSelect(($event.target as HTMLSelectElement).value)"
                class="dropdown-select dropdown-select--with-icon text-xs"
              >
                <option
                  v-for="model in modelOptions"
                  :key="model.id"
                  :value="model.id"
                >
                  {{ model.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Send Button -->
          <div class="absolute right-3 bottom-3">
            <button
              @click="handlePrompt"
              :disabled="!prompt.trim() || !activeInstance || activeInstance.isProcessing"
              class="btn-3d flex items-center justify-center w-9 h-9 rounded-full transition-all duration-300"
              :class="prompt.trim() && activeInstance && !activeInstance.isProcessing
                ? 'bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 border border-gray-700/50 dark:border-gray-300/50 shadow-lg hover:shadow-xl'
                : 'bg-gradient-to-b from-gray-200 via-gray-100 to-gray-50 dark:from-white/[0.08] dark:via-white/[0.05] dark:to-white/[0.03] text-gray-400 dark:text-white/40 cursor-not-allowed border border-gray-300/70 dark:border-white/[0.12] shadow-sm'"
            >
              <i v-if="activeInstance?.isProcessing" class="fas fa-circle-notch fa-spin text-sm"></i>
              <i v-else class="fas fa-arrow-up text-sm"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { ChatConversation } from '../../organisms/chat'
import type { BuilderMode } from '../../../types/components'
import type { AIMessage, AIModel } from '../../../types/index'

// Props
const props = defineProps<{
  selectedApp: any
  onPromptSubmit: (prompt: string) => Promise<void>
  onModelSelect: (modelId: string) => Promise<void>
  onModeSwitch: (mode: BuilderMode) => Promise<void>
  onExamplePrompt: (example: string) => void
  isCollapsed?: boolean
  isManagerOpen?: boolean
}>()

defineEmits<{
  (e: 'toggleManager'): void
}>()

const store = useAgentStore()
const activeInstance = computed(() => store.activeInstance)
const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)

const modelOptions = computed<AIModel[]>(() => {
  const available = (store.availableModels || []).filter(model => model.id === 'gpt-5.5')
  if (available.length > 0) {
    return available
  }
  return [
    {
      id: 'gpt-5.5',
      name: 'GPT 5.5',
      provider: 'openai'
    } as AIModel
  ]
})

// Helper to get friendly display name from file path
function getDisplayName(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  const filename = parts[parts.length - 1] ?? ''
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
  if (activeInstance.value?.mode === 'agent') {
    return 'Ask me to edit files or chat about your project...'
  }
  return 'What would you like to build today?'
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
  const maxHeight = 280
  promptTextarea.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

async function handlePrompt() {
  if (!prompt.value.trim() || !activeInstance.value || activeInstance.value.isProcessing) return
  
  const promptText = prompt.value
  prompt.value = '' // Clear immediately
  
  // Reset textarea height
  if (promptTextarea.value) {
    promptTextarea.value.style.height = '130px'
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
</script>

<style scoped>
/* Dropdown wrapper provides room for leading icon */
.dropdown-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.dropdown-icon {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.6875rem;
  color: rgba(107, 114, 128, 0.8);
  pointer-events: none;
  transition: color 0.2s ease;
  z-index: 1;
}

.dark .dropdown-icon {
  color: rgba(255, 255, 255, 0.55);
}

.dropdown-wrapper:hover .dropdown-icon {
  color: rgb(55, 65, 81);
}

.dark .dropdown-wrapper:hover .dropdown-icon {
  color: rgba(255, 255, 255, 0.85);
}

/* Enhanced dropdown select */
.dropdown-select {
  background-image: url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27rgba(107,114,128,0.8)%27 stroke-width=%272.5%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpolyline points=%276 9 12 15 18 9%27%3e%3c/polyline%3e%3c/svg%3e');
  background-repeat: no-repeat;
  background-position: right 0.55rem center;
  background-size: 0.85em;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(209, 213, 219, 0.8);
  color: rgb(55, 65, 81);
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 0.375rem 1.75rem 0.375rem 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  transition: all 0.18s ease;
  outline: none;
}

.dropdown-select--with-icon {
  padding-left: 1.65rem;
}

.dark .dropdown-select {
  background-image: url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27rgba(255,255,255,0.6)%27 stroke-width=%272.5%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpolyline points=%276 9 12 15 18 9%27%3e%3c/polyline%3e%3c/svg%3e');
  background-color: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.85);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.dropdown-select:hover {
  background-color: rgba(255, 255, 255, 1);
  border-color: rgba(156, 163, 175, 0.9);
  color: rgb(17, 24, 39);
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.dark .dropdown-select:hover {
  background-color: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.95);
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.dropdown-select:focus,
.dropdown-select:focus-visible {
  border-color: rgba(99, 102, 241, 0.55);
  box-shadow:
    0 0 0 3px rgba(99, 102, 241, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  outline: none;
}

.dark .dropdown-select:focus,
.dark .dropdown-select:focus-visible {
  border-color: rgba(129, 140, 248, 0.5);
  box-shadow:
    0 0 0 3px rgba(129, 140, 248, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
}


/* Style dropdown options to match the page */
.dropdown-select option {
  background-color: white;
  color: #374151;
  padding: 8px 12px;
  font-size: 0.75rem;
  font-weight: 500;
  outline: none !important;
}

.dark .dropdown-select option {
  background-color: #0a0a0a;
  color: rgba(255, 255, 255, 0.7);
  outline: none !important;
}

.dropdown-select option:focus,
.dropdown-select option:active,
.dropdown-select option:hover {
  outline: none !important;
  box-shadow: none !important;
}

/* Remove ALL focus rings and outlines from textarea */
textarea,
textarea:hover,
textarea:focus,
textarea:focus-visible,
textarea:active {
  outline: 0 !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-offset: 0 !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  -webkit-tap-highlight-color: transparent !important;
  border-color: rgb(229 231 235) !important;
  transition: none !important;
}

.dark textarea,
.dark textarea:hover,
.dark textarea:focus,
.dark textarea:focus-visible,
.dark textarea:active {
  border-color: rgba(255, 255, 255, 0.06) !important;
}

/* 3D Printed Button Effect - matching homepage */
.btn-3d {
  transform: translateZ(0);
  box-shadow: 
    /* Tight shadow for immediate depth */
    0 2px 3px -1px rgba(0, 0, 0, 0.4),
    /* Medium shadow for body lift */
    0 6px 12px -3px rgba(0, 0, 0, 0.35),
    /* Large diffuse shadow */
    0 16px 32px -8px rgba(0, 0, 0, 0.3),
    0 24px 48px -12px rgba(0, 0, 0, 0.2),
    /* Bottom edge thickness */
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    /* Inset highlights */
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.2),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}

.dark .btn-3d {
  box-shadow: 
    /* Tight shadow for immediate depth */
    0 2px 3px -1px rgba(0, 0, 0, 0.1),
    /* Medium shadow for body lift */
    0 6px 12px -3px rgba(0, 0, 0, 0.1),
    /* Large diffuse shadow */
    0 16px 32px -8px rgba(0, 0, 0, 0.1),
    0 24px 48px -12px rgba(0, 0, 0, 0.08),
    /* Bottom edge thickness */
    0 3px 0 -1px rgba(0, 0, 0, 0.15),
    /* Inset highlights */
    inset 0 3px 6px 0 rgba(255, 255, 255, 0.9),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.08);
}

/* Refined minimal scrollbar - matching homepage */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}
</style>
