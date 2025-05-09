<template>
  <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
    <div :class="[`absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-${color}-500 to-${secondaryColor}-500`]"></div>
    <div class="pl-4">
      <div class="flex items-center mb-4">
        <div :class="[`w-8 h-8 bg-${color}-500/20 rounded-full flex items-center justify-center mr-3`]">
          <span :class="[`text-${color}-400 font-bold`]">{{ number }}</span>
        </div>
        <h2 class="text-2xl font-bold text-white m-0">{{ title }}</h2>
      </div>
      <div class="ml-11">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  number: string | number;
  title: string;
  color?: string;
  secondaryColor?: string;
}>(), {
  color: 'primary',
  secondaryColor: 'violet'
});
</script> 