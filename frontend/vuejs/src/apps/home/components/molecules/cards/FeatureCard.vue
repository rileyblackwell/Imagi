<!-- Reusable feature card component -->
<template>
  <div 
    class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl p-8 border border-dark-700/40 transition-all duration-300 hover:-translate-y-1 relative overflow-hidden hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]"
    :class="[
      hoverBorderClass,
    ]"
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
    
    <!-- Enhanced icon container with vibrant gradients - no tilting -->
    <div 
      class="w-16 h-16 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-all duration-500 shadow-lg relative overflow-hidden"
      :class="iconBgClass"
    >
      <i 
        class="text-white text-2xl"
        :class="icon"
      ></i>
      
      <!-- Subtle inner glow for the icon -->
      <div class="absolute inset-0 rounded-xl bg-white/10 opacity-0 group-hover:opacity-30 transition-all duration-300 blur-sm"></div>
    </div>
    
    <h3 
      class="text-2xl font-semibold text-white mb-4 transition-colors duration-300"
      :class="titleHoverClass"
    >
      {{ title }}
    </h3>
    
    <p class="text-gray-100 text-base leading-relaxed">{{ description }}</p>
    
    <!-- Border highlight effect -->
    <div 
      class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"
      :class="bottomGradientClass"
    ></div>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'FeatureCard',
  props: {
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
    
    const hoverBorderClass = computed(() => `hover:border-${props.color}-500/50`);
    const gradientFromClass = computed(() => `from-${props.color}-500/0 via-${props.color}-500/60 to-${props.color}-500/0`);
    const innerGlowClass = computed(() => `from-${props.color}-500/10 to-${secondaryColor.value}-500/10`);
    
    // Static vibrant gradient without animation
    const iconBgClass = computed(() => 
      `bg-gradient-to-br from-${props.color}-400 via-${secondaryColor.value}-500 to-${tertiaryColor.value}-500 group-hover:from-${props.color}-300 group-hover:via-${secondaryColor.value}-400 group-hover:to-${tertiaryColor.value}-400`
    );
    
    const titleHoverClass = computed(() => `group-hover:text-${props.color}-300`);
    const bottomGradientClass = computed(() => `from-${props.color}-500/0 via-${props.color}-500 to-${props.color}-500/0`);

    return {
      hoverBorderClass,
      gradientFromClass,
      innerGlowClass,
      iconBgClass,
      titleHoverClass,
      bottomGradientClass,
      secondaryColor,
      tertiaryColor
    }
  }
})
</script>

<style scoped>
.shadow-glow {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 255, 204, 0.1);
}

/* Removed shimmer animation */
</style> 