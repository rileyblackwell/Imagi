<template>
  <div 
    :class="[
      'group relative backdrop-blur-sm bg-dark-800/40 border border-gray-800/60 shadow-xl rounded-2xl overflow-hidden transition-all duration-500',
      hoverable ? 'transform hover:-translate-y-1 hover:shadow-[0_0_20px_-5px_rgba(99,102,241,0.4)]' : '',
      customClass
    ]"
  >
    <!-- Card top highlight -->
    <div class="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-primary-500/0 via-primary-500/60 to-primary-500/0"></div>
    
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 from-primary-900 to-violet-900 transition-opacity duration-300 group-hover:opacity-20"></div>
    
    <!-- Glowing orb decoration -->
    <div v-if="showDecoration" class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-10 blur-3xl transition-opacity duration-500 group-hover:opacity-20 bg-primary-500"></div>
    
    <div v-if="$slots.header" :class="['p-6 border-b border-white/10', headerClass]">
      <slot name="header"></slot>
    </div>
    <div :class="['p-6', contentClass]">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" :class="['p-6 border-t border-white/10', footerClass]">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'PaymentCard',
  props: {
    hoverable: {
      type: Boolean,
      default: false
    },
    showDecoration: {
      type: Boolean,
      default: true
    },
    headerClass: {
      type: String,
      default: ''
    },
    contentClass: {
      type: String,
      default: ''
    },
    footerClass: {
      type: String,
      default: ''
    },
    customClass: {
      type: String,
      default: ''
    }
  }
})
</script>

<style scoped>
/* Subtle glow effect for cards */
.backdrop-blur-sm {
  position: relative;
}

.backdrop-blur-sm::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  filter: blur(20px);
  opacity: 0.1;
  background: radial-gradient(circle at top right, var(--tw-gradient-stops));
  --tw-gradient-from: theme('colors.primary.500');
  --tw-gradient-stops: var(--tw-gradient-from), transparent 70%;
  border-radius: inherit;
  transform: translate(0, 0) scale(0.95);
  pointer-events: none;
  transition: opacity 0.3s ease-in-out;
}

.backdrop-blur-sm:hover::after {
  opacity: 0.15;
}
</style> 