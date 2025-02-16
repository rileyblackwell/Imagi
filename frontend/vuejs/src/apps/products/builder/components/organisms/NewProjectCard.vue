<template>
  <div class="group relative">
    <!-- Animated Border Gradient -->
    <div class="absolute -inset-[1px] rounded-2xl bg-gradient-to-r from-primary-500/50 via-violet-500/50 to-indigo-500/50 opacity-0 group-hover:opacity-100 blur transition duration-500"></div>
    
    <!-- Card Content -->
    <div class="relative h-full bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 transition-all duration-300">
      <div class="flex flex-col h-full">
        <!-- Header -->
        <div class="w-14 h-14 bg-gradient-to-br from-primary-500 to-violet-500 rounded-xl flex items-center justify-center mb-6 transform group-hover:scale-110 transition-transform duration-300">
          <i class="fas fa-plus text-2xl text-white"></i>
        </div>
        
        <h2 class="text-2xl font-bold text-white mb-4">Create New Project</h2>
        <p class="text-gray-400 mb-8">Start fresh with a new website project. Use natural language to describe your vision and let AI bring it to life.</p>
        
        <!-- Project Form -->
        <ProjectForm
          :name="modelValue"
          :description="''"
          :loading="isLoading"
          class="mt-auto"
          @update:name="$emit('update:modelValue', $event)"
          @submit="$emit('submit')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ProjectForm } from '../molecules/forms'

interface Props {
  modelValue: string
  isLoading?: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit'): void
}>()
</script>
