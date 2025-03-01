<template>
  <div>
    <!-- Model Selection Cards -->
    <div class="grid gap-3">
      <button
        v-for="model in availableModels"
        :key="model.id"
        class="flex items-center justify-between p-3 rounded-lg border transition-colors"
        :class="[
          modelId === model.id
            ? 'bg-primary-500/20 border-primary-500'
            : 'bg-dark-800 border-dark-700 hover:border-dark-600'
        ]"
        @click="handleModelSelect(model.id)"
      >
        <div class="flex items-center space-x-3">
          <!-- Model Icon -->
          <div 
            class="w-8 h-8 rounded-full flex items-center justify-center"
            :class="[
              getModelTypeClass(model)
            ]"
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
        </div>
        
        <!-- Selected Indicator -->
        <div v-if="modelId === model.id" class="h-2 w-2 rounded-full bg-primary-500" />
      </button>
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
      >
        <i class="fas fa-exclamation-triangle mr-1"></i>
        {{ rateLimitWarning }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ModelService } from '../../../services/modelService'
import type { AIModel } from '../../../types/builder'

const props = defineProps<{
  modelId: string | null
  models: AIModel[]
  mode: 'chat' | 'build'
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

const rateLimitWarning = ref<string | null>(null)

const availableModels = computed(() => {
  return props.models.filter(model => {
    if (props.mode === 'build') {
      return ModelService.canGenerateCode(model)
    }
    return true
  })
})

const selectedModelConfig = computed(() => {
  if (!props.modelId) return null
  const model = props.models.find(m => m.id === props.modelId)
  return model ? ModelService.getConfig(model) : null
})

const modelConfig = (model: AIModel) => ModelService.getConfig(model)

const handleModelSelect = async (modelId: string) => {
  try {
    // Check rate limit before allowing selection
    await ModelService.checkRateLimit(modelId)
    rateLimitWarning.value = null
    emit('update:modelId', modelId)
  } catch (err) {
    rateLimitWarning.value = err instanceof Error ? err.message : 'Rate limit exceeded'
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
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}
</style>
