<template>
  <!-- Ultra-Premium Background Effects System -->
  <div class="absolute inset-0 overflow-hidden pointer-events-none">
    <!-- Multi-layered sophisticated pattern system -->
    <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.008]"></div>
    <div class="absolute inset-0 bg-noise opacity-[0.005] mix-blend-overlay"></div>
    
    <!-- Advanced gradient orchestration for depth -->
    <div class="absolute inset-0 bg-gradient-to-br from-dark-900/95 via-dark-950/98 to-dark-900/90"></div>
    <div class="absolute inset-0 bg-gradient-to-tr from-indigo-950/4 via-transparent to-violet-950/3"></div>
    <div class="absolute inset-0 bg-gradient-to-bl from-transparent via-fuchsia-950/2 to-transparent"></div>
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(120,119,198,0.008),transparent_70%)]"></div>
    
    <!-- Premium floating orbs with sophisticated staggered choreography -->
    <div class="absolute top-[12%] right-[8%] w-[500px] h-[500px] bg-gradient-to-br from-indigo-600/2 to-violet-600/1.5 rounded-full filter blur-[120px] animate-float-orchestrated-chat-1"></div>
    <div class="absolute bottom-[20%] left-[6%] w-[400px] h-[400px] bg-gradient-to-br from-violet-600/1.5 to-fuchsia-600/1 rounded-full filter blur-[100px] animate-float-orchestrated-chat-2"></div>
    <div class="absolute top-[45%] right-[75%] w-[300px] h-[300px] bg-gradient-to-br from-cyan-600/1 to-blue-600/0.8 rounded-full filter blur-[80px] animate-float-orchestrated-chat-3"></div>
    
    <!-- Sophisticated animated geometric elements -->
    <div class="absolute left-0 right-0 top-[18%] h-px bg-gradient-to-r from-transparent via-indigo-500/6 to-transparent animate-pulse-sophisticated-chat"></div>
    <div class="absolute left-0 right-0 top-[38%] h-px bg-gradient-to-r from-transparent via-violet-500/5 to-transparent animate-pulse-sophisticated-chat delay-1800"></div>
    <div class="absolute left-0 right-0 bottom-[32%] h-px bg-gradient-to-r from-transparent via-fuchsia-500/4 to-transparent animate-pulse-sophisticated-chat delay-3600"></div>
  </div>

  <!-- Main Flex Area with ChatGPT-like structure spanning full width and height -->
  <div class="flex-1 flex flex-col overflow-hidden relative z-10 h-full w-full">
    <!-- Chat Conversation Area with larger proportion like ChatGPT -->
    <div class="flex-1 overflow-auto relative min-h-0">
      <!-- Multi-layered premium glassmorphism overlay for chat area -->
      <div class="absolute inset-0 bg-gradient-to-b from-white/[0.008] via-transparent to-white/[0.004] pointer-events-none"></div>
      <div class="absolute inset-0 bg-gradient-to-tr from-indigo-500/[0.003] via-transparent to-violet-500/[0.002] pointer-events-none"></div>
      
      <div class="p-6 h-full relative">
        <div class="max-w-5xl mx-auto h-full relative z-20">
          <ChatConversation 
            :messages="validatedMessages" 
            :isProcessing="isProcessing"
            @use-example="$emit('use-example', $event)"
            @apply-code="handleApplyCode"
          />
        </div>
      </div>
    </div>

    <!-- Compact AI Input Area at bottom like ChatGPT -->
    <div 
      class="shrink-0 relative z-10 w-full bg-dark-950/95 backdrop-blur-xl border-t border-dark-800/50"
      :class="{'opacity-80 pointer-events-none filter blur-sm': isProcessing}"
    >
      
      <div class="w-full">
        <!-- Inner content container with ChatGPT-like compact design -->
        <div class="max-w-4xl mx-auto px-6 py-4">
          <!-- Compact input container -->
          <div class="relative group/input">
            <!-- Subtle glow effect -->
            <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-500/4 via-indigo-500/3 to-violet-500/4 rounded-2xl opacity-0 group-focus-within/input:opacity-100 blur transition-all duration-300 pointer-events-none"></div>
            
            <!-- Main input container with ChatGPT-like styling -->
            <div class="relative bg-gradient-to-br from-dark-800/90 via-dark-700/85 to-dark-800/80 backdrop-blur-xl border border-dark-600/40 group-focus-within/input:border-violet-400/30 hover:border-dark-500/60 rounded-2xl shadow-lg shadow-black/20 transition-all duration-300 overflow-hidden">
              <!-- Subtle header line -->
              <div class="h-0.5 w-full bg-gradient-to-r from-indigo-400/20 via-violet-400/15 to-indigo-400/20 opacity-50"></div>
              
              <div class="relative z-10 p-4">
                <!-- Compact Mode Indicator -->
                <div class="mb-3">
                  <ModeIndicator 
                    :mode="mode" 
                    :selected-file="selectedFile" 
                    :selected-model-id="selectedModelId"
                    :available-models="availableModels"
                  />
                </div>
                
                <!-- Compact Chat Input -->
                <div class="relative">
                  <ChatInputArea
                    v-model="localPrompt"
                    :placeholder="promptPlaceholder"
                    :focused="true"
                    :is-processing="isProcessing"
                    :show-examples="false"
                    @submit="handleSubmit"
                    @examples="$emit('examples')"
                  >
                    <template #mode-indicator>
                      <!-- Empty mode indicator slot since we moved it outside -->
                    </template>
                  </ChatInputArea>
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
/* Sophisticated orchestrated floating animations for chat */
@keyframes float-orchestrated-chat-1 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  30% { transform: translateY(-25px) translateX(15px) rotate(0.4deg) scale(1.02); }
  60% { transform: translateY(-10px) translateX(25px) rotate(-0.2deg) scale(1.03); }
  85% { transform: translateY(-20px) translateX(-5px) rotate(0.3deg) scale(1.01); }
}

