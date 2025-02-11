<template>
  <div class="h-[calc(100vh-12rem)] rounded-lg border border-dark-700 bg-dark-900">
    <div class="flex items-center justify-between p-4 border-b border-dark-700">
      <div class="flex items-center space-x-2">
        <span class="text-gray-400">{{ fileName }}</span>
        <span v-if="hasUnsavedChanges" class="text-yellow-500 text-sm">(unsaved changes)</span>
      </div>
      <ActionButton
        variant="primary"
        :disabled="!hasUnsavedChanges || isLoading"
        @click="$emit('save')"
      >
        {{ isLoading ? 'Saving...' : 'Save' }}
      </ActionButton>
    </div>
    <textarea
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="'Enter code here...'"
      class="w-full h-[calc(100%-64px)] bg-dark-900 text-white p-4 font-mono resize-none focus:outline-none"
      spellcheck="false"
      wrap="off"
    ></textarea>
  </div>
</template>

<script setup>
import { ActionButton } from '@/apps/builder/components';

defineProps({
  modelValue: {
    type: String,
    required: true
  },
  fileName: {
    type: String,
    default: 'Untitled'
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

defineEmits(['update:modelValue', 'save']);
</script>

<style scoped>
textarea {
  tab-size: 2;
  -moz-tab-size: 2;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  line-height: 1.5;
  font-size: 0.875rem;
}
</style>
