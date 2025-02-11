<template>
  <div class="flex items-center justify-between p-4 border-b border-dark-700">
    <div class="flex items-center space-x-4">
      <h2 class="text-lg font-semibold text-white">
        {{ projectName }}
      </h2>
      <span class="text-sm text-gray-400">{{ selectedModel }}</span>
    </div>
    <div class="flex items-center space-x-4">
      <select
        v-model="selectedModelValue"
        class="bg-dark-900 border border-dark-600 rounded-lg text-white px-3 py-2 text-sm"
      >
        <option
          v-for="model in models"
          :key="model.id"
          :value="model.id"
        >
          {{ model.name }}
        </option>
      </select>
      <ActionButton
        variant="secondary"
        icon="fa-undo"
        :disabled="!canUndo || isLoading"
        @click="$emit('undo')"
      >
        Undo
      </ActionButton>
      <ActionButton
        variant="primary"
        icon="fa-save"
        :disabled="!hasUnsavedChanges || isLoading"
        @click="$emit('save')"
      >
        Save
      </ActionButton>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { ActionButton } from '@/apps/builder/components';

const props = defineProps({
  projectName: {
    type: String,
    default: 'Untitled Project'
  },
  selectedModel: {
    type: String,
    required: true
  },
  models: {
    type: Array,
    default: () => []
  },
  canUndo: {
    type: Boolean,
    default: false
  },
  hasUnsavedChanges: {
    type: Boolean,
    default: false
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const selectedModelValue = computed({
  get: () => props.selectedModel,
  set: (value) => emit('update:selectedModel', value)
});

const emit = defineEmits(['update:selectedModel', 'undo', 'save']);
</script>
