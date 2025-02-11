<template>
  <div class="bg-dark-800 rounded-lg p-6">
    <div class="flex items-center">
      <div :class="[`text-${color}-400`, 'bg-dark-700 rounded-lg p-3']">
        <i :class="[icon, 'text-lg']"></i>
      </div>
      <div class="ml-4">
        <p class="text-sm text-gray-400">{{ title }}</p>
        <div class="flex items-baseline">
          <h3 class="text-2xl font-bold text-white">{{ value }}</h3>
          <span
            v-if="trend"
            :class="[
              getTrendColor(trend),
              'ml-2 text-sm font-medium'
            ]"
          >
            {{ trend }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  value: number | string;
  icon: string;
  trend?: string;
  color?: string;
}

defineProps<Props>()

function getTrendColor(trend: string): string {
  return trend.startsWith('+') 
    ? 'text-green-400' 
    : trend.startsWith('-') 
      ? 'text-red-400' 
      : 'text-gray-400'
}
</script>
