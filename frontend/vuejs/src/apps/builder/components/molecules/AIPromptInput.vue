<template>
  <div class="w-full max-w-6xl mx-auto">
    <div class="relative">
      <textarea
        id="user-input"
        v-model="inputValue"
        :disabled="loading"
        rows="2"
        class="w-full resize-none bg-dark-900 border border-dark-600 rounded-lg text-white px-4 py-3 pr-24 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500/20 placeholder-gray-500"
        :class="{ 'opacity-50': loading }"
        placeholder="Describe what you want to build..."
        @keydown.enter.exact.prevent="handleSubmit"
        @keydown.enter.shift.exact.prevent="newline"
        @keydown.enter.meta.exact.prevent="handleSubmit"
      ></textarea>
      
      <!-- Send Button -->
      <button
        class="absolute right-2 bottom-2 px-4 py-1.5 bg-primary-500 text-white rounded-md text-sm font-medium transition-colors hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        :disabled="!canSubmit || loading"
        @click="handleSubmit"
      >
        <i class="fas fa-circle-notch fa-spin mr-2" v-if="loading"></i>
        <i class="fas fa-paper-plane mr-2" v-else></i>
        Send
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{
  modelValue: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit'): void
}>()

const inputValue = ref(props.modelValue)

const canSubmit = computed(() => inputValue.value.trim().length > 0)

const handleSubmit = () => {
  if (canSubmit.value && !props.loading) {
    emit('submit')
  }
}

const newline = (event: KeyboardEvent) => {
  const textarea = event.target as HTMLTextAreaElement
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  
  inputValue.value = 
    inputValue.value.substring(0, start) + 
    '\n' + 
    inputValue.value.substring(end)
  
  // Set cursor position after newline
  setTimeout(() => {
    textarea.selectionStart = textarea.selectionEnd = start + 1
  }, 0)
}

// Watch for external value changes
watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
})

// Emit changes to parent
watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>

<style scoped>
textarea {
  min-height: 64px;
  max-height: 200px;
}

textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>