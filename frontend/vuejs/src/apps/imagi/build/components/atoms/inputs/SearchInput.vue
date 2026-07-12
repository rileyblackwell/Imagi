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
      <i v-if="!isProject" class="fas fa-search absolute left-3 top-1/2 -translate-y-1/2 text-blue-950/40 dark:text-white/40"></i>
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
    ? 'relative z-10 w-full pl-11 pr-4 py-3 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.12] focus:border-blue-400 dark:focus:border-blue-300/50 hover:border-blue-300 dark:hover:border-white/[0.18] rounded-xl text-blue-950 dark:text-white/90 placeholder-blue-950/40 dark:placeholder-white/30 transition-all duration-300 backdrop-blur-sm hover:bg-blue-50/50 dark:hover:bg-white/[0.05] focus:bg-white dark:focus:bg-white/[0.05] focus:shadow-lg focus:shadow-blue-500/20 outline-none'
    : 'w-full px-4 py-2 pl-10 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.12] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white/90 placeholder-blue-950/40 dark:placeholder-white/30 focus:ring-2 focus:ring-blue-500/20 transition-all duration-200 outline-none'
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
