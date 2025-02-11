<template>
  <div>
    <!-- Progress Label -->
    <div v-if="showLabel" class="flex justify-between mb-1 text-sm">
      <span class="text-gray-400">{{ label }}</span>
      <span class="text-gray-400">{{ percentage }}%</span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-dark-700 rounded-full h-2 overflow-hidden">
      <div
        class="h-full transition-all duration-500 ease-out rounded-full"
        :class="[colorClass]"
        :style="{ width: `${percentage}%` }"
      ></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    value: {
      type: Number,
      required: true
    },
    total: {
      type: Number,
      required: true
    },
    label: {
      type: String,
      default: ''
    },
    showLabel: {
      type: Boolean,
      default: false
    },
    color: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'success', 'warning', 'error'].includes(value)
    }
  },
  computed: {
    percentage() {
      return Math.round((this.value / this.total) * 100)
    },
    colorClass() {
      const colors = {
        primary: 'bg-primary-500',
        success: 'bg-green-500',
        warning: 'bg-yellow-500',
        error: 'bg-red-500'
      }
      return colors[this.color]
    }
  }
}
</script>
