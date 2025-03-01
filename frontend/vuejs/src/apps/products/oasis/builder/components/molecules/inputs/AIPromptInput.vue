<template>
  <div class="relative">
    <div class="flex items-end border border-dark-700 rounded-lg bg-dark-900 shadow-lg">
      <!-- Auto-expanding textarea -->
      <textarea
        id="user-input"
        ref="textareaRef"
        v-model="inputValue"
        :placeholder="placeholder"
        class="flex-1 bg-transparent text-white px-4 py-3 max-h-[200px] min-h-[56px] focus:outline-none resize-none overflow-y-auto"
        :rows="rows"
        @input="autoResize"
        @keydown.enter.prevent="handleEnterKey"
      ></textarea>
      
      <!-- Send button -->
      <button
        @click="handleSubmit"
        class="p-3 mr-2 mb-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        :class="[
          inputValue.trim() 
            ? 'bg-primary-500 hover:bg-primary-600' 
            : 'bg-dark-700'
        ]"
        :disabled="loading || !inputValue.trim()"
        :title="loading ? 'Processing...' : 'Send message'"
      >
        <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
      </button>
    </div>
    
    <!-- Mode indicator and helper text -->
    <div class="mt-2 flex justify-between items-center text-xs text-gray-500">
      <div>
        <span class="inline-flex items-center">
          <i class="fas mr-1" :class="mode === 'chat' ? 'fa-comments' : 'fa-code'"></i>
          {{ mode === 'chat' ? 'Chat Mode' : 'Build Mode' }}
        </span>
      </div>
      <div>
        <kbd class="px-1 py-0.5 bg-dark-800 rounded text-gray-400">Enter</kbd>
        <span class="mx-1">to send</span>
        <kbd class="px-1 py-0.5 bg-dark-800 rounded text-gray-400">Shift+Enter</kbd>
        <span class="mx-1">for new line</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps<{
  modelValue: string
  loading?: boolean
  mode?: 'chat' | 'build'
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string): void
}>()

const inputValue = ref(props.modelValue)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const rows = ref(1)

watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
  nextTick(() => autoResize())
})

watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
})

const autoResize = () => {
  if (!textareaRef.value) return
  
  // Reset height to calculate proper scrollHeight
  textareaRef.value.style.height = 'auto'
  
  // Set new height based on content
  const newHeight = Math.min(textareaRef.value.scrollHeight, 200)
  textareaRef.value.style.height = `${newHeight}px`
  
  // Update rows for accessibility
  rows.value = Math.max(1, Math.min(10, Math.ceil(newHeight / 24)))
}

const handleEnterKey = (event: KeyboardEvent) => {
  if (event.shiftKey) {
    // Allow Shift+Enter for new line
    const textarea = event.target as HTMLTextAreaElement
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    inputValue.value = 
      inputValue.value.substring(0, start) + 
      '\n' + 
      inputValue.value.substring(end)
    
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 1
      autoResize()
    })
  } else {
    // Regular Enter submits the form
    handleSubmit()
  }
}

const handleSubmit = () => {
  if (!inputValue.value.trim() || props.loading) return
  emit('submit', inputValue.value)
}

onMounted(() => {
  autoResize()
})
</script>

<style scoped>
textarea {
  font-family: inherit;
  line-height: 1.5;
  font-size: 0.875rem;
}

/* Hide scrollbar but allow scrolling */
textarea::-webkit-scrollbar {
  width: 4px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.700');
  border-radius: 9999px;
}
</style>
