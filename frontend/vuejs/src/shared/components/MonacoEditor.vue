<template>
  <div class="monaco-editor-container" :style="{ height: height || '100%' }">
    <div ref="editorContainer" class="editor-instance h-full w-full"></div>
  </div>
</template>

<script>
import { defineComponent, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as monaco from 'monaco-editor'

export default defineComponent({
  name: 'MonacoEditor',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    language: {
      type: String,
      default: 'javascript'
    },
    theme: {
      type: String,
      default: 'vs-dark'
    },
    height: {
      type: String,
      default: null
    },
    options: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    let editor = null
    let preventTriggerChangeEvent = false

    const initMonaco = async () => {
      const container = document.querySelector('.editor-instance')
      if (!container) return

      // Configure default options
      const defaultOptions = {
        value: props.modelValue,
        language: props.language,
        theme: props.theme,
        automaticLayout: true,
        minimap: {
          enabled: false
        },
        scrollBeyondLastLine: false,
        fontSize: 14,
        lineNumbers: 'on',
        roundedSelection: true,
        scrollbar: {
          useShadows: false,
          verticalScrollbarSize: 8,
          horizontalScrollbarSize: 8
        },
        ...props.options
      }

      editor = monaco.editor.create(container, defaultOptions)

      // Handle content changes
      editor.onDidChangeModelContent(() => {
        if (!preventTriggerChangeEvent) {
          const value = editor.getValue()
          emit('update:modelValue', value)
          emit('change', value)
        }
      })
    }

    // Watch for prop changes
    watch(() => props.modelValue, (newValue) => {
      if (editor && newValue !== editor.getValue()) {
        preventTriggerChangeEvent = true
        editor.setValue(newValue)
        preventTriggerChangeEvent = false
      }
    })

    watch(() => props.language, (newValue) => {
      if (editor) {
        monaco.editor.setModelLanguage(editor.getModel(), newValue)
      }
    })

    watch(() => props.theme, (newValue) => {
      if (editor) {
        monaco.editor.setTheme(newValue)
      }
    })

    // Lifecycle hooks
    onMounted(async () => {
      await nextTick()
      await initMonaco()
    })

    onBeforeUnmount(() => {
      if (editor) {
        editor.dispose()
      }
    })

    return {}
  }
})
</script>

<style>
.monaco-editor-container {
  @apply rounded-lg overflow-hidden;
}

.editor-instance {
  @apply rounded-lg overflow-hidden;
}
</style> 