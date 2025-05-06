<template>
  <div>
    <!-- Debug info (hidden in production) -->
    <div v-if="false" class="mb-2 p-2 bg-dark-800 rounded text-xs text-gray-400">
      Models: {{ models.length }}, Available: {{ availableModels.length }}
    </div>
    
    <!-- Modern Model Selection Dropdown -->
    <div class="relative">
      <!-- Dropdown Trigger Button with Enhanced Design -->
      <button
        @click="toggleDropdown"
        class="w-full flex items-center justify-between p-3 rounded-lg border transition-all duration-300 bg-dark-800/70 backdrop-blur-sm border-dark-700/50 hover:border-primary-500/30 group"
        :class="{ 'border-primary-500/40 bg-gradient-to-r from-primary-500/10 to-violet-500/10': isDropdownOpen }"
      >
        <!-- Subtle glow effect on hover -->
        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-lg blur opacity-0 group-hover:opacity-50 transition duration-300"></div>
        
        <div v-if="selectedModel" class="relative flex items-center space-x-3 max-w-[85%]">
          <!-- Selected Model Icon with enhanced styling -->
          <div 
            class="w-9 h-9 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105"
            :class="[getModelTypeClass(selectedModel)]"
          >
            <i class="fas" :class="getModelTypeIcon(selectedModel)"></i>
          </div>
          
          <!-- Selected Model Info with improved typography -->
          <div class="flex flex-col text-left">
            <span class="font-medium text-gray-200 group-hover:text-white transition-colors">{{ selectedModel.name }}</span>
            <div class="flex items-center gap-1 text-xs truncate max-w-[150px]">
              <span class="text-gray-400">{{ selectedModel.description }}</span>
              <span class="text-xs font-semibold ml-auto px-1.5 py-0.5 rounded-md bg-primary-500/20 text-primary-300 border border-primary-500/20">${{ formatPrice(selectedModel.costPerRequest) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="relative flex items-center space-x-3">
          <div class="w-9 h-9 rounded-lg bg-dark-700/50 flex items-center justify-center text-gray-400 border border-dark-600/30">
            <i class="fas fa-robot"></i>
          </div>
          <span class="text-gray-400">Select a model</span>
        </div>
        
        <!-- Dropdown Arrow with animation -->
        <i class="fas fa-chevron-down text-gray-400 transition-transform duration-300 relative"
           :class="{ 'transform rotate-180 text-primary-400': isDropdownOpen }"></i>
      </button>
      
      <!-- Enhanced Dropdown Menu -->
      <div 
        v-show="isDropdownOpen" 
        class="absolute z-50 w-full mt-2 bg-dark-800/90 backdrop-blur-md border border-dark-700/50 rounded-xl shadow-lg overflow-hidden"
      >
        <!-- Subtle header -->
        <div class="px-3 py-2 border-b border-dark-700/50 text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Available Models
        </div>
        
        <div class="max-h-60 overflow-y-auto py-1">
          <button
            v-for="model in displayModels"
            :key="model.id"
            class="w-full flex items-start gap-1 p-3 hover:bg-dark-700/50 transition-all duration-200 group relative"
            :class="{ 'bg-gradient-to-r from-primary-500/10 to-violet-500/10 border-l-2 border-l-primary-500': modelId === model.id }"
            @click="handleModelSelect(model.id)"
          >
            <!-- Subtle hover effect -->
            <div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 to-primary-500/0 opacity-0 group-hover:opacity-10 transition-opacity duration-300"></div>
            
            <!-- Model Icon with enhanced styling -->
            <div 
              class="w-9 h-9 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105"
              :class="[getModelTypeClass(model)]"
            >
              <i class="fas" :class="getModelTypeIcon(model)"></i>
            </div>
            
            <!-- Model Info with improved layout -->
            <div class="flex flex-col text-left flex-1 min-w-0">
              <span class="font-medium text-gray-200 group-hover:text-white transition-colors">{{ model.name }}</span>
              <span class="text-gray-400 group-hover:text-gray-200 transition-colors whitespace-normal break-words pt-1 block text-xs" :title="model.description">{{ model.description }}</span>
            </div>
            <div class="flex flex-col items-center justify-between h-full flex-shrink-0">
              <span class="text-xs font-semibold px-1.5 py-0.5 rounded-md bg-primary-500/20 text-primary-300 border border-primary-500/20 whitespace-nowrap">${{ formatPrice(model.costPerRequest) }}</span>
              <span v-if="modelId === model.id" class="text-primary-400"><i class="fas fa-check"></i></span>
            </div>
          </button>
        </div>
      </div>
      
      <!-- Overlay to close dropdown when clicking outside -->
      <div
        v-if="isDropdownOpen"
        class="fixed inset-0 z-40"
        @click="closeDropdown"
      ></div>
    </div>
    
    <!-- No Models Available Message with improved styling -->
    <div v-if="displayModels.length === 0" class="mt-2 p-3 bg-dark-800/70 backdrop-blur-sm rounded-lg text-center text-gray-400 text-sm border border-dark-700/50">
      <i class="fas fa-exclamation-circle mr-1 text-gray-500"></i>
      No AI models available
    </div>

    <!-- Model Details with enhanced styling -->
    <TransitionGroup 
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div 
        v-if="rateLimitWarning"
        class="mt-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg text-yellow-400 text-xs backdrop-blur-sm"
        :key="'warning'"
      >
        <i class="fas fa-exclamation-triangle mr-1"></i>
        {{ rateLimitWarning }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { ModelsService } from '../../../services/modelsService'
import { AI_MODELS } from '../../../types/services'
import type { AIModel } from '../../../types/services'

const props = defineProps<{
  modelId: string | null
  models: AIModel[]
  mode: 'chat' | 'build'
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

// Local state
const rateLimitWarning = ref<string | null>(null)
const isDropdownOpen = ref(false)
const defaultModels = ref<AIModel[]>(AI_MODELS)
const isLoadingModels = ref(false)

// Methods - defined before they're used in watchers
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleModelSelect = async (modelId: string) => {
  try {
    // Validate the model exists in either available models or default models
    const modelExists = displayModels.value.some(m => m.id === modelId) || 
                       defaultModels.value.some(m => m.id === modelId)
    
    if (!modelExists) {
      throw new Error(`Model ${modelId} not found in available models`)
    }
    
    // Check rate limit before allowing selection
    await ModelsService.checkRateLimit(modelId)
    rateLimitWarning.value = null
    
    // Emit the update event
    emit('update:modelId', modelId)
    
    // Force a DOM update to ensure the change is reflected
    setTimeout(() => {
      // Use window instead of document for event dispatching
      const event = new CustomEvent('model-changed', { 
        detail: modelId,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
    }, 50)
    
    isDropdownOpen.value = false // Close dropdown after selection
  } catch (err) {
    console.error('Error selecting model', err)
    rateLimitWarning.value = err instanceof Error ? err.message : 'Error selecting model'
  }
}

// Utility functions are now imported from utils/modelIconUtils.ts
import { getModelTypeIcon, getModelTypeClass } from '@/apps/products/oasis/builder/utils/modelIconUtils'


// Format price for display
const formatPrice = (price: number | undefined): string => {
  if (price === undefined || price === null) return '0.00';
  return price >= 0.01 ? price.toFixed(2) : price.toFixed(3);
}

// Fetch models from API on mount
const fetchModels = async () => {
  isLoadingModels.value = true
  try {
    const apiModels = await ModelsService.getAvailableModels()
    if (apiModels && apiModels.length > 0) {
      defaultModels.value = apiModels
    }
  } catch (err) {
    console.error('Error fetching models:', err)
    // Keep using the default models
  } finally {
    isLoadingModels.value = false
  }
}

// Debug on mount
onMounted(() => {
  // Fetch available models from API
  fetchModels()
})

// Watch for changes in models prop
watch(() => props.models, (newModels) => {
  // Models changed
}, { immediate: true })

const availableModels = computed(() => {
  // Ensure we're filtering and displaying all available models
  const filtered = props.models.filter(model => {
    // For build mode, only show models that can generate code
    if (props.mode === 'build') {
      return ModelsService.canGenerateCode(model)
    }
    // For chat mode, show all models
    return true
  })
  
  // If no models from props, use default models
  return filtered.length > 0 ? filtered : defaultModels.value
})

// Filter models based on mode
const displayModels = computed(() => {
  return availableModels.value.filter(model => {
    if (props.mode === 'build') {
      return ModelsService.canGenerateCode(model)
    }
    return true
  })
})

// Selected model
const selectedModel = computed(() => {
  if (!props.modelId) return null
  
  // First try to find the model in the available models
  const model = displayModels.value.find(m => m.id === props.modelId)
  if (model) return model
  
  // If not found, check in the default models
  const defaultModel = defaultModels.value.find(m => m.id === props.modelId)
  return defaultModel || null
})
</script>

<style scoped>
/* Custom scrollbar for dropdown */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.600') transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.600');
  border-radius: 2px;
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
