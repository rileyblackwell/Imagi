<template>
  <div 
    class="bg-white dark:bg-white rounded-2xl p-8 border border-gray-200 dark:border-gray-300 relative overflow-hidden shadow-md"
  >
    <!-- Step number indicator -->
    <div class="flex items-start mb-6">
      <!-- Step number with solid color background -->
      <div 
        class="w-14 h-14 rounded-xl flex items-center justify-center shadow-lg text-xl font-bold text-white mr-4 relative overflow-hidden"
        :class="[`bg-${colorScheme.primary}-500`]"
      >
        {{ number }}
      </div>
      
      <h3 
        class="text-2xl font-semibold text-gray-900 dark:text-black pt-2"
      >{{ title }}</h3>
    </div>
    
    <p class="text-gray-600 dark:text-black text-base leading-relaxed mb-6">{{ description }}</p>
    
    <!-- Icon display with solid color background -->
    <div 
      v-if="icon" 
      class="w-16 h-16 rounded-xl flex items-center justify-center relative shadow-lg overflow-hidden"
      :class="[`bg-${colorScheme.primary}-500`]"
    >
      <i :class="icon" class="text-white text-2xl relative z-10"></i>
    </div>
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