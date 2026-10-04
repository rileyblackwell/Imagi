<template>
  <div class="flex items-center gap-2.5">
    <div
      class="w-5 h-5 rounded-md flex items-center justify-center transition-all duration-300"
      :class="checked
        ? 'bg-orange-100 dark:bg-orange-400/[0.16] border border-orange-200/80 dark:border-orange-400/30'
        : 'bg-white/70 dark:bg-white/[0.04] border border-ink/[0.1] dark:border-white/[0.12]'"
    >
      <i
        class="fas text-[10px] transition-all duration-300"
        :class="checked
          ? 'fa-check text-orange-600 dark:text-orange-300'
          : 'fa-circle text-ink/20 dark:text-bone/20'"
      ></i>
    </div>
    <span
      class="text-sm transition-colors duration-300"
      :class="checked ? 'text-ink/80 dark:text-bone/85' : 'text-ink/40 dark:text-bone/40'"
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
