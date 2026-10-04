<template>
  <div class="flex items-center gap-2.5">
    <div
      class="w-5 h-5 rounded-md flex items-center justify-center transition-all duration-300"
      :class="checked
        ? 'bg-orange-100 dark:bg-orange-400/[0.16] border border-orange-200/80 dark:border-orange-400/30'
        : 'bg-white/70 dark:bg-white/[0.04] border border-blue-950/[0.1] dark:border-white/[0.12]'"
    >
      <i
        class="fas text-[10px] transition-all duration-300"
        :class="checked
          ? 'fa-check text-orange-600 dark:text-orange-300'
          : 'fa-circle text-blue-950/20 dark:text-blue-100/20'"
      ></i>
    </div>
    <span
      class="text-sm transition-colors duration-300"
      :class="checked ? 'text-blue-950/80 dark:text-blue-100/85' : 'text-blue-950/40 dark:text-blue-100/40'"
    >
      {{ text }}
    </span>
  </div>
</template>

<script setup>
defineProps({
  checked: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    required: true
  }
})
</script>
