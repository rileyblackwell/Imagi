<template>
  <div
    :class="[
      'payment-card group relative backdrop-blur-sm bg-white/85 dark:bg-white/[0.045] border border-blue-950/[0.08] dark:border-white/[0.1] rounded-2xl overflow-hidden transition-all duration-300',
      hoverable ? 'hoverable' : '',
      customClass
    ]"
  >
    <!-- Soft baby-blue orb decoration -->
    <div v-if="showDecoration" class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full blur-3xl pointer-events-none bg-[#9ecdf3]/25 dark:bg-blue-400/10 transition-opacity duration-500" aria-hidden="true"></div>

    <div v-if="$slots.header" :class="['p-6 border-b border-blue-950/[0.08] dark:border-white/[0.1]', headerClass]">
      <slot name="header"></slot>
    </div>
    <div :class="['p-6', contentClass]">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" :class="['p-6 border-t border-blue-950/[0.08] dark:border-white/[0.1]', footerClass]">
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
/* Crisp, sharply-defined card: hairline edge + tight layered shadow */
.payment-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .payment-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Gentle lift on hover for hoverable cards */
.payment-card.hoverable:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.1),
    0 24px 44px -12px rgba(15, 23, 42, 0.14);
}

.dark .payment-card.hoverable:hover {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 12px 24px -4px rgba(0, 0, 0, 0.5),
    0 28px 48px -12px rgba(0, 0, 0, 0.6);
}

@media (prefers-reduced-motion: reduce) {
  .payment-card.hoverable:hover {
    transform: none;
  }
}
</style> 