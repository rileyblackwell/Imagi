<template>
  <div class="p-4 border-b border-dark-700">
    <label class="block text-sm font-medium text-gray-400 mb-2">AI Model</label>
    <select
      v-model="selectedModelId"
      class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2"
      @change="handleModelChange"
    >
      <option value="" disabled>Select an AI model</option>
      <option
        v-for="model in models"
        :key="model.id"
        :value="model.id"
        :disabled="model.disabled"
      >
        {{ model.name }} 
        <span v-if="model.costPerRequest" class="text-gray-400">
          (${model.costPerRequest}/request)
        </span>
      </option>
    </select>
    <p v-if="selectedModel?.description" class="mt-2 text-sm text-gray-400">
      {{ selectedModel.description }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { AIModel } from '@/apps/builder/types/builder'

const props = defineProps<{
  models: AIModel[]
  modelId: string | null
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

const selectedModelId = ref<string | null>(props.modelId)

const selectedModel = computed(() => 
  props.models.find(m => m.id === selectedModelId.value)
)

const handleModelChange = () => {
  if (selectedModelId.value) {
    emit('update:modelId', selectedModelId.value)
  }
}

// Update local state when prop changes
watch(() => props.modelId, (newVal: string | null) => {
  selectedModelId.value = newVal
})
</script>
