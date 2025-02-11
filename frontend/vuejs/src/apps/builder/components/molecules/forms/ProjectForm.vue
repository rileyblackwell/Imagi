<template>
  <form @submit.prevent="$emit('submit')" class="space-y-6">
    <div class="relative">
      <input
        :value="value"
        @input="$emit('update:value', $event.target.value)"
        type="text"
        placeholder="Enter project name"
        class="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 focus:border-primary-500/50 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
        required
      >
    </div>
    <ActionButton
      type="submit"
      :disabled="isLoading || !value.trim()"
      icon="fa-magic"
      fullWidth
    >
      <span v-if="isLoading">Creating Project...</span>
      <span v-else>Create Project</span>
    </ActionButton>
  </form>
</template>

<script setup>
import { ActionButton } from '@/apps/builder/components';

defineProps({
  value: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['update:value', 'submit']);
</script>
