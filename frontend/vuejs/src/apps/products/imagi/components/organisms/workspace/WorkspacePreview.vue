<template>
  <div class="relative w-full h-full flex flex-col bg-white dark:bg-[#0a0a0a]">
    <!-- Loading state -->
    <div
      v-if="isLoading"
      class="flex-1 flex flex-col items-center justify-center gap-3 text-gray-600 dark:text-white/60"
    >
      <i class="fas fa-spinner fa-spin text-2xl"></i>
      <span class="text-sm font-medium">Starting preview server…</span>
    </div>

    <!-- Error state -->
    <div
      v-else-if="error"
      class="flex-1 flex flex-col items-center justify-center gap-4 px-8 text-center"
    >
      <div class="w-12 h-12 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 rounded-xl flex items-center justify-center">
        <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400"></i>
      </div>
      <p class="text-sm text-gray-700 dark:text-white/70 max-w-md">{{ error }}</p>
      <button
        @click="loadPreview"
        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] text-sm font-medium text-gray-700 dark:text-white/70 transition-colors"
      >
        <i class="fas fa-sync-alt text-xs"></i>
        Retry
      </button>
    </div>

    <!-- Ready state: app + page selectors + iframe -->
    <template v-else-if="previewUrl">
      <div class="flex flex-col gap-2 px-3 py-2 border-b border-gray-200 dark:border-white/[0.08] bg-gray-50 dark:bg-white/[0.02]">
        <div class="flex items-center gap-2 flex-wrap">
          <button
            type="button"
            @click="reload"
            title="Refresh page"
            class="inline-flex items-center justify-center w-9 h-9 shrink-0 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-100 dark:hover:bg-white/[0.06] text-gray-700 dark:text-white/70 transition-colors"
          >
            <i class="fas fa-sync-alt text-sm"></i>
          </button>

          <button
            type="button"
            @click="goHome"
            title="Go to home page"
            class="inline-flex items-center justify-center w-9 h-9 shrink-0 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-100 dark:hover:bg-white/[0.06] text-gray-700 dark:text-white/70 transition-colors"
          >
            <i class="fas fa-home text-sm"></i>
          </button>

          <!-- App selector -->
          <div class="flex items-center gap-2 min-w-0 flex-1">
            <div class="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-white/50 shrink-0">
              <i class="fas fa-cube text-sm"></i>
              <span>App</span>
            </div>
            <div class="relative flex-1 min-w-[8rem]">
              <select
                v-model="selectedApp"
                @change="onAppChange"
                :disabled="apps.length === 0"
                class="w-full appearance-none rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] focus:border-gray-400 dark:focus:border-white/20 outline-none py-2 pl-3 pr-9 text-sm font-medium text-gray-900 dark:text-white/90 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option v-if="apps.length === 0" value="">No apps yet</option>
                <option
                  v-for="app in apps"
                  :key="app.name"
                  :value="app.name"
                >
                  {{ app.title }}
                </option>
              </select>
              <i class="fas fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 dark:text-white/40 pointer-events-none"></i>
            </div>
          </div>

          <!-- Page selector -->
          <div class="flex items-center gap-2 min-w-0 flex-1">
            <div class="flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-white/50 shrink-0">
              <i class="fas fa-file-alt text-sm"></i>
              <span>Page</span>
            </div>
            <div class="relative flex-1 min-w-[8rem]">
              <select
                v-model="selectedPath"
                @change="onPageSelect"
                :disabled="pagesForSelectedApp.length === 0"
                class="w-full appearance-none rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] focus:border-gray-400 dark:focus:border-white/20 outline-none py-2 pl-3 pr-9 text-sm font-medium text-gray-900 dark:text-white/90 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option v-if="pagesForSelectedApp.length === 0" value="">No pages yet</option>
                <option
                  v-for="page in pagesForSelectedApp"
                  :key="page.path"
                  :value="page.path"
                >
                  {{ page.title }}
                </option>
                <option
                  v-if="!isPathInSelectedApp && currentPath"
                  :value="currentPath"
                >
                  Current — {{ currentPath }}
                </option>
              </select>
              <i class="fas fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 dark:text-white/40 pointer-events-none"></i>
            </div>
          </div>

        </div>
      </div>

      <iframe
        :key="iframeKey"
        :src="iframeSrc"
        class="flex-1 w-full border-0 bg-white"
        sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals"
      ></iframe>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { PreviewService } from '../../../services/previewService'
import { useAgentStore } from '../../../stores/agentStore'
import type { ProjectFile } from '../../../types/components'

const props = defineProps<{
  projectId: string
}>()

const store = useAgentStore()

const isLoading = ref(false)
const error = ref<string | null>(null)
const previewUrl = ref<string | null>(null)
const iframeKey = ref(0)
const currentPath = ref('/')
const selectedApp = ref('')
const selectedPath = ref('/')

const baseOrigin = computed(() => {
  if (!previewUrl.value) return ''
  try {
    return new URL(previewUrl.value).origin
  } catch {
    return previewUrl.value
  }
})