@keyframes float-orchestrated-chat-2 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  25% { transform: translateY(20px) translateX(-15px) rotate(-0.3deg) scale(1.04); }
  65% { transform: translateY(-10px) translateX(20px) rotate(0.2deg) scale(1.02); }
  90% { transform: translateY(5px) translateX(-8px) rotate(-0.1deg) scale(1.01); }
}

@keyframes float-orchestrated-chat-3 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  40% { transform: translateY(15px) translateX(-20px) rotate(0.5deg) scale(1.05); }
  75% { transform: translateY(-15px) translateX(10px) rotate(-0.3deg) scale(1.03); }
}

@keyframes pulse-sophisticated-chat {
  0%, 100% { 
    opacity: 0.6; 
    transform: scaleX(1); 
  }
  25% { 
    opacity: 0.2; 
    transform: scaleX(1.01); 
  }
  50% { 
    opacity: 0.4; 
    transform: scaleX(0.99); 
  }
  75% { 
    opacity: 0.15; 
    transform: scaleX(1.005); 
  }
}

.animate-float-orchestrated-chat-1 {
  animation: float-orchestrated-chat-1 30s ease-in-out infinite;
}

.animate-float-orchestrated-chat-2 {
  animation: float-orchestrated-chat-2 35s ease-in-out infinite reverse;
}

.animate-float-orchestrated-chat-3 {
  animation: float-orchestrated-chat-3 40s ease-in-out infinite;
}

.animate-pulse-sophisticated-chat {
  animation: pulse-sophisticated-chat 5s ease-in-out infinite;
}

/* Sophisticated delay system for chat */
.delay-1800 {
  animation-delay: 1800ms;
}

/* Smooth transitions for chat UI */
.flex-1 {
  transition: height 0.3s ease-in-out;
}

/* Improved scrollbar styles */
.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.700') transparent;
}

.overflow-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.700');
  border-radius: 9999px;
}

/* Ensure chat area expands properly */
.flex-col {
  display: flex;
  flex-direction: column;
}

/* Transition effect for message appearance */
@keyframes message-appear {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ensure the chat container takes full height */
.h-full {
  height: 100%;
  min-height: 0; /* This is important for flex children to respect parent height */
}

/* Fix for overflow issues in chat area */
.overflow-hidden {
  overflow: hidden;
}

.overflow-auto {
  overflow: auto;
}

/* Make sure the main container expands properly */
.flex-1 {
  flex: 1 1 0%;
  min-height: 0; /* Important for Firefox */
}
</style> 