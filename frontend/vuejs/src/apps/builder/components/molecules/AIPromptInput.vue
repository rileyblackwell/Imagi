<template>
  <div class="p-4 border-t border-dark-700">
    <div class="flex items-center space-x-4">
      <input
        id="user-input"
        v-model="inputValue"
        type="text"
        placeholder="Describe what you want to build..."
        class="flex-1 bg-dark-900 border border-dark-600 rounded-lg text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
        @keyup.enter="handleSubmit"
      >
      <button
        @click="handleSubmit"
        class="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="loading || !inputValue.trim()"
      >
        <i class="fas fa-magic mr-2"></i>
        Generate
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string): void
}>()

const inputValue = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
})

watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
})

const handleSubmit = () => {
  if (!inputValue.value.trim() || props.loading) return
  emit('submit', inputValue.value)
}
</script>
