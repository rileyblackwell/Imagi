<template>
  <!-- Premium dark-themed layout - Matching Home Page -->
  <div
    class="bg-[#050508] relative overflow-hidden w-full"
    :class="compact ? '' : 'flex-1 flex flex-col h-full'"
  >
    <!-- Premium Background System (for non-compact mode only) -->
    <div v-if="!compact" class="absolute inset-0 pointer-events-none overflow-hidden">
      <!-- Base gradient mesh -->
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(120,119,198,0.1),transparent_50%)]"></div>
      <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_80%_50%,rgba(78,68,206,0.06),transparent_40%)]"></div>
      
      <!-- Subtle grain texture -->
      <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
      
      <!-- Floating orbs -->
      <div class="absolute -top-[15%] right-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-600/6 to-violet-600/3 blur-[120px] animate-float-slow"></div>
      <div class="absolute bottom-[5%] left-[15%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-fuchsia-600/5 to-purple-600/2 blur-[100px] animate-float-delayed"></div>
    </div>
    
    <!-- Chat Conversation Area -->
    <div v-if="showConversation" class="flex-1 overflow-auto relative min-h-0 z-10">
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

    <!-- Premium Input Section at Bottom -->
    <div class="shrink-0 relative z-10 w-full">
      <!-- Background overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-[#050508]/95 via-[#050508]/70 to-transparent pointer-events-none"></div>
      
      <div class="relative z-10 w-full">
        <!-- Content container -->
        <div class="max-w-4xl mx-auto px-6 py-6">
          <!-- Premium glass card - Matching Home Page CTA Style -->
          <div class="group relative">
            <!-- Background glow -->
            <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
            
            <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-visible">
              <!-- Accent line -->
              <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
              
              <!-- Decorative elements -->
              <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
              <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
            
              <!-- Content -->
              <div class="relative z-10 p-6 md:p-8">
                <!-- Header section -->
                <div class="mb-4">
                  <!-- Badge matching home page -->
                  <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-4">
                    <i :class="mode === 'chat' ? 'fas fa-comments' : 'fas fa-code'" class="text-xs text-violet-400/80"></i>
                    <span class="text-sm font-medium text-white/60">
                      {{ mode === 'chat' ? 'AI Chat' : 'Code Generation' }}
                    </span>
                  </div>
                  
                  <!-- Title section -->
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      <h3 class="text-lg font-semibold text-white/90 leading-tight">
                        {{ mode === 'chat' ? 'Ask me anything' : 'Describe what to build' }}
                      </h3>
                      <p class="text-white/50 text-sm mt-2 leading-relaxed">
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
                      <!-- Dropdown Trigger Button - Premium Style -->
                      <button
                        @click="toggleModeDropdown"
                        class="w-full flex items-center justify-between p-2.5 rounded-xl border transition-all duration-300 bg-white/[0.03] backdrop-blur-sm border-white/[0.08] hover:bg-white/[0.05] hover:border-white/[0.12] group"
                        :class="{ 'border-violet-400/40 bg-white/[0.05]': isModeDropdownOpen }"
                        aria-haspopup="listbox"
                        :aria-expanded="isModeDropdownOpen ? 'true' : 'false'"
                      >
                        <div class="relative flex items-center space-x-2">
                          <div class="w-8 h-8 rounded-lg flex items-center justify-center border bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border-violet-500/20">
                            <i class="text-violet-400" :class="mode === 'chat' ? 'fas fa-comments' : 'fas fa-code'"></i>
                          </div>
                          <span class="text-sm font-medium text-white/70 group-hover:text-white/90 transition-colors">{{ mode === 'chat' ? 'Chat' : 'Build' }}</span>
                        </div>
                        <i class="fas fa-chevron-down text-white/40 transition-transform duration-300"
                           :class="{ 'transform rotate-180 text-violet-400': isModeDropdownOpen }"></i>
                      </button>

                      <!-- Dropdown Menu - Premium Style -->
                      <div
                        v-show="isModeDropdownOpen"
                        class="absolute z-50 w-full mt-2 bg-[#0a0a0f]/95 backdrop-blur-xl border border-white/[0.08] rounded-xl shadow-2xl shadow-black/50 overflow-hidden"
                        role="listbox"
                        aria-label="Select mode"
                      >
                        <div class="max-h-48 py-1">
                          <button
                            class="w-full flex items-center gap-2 p-3 hover:bg-white/[0.05] transition-all duration-200 group relative"
                            :class="{ 'bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 border-l-2 border-l-violet-500': mode === 'chat' }"
                            role="option"
                            :aria-selected="mode === 'chat'"
                            @click="handleSelectMode('chat')"
                          >
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center border bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border-violet-500/20">
                              <i class="fas fa-comments text-violet-400"></i>
                            </div>
                            <span class="flex-1 text-left text-sm text-white/70 group-hover:text-white/90">Chat</span>
                            <span v-if="mode === 'chat'" class="text-violet-400"><i class="fas fa-check"></i></span>
                          </button>
                          <button
                            class="w-full flex items-center gap-2 p-3 hover:bg-white/[0.05] transition-all duration-200 group relative"
                            :class="{ 'bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 border-l-2 border-l-violet-500': mode === 'build' }"
                            role="option"
                            :aria-selected="mode === 'build'"
                            @click="handleSelectMode('build')"
                          >
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center border bg-gradient-to-br from-fuchsia-500/20 to-violet-500/20 border-fuchsia-500/20">
                              <i class="fas fa-code text-fuchsia-400"></i>
                            </div>
                            <span class="flex-1 text-left text-sm text-white/70 group-hover:text-white/90">Build</span>
                            <span v-if="mode === 'build'" class="text-violet-400"><i class="fas fa-check"></i></span>
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
                    </div>
              
              <!-- Input form section -->
              <div class="relative">
                <!-- Chat Input -->
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
                
                <!-- Keyboard shortcuts -->
                <div class="flex justify-between items-center mt-4 px-1">
                  <div class="flex-1"></div>
                  
                  <div class="flex-shrink-0">
                    <div class="text-xs text-white/30 flex items-center gap-3">
                      <span class="flex items-center gap-1.5">
                        <kbd class="px-2 py-1 bg-white/[0.03] rounded-md border border-white/[0.08] text-white/50 text-xs font-medium">⏎</kbd> 
                        <span>to send</span>
                      </span>
                      <span class="text-white/20">•</span>
                      <span class="flex items-center gap-1.5">
                        <kbd class="px-2 py-1 bg-white/[0.03] rounded-md border border-white/[0.08] text-white/50 text-xs font-medium">⇧⏎</kbd> 
                        <span>for new line</span>
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
  // When true, render a compact layout suitable for placing under other content
  compact?: boolean
  // Controls whether the conversation feed is shown
  showConversation?: boolean
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

// Derived props with defaults
const compact = computed(() => props.compact === true)
const showConversation = computed(() => props.showConversation !== false)

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
/* Float animations - Matching Home Page */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-25px, -30px) scale(1.03);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 30s ease-in-out infinite;
  animation-delay: -5s;
}

/* Premium scrollbar */
.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.overflow-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
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