const iframeSrc = computed(() => {
  if (!previewUrl.value) return ''
  if (!baseOrigin.value) return previewUrl.value
  return baseOrigin.value + normalizePath(currentPath.value)
})

interface Page {
  title: string
  path: string
}

interface AppEntry {
  name: string
  title: string
  pages: Page[]
}

function toKebabCase(input: string): string {
  return input
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/\s+/g, '-')
    .replace(/_+/g, '-')
    .toLowerCase()
}

function humanize(input: string): string {
  return input
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[-_]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, c => c.toUpperCase())
}

const apps = computed<AppEntry[]>(() => {
  const files: ProjectFile[] = (store.files || []) as ProjectFile[]
  const viewRegex = /(?:^|\/)(?:frontend\/vuejs\/)?src\/apps\/([^/]+)\/views\/([^/]+)\.vue$/i
  const appMap = new Map<string, AppEntry>()

  for (const file of files) {
    if (!file?.path) continue
    const match = file.path.match(viewRegex)
    if (!match) continue
    const appName = match[1]!
    const viewName = match[2]!
    const base = viewName.endsWith('View') ? viewName.slice(0, -4) : viewName
    const slug = toKebabCase(base)
    const path = appName === 'home' && slug === 'home' ? '/' : `/${appName}/${slug}`

    let app = appMap.get(appName)
    if (!app) {
      app = { name: appName, title: humanize(appName), pages: [] }
      appMap.set(appName, app)
    }
    if (!app.pages.some(p => p.path === path)) {
      app.pages.push({ title: humanize(base), path })
    }
  }

  return Array.from(appMap.values()).sort((a, b) => a.title.localeCompare(b.title))
})

const pagesForSelectedApp = computed<Page[]>(() => {
  const app = apps.value.find(a => a.name === selectedApp.value)
  return app ? app.pages : []
})

const isPathInSelectedApp = computed(() =>
  pagesForSelectedApp.value.some(p => p.path === currentPath.value)
)

function appNameFromPath(path: string): string | null {
  if (path === '/' || path === '') return apps.value.some(a => a.name === 'home') ? 'home' : null
  const m = path.match(/^\/([^/]+)/)
  return m ? m[1]! : null
}

function normalizePath(input: string): string {
  const trimmed = (input || '').trim()
  if (!trimmed) return '/'
  if (/^https?:\/\//i.test(trimmed)) {
    try {
      const u = new URL(trimmed)
      return u.pathname + u.search + u.hash
    } catch {
      return '/'
    }
  }
  return trimmed.startsWith('/') ? trimmed : '/' + trimmed
}

function navigateTo(path: string) {
  const next = normalizePath(path)
  if (next === currentPath.value) {
    iframeKey.value++
  } else {
    currentPath.value = next
  }
  selectedPath.value = next
  const appFromPath = appNameFromPath(next)
  if (appFromPath && apps.value.some(a => a.name === appFromPath)) {
    selectedApp.value = appFromPath
  }
}

function onAppChange() {
  const app = apps.value.find(a => a.name === selectedApp.value)
  if (app && app.pages.length > 0) {
    navigateTo(app.pages[0]!.path)
  }
}

function onPageSelect() {
  navigateTo(selectedPath.value)
}

function goHome() {
  navigateTo('/')
}

function syncSelectionFromCurrent() {
  const appFromPath = appNameFromPath(currentPath.value)
  if (appFromPath && apps.value.some(a => a.name === appFromPath)) {
    selectedApp.value = appFromPath
  } else if (!selectedApp.value && apps.value.length > 0) {
    selectedApp.value = apps.value[0]!.name
  }
  if (isPathInSelectedApp.value || pagesForSelectedApp.value.length === 0) {
    selectedPath.value = currentPath.value
  } else {
    selectedPath.value = currentPath.value
  }
}

async function loadPreview() {
  if (!props.projectId) return
  isLoading.value = true
  error.value = null
  try {
    const response = await PreviewService.generatePreview(props.projectId)
    if (response && response.previewUrl) {
      previewUrl.value = response.previewUrl
      try {
        const u = new URL(response.previewUrl)
        const initial = (u.pathname || '/') + u.search + u.hash
        currentPath.value = initial
      } catch {
        currentPath.value = '/'
      }
      syncSelectionFromCurrent()
      iframeKey.value++
    } else {
      error.value = 'Preview server failed to start.'
    }
  } catch (e) {
    // Keep the failure local to this component — never call store.setError, or
    // the workspace-level error path can navigate the user back to /projects.
    error.value = e instanceof Error ? e.message : 'Preview server failed to start.'
  } finally {
    isLoading.value = false
  }
}

function reload() {
  if (previewUrl.value) {
    iframeKey.value++
  } else {
    loadPreview()
  }
}

onMounted(loadPreview)

watch(
  () => props.projectId,
  (next, prev) => {
    if (next && next !== prev) {
      previewUrl.value = null
      loadPreview()
    }
  }
)

watch(currentPath, () => {
  syncSelectionFromCurrent()
})

watch(apps, () => {
  if (!selectedApp.value && apps.value.length > 0) {
    syncSelectionFromCurrent()
  }
})

defineExpose({ reload, loadPreview, navigateTo })
</script>
