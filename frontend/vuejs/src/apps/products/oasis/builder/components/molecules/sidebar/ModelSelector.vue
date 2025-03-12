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
        <div v-if="selectedModel" class="flex items-center space-x-3">
          <!-- Selected Model Icon -->
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="[getModelTypeClass(selectedModel)]"
          >
            <i class="fas" :class="getModelTypeIcon(selectedModel)"></i>
          </div>
          
          <!-- Selected Model Info -->
          <div class="flex flex-col text-left">
            <span class="font-medium text-gray-200">{{ selectedModel.name }}</span>
            <span class="text-xs text-gray-400 truncate max-w-[150px]">
              {{ selectedModel.description }}
            </span>
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
              class="w-8 h-8 rounded-full flex items-center justify-center"
              :class="[getModelTypeClass(model)]"
            >
              <i class="fas" :class="getModelTypeIcon(model)"></i>
            </div>
            
            <!-- Model Info -->
            <div class="flex flex-col text-left">
              <span class="font-medium text-gray-200">{{ model.name }}</span>
              <span class="text-xs text-gray-400">
                {{ model.description }}
              </span>
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
        v-if="selectedModelConfig" 
        class="mt-3 p-3 bg-dark-800 rounded-lg text-sm"
        :key="'config'"
      >
        <div class="flex justify-between text-gray-400 mb-1">
          <span>Context window:</span>
          <span>{{ formatNumber(selectedModelConfig.contextWindow) }} tokens</span>
        </div>
        <div class="flex justify-between text-gray-400">
          <span>Capabilities:</span>
          <span class="text-right">{{ formatCapabilities(selectedModelConfig.capabilities) }}</span>
        </div>
      </div>

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
import { ModelService } from '../../../services'
import { AI_MODELS } from '../../../types/builder'
import type { AIModel } from '../../../types/builder'

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
      // Trigger a custom event that the parent component can listen for
      document.dispatchEvent(new CustomEvent('model-selection-updated', { 
        detail: { modelId }
      }))
    }, 50)
    
    isDropdownOpen.value = false // Close dropdown after selection
  } catch (err) {
    rateLimitWarning.value = err instanceof Error ? err.message : 'Error selecting model'
  }
}

// Utility functions
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K'
  }
  return num.toString()
}

const formatCapabilities = (capabilities: string[]): string => {
  if (!capabilities || !Array.isArray(capabilities)) return 'None'
  
  return capabilities
    .map(cap => cap.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '))
    .join(', ')
}

const getModelTypeClass = (model: AIModel): string => {
  // Use type assertion to avoid type errors
  const modelType = (model as any).type || (model as any).provider || 'unknown';
  
  if (modelType === 'anthropic') {
    return 'bg-blue-500/20 text-blue-400';
  } else if (modelType === 'openai') {
    return 'bg-green-500/20 text-green-400';
  }
  
  return 'bg-gray-500/20 text-gray-400';
}

const getModelTypeIcon = (model: AIModel): string => {
  // Use type assertion to avoid type errors
  const modelType = (model as any).type || (model as any).provider || 'unknown';
  
  if (modelType === 'anthropic') {
    return 'fa-robot';
  } else if (modelType === 'openai') {
    return 'fa-brain';
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

// Get the configuration for the selected model
const selectedModelConfig = computed(() => {
  if (!selectedModel.value) return null
  return ModelService.getConfig(selectedModel.value)
})

// Auto-select first model if none selected
watch(() => displayModels.value, async (models) => {
  if (models.length > 0 && !props.modelId) {
    await handleModelSelect(models[0].id)
  }
}, { immediate: true })
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
