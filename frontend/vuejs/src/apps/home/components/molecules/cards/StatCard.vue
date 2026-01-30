<template>
  <div 
    class="bg-white dark:bg-white rounded-2xl p-8 border border-gray-200 dark:border-gray-300 relative overflow-hidden shadow-md"
  >
    <div class="flex items-start mb-4">
      <!-- Icon container with solid color background -->
      <div 
        class="w-16 h-16 rounded-xl flex items-center justify-center mr-6 shadow-lg relative overflow-hidden"
        :class="iconBgClass"
      >
        <i 
          class="text-white text-2xl"
          :class="icon"
        ></i>
      </div>
      
      <div>
        <h3 
          class="text-4xl font-bold mb-1"
          :class="valueTextClass"
        >
          {{ formatValue }}
        </h3>
        <p class="text-gray-600 dark:text-black text-lg">{{ label }}</p>
      </div>
    </div>
    
    <p v-if="description" class="text-gray-600 dark:text-black text-base mt-4 leading-relaxed">{{ description }}</p>
    
    <!-- Enhanced percentage indicator (only for percentage values) -->
    <div 
      v-if="isPercentage" 
      class="absolute top-4 right-4 w-14 h-14 flex items-center justify-center"
    >
      <svg class="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        <circle 
          cx="50" cy="50" r="40" 
          class="fill-none stroke-dark-600" 
          stroke-width="8"
        />
        <circle 
          cx="50" cy="50" r="40" 
          class="fill-none stroke-current transition-all duration-500 ease-out" 
          :class="progressRingClass"
          stroke-width="8"
          :stroke-dasharray="calculateCircumference" 
          :stroke-dashoffset="calculateOffset"
        />
      </svg>
      <span 
        class="absolute text-sm font-bold"
        :class="progressTextClass"
      >
        {{ percentageValue }}%
      </span>
    </div>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'StatCard',
  props: {
    value: {
      type: [Number, String],
      required: true
    },
    label: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      required: true
    },
    prefix: {
      type: String,
      default: ''
    },
    suffix: {
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
    // Enhanced color mapping system for vibrant gradients
    const secondaryColor = computed(() => {
      const colorMap = {
        'primary': 'violet',
        'indigo': 'purple',
        'violet': 'fuchsia',
        'green': 'emerald',
        'purple': 'indigo',
        'fuchsia': 'pink',
        'cyan': 'blue',
        'amber': 'orange',
        'rose': 'pink',
        'teal': 'cyan',
        'blue': 'indigo',
        'orange': 'amber',
        'emerald': 'teal',
        'pink': 'fuchsia'
      };
      return colorMap[props.color] || 'violet';
    });
    
    // Get a third complementary color for more complex gradients
    const tertiaryColor = computed(() => {
      const colorMap = {
        'primary': 'blue',
        'indigo': 'blue',
        'violet': 'indigo',
        'green': 'teal',
        'purple': 'fuchsia',
        'fuchsia': 'purple',
        'cyan': 'teal',
        'amber': 'yellow',
        'rose': 'red',
        'teal': 'green',
        'blue': 'cyan',
        'orange': 'red',
        'emerald': 'green',
        'pink': 'rose'
      };
      return colorMap[props.color] || 'blue';
    });
    
    const formatValue = computed(() => {
      const val = typeof props.value === 'number' ? props.value.toLocaleString() : props.value;
      return `${props.prefix}${val}${props.suffix}`;
    });
    
    const isPercentage = computed(() => {
      const numValue = parseFloat(props.value);
      return !isNaN(numValue) && props.suffix === '%' && numValue >= 0 && numValue <= 100;
    });
    
    const percentageValue = computed(() => {
      return isPercentage.value ? parseFloat(props.value) : 0;
    });
    
    const calculateCircumference = 2 * Math.PI * 40;
    
    const calculateOffset = computed(() => {
      if (!isPercentage.value) return 0;
      return calculateCircumference - (percentageValue.value / 100) * calculateCircumference;
    });
    
    // Simple solid color background for icon
    const iconBgClass = computed(() => 
      `bg-${props.color}-500`
    );
    
    const valueTextClass = computed(() => `text-${props.color}-300`);
    const progressRingClass = computed(() => `text-${props.color}-400`);
    const progressTextClass = computed(() => `text-${props.color}-300`);
    
    return {
      formatValue,
      isPercentage,
      percentageValue,
      calculateCircumference,
      calculateOffset,
      iconBgClass,
      valueTextClass,
      progressRingClass,
      progressTextClass,
      tertiaryColor
    }
  }
})
</script>

<style scoped>
/* Removed shimmer animation */
</style> 