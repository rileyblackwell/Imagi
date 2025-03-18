<template>
  <div class="flex-1 flex flex-col overflow-hidden relative">
    <!-- Background decorative elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Gradient effect -->
      <div class="absolute inset-0 bg-gradient-to-br from-dark-900 to-dark-950"></div>
      
      <!-- Animated orbs -->
      <div class="absolute top-[10%] right-[5%] w-96 h-96 bg-primary-600/10 rounded-full filter blur-3xl opacity-30 animate-float-slow"></div>
      <div class="absolute bottom-[20%] left-[10%] w-64 h-64 bg-violet-600/10 rounded-full filter blur-2xl opacity-20 animate-float-slow-reverse"></div>
      
      <!-- Grid pattern overlay -->
      <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
    </div>

    <!-- Loading Overlay -->
    <div 
      v-if="isProcessing"
      class="absolute inset-0 bg-dark-950/70 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div class="text-center">
        <div class="inline-block w-12 h-12 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mb-4"></div>
        <p class="text-lg text-white font-medium">Processing...</p>
        <p class="text-sm text-gray-400 mt-1">The AI is working on your request</p>
      </div>
    </div>

    <!-- Chat Conversation Area -->
    <div class="flex-1 overflow-auto px-4 py-2">
      <div class="max-w-4xl mx-auto">
        <ChatConversation 
          :messages="messages" 
          @use-example="$emit('use-example', $event)"
        />
      </div>
    </div>

    <!-- AI Input Area -->
    <div 
      class="shrink-0 p-4 border-t border-dark-700/50 bg-dark-900/80 backdrop-blur-md shadow-lg relative"
      :class="{'opacity-50 pointer-events-none': isProcessing}"
    >
      <!-- Gradient header line -->
      <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-500/30 to-transparent"></div>
      
      <div class="max-w-4xl mx-auto">
        <ChatInputArea
          v-model="localPrompt"
          :placeholder="promptPlaceholder"
          :focused="true"
          :is-processing="isProcessing"
          :show-examples="showExamples"
          @submit="handleSubmit"
          @examples="$emit('examples')"
        >
          <template #mode-indicator>
            <ModeIndicator 
              :mode="mode" 
              :selected-file="selectedFile" 
              :selected-model-id="selectedModelId"
              :available-models="availableModels"
            />
          </template>
          
          <template #examples v-if="promptExamples && promptExamples.length > 0">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-2">
              <button
                v-for="example in promptExamples"
                :key="example.text"
                class="text-left p-3 bg-dark-800/60 hover:bg-dark-800/90 rounded-md border border-dark-700/50 hover:border-primary-500/40 text-gray-300 transition-all duration-200 backdrop-blur-sm hover:shadow-md"
                @click="$emit('use-example', example.text)"
              >
                <p class="font-medium text-white">{{ example.title }}</p>
                <p class="text-sm text-gray-400 mt-1 line-clamp-2">{{ example.text }}</p>
              </button>
            </div>
          </template>
        </ChatInputArea>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ChatConversation } from '../../organisms/chat'
import { ChatInputArea, ModeIndicator } from '../../molecules'
import type { AIMessage, BuilderMode } from '../../../types'
import type { AIModel } from '../../../types/builder'

// Define a compatible type that matches both versions
interface SelectedFile {
  path: string;
  type: string;
  content: string;
  lastModified?: string;
  id?: string;
  name?: string;
}

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

// Emits
const emit = defineEmits([
  'update:modelValue',
  'submit',
  'examples',
  'use-example'
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
  emit('submit')
}
</script>

<style scoped>
/* Background grid pattern */
.bg-grid-pattern {
  background-image: linear-gradient(to right, theme('colors.dark.800') 1px, transparent 1px),
                    linear-gradient(to bottom, theme('colors.dark.800') 1px, transparent 1px);
  background-size: 20px 20px;
}

/* Animation for floating orbs */
@keyframes float-slow {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
}

@keyframes float-slow-reverse {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(20px) translateX(-10px); }
}

.animate-float-slow {
  animation: float-slow 20s ease-in-out infinite;
}

.animate-float-slow-reverse {
  animation: float-slow-reverse 25s ease-in-out infinite;
}
</style> 