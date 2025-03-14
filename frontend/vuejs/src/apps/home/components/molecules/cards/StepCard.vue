<template>
  <div 
    class="group bg-gradient-to-b from-dark-800/90 to-dark-900/90 backdrop-blur-lg rounded-2xl p-8 border border-dark-700/30 transition-all duration-300 hover:-translate-y-1 relative overflow-hidden shadow-lg hover:shadow-xl"
  >
    <!-- Card top highlight -->
    <div 
      class="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent opacity-40 group-hover:opacity-100 transition-opacity duration-300"
      :class="[`via-${colorScheme.primary}-500/60 to-transparent`]"
    ></div>
    
    <!-- Step number indicator -->
    <div class="flex items-start mb-6">
      <!-- Step number with vibrant gradient background - no animations -->
      <div 
        class="w-14 h-14 rounded-xl flex items-center justify-center shadow-lg text-xl font-bold text-white mr-4 transition-all duration-300 transform group-hover:scale-110 relative overflow-hidden"
        :class="[`bg-gradient-to-br from-${colorScheme.primary}-400 via-${colorScheme.secondary}-500 to-${colorScheme.tertiary}-500 group-hover:from-${colorScheme.primary}-300 group-hover:via-${colorScheme.secondary}-400 group-hover:to-${colorScheme.tertiary}-400`]"
      >
        <div class="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-30 transition-all duration-300"></div>
        {{ number }}
      </div>
      
      <h3 
        class="text-2xl font-semibold text-white transition-colors duration-300 pt-2"
        :class="[`group-hover:text-${colorScheme.primary}-300`]"
      >{{ title }}</h3>
    </div>
    
    <p class="text-gray-100 text-base leading-relaxed mb-6">{{ description }}</p>
    
    <!-- Enhanced icon display with static vibrant gradients - no animations -->
    <div 
      v-if="icon" 
      class="w-16 h-16 rounded-xl flex items-center justify-center transition-all duration-300 transform group-hover:scale-110 relative shadow-lg overflow-hidden"
      :class="[`bg-gradient-to-br from-${colorScheme.primary}-400 via-${colorScheme.secondary}-500 to-${colorScheme.tertiary}-500 group-hover:from-${colorScheme.primary}-300 group-hover:via-${colorScheme.secondary}-400 group-hover:to-${colorScheme.tertiary}-400`]"
    >
      <i :class="icon" class="text-white text-2xl relative z-10"></i>
      <!-- Improved glow effect -->
      <div class="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-30 transition-all duration-300"></div>
    </div>
    
    <!-- Border highlight effect -->
    <div 
      class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"
      :class="[`via-${colorScheme.primary}-500 to-transparent`]"
    ></div>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'StepCard',
  props: {
    number: {
      type: [Number, String],
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
      default: ''
    },
    color: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'indigo', 'violet', 'fuchsia', 'purple', 'green', 'cyan', 'amber', 'rose', 'teal', 'blue', 'orange', 'emerald', 'pink'].includes(value)
    }
  },
  setup(props) {
    // Dynamic color scheme based on step number or specified color
    const colorScheme = computed(() => {
      // Use either the provided color or generate one based on the step number
      let baseColor = props.color;
      
      if (baseColor === 'primary' && typeof props.number === 'number') {
        // Create a rotating color scheme based on step number
        const colorOptions = ['primary', 'violet', 'indigo', 'cyan', 'emerald', 'amber', 'rose', 'fuchsia'];
        baseColor = colorOptions[(props.number - 1) % colorOptions.length];
      }
      
      const colorMappings = {
        'primary': { primary: 'primary', secondary: 'violet', tertiary: 'blue' },
        'indigo': { primary: 'indigo', secondary: 'purple', tertiary: 'blue' },
        'violet': { primary: 'violet', secondary: 'indigo', tertiary: 'fuchsia' },
        'green': { primary: 'green', secondary: 'emerald', tertiary: 'teal' },
        'purple': { primary: 'purple', secondary: 'indigo', tertiary: 'violet' },
        'fuchsia': { primary: 'fuchsia', secondary: 'violet', tertiary: 'pink' },
        'cyan': { primary: 'cyan', secondary: 'blue', tertiary: 'teal' },
        'amber': { primary: 'amber', secondary: 'orange', tertiary: 'yellow' },
        'rose': { primary: 'rose', secondary: 'pink', tertiary: 'red' },
        'teal': { primary: 'teal', secondary: 'cyan', tertiary: 'emerald' },
        'blue': { primary: 'blue', secondary: 'indigo', tertiary: 'cyan' },
        'orange': { primary: 'orange', secondary: 'amber', tertiary: 'red' },
        'emerald': { primary: 'emerald', secondary: 'green', tertiary: 'teal' },
        'pink': { primary: 'pink', secondary: 'rose', tertiary: 'fuchsia' }
      };
      
      return colorMappings[baseColor] || colorMappings.primary;
    });
    
    return {
      colorScheme
    }
  }
})
</script>

<style scoped>
/* Removed animations */
</style> 