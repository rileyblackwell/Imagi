<template>
  <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
    <div class="flex flex-col h-full">
      <div class="w-14 h-14 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-xl flex items-center justify-center mb-6">
        <i class="fas fa-plus-circle text-2xl text-white"></i>
      </div>
      
      <h2 class="text-2xl font-bold text-white mb-4">Create New Project</h2>
      <p class="text-gray-400 mb-8">Start fresh with a new website project. Use natural language to describe your vision and let AI bring it to life.</p>
      
      <ProjectForm
        :value="modelValue"
        @update:value="$emit('update:modelValue', $event)"
        :is-loading="isLoading"
        @submit="$emit('submit')"
      />
    </div>
  </div>
</template>

<script setup>
import { ProjectForm } from '@/apps/builder/components';

defineProps({
  modelValue: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['update:modelValue', 'submit']);
</script>
