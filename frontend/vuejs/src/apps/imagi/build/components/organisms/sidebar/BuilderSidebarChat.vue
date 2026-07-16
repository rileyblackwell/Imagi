<template>
  <div v-if="!isCollapsed" class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] border-r border-blue-100 dark:border-white/[0.08] transition-colors duration-300">
    <!-- Header: manager toggle + instance title -->
    <div class="shrink-0 flex items-center gap-2 px-3 py-2 border-b border-blue-100 dark:border-white/[0.08]">
      <div v-if="!isManagerOpen" class="relative group">
        <button
          class="flex items-center justify-center w-8 h-8 rounded-md text-blue-950/60 dark:text-white/60 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white transition-colors duration-200"
          @click="$emit('toggleManager')"
        >
          <i class="fas fa-chevron-right text-sm"></i>
        </button>
        <div
          class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Show agent manager
        </div>
      </div>
      <div class="flex-1 min-w-0 text-xs font-semibold text-blue-950/80 dark:text-white/80 truncate">
        {{ activeInstance?.title || 'New instance' }}
      </div>
      <div v-if="onCollapseSidebar" class="relative group shrink-0">
        <button
          class="flex items-center justify-center w-8 h-8 rounded-md text-blue-950/60 dark:text-white/60 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white transition-colors duration-200"
          @click="onCollapseSidebar()"
        >
          <i class="fas fa-chevron-left text-sm"></i>
        </button>
        <div
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Collapse sidebar
        </div>
      </div>
    </div>

    <!-- Conversation Area (scrollable) -->
    <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <ChatConversation
        :messages="ensureValidMessages(activeInstance?.conversation || [])"
        :is-processing="!!activeInstance?.isProcessing"
        :status-text="activeInstance?.statusText || ''"
        @use-example="handleExamplePrompt"
        class="flex-1"
      />
    </div>

    <!-- Chat Input Section (fixed at bottom) -->
    <div class="shrink-0 bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
      <div class="px-2 pt-1 pb-3">
        <!-- Input shell: textarea on top, controls toolbar below -->
        <div class="chat-input-shell rounded-xl bg-blue-50/50 dark:bg-white/[0.03] border border-blue-200/70 dark:border-white/[0.08]">
          <textarea
            ref="promptTextarea"
            v-model="prompt"
            :placeholder="promptPlaceholder"
            @keydown.enter.exact.prevent="handlePrompt"
            @keydown.enter.shift.exact="() => {}"
            @input="autoResizeTextarea"
            :disabled="!activeInstance || activeInstance.isProcessing"
            rows="4"
            class="chat-textarea w-full bg-transparent text-blue-950 dark:text-white/90 placeholder-blue-950/40 dark:placeholder-white/30 text-sm px-3 pt-3 pb-1 resize-none leading-relaxed"
            style="min-height: 92px; max-height: 240px;"
          ></textarea>

          <!-- Controls toolbar: model + reasoning side by side on the left, send pinned right -->
          <div class="flex items-center justify-between gap-2 px-2 pb-2 pt-1">
            <div class="flex flex-nowrap items-center gap-1.5 min-w-0">
              <!-- Model Dropdown -->
              <div class="dropdown-wrapper" title="Model">
                <i class="fas fa-microchip dropdown-icon"></i>
                <select
                  :value="activeInstance?.selectedModelId ?? ''"
                  :disabled="!activeInstance"
                  aria-label="Model"
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

              <!-- Reasoning Effort Dropdown -->
              <div class="dropdown-wrapper" title="How much reasoning the model uses">
                <i class="fas fa-brain dropdown-icon"></i>
                <select
                  :value="activeInstance?.selectedEffort ?? 'medium'"
                  :disabled="!activeInstance"
                  aria-label="Reasoning effort"
                  @change="handleEffortSelect(($event.target as HTMLSelectElement).value as ReasoningEffort)"
                  class="dropdown-select dropdown-select--with-icon text-xs"
                >
                  <option
                    v-for="effort in effortOptions"
                    :key="effort.id"
                    :value="effort.id"
                  >
                    {{ effort.name }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Send Button -->
            <button
              @click="handlePrompt"
              :disabled="!prompt.trim() || !activeInstance || activeInstance.isProcessing"
              aria-label="Send message"
              class="btn-send flex shrink-0 items-center justify-center w-9 h-9 rounded-full transition-all duration-300"
              :class="prompt.trim() && activeInstance && !activeInstance.isProcessing
                ? 'btn-send--active text-blue-950 border border-white/60 dark:border-white/30 shadow-lg hover:shadow-xl'
                : 'bg-blue-100/60 dark:bg-white/[0.05] text-blue-950/40 dark:text-white/40 cursor-not-allowed border border-blue-200/70 dark:border-white/[0.12] shadow-sm'"
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
import type { AIMessage, AIModel } from '../../../types/index'
import type { ReasoningEffort, ReasoningEffortOption } from '../../../types/services'
import { REASONING_EFFORTS } from '../../../types/services'

// Props
const props = defineProps<{
  selectedApp: any
  onPromptSubmit: (prompt: string) => Promise<void>
  onModelSelect: (modelId: string) => Promise<void>
  onEffortSelect: (effort: ReasoningEffort) => Promise<void>
  onExamplePrompt: (example: string) => void
  onCollapseSidebar?: () => void
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
  const available = (store.availableModels || []).filter(model => model.id.startsWith('gpt-5.6'))
  if (available.length > 0) {
    return available
  }
  return [
    { id: 'gpt-5.6-sol', name: 'GPT 5.6 Sol', provider: 'openai' } as AIModel,
    { id: 'gpt-5.6-terra', name: 'GPT 5.6 Terra', provider: 'openai' } as AIModel,
    { id: 'gpt-5.6-luna', name: 'GPT 5.6 Luna', provider: 'openai' } as AIModel
  ]
})

