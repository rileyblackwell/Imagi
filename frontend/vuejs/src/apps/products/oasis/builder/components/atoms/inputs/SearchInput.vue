<template>
  <div :class="wrapperClass">
    <div class="relative flex items-center">
      <div v-if="isProject" class="absolute left-4 flex items-center justify-center w-4 h-4 z-20">
        <i class="fas fa-search text-white text-sm search-light-glow"></i>
      </div>
      <input
        type="text"
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        :class="inputClass"
        :placeholder="placeholder"
      >
      <i v-if="!isProject" class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: string
  placeholder?: string
  variant?: 'default' | 'project'
}>(), {
  placeholder: 'Search...',
  variant: 'default'
})

const isProject = computed(() => props.variant === 'project')

const wrapperClass = computed(() => isProject.value ? 'relative group flex-1 max-w-md' : 'relative')

const inputClass = computed(() =>
  isProject.value
    ? 'relative z-10 w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20'
    : 'w-full px-4 py-2 pl-10 bg-dark-900/50 border border-dark-600 focus:border-primary-500/50 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200'
)

defineEmits(['update:modelValue']);
</script>

<style scoped>
/* Project variant glow effect */
.search-light-glow {
  text-shadow:
    0 0 3px rgba(255, 255, 255, 0.4),
    0 0 6px rgba(255, 255, 255, 0.3),
    0 0 9px rgba(255, 255, 255, 0.2),
    0 0 12px rgba(255, 255, 255, 0.1);
  filter: brightness(1.05);
}
</style>
