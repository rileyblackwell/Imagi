<template>
  <div class="p-4 border-b border-dark-700">
    <label class="block text-sm font-medium text-gray-400 mb-2">AI Model</label>
    <select
      v-model="selectedModelId"
      class="w-full bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2"
      @change="handleModelChange"
    >
      <option
        v-for="model in models"
        :key="model.id"
        :value="model.id"
      >
        {{ model.name }}
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { AIModel } from '../../../types/builder';

const props = defineProps<{
  models: AIModel[];
  modelId: string | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void;
}>();

const selectedModelId = ref<string | null>(props.modelId);

const handleModelChange = () => {
  if (selectedModelId.value) {
    emit('update:modelId', selectedModelId.value);
  }
};

watch(() => props.modelId, (newVal) => {
  selectedModelId.value = newVal;
});
</script>
