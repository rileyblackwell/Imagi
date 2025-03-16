<template>
  <div class="preview-panel relative">
    <!-- Background glass effect -->
    <div class="absolute inset-0 bg-dark-900/30 backdrop-blur-sm rounded-md pointer-events-none"></div>
    
    <!-- HTML/Vue Preview -->
    <div v-if="['html', 'vue'].includes(fileType as string)" class="preview-frame relative z-10">
      <div v-html="sanitizedContent" class="preview-content" />
    </div>

    <!-- Markdown Preview -->
    <div v-else-if="fileType === 'md' as EditorLanguage" class="prose prose-invert max-w-none p-4 relative z-10">
      <div v-html="markdownContent" />
    </div>

    <!-- JSON Preview -->
    <div v-else-if="fileType === 'json' as EditorLanguage" class="font-mono text-sm whitespace-pre-wrap p-4 relative z-10 bg-dark-950/50 rounded-md shadow-inner">
      {{ formattedJSON }}
    </div>

    <!-- CSS Preview -->
    <div v-else-if="['css', 'scss'].includes(fileType as string)" class="preview-frame relative z-10">
      <div class="preview-content">
        <div class="css-preview-demo bg-dark-900/50 p-6 rounded-md shadow-inner" ref="cssPreviewRef">
          <!-- Demo elements for CSS preview -->
          <h3 class="text-lg font-medium text-white mb-4">CSS Preview</h3>
          <div class="demo-element p-4 bg-dark-800/80 rounded-md mb-3 border border-dark-700/50">Demo Element</div>
          <button class="demo-button px-4 py-2 bg-primary-500/50 rounded-md mb-3 hover:bg-primary-500/70 transition-colors">Demo Button</button>
          <input type="text" class="demo-input w-full p-2 bg-dark-800/80 rounded-md border border-dark-700/50 focus:border-primary-500/50 outline-none transition-colors" placeholder="Demo Input">
        </div>
      </div>
    </div>

    <!-- Default/Unsupported -->
    <div v-else class="text-gray-400 text-center py-12 relative z-10">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-dark-800/50 backdrop-blur-md mb-4 border border-dark-700/50">
        <i class="fas fa-eye-slash text-2xl text-gray-400" />
      </div>
      <p class="text-lg">Preview not available for this file type</p>
      <p class="text-sm text-gray-500 mt-2">{{ fileType ? fileType.toUpperCase() : 'Unknown' }} files cannot be previewed</p>
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
  @apply min-h-[200px] h-full rounded-md overflow-hidden;
}

.preview-frame {
  @apply h-full overflow-auto p-4;
}

.preview-content {
  @apply min-h-[200px] bg-dark-900/50 rounded-md p-4 border border-dark-700/30;
}

:deep(.prose) {
  @apply text-gray-300;
}

:deep(.prose h1),
:deep(.prose h2),
:deep(.prose h3) {
  @apply text-white border-b border-dark-700/50 pb-2;
}

:deep(.prose a) {
  @apply text-primary-400 hover:text-primary-300 no-underline border-b border-primary-500/30 hover:border-primary-500/70 transition-all;
}

:deep(.prose code) {
  @apply bg-dark-800 text-primary-300 px-1.5 py-0.5 rounded text-sm;
}

:deep(.prose pre) {
  @apply bg-dark-900 border border-dark-700/50 rounded-md p-4;
}

:deep(.prose blockquote) {
  @apply border-l-4 border-primary-500/30 bg-dark-800/50 rounded-r-md pl-4 py-1 italic;
}

:deep(.prose ul),
:deep(.prose ol) {
  @apply pl-5;
}

:deep(.prose li) {
  @apply mb-1;
}

:deep(.prose table) {
  @apply border-collapse w-full;
}

:deep(.prose th) {
  @apply bg-dark-800 text-white font-medium text-left p-2 border border-dark-700/50;
}

:deep(.prose td) {
  @apply p-2 border border-dark-700/50;
}

:deep(.prose img) {
  @apply max-w-full h-auto rounded-md border border-dark-700/50;
}
</style> 