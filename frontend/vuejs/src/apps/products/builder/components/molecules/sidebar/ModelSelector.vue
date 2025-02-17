<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-2">
      <label class="text-sm font-medium text-gray-400">AI Model</label>
      <span v-if="selectedModel?.costPerRequest" class="text-xs text-gray-400">
        ${{ selectedModel.costPerRequest.toFixed(3) }}/req
      </span>
    </div>
    
    <div class="relative">
      <select
        v-model="selectedModelId"
        class="w-full appearance-none bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2.5 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20 pr-10"
        @change="handleModelChange"
      >
        <option value="" disabled>Select Model</option>
        <option
          v-for="model in models"
          :key="model.id"
          :value="model.id"
          :disabled="model.disabled"
          class="py-2"
        >
          {{ model.name }}
        </option>
      </select>
      <div class="absolute inset-y-0 right-0 flex items-center px-3 pointer-events-none">
        <i class="fas fa-chevron-down text-gray-400 text-xs"></i>
      </div>
    </div>
    
    <div v-if="selectedModel?.description" class="mt-3 p-3 bg-dark-800/50 rounded-lg">
      <p class="text-xs text-gray-400 leading-relaxed">
        {{ selectedModel.description }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { AIModel } from '@/apps/products/builder/types/builder'

const props = defineProps<{
  models: AIModel[]
  modelId: string | null
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

const selectedModelId = ref(props.modelId || 'claude-3.5-sonnet')

const selectedModel = computed(() => 
  props.models.find(m => m.id === selectedModelId.value)
)

const handleModelChange = () => {
  if (selectedModelId.value) {
    emit('update:modelId', selectedModelId.value)
  }
}

watch(() => props.modelId, (newVal: string | null) => {
  if (newVal) {
    selectedModelId.value = newVal
  }
})
</script>
