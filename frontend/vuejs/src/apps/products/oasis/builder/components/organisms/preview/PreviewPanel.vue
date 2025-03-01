<template>
  <div class="preview-panel">
    <!-- HTML/Vue Preview -->
    <div v-if="['html', 'vue'].includes(fileType as string)" class="preview-frame">
      <div v-html="sanitizedContent" class="preview-content" />
    </div>

    <!-- Markdown Preview -->
    <div v-else-if="fileType === 'md' as EditorLanguage" class="prose prose-invert max-w-none">
      <div v-html="markdownContent" />
    </div>

    <!-- JSON Preview -->
    <div v-else-if="fileType === 'json' as EditorLanguage" class="font-mono text-sm whitespace-pre-wrap">
      {{ formattedJSON }}
    </div>

    <!-- CSS Preview -->
    <div v-else-if="['css', 'scss'].includes(fileType as string)" class="preview-frame">
      <div class="preview-content">
        <div class="css-preview-demo" ref="cssPreviewRef">
          <!-- Demo elements for CSS preview -->
          <div class="demo-element">Demo Element</div>
          <button class="demo-button">Demo Button</button>
          <input type="text" class="demo-input" placeholder="Demo Input">
        </div>
      </div>
    </div>

    <!-- Default/Unsupported -->
    <div v-else class="text-gray-400 text-center py-8">
      <i class="fas fa-eye-slash text-2xl mb-2" />
      <p>Preview not available for this file type</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'isomorphic-dompurify'
import type { EditorLanguage } from '@/shared/types/editor'

const props = defineProps<{
  content: string
  fileType?: EditorLanguage
}>()

const cssPreviewRef = ref<HTMLElement | null>(null)

// Watch for CSS content changes
watch(() => props.content, (newContent) => {
  if (cssPreviewRef.value && ['css', 'scss'].includes(props.fileType as string)) {
    applyStyles(newContent)
  }
}, { immediate: true })

// Computed properties
const sanitizedContent = computed(() => {
  return DOMPurify.sanitize(props.content)
})

const markdownContent = computed(() => {
  const parsedContent = marked.parse(props.content) as string
  return DOMPurify.sanitize(parsedContent)
})

const formattedJSON = computed(() => {
  try {
    return JSON.stringify(JSON.parse(props.content), null, 2)
  } catch {
    return props.content
  }
})

// Utility functions
const applyStyles = (css: string) => {
  if (!cssPreviewRef.value) return

  // Create a scoped stylesheet
  const styleId = 'preview-styles'
  let styleEl = document.getElementById(styleId) as HTMLStyleElement
  
  if (!styleEl) {
    styleEl = document.createElement('style')
    styleEl.id = styleId
    document.head.appendChild(styleEl)
  }

  // Scope the CSS to our preview container
  const scopedCss = css.replace(/([^{}]*){/g, (match) => {
    const selector = match.slice(0, -1).trim()
    return `.preview-frame .css-preview-demo ${selector} {`
  })

  styleEl.textContent = scopedCss
}

// Clean up styles on component unmount
onBeforeUnmount(() => {
  const styleEl = document.getElementById('preview-styles')
  if (styleEl) {
    styleEl.remove()
  }
})
</script>

<style scoped>
.preview-panel {
  height: 100%;
  overflow: auto;
}

.preview-frame {
  height: 100%;
  background: white;
  color: #1a1a1a;
}

.preview-content {
  padding: 1rem;
}

/* CSS Preview Demo Styles */
.css-preview-demo {
  display: grid;
  gap: 1rem;
  padding: 1rem;
}

.demo-element {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
}

.demo-button {
  padding: 0.5rem 1rem;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
}

.demo-input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 0.375rem;
  width: 100%;
}

/* Markdown Styles */
.prose {
  font-size: 0.875rem;
}

.prose pre {
  background-color: theme('colors.dark.900');
  border: 1px solid theme('colors.dark.700');
  border-radius: 0.375rem;
}

.prose code {
  color: theme('colors.primary.400');
  background-color: theme('colors.dark.900');
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}
</style> 