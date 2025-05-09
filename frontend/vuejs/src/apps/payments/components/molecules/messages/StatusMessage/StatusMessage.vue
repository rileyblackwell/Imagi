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
      return 'bg-green-500/10 border-green-300/30 text-green-300 animate-pulse-slow';
    case 'error':
      return 'bg-red-500/10 border-red-300/30 text-red-300';
    case 'warning':
      return 'bg-yellow-500/10 border-yellow-300/30 text-yellow-300';
    case 'info':
      return 'bg-blue-500/10 border-blue-300/30 text-blue-300';
    default:
      return 'bg-green-500/10 border-green-300/30 text-green-300';
  }
});

const glowClass = computed(() => {
  switch (props.type) {
    case 'success': return 'bg-green-500/5';
    case 'error': return 'bg-red-500/5';
    case 'warning': return 'bg-yellow-500/5';
    case 'info': return 'bg-blue-500/5';
    default: return 'bg-green-500/5';
  }
});

const borderGradientClass = computed(() => {
  switch (props.type) {
    case 'success': return 'from-green-500/0 via-green-500/60 to-green-500/0';
    case 'error': return 'from-red-500/0 via-red-500/60 to-red-500/0';
    case 'warning': return 'from-yellow-500/0 via-yellow-500/60 to-yellow-500/0';
    case 'info': return 'from-blue-500/0 via-blue-500/60 to-blue-500/0';
    default: return 'from-green-500/0 via-green-500/60 to-green-500/0';
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
    case 'success': return 'bg-green-500/20';
    case 'error': return 'bg-red-500/20';
    case 'warning': return 'bg-yellow-500/20';
    case 'info': return 'bg-blue-500/20';
    default: return 'bg-green-500/20';
  }
});

const iconColorClass = computed(() => {
  switch (props.type) {
    case 'success': return 'text-green-400';
    case 'error': return 'text-red-400';
    case 'warning': return 'text-yellow-400';
    case 'info': return 'text-blue-400';
    default: return 'text-green-400';
  }
});

const textColorClass = computed(() => {
  switch (props.type) {
    case 'success': return 'text-green-300';
    case 'error': return 'text-red-300';
    case 'warning': return 'text-yellow-300';
    case 'info': return 'text-blue-300';
    default: return 'text-green-300';
  }
});
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 0.9; }
  50% { opacity: 1; }
}

.animate-pulse-slow {
  animation: pulse-slow 4s ease-in-out infinite;
}
</style> 