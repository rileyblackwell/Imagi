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
          <div class="relative rounded-3xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden">
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
                  
                  <!-- Mode indicator in top right corner matching dashboard stats -->
                  <div class="ml-4">
                    <ModeIndicator 
                      :mode="mode" 
                      :selected-file="selectedFile" 
                      :selected-model-id="selectedModelId"
                      :available-models="availableModels"
                    />
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
import { ModeIndicator } from '../../molecules/display'
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
});

// Emits
const emit = defineEmits([
  'update:modelValue',
  'submit',
  'examples',
  'use-example',
  'apply-code'
])

// Local state
const localPrompt = ref(props.modelValue)

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