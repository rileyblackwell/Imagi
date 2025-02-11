<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { EditorView } from '@/shared/components/molecules'
import type { EditorOptions, EditorLanguage } from '@/shared/types/editor'

const props = defineProps<{
  modelValue: string // Changed from content to modelValue for v-model convention
  language?: EditorLanguage
  readOnly?: boolean
  placeholder?: string
  wrap?: 'off' | 'on'
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void // Changed to match v-model convention
  (e: 'change', value: string): void
}>()

const editorOptions = ref<EditorOptions>({
  language: props.language || 'typescript',
  theme: 'dark',
  readOnly: props.readOnly
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  emit('change', target.value)
}
</script>

<template>
  <div class="h-full rounded-lg border border-dark-700 bg-dark-900">
    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      class="w-full h-full bg-dark-900 text-white p-4 font-mono resize-none focus:outline-none"
      @input="handleInput"
      :spellcheck="false"
      :wrap="wrap"
    ></textarea>
  </div>
</template>

<style scoped>
textarea {
  tab-size: 2;
  -moz-tab-size: 2;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  line-height: 1.5;
  font-size: 0.875rem;
}
</style>
