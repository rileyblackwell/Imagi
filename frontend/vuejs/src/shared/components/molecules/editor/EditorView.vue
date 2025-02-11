<template>
  <div class="w-full h-full">
    <div ref="editorContainer" class="h-full"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { Editor, EditorOptions } from '@/shared/types'

const props = withDefaults(defineProps<{
  modelValue: string
  options?: EditorOptions
}>(), {
  options: () => ({
    language: 'typescript',
    theme: 'dark',
    lineNumbers: true,
    minimap: true
  })
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}>()

const editorContainer = ref<HTMLElement | null>(null)

// ...rest of editor implementation...
</script>
