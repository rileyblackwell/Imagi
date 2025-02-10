<template>
  <div class="mt-8 space-y-4">
    <p class="text-center text-gray-400">
      {{ mainText }}
      <router-link :to="mainLink.to" class="text-primary-400 hover:text-primary-300 font-medium">
        {{ mainLink.text }}
      </router-link>
    </p>
    <div class="flex flex-col items-center space-y-2">
      <div class="w-full border-t border-dark-700"></div>
      <slot name="additional-links"></slot>
      <router-link to="/" class="text-gray-400 hover:text-gray-300">
        Back to Home
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  mainText: {
    type: String,
    default: ''
  },
  mainLink: {
    type: Object,
    default: () => ({ to: '', text: '' })
  }
})

const validateMainLink = (link) => {
  if (!link) return false
  if (typeof link !== 'object') return false
  if (!link.to || !link.text) return false
  if (typeof link.to !== 'string' || typeof link.text !== 'string') return false
  return true
}

watch(() => props.mainLink, (newLink) => {
  if (!validateMainLink(newLink)) {
    console.warn('AuthLinks: Invalid mainLink prop')
  }
}, { immediate: true })
</script>