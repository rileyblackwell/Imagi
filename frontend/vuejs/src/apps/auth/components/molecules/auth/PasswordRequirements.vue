<template>
  <div class="rounded-md bg-dark-700 p-4">
    <h4 class="text-sm font-medium text-white mb-2">Password Requirements:</h4>
    <ul class="space-y-1">
      <li 
        v-for="(requirement, index) in requirements" 
        :key="index"
        :class="{ 'text-green-500': requirement.met, 'text-gray-400': !requirement.met }" 
        class="text-sm flex items-center"
      >
        <i :class="['fas', requirement.met ? 'fa-check text-green-500' : 'fa-times text-gray-400', 'mr-2']"></i>
        {{ requirement.text }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  password: {
    type: String,
    required: true
  }
})

const requirements = computed(() => [
  {
    text: 'At least 8 characters',
    met: props.password.length >= 8
  },
  {
    text: 'One uppercase letter',
    met: /[A-Z]/.test(props.password)
  },
  {
    text: 'One lowercase letter',
    met: /[a-z]/.test(props.password)
  },
  {
    text: 'One number',
    met: /\d/.test(props.password)
  },
  {
    text: 'One special character',
    met: /[!@#$%^&*(),.?":{}|<>]/.test(props.password)
  }
])

// Expose validation state to parent
defineExpose({
  isValid: computed(() => requirements.value.every(req => req.met))
})
</script> 