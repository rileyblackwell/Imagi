<template>
  <div class="flex items-center gap-2">
    <i class="fas fa-check text-xs"
       :class="checked ? 'text-green-400' : 'text-gray-600'">
    </i>
    <span :class="[
      'text-sm transition-colors duration-200',
      checked ? 'text-gray-200' : 'text-gray-400'
    ]">{{ text }}</span>
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
