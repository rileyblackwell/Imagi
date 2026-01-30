<template>
  <div class="code-block">
    <div class="code-header flex justify-between items-center p-2 bg-dark-900 border-b border-dark-700 rounded-t-lg">
      <div class="language-tag text-xs font-mono text-gray-400">{{ language }}</div>
      <button 
        class="copy-button text-gray-400 hover:text-white p-1 rounded transition-colors"
        @click="copyToClipboard"
        :title="copyStatus ? 'Copied!' : 'Copy to clipboard'"
      >
        <i class="fas" :class="copyStatus ? 'fa-check' : 'fa-copy'"></i>
      </button>
    </div>
    <pre class="bg-dark-900 p-3 rounded-b-lg overflow-x-auto text-sm border border-dark-700/50 text-gray-200 font-mono"><code>{{ code }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Props
const props = defineProps<{
  code: string
  language: string
}>()

// State
const copyStatus = ref(false)

// Methods
function copyToClipboard() {
  navigator.clipboard.writeText(props.code)
    .then(() => {
      copyStatus.value = true
      setTimeout(() => {
        copyStatus.value = false
      }, 2000)
    })
    .catch(err => {
      console.error('Failed to copy code:', err)
    })
}
</script>

<style scoped>
.code-block {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

pre {
  white-space: pre-wrap;
  word-break: break-all;
}
</style> 