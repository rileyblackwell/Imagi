s<template>
  <button
    class="flex items-center w-full px-4 py-3 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors duration-200"
    @click="handleClick"
  >
    <i :class="[icon, 'text-primary-400 mr-3 w-5']"></i>
    <span class="text-white">{{ title }}</span>
    <i class="fas fa-chevron-right ml-auto text-gray-500"></i>
  </button>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  route: {
    type: [String, Object],
    required: true
  }
})

function handleClick() {
  router.push(props.route)
}
</script>
