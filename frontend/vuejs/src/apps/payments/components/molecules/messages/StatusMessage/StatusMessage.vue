<template>
  <div 
    v-if="show"
    :class="[
      'relative backdrop-blur-sm border rounded-2xl p-6 mb-8 shadow-lg overflow-hidden',
      typeClasses
    ]"
  >
    <!-- Glow effects -->
    <div :class="['absolute -inset-1 blur-md rounded-2xl -z-10', glowClass]"></div>
    <div :class="['absolute top-0 inset-x-0 h-px bg-gradient-to-r', borderGradientClass]"></div>
    
    <div class="flex items-center">
      <div :class="['flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-4', iconBgClass]">
        <i :class="[iconClass, iconColorClass]"></i>
      </div>
      <div>
        <h3 class="font-medium mb-1 text-lg" :class="textColorClass">{{ title }}</h3>
        <p :class="textColorClass">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  type: {
    type: String,
    default: 'success',
    validator: (value: string) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  show: {
    type: Boolean,
    default: true
  }
});

const typeClasses = computed(() => {
  switch (props.type) {
    case 'success':
      return 'bg-emerald-50/80 border-emerald-200/70 dark:bg-emerald-400/[0.07] dark:border-emerald-300/[0.18]';
    case 'error':
      return 'bg-red-50/80 border-red-200/70 dark:bg-red-500/10 dark:border-red-400/25';
    case 'warning':
      return 'bg-amber-50/80 border-amber-200/70 dark:bg-amber-400/[0.08] dark:border-amber-300/[0.2]';
    case 'info':
      return 'bg-blue-50/80 border-blue-200/70 dark:bg-blue-400/10 dark:border-blue-400/25';
    default:
      return 'bg-emerald-50/80 border-emerald-200/70 dark:bg-emerald-400/[0.07] dark:border-emerald-300/[0.18]';
  }
});

const glowClass = computed(() => {
  switch (props.type) {
    case 'success': return 'bg-emerald-500/5';
    case 'error': return 'bg-red-500/5';
    case 'warning': return 'bg-amber-500/5';
    case 'info': return 'bg-blue-500/5';
    default: return 'bg-emerald-500/5';
  }
});

const borderGradientClass = computed(() => {
  switch (props.type) {
    case 'success': return 'from-emerald-500/0 via-emerald-500/40 to-emerald-500/0 dark:via-emerald-400/40';
    case 'error': return 'from-red-500/0 via-red-500/40 to-red-500/0 dark:via-red-400/40';
    case 'warning': return 'from-amber-500/0 via-amber-500/40 to-amber-500/0 dark:via-amber-400/40';
    case 'info': return 'from-blue-500/0 via-blue-500/40 to-blue-500/0 dark:via-blue-400/40';
    default: return 'from-emerald-500/0 via-emerald-500/40 to-emerald-500/0 dark:via-emerald-400/40';
  }
});

const iconClass = computed(() => {
  switch (props.type) {
    case 'success': return 'fas fa-check';
    case 'error': return 'fas fa-exclamation-triangle';
    case 'warning': return 'fas fa-exclamation-circle';
    case 'info': return 'fas fa-info-circle';
    default: return 'fas fa-check';
  }
});

const iconBgClass = computed(() => {
  switch (props.type) {
    case 'success': return 'bg-emerald-100 dark:bg-emerald-400/[0.14] ring-1 ring-emerald-200/80 dark:ring-emerald-300/[0.18]';
    case 'error': return 'bg-red-100 dark:bg-red-400/[0.14] ring-1 ring-red-200/80 dark:ring-red-300/[0.18]';
    case 'warning': return 'bg-amber-100 dark:bg-amber-400/[0.14] ring-1 ring-amber-200/80 dark:ring-amber-300/[0.18]';
    case 'info': return 'bg-blue-100 dark:bg-blue-400/[0.14] ring-1 ring-blue-200/80 dark:ring-blue-300/[0.18]';
    default: return 'bg-emerald-100 dark:bg-emerald-400/[0.14] ring-1 ring-emerald-200/80 dark:ring-emerald-300/[0.18]';
  }
});

const iconColorClass = computed(() => {
  switch (props.type) {
    case 'success': return 'text-emerald-600 dark:text-emerald-300';
    case 'error': return 'text-red-600 dark:text-red-400';
    case 'warning': return 'text-amber-600 dark:text-amber-300';
    case 'info': return 'text-blue-600 dark:text-blue-300';
    default: return 'text-emerald-600 dark:text-emerald-300';
  }
});

const textColorClass = computed(() => {
  switch (props.type) {
    case 'success': return 'text-emerald-800 dark:text-emerald-200';
    case 'error': return 'text-red-700 dark:text-red-300';
    case 'warning': return 'text-amber-800 dark:text-amber-200';
    case 'info': return 'text-blue-800 dark:text-blue-200';
    default: return 'text-emerald-800 dark:text-emerald-200';
  }
});
</script>

 