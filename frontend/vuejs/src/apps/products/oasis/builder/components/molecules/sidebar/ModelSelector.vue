<template>
  <div>
    <!-- Debug info (hidden in production) -->
    <div v-if="false" class="mb-2 p-2 bg-dark-800 rounded text-xs text-gray-400">
      Models: {{ models.length }}, Available: {{ availableModels.length }}
    </div>
    
    <!-- Model Selection Dropdown -->
    <div class="relative">
      <button
        @click="toggleDropdown"
        class="w-full flex items-center justify-between p-3 rounded-lg border transition-colors bg-dark-800 border-dark-700 hover:border-dark-600"
        :class="{ 'border-primary-500 bg-primary-500/10': isDropdownOpen }"
      >
        <div v-if="selectedModel" class="flex items-center space-x-3 max-w-[85%]">
          <!-- Selected Model Icon -->
          <div 
            class="w-8 h-8 rounded-md flex items-center justify-center"
            :class="[getModelTypeClass(selectedModel)]"
          >
            <i class="fas" :class="getModelTypeIcon(selectedModel)"></i>
          </div>
          
          <!-- Selected Model Info -->
          <div class="flex flex-col text-left">
            <span class="font-medium text-gray-200">{{ selectedModel.name }}</span>
            <div class="flex items-center gap-1 text-xs truncate max-w-[150px]">
              <span class="text-gray-400">{{ selectedModel.description }}</span>
              <span class="text-xs font-semibold ml-auto px-1.5 py-0.5 rounded-md bg-primary-500/20 text-primary-300">${{ formatPrice(selectedModel.costPerRequest) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="flex items-center space-x-3">
          <div class="w-8 h-8 rounded-full bg-gray-500/20 flex items-center justify-center text-gray-400">
            <i class="fas fa-robot"></i>
          </div>
          <span class="text-gray-400">Select a model</span>
        </div>
        
        <!-- Dropdown Arrow -->
        <i class="fas fa-chevron-down text-gray-400 transition-transform duration-200"
           :class="{ 'transform rotate-180': isDropdownOpen }"></i>
      </button>
      
      <!-- Dropdown Menu -->
      <div 
        v-show="isDropdownOpen" 
        class="absolute z-50 w-full mt-1 bg-dark-800 border border-dark-700 rounded-lg shadow-lg overflow-hidden"
      >
        <div class="max-h-60 overflow-y-auto py-1">
          <button
            v-for="model in displayModels"
            :key="model.id"
            class="w-full flex items-center space-x-3 p-3 hover:bg-dark-700 transition-colors"
            :class="{ 'bg-primary-500/10': modelId === model.id }"
            @click="handleModelSelect(model.id)"
          >
            <!-- Model Icon -->
            <div 
              class="w-8 h-8 rounded-md flex items-center justify-center"
              :class="[getModelTypeClass(model)]"
            >
              <i class="fas" :class="getModelTypeIcon(model)"></i>
            </div>
            
            <!-- Model Info -->
            <div class="flex flex-col text-left">
              <span class="font-medium text-gray-200">{{ model.name }}</span>
              <div class="flex items-center gap-1 text-xs">
                <span class="text-gray-400">{{ model.description }}</span>
                <span class="text-xs font-semibold ml-auto px-1.5 py-0.5 rounded-md bg-primary-500/20 text-primary-300">${{ formatPrice(model.costPerRequest) }}</span>
              </div>
            </div>
            
            <!-- Selected Indicator -->
            <div v-if="modelId === model.id" class="ml-auto">
              <i class="fas fa-check text-primary-500"></i>
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
    
    <!-- No Models Available Message -->
    <div v-if="displayModels.length === 0" class="p-3 bg-dark-800 rounded-lg text-center text-gray-400 text-sm mt-2">
      No AI models available
    </div>

    <!-- Model Details -->
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
        class="mt-2 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded text-yellow-400 text-xs"
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
import { ModelService } from '../../../services/agentService'
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
    await ModelService.checkRateLimit(modelId)
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

// Utility functions
const getModelTypeClass = (model: AIModel): string => {
  // Use type assertion to avoid type errors
  const modelType = (model as any).type || (model as any).provider || 'unknown';
  
  if (modelType === 'anthropic') {
    return 'bg-gradient-to-br from-blue-600/20 to-indigo-600/20 text-blue-400 border border-blue-500/20';
  } else if (modelType === 'openai') {
    return 'bg-gradient-to-br from-emerald-600/20 to-green-600/20 text-emerald-400 border border-emerald-500/20';
  }
  
  return 'bg-gradient-to-br from-gray-600/20 to-gray-700/20 text-gray-400 border border-gray-500/20';
}

const getModelTypeIcon = (model: AIModel): string => {
  // Special cases for high-tier models to use brain icon
  if (model.id === 'claude-3-7-sonnet-20250219' || model.id === 'gpt-4o') {
    return 'fa-brain';
  }
  
  // Standard provider-based icons for other models
  const modelType = (model as any).type || (model as any).provider || 'unknown';
  
  if (modelType === 'anthropic') {
    return 'fa-diamond'; // More modern Anthropic logo representation
  } else if (modelType === 'openai') {
    return 'fa-bolt'; // More modern OpenAI logo representation
  }
  
  return 'fa-question';
}

// Debug on mount
onMounted(() => {
  // Component mounted
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
      return ModelService.canGenerateCode(model)
    }
    // For chat mode, show all models
    return true
  })
  
  // If no models are available, use default models
  return filtered.length > 0 ? filtered : defaultModels.value
})

// Compute the models to display, falling back to defaults if needed
const displayModels = computed(() => {
  // This computes models for display, falling back to defaults if needed
  return availableModels.value
})

// Find the selected model object
const selectedModel = computed(() => {
  // First try to find in display models
  const model = displayModels.value.find(m => m.id === props.modelId)
  if (model) return model
  
  // If not found but we have a modelId, try to find in default models
  if (props.modelId) {
    const defaultModel = defaultModels.value.find(m => m.id === props.modelId)
    if (defaultModel) return defaultModel
  }
  
  // If still not found, return the first available model
  return displayModels.value[0] || null
})

// Auto-select first model if none selected
watch(() => displayModels.value, async (models) => {
  if (models.length > 0 && !props.modelId) {
    await handleModelSelect(models[0].id)
  }
}, { immediate: true })

// Add this function to the script section
const formatPrice = (price?: number): string => {
  if (price === undefined || price === null) return '0.00';
  // Show fewer decimal places for larger prices
  return price >= 0.01 ? price.toFixed(2) : price.toFixed(3);
}
</script>

<style scoped>
/* Scrollbar styling for dropdown */
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
</style>
