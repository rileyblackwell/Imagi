<template>
  <div class="flex items-center justify-between px-4 py-2 bg-dark-800 border-b border-dark-700">
    <div class="flex items-center space-x-4">
      <h2 class="text-lg font-semibold text-white">
        {{ title }}
      </h2>
      <span v-if="subtitle" class="text-sm text-gray-400">
        {{ subtitle }}
      </span>
    </div>
    <div class="flex items-center space-x-2">
      <slot name="actions">
        <span v-if="unsavedChanges" class="text-yellow-500 text-sm">
          Unsaved changes
        </span>
        <button
          v-if="showSave"
          @click="$emit('save')"
          class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg"
          :disabled="!unsavedChanges || loading"
        >
          Save Changes
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  unsavedChanges?: boolean
  showSave?: boolean
  loading?: boolean
}>()

defineEmits<{
  (e: 'save'): void
}>()
</script>
