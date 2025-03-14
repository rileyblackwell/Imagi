<template>
  <div 
    class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl p-8 border border-dark-700/40 transition-all duration-300 hover:-translate-y-1 relative overflow-hidden shadow-lg hover:shadow-xl"
    :class="hoverBorderClass"
  >
    <!-- Card top highlight -->
    <div 
      class="absolute top-0 inset-x-0 h-px bg-gradient-to-r opacity-40 group-hover:opacity-100 transition-opacity duration-300"
      :class="gradientFromClass"
    ></div>
    
    <!-- Card inner glow -->
    <div 
      class="absolute inset-0 bg-gradient-to-br opacity-10 group-hover:opacity-30 transition-opacity duration-500"
      :class="innerGlowClass"
    ></div>
    
    <div class="flex items-start mb-4">
      <!-- Enhanced icon container with vibrant gradients - no tilting -->
      <div 
        class="w-16 h-16 rounded-xl flex items-center justify-center mr-6 group-hover:scale-110 transition-all duration-500 shadow-lg relative overflow-hidden"
        :class="iconBgClass"
      >
        <i 
          class="text-white text-2xl"
          :class="icon"
        ></i>
        
        <!-- Subtle inner glow for the icon -->
        <div class="absolute inset-0 rounded-xl bg-white/10 opacity-0 group-hover:opacity-30 transition-all duration-300 blur-sm"></div>
      </div>
      
      <div>
        <h3 
          class="text-4xl font-bold mb-1 transition-colors duration-300"
          :class="valueTextClass"
        >
          {{ formatValue }}
        </h3>
        <p class="text-gray-300 text-lg">{{ label }}</p>
      </div>
    </div>
    
    <p v-if="description" class="text-gray-100 text-base mt-4 leading-relaxed">{{ description }}</p>
    
    <!-- Border highlight effect -->
    <div 
      class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"
      :class="bottomGradientClass"
    ></div>
    
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
    
    const hoverBorderClass = computed(() => `hover:border-${props.color}-500/50`);
    const gradientFromClass = computed(() => `from-${props.color}-500/0 via-${props.color}-500/60 to-${props.color}-500/0`);
    const innerGlowClass = computed(() => `from-${props.color}-500/10 to-${secondaryColor.value}-500/10`);
    
    // Static vibrant gradient without animation
    const iconBgClass = computed(() => 
      `bg-gradient-to-br from-${props.color}-400 via-${secondaryColor.value}-500 to-${tertiaryColor.value}-500 group-hover:from-${props.color}-300 group-hover:via-${secondaryColor.value}-400 group-hover:to-${tertiaryColor.value}-400`
    );
    
    const valueTextClass = computed(() => `text-${props.color}-300`);
    const bottomGradientClass = computed(() => `from-${props.color}-500/0 via-${props.color}-500 to-${props.color}-500/0`);
    const progressRingClass = computed(() => `text-${props.color}-400`);
    const progressTextClass = computed(() => `text-${props.color}-300`);
    
    return {
      formatValue,
      isPercentage,
      percentageValue,
      calculateCircumference,
      calculateOffset,
      hoverBorderClass,
      gradientFromClass,
      innerGlowClass,
      iconBgClass,
      valueTextClass,
      bottomGradientClass,
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