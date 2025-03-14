<template>
  <div 
    :class="[
      'bg-dark-800 rounded-lg shadow-xl overflow-hidden border border-dark-700',
      hoverable ? 'transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl hover:shadow-primary-500/10' : '',
      customClass
    ]"
  >
    <div v-if="$slots.header" class="p-6 border-b border-dark-700">
      <slot name="header"></slot>
    </div>
    <div :class="['p-6', contentClass]">
      <slot></slot>
    </div>
    <div v-if="$slots.footer" :class="['p-6 border-t border-dark-700', footerClass]">
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