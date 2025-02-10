<template>
  <div class="rounded-xl bg-dark-800/50 backdrop-blur-sm p-4 border border-dark-700">
    <h4 class="text-sm font-medium text-white mb-3">Password Requirements:</h4>
    <ul class="space-y-2">
      <li 
        v-for="(requirement, index) in requirements" 
        :key="index"
        class="text-sm flex items-center transition-colors duration-300"
        :class="{ 'text-green-400': requirement.met, 'text-gray-400': !requirement.met }" 
      >
        <i :class="[
          'fas',
          requirement.met ? 'fa-check text-green-400' : 'fa-times text-gray-400',
          'mr-2 w-4 transition-all duration-300'
        ]"></i>
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