const effortOptions = computed<ReasoningEffortOption[]>(() => REASONING_EFFORTS)

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

const promptPlaceholder = computed(() => 'Ask me to build, edit, or explain anything in your project...')

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
      const content = m.content || ''
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
  const maxHeight = 240
  promptTextarea.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

async function handlePrompt() {
  if (!prompt.value.trim() || !activeInstance.value || activeInstance.value.isProcessing) return
  
  const promptText = prompt.value
  prompt.value = '' // Clear immediately
  
  // Reset textarea height
  if (promptTextarea.value) {
    promptTextarea.value.style.height = '92px'
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

async function handleEffortSelect(effort: ReasoningEffort) {
  await props.onEffortSelect(effort)
}
</script>

<style scoped>
/* Input shell wraps the textarea + controls toolbar as one field */
.chat-input-shell {
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.chat-input-shell:focus-within {
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.dark .chat-input-shell:focus-within {
  border-color: rgba(147, 197, 253, 0.5);
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.18);
}

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
  border: 1px solid rgba(191, 219, 254, 0.9);
  color: rgb(23, 37, 84);
  font-weight: 600;
  letter-spacing: 0.01em;
  padding: 0.3rem 1.5rem 0.3rem 0.6rem;
  border-radius: 0.5rem;
  cursor: pointer;
  text-overflow: ellipsis;
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
  padding-left: 1.5rem;
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
  background-color: rgba(239, 246, 255, 1);
  border-color: rgba(147, 197, 253, 0.95);
  color: rgb(23, 37, 84);
  box-shadow:
    0 2px 6px rgba(30, 58, 138, 0.08),
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
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow:
    0 0 0 3px rgba(59, 130, 246, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  outline: none;
}

.dark .dropdown-select:focus,
.dark .dropdown-select:focus-visible {
  border-color: rgba(147, 197, 253, 0.5);
  box-shadow:
    0 0 0 3px rgba(147, 197, 253, 0.18),
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

/* Textarea sits inside the input shell, which owns the border/focus ring */
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
  border: none !important;
  transition: none !important;
}

/* Baby-blue send button - matching the site's primary "Start Building" button */
.btn-send {
  transform: translateY(0) translateZ(0);
}

.btn-send--active {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.dark .btn-send--active {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
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
