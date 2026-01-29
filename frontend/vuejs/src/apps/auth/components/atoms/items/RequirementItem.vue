<template>
  <div class="flex items-center gap-2.5">
    <div 
      class="w-5 h-5 rounded-md flex items-center justify-center transition-all duration-300"
      :class="checked 
        ? 'bg-emerald-500/20 border border-emerald-500/40' 
        : 'bg-black/[0.03] dark:bg-white/[0.03] border border-black/[0.08] dark:border-white/[0.08]'"
    >
      <i 
        class="fas text-[10px] transition-all duration-300"
        :class="checked 
          ? 'fa-check text-emerald-500 dark:text-emerald-400' 
          : 'fa-circle text-black/20 dark:text-white/20'"
      ></i>
    </div>
    <span 
      class="text-sm transition-colors duration-300"
      :class="checked ? 'text-black/80 dark:text-white/80' : 'text-black/40 dark:text-white/40'"
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
