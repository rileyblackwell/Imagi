<template>
  <div class="p-4">
    <label class="block text-sm font-medium text-gray-200 mb-2">
      AI Model
    </label>
    
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
          <div class="flex flex-col">
            <span class="font-medium">{{ model.name }}</span>
            <span class="text-sm text-gray-400">
              {{ modelConfig(model).capabilities.join(' • ') }}
            </span>
          </div>
        </div>
        
        <div v-if="modelId === model.id" class="h-2 w-2 rounded-full bg-primary-500" />
      </button>
    </div>

    <!-- Model Info -->
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
        <div class="flex justify-between text-gray-400">
          <span>Max tokens:</span>
          <span>{{ selectedModelConfig.maxTokens.toLocaleString() }}</span>
        </div>
        <div class="flex justify-between text-gray-400">
          <span>Requests/min:</span>
          <span>{{ selectedModelConfig.rateLimits.requestsPerMinute }}</span>
        </div>
      </div>

      <div 
        v-if="rateLimitWarning"
        class="mt-2 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded text-yellow-400 text-xs"
      >
        Rate limit warning: {{ rateLimitWarning }}
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
</script>
