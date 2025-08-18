<template>
  <!-- Main dark-themed layout with sophisticated background -->
  <div class="flex-1 flex flex-col overflow-hidden h-full w-full bg-dark-950 relative">
    <!-- Enhanced sophisticated background effects matching About page -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <!-- Enhanced Pattern Overlay -->
      <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
      <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      <div class="absolute inset-0 bg-gradient-to-br from-dark-950/95 via-dark-900 to-violet-950/10"></div>
      
      <!-- Enhanced floating orbs -->
      <div class="absolute -top-[15%] right-[10%] w-[600px] h-[600px] rounded-full bg-indigo-600/4 blur-[120px] animate-float"></div>
      <div class="absolute bottom-[5%] left-[15%] w-[500px] h-[500px] rounded-full bg-violet-600/3 blur-[100px] animate-float-delay"></div>
    </div>
    
    <!-- Chat Conversation Area -->
    <div class="flex-1 overflow-auto relative min-h-0 z-10">
      <!-- Enhanced multi-layered premium background overlay -->
      <div class="absolute inset-0 bg-gradient-to-b from-white/[0.01] via-transparent to-white/[0.005] pointer-events-none"></div>
      <div class="absolute inset-0 bg-gradient-to-tr from-indigo-500/[0.004] via-transparent to-violet-500/[0.003] pointer-events-none"></div>
      
      <div class="h-full relative">
        <div class="max-w-4xl mx-auto h-full relative z-20">
          <ChatConversation 
            :messages="validatedMessages" 
            :isProcessing="isProcessing"
            @use-example="$emit('use-example', $event)"
            @apply-code="handleApplyCode"
          />
        </div>
      </div>
    </div>

    <!-- Enhanced Input Section at Bottom -->
    <div class="shrink-0 relative z-10 w-full">
      <!-- Enhanced background overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-dark-950/85 via-dark-950/50 to-transparent pointer-events-none"></div>
      <div class="absolute inset-0 bg-gradient-to-t from-dark-900/20 via-transparent to-transparent pointer-events-none"></div>
      
      <div class="relative z-10 w-full">
        <!-- Content container matching dashboard layout -->
        <div class="max-w-4xl mx-auto px-6 py-6">
          <!-- Modern glassmorphism container matching project library style -->
          <div class="relative rounded-3xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-visible">
            <!-- Sleek gradient header matching dashboard -->
            <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
            
            <!-- Subtle background effects matching dashboard -->
            <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50"></div>
            
            <!-- Content with dashboard-style padding -->
            <div class="relative z-10 p-6">
              <!-- Header section with pill badge matching dashboard style -->
              <div class="mb-4">
                <!-- Modern pill badge matching dashboard -->
                <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-3 backdrop-blur-sm">
                  <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
                  <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">
                    {{ mode === 'chat' ? 'AI Chat' : 'Code Generation' }}
                  </span>
                </div>
                
                <!-- Title section matching dashboard style -->
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-white leading-tight">
                      {{ mode === 'chat' ? 'Ask me anything' : 'Describe what to build' }}
                    </h3>
                    <p class="text-gray-400 text-sm mt-1 leading-relaxed">
                      {{ mode === 'chat' 
                          ? 'Get help with your project, code review, or technical questions' 
                          : 'Tell me what you want to create and I\'ll generate the code' }}
                    </p>
                  </div>
                  
                  <!-- Controls in top right: Model selector + Mode toggle -->
                  <div class="ml-4 flex items-start gap-3">
                    <div class="min-w-[220px]">
                      <ModelSelector 
                        :models="availableModels"
                        :model-id="selectedModelId"
                        :mode="mode"
                        @update:model-id="(id: string) => $emit('update:model-id', id)"
                      />
                    </div>
                    <div class="relative min-w-[160px]">
                      <!-- Dropdown Trigger Button (matches ModelSelector style) -->
                      <button
                        @click="toggleModeDropdown"
                        class="w-full flex items-center justify-between p-2.5 rounded-lg border transition-all duration-300 bg-dark-800/70 backdrop-blur-sm border-dark-700/50 hover:border-primary-500/30 group"
                        :class="{ 'border-primary-500/40 bg-gradient-to-r from-primary-500/10 to-violet-500/10': isModeDropdownOpen }"
                        aria-haspopup="listbox"
                        :aria-expanded="isModeDropdownOpen ? 'true' : 'false'"
                      >
                        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-lg blur opacity-0 group-hover:opacity-50 transition duration-300"></div>
                        <div class="relative flex items-center space-x-2">
                          <div class="w-8 h-8 rounded-lg flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 shadow-[0_0_12px_rgba(139,92,246,0.15)]">
                            <i class="fas bg-gradient-to-br from-primary-300 to-violet-300 bg-clip-text text-transparent drop-shadow-[0_0_6px_rgba(139,92,246,0.35)]" :class="mode === 'chat' ? 'fa-comments' : 'fa-code'"></i>
                          </div>
                          <span class="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">{{ mode === 'chat' ? 'Chat' : 'Build' }}</span>
                        </div>
                        <i class="fas fa-chevron-down text-gray-400 transition-transform duration-300 relative"
                           :class="{ 'transform rotate-180 text-primary-400': isModeDropdownOpen }"></i>
                      </button>

                      <!-- Dropdown Menu -->
                      <div
                        v-show="isModeDropdownOpen"
                        class="absolute z-50 w-full mt-2 bg-dark-800/90 backdrop-blur-md border border-dark-700/50 rounded-xl shadow-lg overflow-hidden"
                        role="listbox"
                        aria-label="Select mode"
                      >
                        <div class="max-h-48 py-1">
                          <button
                            class="w-full flex items-center gap-2 p-3 hover:bg-dark-700/50 transition-all duration-200 group relative"
                            :class="{ 'bg-gradient-to-r from-primary-500/10 to-violet-500/10 border-l-2 border-l-primary-500': mode === 'chat' }"
                            role="option"
                            :aria-selected="mode === 'chat'"
                            @click="handleSelectMode('chat')"
                          >
                            <div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 to-primary-500/0 opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center border bg-gradient-to-br from-indigo-500/15 to-sky-500/15 border-indigo-400/30 shadow-[0_0_10px_rgba(99,102,241,0.18)]">
                              <i class="fas fa-comments bg-gradient-to-br from-indigo-300 to-sky-300 bg-clip-text text-transparent"></i>
                            </div>
                            <span class="flex-1 text-left text-sm text-gray-200 group-hover:text-white">Chat</span>
                            <span v-if="mode === 'chat'" class="text-primary-400"><i class="fas fa-check"></i></span>
                          </button>
                          <button
                            class="w-full flex items-center gap-2 p-3 hover:bg-dark-700/50 transition-all duration-200 group relative"
                            :class="{ 'bg-gradient-to-r from-primary-500/10 to-violet-500/10 border-l-2 border-l-primary-500': mode === 'build' }"
                            role="option"
                            :aria-selected="mode === 'build'"
                            @click="handleSelectMode('build')"
                          >
                            <div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 to-primary-500/0 opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center border bg-gradient-to-br from-violet-500/15 to-fuchsia-500/15 border-violet-400/30 shadow-[0_0_10px_rgba(139,92,246,0.18)]">
                              <i class="fas fa-code bg-gradient-to-br from-violet-300 to-fuchsia-300 bg-clip-text text-transparent"></i>
                            </div>
                            <span class="flex-1 text-left text-sm text-gray-200 group-hover:text-white">Build</span>
                            <span v-if="mode === 'build'" class="text-primary-400"><i class="fas fa-check"></i></span>
                          </button>
                        </div>
                      </div>

                      <!-- Overlay to close dropdown when clicking outside -->
                      <div
                        v-if="isModeDropdownOpen"
                        class="fixed inset-0 z-40"
                        @click="closeModeDropdown"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Input form section -->
              <div class="relative">
                <!-- Chat Input with enhanced styling to match dashboard inputs -->
                <div class="relative group/input">
                  <!-- Enhanced glow effect on focus matching dashboard -->
                  <div class="absolute inset-0 bg-gradient-to-r from-violet-500/12 to-indigo-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                  
                  <ChatInputArea
                    v-model="localPrompt"
                    :placeholder="promptPlaceholder"
                    :focused="true"
                    :is-processing="isProcessing"
                    :show-examples="false"
                    @submit="handleSubmit"
                    @examples="$emit('examples')"
                    class="relative z-10"
                  >
                    <template #mode-indicator>
                      <!-- Empty since we moved it to header -->
                    </template>
                  </ChatInputArea>
                </div>
                
                <!-- Bottom section with keyboard shortcuts matching dashboard style -->
                <div class="flex justify-between items-center mt-4 px-1">
                  <!-- Left side - empty for balance -->
                  <div class="flex-1"></div>
                  
                  <!-- Enhanced keyboard shortcuts on the right matching dashboard -->
                  <div class="flex-shrink-0">
                    <div class="text-xs text-gray-400 flex items-center gap-3">
                      <span class="flex items-center gap-1.5">
                        <kbd class="px-2 py-1 bg-dark-800/80 rounded-md border border-dark-700/60 text-gray-300 text-xs font-medium shadow-sm">⏎</kbd> 
                        <span class="text-gray-500">to send</span>
                      </span>
                      <span class="text-gray-600/40">•</span>
                      <span class="flex items-center gap-1.5">
                        <kbd class="px-2 py-1 bg-dark-800/80 rounded-md border border-dark-700/60 text-gray-300 text-xs font-medium shadow-sm">⇧⏎</kbd> 
                        <span class="text-gray-500">for new line</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ChatConversation } from '../../organisms/chat'
