<template>
  <div 
    class="group bg-gradient-to-b from-dark-800/60 to-dark-900/60 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:-translate-y-1 relative overflow-hidden hover:shadow-lg"
    :class="[
      `hover:border-${color}-500/30`
    ]"
  >
    <div 
      class="absolute top-0 inset-x-0 h-px bg-gradient-to-r"
      :class="[
        `from-${color}-500/0 via-${color}-500/40 to-${color}-500/0`
      ]"
    ></div>
    <div class="p-6 text-center">
      <div 
        class="w-12 h-12 mx-auto rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300"
        :class="[
          `bg-gradient-to-br from-${color}-500/20 to-${color === 'primary' ? 'violet' : 'violet'}-500/20`
        ]"
      >
        <i 
          :class="[
            icon,
            `text-${color}-400`
          ]"
        ></i>
      </div>
      <div 
        class="text-4xl font-bold bg-clip-text text-transparent mb-1 group-hover:scale-105 transition-transform"
        :class="[
          `bg-gradient-to-r from-${color}-400 to-${color === 'primary' ? 'violet' : color === 'indigo' ? 'violet' : color === 'green' ? 'emerald' : 'fuchsia'}-400`
        ]"
      >{{ value }}</div>
      <p class="text-gray-400 uppercase text-xs tracking-wider font-medium">{{ label }}</p>
      
      <!-- Visualization: Circle Progress, Clock, or Custom Icon -->
      <div class="w-24 h-24 mx-auto mt-3 relative">
        <!-- Clock visualization -->
        <template v-if="isClock">
          <svg class="w-full h-full" viewBox="0 0 100 100">
            <circle class="text-dark-700 stroke-current" stroke-width="4" fill="transparent" r="38" cx="50" cy="50"></circle>
            <circle 
              class="stroke-current" 
              :class="[`text-${color}-500`]"
              stroke-width="4" 
              fill="transparent" 
              r="38" 
              cx="50" 
              cy="50"
            ></circle>
            <!-- Clock hands -->
            <line x1="50" y1="50" x2="50" y2="25" stroke="currentColor" :class="[`text-${color}-400`]" stroke-width="2" stroke-linecap="round"></line>
            <line x1="50" y1="50" x2="65" y2="50" stroke="currentColor" :class="[`text-${color}-400`]" stroke-width="2" stroke-linecap="round"></line>
            <circle :class="[`text-${color}-500 fill-current`]" r="3" cx="50" cy="50"></circle>
          </svg>
        </template>
        
        <!-- Percentage circle visualization -->
        <template v-else-if="percent !== null">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle class="text-dark-700 stroke-current" stroke-width="4" fill="transparent" r="38" cx="50" cy="50"></circle>
            <circle 
              class="stroke-current" 
              :class="[`text-${color}-500`]"
              stroke-width="4" 
              stroke-linecap="round" 
              fill="transparent" 
              r="38" 
              cx="50" 
              cy="50" 
              stroke-dasharray="239" 
              :stroke-dashoffset="calculateStrokeDashoffset"
            ></circle>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-xs text-gray-300">{{ percent }}%</span>
          </div>
        </template>
        
        <!-- Custom icon visualization -->
        <template v-else>
          <div 
            class="flex items-center justify-center h-full w-full"
          >
            <div 
              class="w-16 h-16 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-500 bg-gradient-to-br"
              :class="[
                `from-${color}-500/20 via-${color}-500/15 to-${color === 'primary' ? 'violet' : color === 'indigo' ? 'violet' : 'purple'}-500/10`
              ]"
            >
              <i 
                :class="[
                  secondaryIcon || icon,
                  `text-${color}-400 text-3xl`
                ]"
              ></i>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'StatCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    value: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    percent: {
      type: Number,
      default: null
    },
    color: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'indigo', 'violet', 'green', 'purple', 'fuchsia'].includes(value)
    },
    isClock: {
      type: Boolean,
      default: false
    },
    secondaryIcon: {
      type: String,
      default: null
    }
  },
  setup(props) {
    // Calculate the stroke-dashoffset based on the percentage
    const calculateStrokeDashoffset = computed(() => {
      if (props.percent === null) return 0;
      
      // The circumference of the circle is 2πr
      // For r=38, the circumference is approximately 239
      const circumference = 2 * Math.PI * 38;
      return circumference - (props.percent / 100) * circumference;
    });

    return {
      calculateStrokeDashoffset
    }
  }
})
</script> 