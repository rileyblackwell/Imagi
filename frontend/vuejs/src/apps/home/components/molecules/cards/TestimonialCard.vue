<template>
  <div 
    class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl p-7 border border-dark-700/40 transition-all duration-300 hover:-translate-y-1 relative overflow-hidden hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]"
    :class="[
      `hover:border-${color}-500/30`,
    ]"
  >
    <!-- Card top highlight -->
    <div 
      class="absolute top-0 inset-x-0 h-px bg-gradient-to-r"
      :class="[
        `from-${color}-500/0 via-${color}-500/40 to-${color}-500/0`
      ]"
    ></div>
    
    <!-- Decorative corner accent -->
    <div class="absolute top-0 right-0 w-20 h-20 overflow-hidden">
      <div 
        class="absolute -top-10 -right-10 w-20 h-20 rounded-full blur-md group-hover:opacity-100 opacity-50 transition-opacity duration-500"
        :class="[
          `bg-gradient-to-br from-${color}-500/10 to-${color}-500/5`
        ]"
      ></div>
    </div>
    
    <!-- Card inner glow -->
    <div 
      class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
      :class="[
        `bg-gradient-to-br from-${color}-500/5 to-${color === 'primary' ? 'violet' : color === 'indigo' ? 'violet' : 'purple'}-500/5`
      ]"
    ></div>
    
    <div class="flex items-center mb-4">
      <div 
        class="flex group-hover:scale-105 transition-transform"
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
    
    <p class="text-gray-300 mb-5 relative text-sm">
      <span 
        class="absolute -left-1 -top-1 text-4xl font-serif"
        :class="[
          `text-${color}-500/20`
        ]"
      >"</span>
      <span class="relative">{{ quote }}</span>
      <span 
        class="absolute -right-1 bottom-0 text-4xl font-serif"
        :class="[
          `text-${color}-500/20`
        ]"
      >"</span>
    </p>
    
    <div class="flex items-center">
      <div 
        class="w-9 h-9 rounded-full flex items-center justify-center shadow-md"
        :class="[
          `bg-gradient-to-br from-${color}-500 to-${color === 'primary' ? 'violet' : color === 'indigo' ? 'violet' : 'purple'}-500 ring-2 ring-${color}-500/10`
        ]"
      >
        <span class="text-white font-semibold text-sm">{{ avatarInitials }}</span>
      </div>
      <div class="ml-3">
        <div 
          class="text-white font-semibold transition-colors text-sm"
          :class="[
            `group-hover:text-${color}-300`
          ]"
        >{{ name }}</div>
        <div class="text-gray-400 text-xs">{{ position }}</div>
      </div>
    </div>
    
    <!-- Border highlight effect -->
    <div 
      class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"
      :class="[
        `from-${color}-500/0 via-${color}-500 to-${color}-500/0`
      ]"
    ></div>
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