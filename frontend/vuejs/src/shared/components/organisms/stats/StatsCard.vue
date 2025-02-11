<template>
  <div class="bg-dark-800/50 backdrop-blur-sm border border-dark-700 rounded-xl p-6">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-gray-400 text-sm mb-1">{{ title }}</p>
        <h3 class="text-2xl font-bold" :class="`text-${color}-400`">{{ value }}</h3>
        <div v-if="trend" class="mt-2 flex items-center">
          <span 
            class="text-xs font-medium"
            :class="trendClass"
          >
            {{ trend }}
          </span>
        </div>
      </div>
      <div 
        class="p-3 rounded-lg"
        :class="`bg-${color}-500/10`"
      >
        <i 
          class="text-lg"
          :class="[icon, `text-${color}-400`]"
        ></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: number | string
  icon: string
  color?: 'primary' | 'success' | 'warning' | 'info'
  trend?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary'
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  return props.trend.startsWith('+') 
    ? 'text-green-400' 
    : 'text-red-400'
})
</script>
