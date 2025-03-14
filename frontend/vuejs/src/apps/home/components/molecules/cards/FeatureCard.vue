<!-- Reusable feature card component -->
<template>
  <div 
    class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl p-7 border border-dark-700/40 transition-all duration-300 hover:-translate-y-1 relative overflow-hidden hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]"
    :class="[
      hoverBorderClass,
    ]"
  >
    <!-- Card top highlight -->
    <div 
      class="absolute top-0 inset-x-0 h-px bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity duration-300"
      :class="gradientFromClass"
    ></div>
    
    <!-- Card inner glow -->
    <div 
      class="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity duration-500"
      :class="innerGlowClass"
    ></div>
    
    <div 
      class="w-11 h-11 rounded-xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-md"
      :class="iconBgClass"
    >
      <i 
        class="text-white text-lg"
        :class="icon"
      ></i>
    </div>
    
    <h3 
      class="text-xl font-semibold text-white mb-3 transition-colors duration-300"
      :class="titleHoverClass"
    >
      {{ title }}
    </h3>
    
    <p class="text-gray-300 text-sm">{{ description }}</p>
    
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
      validator: (value) => ['primary', 'indigo', 'violet', 'fuchsia', 'purple', 'green'].includes(value)
    }
  },
  setup(props) {
    const hoverBorderClass = computed(() => `hover:border-${props.color}-500/30`);
    const gradientFromClass = computed(() => `from-${props.color}-500/0 via-${props.color}-500/40 to-${props.color}-500/0`);
    const innerGlowClass = computed(() => `from-${props.color}-500/5 to-${props.color === 'primary' ? 'violet' : 'purple'}-500/5`);
    const iconBgClass = computed(() => `bg-gradient-to-br from-${props.color}-500 to-${props.color === 'primary' ? 'indigo' : props.color === 'indigo' ? 'violet' : 'purple'}-500`);
    const titleHoverClass = computed(() => `group-hover:text-${props.color}-300`);
    const bottomGradientClass = computed(() => `from-${props.color}-500/0 via-${props.color}-500 to-${props.color}-500/0`);

    return {
      hoverBorderClass,
      gradientFromClass,
      innerGlowClass,
      iconBgClass,
      titleHoverClass,
      bottomGradientClass
    }
  }
})
</script>

<style scoped>
.shadow-glow {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 255, 204, 0.1);
}
</style> 