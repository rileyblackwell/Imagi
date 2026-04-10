<!-- Reusable feature card component -->
<template>
  <div 
    class="bg-white dark:bg-white rounded-2xl p-8 border border-gray-200 dark:border-gray-300 relative overflow-hidden shadow-md"
  >
    <!-- Icon container with solid color background -->
    <div 
      class="w-16 h-16 rounded-xl flex items-center justify-center mb-6 shadow-lg relative overflow-hidden"
      :class="iconBgClass"
    >
      <i 
        class="text-white text-2xl"
        :class="icon"
      ></i>
    </div>
    
    <h3 
      class="text-2xl font-semibold text-gray-900 dark:text-black mb-4"
    >
      {{ title }}
    </h3>
    
    <p class="text-gray-600 dark:text-black text-base leading-relaxed">{{ description }}</p>
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
    
    // Simple solid color background for icon
    const iconBgClass = computed(() => 
      `bg-${props.color}-500`
    );

    return {
      iconBgClass,
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