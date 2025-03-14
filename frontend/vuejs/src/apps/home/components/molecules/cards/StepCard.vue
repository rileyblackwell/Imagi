<template>
  <div class="relative">
    <div 
      class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl p-7 border border-dark-700/40 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]"
      :class="[
        `hover:border-${color}-500/30`,
      ]"
    >
      <div 
        class="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 rounded-full bg-dark-900 flex items-center justify-center text-sm z-10 font-bold"
        :class="[
          `ring-2 ring-${color}-500/50 text-${color}-400`
        ]"
      >{{ stepNumber }}</div>
      
      <!-- Card top highlight -->
      <div 
        class="absolute top-0 inset-x-0 h-px bg-gradient-to-r"
        :class="[
          `from-${color}-500/0 via-${color}-500/40 to-${color}-500/0`
        ]"
      ></div>
      
      <!-- Card inner glow -->
      <div 
        class="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        :class="[
          `from-${color}-500/5 to-${gradientEndColor}-500/5`
        ]"
      ></div>
      
      <div 
        class="w-11 h-11 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-md"
        :class="[
          `bg-gradient-to-br from-${color}-500 to-${gradientEndColor}-500`
        ]"
      >
        <i 
          class="text-white text-lg"
          :class="icon"
        ></i>
      </div>
      
      <h3 
        class="text-xl font-semibold text-white mb-3 transition-colors"
        :class="[
          `group-hover:text-${color}-300`
        ]"
      >
        {{ title }}
      </h3>
      
      <p class="text-gray-300 text-sm">{{ description }}</p>
      
      <!-- Border highlight effect -->
      <div 
        class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"
        :class="[
          `from-${color}-500/0 via-${color}-500 to-${color}-500/0`
        ]"
      ></div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'StepCard',
  props: {
    stepNumber: {
      type: Number,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    color: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'indigo', 'violet', 'fuchsia', 'purple', 'green'].includes(value)
    }
  },
  setup(props) {
    // Determine the gradient end color based on primary color
    const gradientEndColor = computed(() => {
      const colorMap = {
        primary: 'indigo',
        indigo: 'violet',
        violet: 'purple',
        fuchsia: 'pink',
        purple: 'fuchsia',
        green: 'emerald'
      };
      return colorMap[props.color] || 'violet';
    });

    return {
      gradientEndColor
    }
  }
})
</script> 