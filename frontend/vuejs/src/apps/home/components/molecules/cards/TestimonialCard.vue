<template>
  <div 
    class="bg-white dark:bg-white rounded-2xl p-8 border border-gray-200 dark:border-gray-300 relative overflow-hidden shadow-md"
  >
    <div class="flex items-center mb-5">
      <div 
        class="flex"
        :class="[
          `text-${color}-400`
        ]"
      >
        <i class="fas fa-star text-sm"></i>
        <i class="fas fa-star text-sm"></i>
        <i class="fas fa-star text-sm"></i>
        <i class="fas fa-star text-sm"></i>
        <i class="fas fa-star text-sm"></i>
      </div>
    </div>
    
    <!-- Quote without decorative quote marks -->
    <p class="text-gray-600 dark:text-black mb-6 text-base leading-relaxed">
      {{ quote }}
    </p>
    
    <div class="flex items-center">
      <div 
        class="w-10 h-10 rounded-full flex items-center justify-center shadow-md"
        :class="[
          `bg-${color}-500`
        ]"
      >
        <span class="text-white font-semibold text-sm">{{ avatarInitials }}</span>
      </div>
      <div class="ml-3">
        <div 
          class="text-gray-900 dark:text-black font-semibold text-sm"
        >{{ name }}</div>
        <div class="text-gray-600 dark:text-black text-xs">{{ position }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'TestimonialCard',
  props: {
    quote: {
      type: String,
      required: true
    },
    avatarInitials: {
      type: String,
      required: true
    },
    name: {
      type: String,
      required: true
    },
    position: {
      type: String,
      required: true
    },
    color: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'indigo', 'violet', 'purple', 'fuchsia'].includes(value)
    }
  }
})
</script> 