import { ChatInputArea } from '../../molecules'
import ModelSelector from '../../molecules/sidebar/ModelSelector.vue'
import type { BuilderMode } from '../../../types/components'
import type { AIModel, AIMessage } from '../../../types/services'
import type { SelectedFile } from '../../../types/components'

// Props
const props = defineProps<{
  messages: AIMessage[]
  isProcessing: boolean
  mode: BuilderMode
  selectedFile: SelectedFile | null
  selectedModelId: string | null
  availableModels: AIModel[]
  promptPlaceholder: string
  showExamples: boolean
  promptExamples: Array<{title: string, text: string}> | null
  modelValue: string
}>()

// Ensure all messages have required properties
const validatedMessages = computed(() => {
  if (!props.messages || !Array.isArray(props.messages) || props.messages.length === 0) {
    return []
  }
  
  // First filter out system messages related to file switching if not in chat mode
  const filteredMessages = props.messages.filter(message => {
    // If we're in build mode, filter out system messages about file switching
    if (props.mode !== 'chat' && message.role === 'system') {
      // Filter out messages about file switching or mode switching
      if (message.content && (
        message.content.includes('Switched to file:') || 
        message.content.includes('Switched to build mode')
      )) {
        return false;
      }
    }
    return true;
  });
  
  const processed = filteredMessages.map(message => {
    // Ensure each message has valid content
    let content = message.content
    
    // Handle potential null or undefined content
    if (content === null || content === undefined) {
      content = '';
    }
    
    // If content is an object rather than a string (can happen with some API responses)
    if (typeof content === 'object') {
      try {
        content = JSON.stringify(content);
      } catch (e) {
        content = String(content);
      }
    }
    
    // Ensure each message has at least role, content, and timestamp
    return {
      role: message.role || 'user',
      content: content || '',
      timestamp: message.timestamp || Date.now(),
      code: message.code || undefined,
      id: message.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
  });
  
  return processed;
})


// Emits
const emit = defineEmits([
  'update:modelValue',
  'update:model-id',
  'update:mode',
  'submit',
  'examples',
  'use-example',
  'apply-code'
])

// Local state
const localPrompt = ref(props.modelValue)
const isModeDropdownOpen = ref(false)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  localPrompt.value = newValue
})

// Update parent model
watch(localPrompt, (newValue) => {
  emit('update:modelValue', newValue)
})

// Methods
function handleSubmit() {
  if (!localPrompt.value.trim()) return
  emit('submit')
}

function handleApplyCode(code: string) {
  emit('apply-code', code)
}

// Mode dropdown handlers
function toggleModeDropdown() {
  isModeDropdownOpen.value = !isModeDropdownOpen.value
}
function closeModeDropdown() {
  isModeDropdownOpen.value = false
}
function handleSelectMode(value: BuilderMode) {
  if (value === 'chat' || value === 'build') {
    emit('update:mode', value)
    closeModeDropdown()
  }
}
</script>

<style scoped>
/* Enhanced animations matching About page */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

/* Sophisticated dark scrollbar styles */
.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.overflow-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.4), rgba(124, 58, 237, 0.3));
  border-radius: 2px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.6), rgba(124, 58, 237, 0.5));
}

/* Ensure chat layout works properly */
.flex-1 {
  flex: 1 1 0%;
  min-height: 0;
}

.h-full {
  height: 100%;
  min-height: 0;
}
</style> 