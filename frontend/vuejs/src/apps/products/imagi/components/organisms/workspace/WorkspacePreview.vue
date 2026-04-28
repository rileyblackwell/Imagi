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

          <!-- Combined App / Page selector -->
          <div class="relative flex-1 min-w-[12rem]" ref="menuRoot">
            <button
              type="button"
              @click="menuOpen = !menuOpen"
              :disabled="apps.length === 0"
              class="w-full flex items-center gap-2 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] focus:border-gray-400 dark:focus:border-white/20 outline-none py-2 pl-3 pr-9 text-sm font-medium text-gray-900 dark:text-white/90 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i class="fas fa-cube text-xs text-gray-500 dark:text-white/50 shrink-0"></i>
              <span class="truncate flex-1 text-left">{{ triggerLabel }}</span>
              <i class="fas fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 dark:text-white/40 pointer-events-none"></i>
            </button>

            <div
              v-if="menuOpen && apps.length > 0"
              class="absolute z-20 mt-1 left-0 min-w-[14rem] rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-lg py-1"
            >
              <div
                v-for="app in apps"
                :key="app.name"
                class="relative"
                @mouseenter="onAppEnter(app.name)"
                @mouseleave="onAppLeave(app.name)"
              >
                <button
                  type="button"
                  @click="hoveredApp = hoveredApp === app.name ? '' : app.name"
                  class="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm text-gray-900 dark:text-white/90 hover:bg-gray-50 dark:hover:bg-white/[0.05]"
                >
                  <span class="flex items-center gap-2 truncate">
                    <i class="fas fa-cube text-xs text-gray-500 dark:text-white/50"></i>
                    {{ app.title }}
                  </span>
                  <i class="fas fa-chevron-right text-[10px] text-gray-400 dark:text-white/40"></i>
                </button>

                <div
                  v-if="hoveredApp === app.name && app.pages.length"
                  class="absolute top-0 left-full ml-1 min-w-[14rem] rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-lg py-1"
                  @mouseenter="onAppEnter(app.name)"
                  @mouseleave="onAppLeave(app.name)"
                >
                  <button
                    v-for="page in app.pages"
                    :key="page.path"
                    type="button"
                    @click="onSelectPage(page.path)"
                    :class="['w-full flex items-center gap-2 px-3 py-2 text-sm text-left',
                             page.path === currentPath
                               ? 'bg-gray-100 dark:bg-white/[0.08] text-gray-900 dark:text-white'
                               : 'text-gray-700 dark:text-white/80 hover:bg-gray-50 dark:hover:bg-white/[0.05]']"
                  >
                    <i class="fas fa-file-alt text-xs text-gray-500 dark:text-white/50"></i>
                    <span class="truncate">{{ page.title }}</span>
                  </button>
                </div>
              </div>
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
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
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
const menuOpen = ref(false)
const hoveredApp = ref('')
const menuRoot = ref<HTMLElement | null>(null)
let leaveTimer: number | null = null

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

    if (path === '/payments/payments') continue

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

function onSelectPage(path: string) {
  navigateTo(path)
  menuOpen.value = false
  hoveredApp.value = ''
}

function onAppEnter(name: string) {
  if (leaveTimer) {
    window.clearTimeout(leaveTimer)
    leaveTimer = null
  }
  hoveredApp.value = name
}

function onAppLeave(name: string) {
  if (leaveTimer) window.clearTimeout(leaveTimer)
  leaveTimer = window.setTimeout(() => {
    if (hoveredApp.value === name) hoveredApp.value = ''
    leaveTimer = null
  }, 120)
}

function onDocClick(e: MouseEvent) {
  if (!menuOpen.value) return
  if (menuRoot.value && !menuRoot.value.contains(e.target as Node)) {
    menuOpen.value = false
    hoveredApp.value = ''
  }
}

const triggerLabel = computed(() => {
  const app = apps.value.find(a => a.name === selectedApp.value)
  const page = pagesForSelectedApp.value.find(p => p.path === currentPath.value)
  if (app && page) return `${app.title} / ${page.title}`
  if (app) return app.title
  if (apps.value.length === 0) return 'No apps yet'
  return 'Select page'
})

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

onMounted(() => {
  loadPreview()
  document.addEventListener('mousedown', onDocClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocClick)
  if (leaveTimer) window.clearTimeout(leaveTimer)
})

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
