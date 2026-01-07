<template>
  <div class="flex h-full w-full flex-col overflow-hidden">
    <!-- Header: title and controls -->
    <div class="px-4 py-3 flex flex-wrap gap-3 items-center border-b border-dark-700/50 bg-dark-850/60 rounded-t-2xl">
      <div class="flex items-center gap-2 min-w-[16rem]">
        <span class="w-9 h-9 rounded-xl flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-200 shadow-inner">
          <i class="fas fa-diagram-project text-sm"></i>
        </span>
        <div class="flex flex-col">
          <span class="text-base font-semibold text-white tracking-tight">System Overview</span>
          <span class="text-[11px] text-gray-400 leading-snug">Drag apps to design your layout. Click to open.</span>
        </div>
      </div>
      <div class="ml-auto flex items-center gap-2 flex-1 justify-end min-w-[14rem]">
        <!-- Connection Mode Toggle -->
        <GlassButton
          size="sm"
          :class="[
            'transition-none',
            connectionMode 
              ? 'bg-primary-500/20 border-primary-500/40 hover:!bg-primary-500/25' 
              : 'hover:!bg-white/5 hover:!border-white/10'
          ]"
          @click="toggleConnectionMode"
        >
          <i class="fas fa-arrow-right-arrow-left text-xs mr-1.5"></i>
          <span class="text-xs">{{ connectionMode ? 'Cancel Connect' : 'Connect Apps' }}</span>
        </GlassButton>

        <!-- Reset Layout -->
        <GlassButton
          size="sm"
          class="transition-none hover:!bg-white/5 hover:!border-white/10"
          @click="resetLayout"
        >
          <i class="fas fa-arrows-rotate text-xs mr-1.5"></i>
          <span class="text-xs">Reset Layout</span>
        </GlassButton>

        <!-- New App -->
        <GlassButton
          size="sm"
          class="transition-none hover:!bg-white/5 hover:!border-white/10"
          @click="onCreateAppClick"
        >
          <span class="mr-2 w-6 h-6 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
            <i class="fas fa-plus"></i>
          </span>
          <span class="bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">New App</span>
        </GlassButton>

        <!-- Preview App -->
        <GlassButton
          size="sm"
          type="button"
          class="transition-none hover:!bg-white/5 hover:!border-white/10"
          @click="onPreviewClick"
        >
          <span class="mr-2 w-6 h-6 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
            <i class="fas fa-eye"></i>
          </span>
          <span class="bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">Preview App</span>
        </GlassButton>

        <!-- Version history dropdown -->
        <div
          class="relative inline-flex items-center text-xs px-3 pr-9 py-2 rounded-md border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-white/20 transition min-w-[16rem]"
          :class="{ 'opacity-60 cursor-not-allowed': isLoadingVersions || !versionHistory.length }"
          ref="versionDropdownRef"
        >
          <span class="mr-2 w-6 h-6 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
            <i class="fas fa-history"></i>
          </span>
          <button
            type="button"
            class="w-full text-left bg-transparent border-0 focus:outline-none text-xs text-current pr-2 pl-1 truncate"
            :disabled="isLoadingVersions || !versionHistory.length"
            :title="currentVersionLabel || (isLoadingVersions ? 'Loading versions…' : (!versionHistory.length ? 'No versions' : 'Version history'))"
            @click="toggleDropdown"
            @keydown.escape.stop.prevent="closeDropdown"
            aria-haspopup="listbox"
            aria-label="Version history"
            :aria-expanded="isDropdownOpen ? 'true' : 'false'"
          >
            <span v-if="isLoadingVersions">Loading versions…</span>
            <span v-else-if="!versionHistory.length">No versions</span>
            <span v-else>{{ currentVersionLabel || 'Version history' }}</span>
          </button>
          <i class="fas fa-chevron-down pointer-events-none absolute right-2 text-gray-400"></i>

          <!-- Dropdown panel -->
          <div
            v-if="isDropdownOpen"
            class="absolute right-0 top-full mt-2 w-[30rem] max-w-[calc(100vw-2rem)] z-20 rounded-xl border border-dark-700/60 bg-dark-900/95 shadow-2xl backdrop-blur-md overflow-hidden"
            role="listbox"
            tabindex="-1"
            @keydown.down.prevent="moveActive(1)"
            @keydown.up.prevent="moveActive(-1)"
            @keydown.enter.prevent="activateActive()"
            ref="dropdownPanelRef"
          >
            <div class="px-3 py-2 border-b border-dark-700/60 bg-dark-900/70 text-[11px] tracking-wide uppercase text-gray-400">Version history</div>

            <!-- Loading state -->
            <div v-if="isLoadingVersions" class="p-3 text-xs text-gray-400">Loading versions…</div>

            <!-- Empty state -->
            <div v-else-if="!versionHistory.length" class="p-3 text-xs text-gray-400">No versions available</div>

            <!-- Versions list -->
            <ul v-else class="max-h-80 overflow-auto py-1">
              <li
                v-for="(v, idx) in versionHistory"
                :key="v.hash || v.commit_hash"
                class="group"
              >
                <button
                  type="button"
                  class="w-full px-3 py-2 text-left flex items-start gap-3 transition"
                  :class="[
                    (v.hash || v.commit_hash) === selectedVersionHash ? 'bg-primary-500/10 ring-1 ring-primary-500/30' : 'hover:bg-white/5 focus:bg-white/5',
                    activeIndex === idx && (v.hash || v.commit_hash) !== selectedVersionHash ? 'bg-white/5' : ''
                  ]"
                  @click="selectVersion(v)"
                  role="option"
                  :aria-selected="(v.hash || v.commit_hash) === selectedVersionHash ? 'true' : 'false'"
                >
                  <span class="mt-0.5 w-7 h-7 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/10 to-violet-500/10 border-primary-500/20 text-primary-300">
                    <i class="fas fa-code-branch"></i>
                  </span>
                  <span class="min-w-0 flex-1">
                    <span class="block text-[13px] leading-5 text-white truncate" :title="v.message || v.description || 'Update'">{{ v.message || v.description || 'Update' }}</span>
                    <span class="mt-0.5 flex items-center gap-2 text-xxs text-gray-400">
                      <span>{{ v.relative_date || v.date || '' }}</span>
                      <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded border border-white/10 bg-white/5 text-[10px] font-mono text-gray-300" :title="v.hash || v.commit_hash || ''">
                        <i class="fas fa-hashtag text-[9px] opacity-70"></i>
                        <span class="truncate max-w-[8rem]">{{ (v.hash || v.commit_hash || '').slice(0, 10) }}</span>
                      </span>
                    </span>
                  </span>
                  <i
                    v-if="(v.hash || v.commit_hash) === selectedVersionHash"
                    class="fas fa-check text-primary-300 ml-2 opacity-90"
                    aria-hidden="true"
                  ></i>
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="apps.length === 0" class="flex-1 flex items-center justify-center p-8">
      <div class="text-center max-w-sm">
        <div class="w-14 h-14 mx-auto mb-3 rounded-xl border border-dashed border-white/15 flex items-center justify-center text-primary-300">
          <i class="fas fa-cubes text-xl"></i>
        </div>
        <div class="text-white font-medium mb-1">No apps yet</div>
        <div class="text-xs text-gray-400 mb-4">Create your first app to start adding pages and components.</div>
        <GradientButton size="sm" @click="$emit('createApp')">
          <i class="fas fa-plus mr-1"></i> Create App
        </GradientButton>
      </div>
    </div>

    <!-- Canvas Container -->
    <div v-else class="flex-1 min-h-0 relative overflow-auto" ref="canvasContainerRef">
      <!-- Loading Overlay -->
      <div
        v-if="isLoadingLayout"
        class="absolute inset-0 z-50 flex items-center justify-center bg-dark-900/80 backdrop-blur-sm"
      >
        <div class="flex flex-col items-center gap-3">
          <div class="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin"></div>
          <span class="text-sm text-gray-400">Loading layout...</span>
        </div>
      </div>

      <!-- Connection Mode Banner -->
      <div
        v-if="connectionMode"
        class="absolute top-4 left-1/2 -translate-x-1/2 z-40 px-4 py-2 rounded-lg bg-primary-500/20 border border-primary-500/40 backdrop-blur-sm"
      >
        <div class="flex items-center gap-2 text-sm text-white">
          <i class="fas fa-arrow-right-arrow-left text-primary-300"></i>
          <span>{{ connectionFromApp ? 'Click another app to connect' : 'Click an app to start connection' }}</span>
          <button
            @click="toggleConnectionMode"
            class="ml-2 px-2 py-1 text-xs rounded bg-white/10 hover:bg-white/20 transition"
          >
            Cancel
          </button>
        </div>
      </div>

      <!-- Grid Background -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="w-full h-full bg-[radial-gradient(circle,_rgba(255,255,255,0.03)_1px,_transparent_1px)] bg-[size:20px_20px]"></div>
      </div>

      <!-- Canvas Content -->
      <div class="relative min-w-[2000px] min-h-[2000px] p-12">
        <!-- SVG Connections Layer -->
        <svg
          class="absolute top-0 left-0 w-full h-full pointer-events-none"
          style="z-index: 1;"
        >
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3, 0 6"
                fill="rgba(139, 92, 246, 0.4)"
              />
            </marker>
          </defs>
          <path
            v-for="connection in connections"
            :key="`${connection.from}-${connection.to}`"
            :d="getConnectionPath(connection)"
            stroke="rgba(139, 92, 246, 0.4)"
            stroke-width="2"
            fill="none"
            marker-end="url(#arrowhead)"
          />
        </svg>

        <!-- Draggable App Nodes -->
        <div
          v-for="app in apps"
          :key="app.key"
          :data-app-key="app.key"
          class="absolute transition-all duration-200"
          :class="{
            'cursor-move': !connectionMode,
            'cursor-pointer': connectionMode,
            'shadow-2xl shadow-primary-500/30 scale-105': draggingApp === app.key,
            'hover:shadow-lg hover:shadow-primary-500/20 hover:scale-[1.02]': draggingApp !== app.key && !connectionMode,
            'ring-2 ring-primary-500/60 animate-pulse': connectionMode && connectionFromApp === app.key
          }"
          :style="{
            left: `${appPositions[app.key]?.x || 0}px`,
            top: `${appPositions[app.key]?.y || 0}px`,
            zIndex: draggingApp === app.key ? 1000 : 2,
            transition: draggingApp === app.key ? 'none' : 'all 0.2s ease-out'
          }"
          @mousedown="!connectionMode && startDrag($event, app)"
        >
          <div
            class="w-[280px] rounded-2xl border bg-dark-950/90 backdrop-blur px-4 py-4 shadow-xl transition"
            :class="[
              connectionMode 
                ? 'border-primary-500/40 hover:border-primary-500/60 hover:bg-dark-900/90' 
                : 'border-white/10 hover:border-primary-500/40'
            ]"
            @click.stop="handleAppClick(app)"
          >
            <div class="flex items-start gap-3">
              <div
                :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center border text-lg shadow-inner shrink-0',
                  app.color.bg,
                  app.color.border,
                  app.color.text
                ]"
              >
                <i :class="app.icon"></i>
                  </div>
              <div class="min-w-0 flex-1">
                <div class="text-sm font-semibold text-white truncate">
                  {{ app.displayName }}
                </div>
                <p class="mt-1 text-[11px] text-gray-400 leading-snug line-clamp-2">
                  {{ app.hint }}
                </p>
                    </div>
                  </div>

            <div class="mt-3 flex items-center justify-between">
              <div class="flex items-center gap-2 text-[10px] text-gray-500">
                <span><i class="fas fa-window text-[9px]"></i> {{ app.stats.screens }}</span>
                <span><i class="fas fa-cube text-[9px]"></i> {{ app.stats.components }}</span>
              </div>
              <div class="text-[11px] text-primary-300">
                      <i class="fas fa-arrow-right text-[10px]"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import type { ProjectFile } from '../../../types/components'
import { GradientButton, GlassButton } from '@/shared/components/atoms'
import { LayoutService } from '../../../services/layoutService'
import { useNotification } from '@/shared/composables/useNotification'

const props = defineProps<{
  files: ProjectFile[]
  projectId?: string
  versionHistory: Array<Record<string, any>>
  isLoadingVersions: boolean
  selectedVersionHash: string
}>()

const emit = defineEmits<{
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createApp'): void
  (e: 'preview'): void
  (e: 'version-reset', version: any): void
  (e: 'update:selectedVersionHash', value: string): void
  (e: 'version-select'): void
}>()

const { showNotification } = useNotification()

// Canvas and dragging state
const canvasContainerRef = ref<HTMLElement | null>(null)
const draggingApp = ref<string | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

// App positions - will be loaded from backend and saved
const appPositions = ref<Record<string, { x: number; y: number }>>({})

// Connections between apps
const connections = ref<Array<{ from: string; to: string }>>([])

// Connection creation mode
const connectionMode = ref(false)
const connectionFromApp = ref<string | null>(null)

// Loading state
const isLoadingLayout = ref(false)

// Auto-grid layout configuration
const GRID_COLUMNS = 4
const HORIZONTAL_SPACING = 320
const VERTICAL_SPACING = 200
const GRID_START_X = 100
const GRID_START_Y = 100

// Debounce timer for auto-save
let saveTimer: NodeJS.Timeout | null = null

// Version dropdown state
const isDropdownOpen = ref(false)
const versionDropdownRef = ref<HTMLElement | null>(null)
const dropdownPanelRef = ref<HTMLElement | null>(null)
const activeIndex = ref<number>(-1)
const currentVersion = computed(() => props.versionHistory.find(v => (v.hash || v.commit_hash) === props.selectedVersionHash))
const currentVersionLabel = computed(() => {
  if (!props.selectedVersionHash) return ''
  const v: any = currentVersion.value
  if (!v) return ''
  const msg = v.message || v.description || 'Update'
  const when = v.relative_date || v.date || ''
  return msg && when ? `${msg} · ${when}` : msg || when || ''
})

function toggleDropdown() {
  if (props.isLoadingVersions || !props.versionHistory.length) return
  isDropdownOpen.value = !isDropdownOpen.value
}
function closeDropdown() { isDropdownOpen.value = false }
function onDocumentClick(e: MouseEvent) {
  const el = versionDropdownRef.value
  if (!el) return
  const target = e.target as Node
  if (!el.contains(target)) {
    isDropdownOpen.value = false
  }
}

function selectVersion(v: any) {
  const val = v.hash || v.commit_hash || ''
  emit('update:selectedVersionHash', val)
  emit('version-select')
  isDropdownOpen.value = false
}

function moveActive(delta: number) {
  const total = props.versionHistory.length
  if (!total) return
  if (activeIndex.value === -1) {
    const idx = props.versionHistory.findIndex(v => (v.hash || v.commit_hash) === props.selectedVersionHash)
    activeIndex.value = idx >= 0 ? idx : 0
  } else {
    activeIndex.value = (activeIndex.value + delta + total) % total
  }
}

function activateActive() {
  const idx = activeIndex.value
  if (idx < 0 || idx >= props.versionHistory.length) return
  const v = props.versionHistory[idx]
  selectVersion(v)
}

watch(isDropdownOpen, async (open) => {
  if (open) {
    activeIndex.value = props.versionHistory.findIndex(v => (v.hash || v.commit_hash) === props.selectedVersionHash)
    await nextTick()
    dropdownPanelRef.value?.focus()
  } else {
    activeIndex.value = -1
  }
})

// Extract apps from files
type GalleryApp = {
  key: string
  name: string
  displayName: string
  files: ProjectFile[]
  icon: string
  color: { bg: string; border: string; text: string }
  hint: string
  stats: {
    screens: number
    components: number
    files: number
  }
}

const apps = computed(() => {
  const map: Record<string, GalleryApp> = {}
  const colorMap = [
    { bg: 'bg-indigo-600/15', border: 'border-indigo-400/30', text: 'text-indigo-300' },
    { bg: 'bg-violet-600/15', border: 'border-violet-400/30', text: 'text-violet-300' },
    { bg: 'bg-emerald-600/15', border: 'border-emerald-400/30', text: 'text-emerald-300' },
    { bg: 'bg-rose-600/15', border: 'border-rose-400/30', text: 'text-rose-300' },
    { bg: 'bg-cyan-600/15', border: 'border-cyan-400/30', text: 'text-cyan-300' },
    { bg: 'bg-amber-600/15', border: 'border-amber-400/30', text: 'text-amber-300' },
  ]

  const guessIcon = (name: string) => {
    const n = name.toLowerCase()
    if (n.includes('auth')) return 'fas fa-lock'
    if (n.includes('home')) return 'fas fa-home'
    if (n.includes('product')) return 'fas fa-box'
    if (n.includes('payment')) return 'fas fa-credit-card'
    if (n.includes('docs')) return 'fas fa-book'
    return 'fas fa-cube'
  }

  const hintFor = (name: string) => {
    const n = name.toLowerCase()
    if (n.includes('auth')) return 'Sign in, sign up, and profile pages'
    if (n.includes('home')) return 'App entry: landing, layout, navigation'
    if (n.includes('product')) return 'Product listings and details'
    if (n.includes('payment')) return 'Checkout, plans, and billing UI'
    if (n.includes('docs')) return 'Documentation pages and guides'
    return 'Pages and components for this part of your app'
  }

  let colorIdx = 0
  props.files.forEach((file) => {
    const normalized = (file.path || '').toLowerCase().replace(/\\/g, '/')
    const match = normalized.match(/\/src\/apps\/([^\/]+)\//)
    if (!match) return
    const rawName = match[1]
    const displayBase = rawName.charAt(0).toUpperCase() + rawName.slice(1)
    const sanitized = displayBase.replace(/spacex/ig, '').trim()
    const displayName = sanitized || 'Main'
    const key = rawName

    if (!map[key]) {
      const color = colorMap[colorIdx % colorMap.length]
      colorIdx += 1
      map[key] = {
        key,
        name: rawName,
        displayName: `${displayName} App`,
        files: [],
        icon: guessIcon(rawName),
        color,
        hint: hintFor(rawName),
        stats: {
          screens: 0,
          components: 0,
          files: 0,
        },
      }
    }
    map[key].files.push(file)
    map[key].stats.files += 1
    if (/\/views\//i.test(normalized)) {
      map[key].stats.screens += 1
    } else if (/\/components\//i.test(normalized)) {
      map[key].stats.components += 1
    }
  })

  const priority = ['home', 'auth', 'payments', 'payment']
  const sortedApps = Object.values(map).sort((a, b) => {
    const an = (a.name || '').toLowerCase()
    const bn = (b.name || '').toLowerCase()
    const ai = priority.indexOf(an)
    const bi = priority.indexOf(bn)
    if (ai !== -1 || bi !== -1) {
      if (ai === -1) return 1
      if (bi === -1) return -1
      return ai - bi
    }
    return a.displayName.localeCompare(b.displayName)
  })
  
  // Debug logging
  console.log('[AppGallery] Detected apps:', sortedApps.map(a => a.name).join(', '))
  console.log('[AppGallery] Total files:', props.files.length)
  
  return sortedApps
})

// Auto-grid layout calculation
function calculateAutoGridPositions() {
  const positions: Record<string, { x: number; y: number }> = {}
  apps.value.forEach((app, index) => {
    const col = index % GRID_COLUMNS
    const row = Math.floor(index / GRID_COLUMNS)
    positions[app.key] = {
      x: GRID_START_X + col * HORIZONTAL_SPACING,
      y: GRID_START_Y + row * VERTICAL_SPACING
    }
  })
  return positions
}

// Initialize positions when apps change
watch(() => apps.value, async (newApps) => {
  if (newApps.length > 0) {
    // Check if we need to load layout from backend
    const needsLoad = newApps.some(app => !appPositions.value[app.key])
    if (needsLoad && !isLoadingLayout.value) {
      await loadLayoutFromBackend()
    }
  }
}, { immediate: true })

// Dragging functions
function startDrag(event: MouseEvent, app: GalleryApp) {
  // Prevent drag if clicking on the card itself to open it
  const target = event.target as HTMLElement
  if (target.closest('[data-app-key]') !== event.currentTarget) {
    return
  }
  
  event.preventDefault()
  draggingApp.value = app.key
  
  const currentPos = appPositions.value[app.key] || { x: 0, y: 0 }
  dragOffset.value = {
    x: event.clientX - currentPos.x,
    y: event.clientY - currentPos.y
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event: MouseEvent) {
  if (!draggingApp.value) return
  
  const container = canvasContainerRef.value
  if (!container) return
  
  // Calculate new position relative to the canvas container
  const containerRect = container.getBoundingClientRect()
  const scrollLeft = container.scrollLeft
  const scrollTop = container.scrollTop
  
  const newX = event.clientX - containerRect.left + scrollLeft - dragOffset.value.x
  const newY = event.clientY - containerRect.top + scrollTop - dragOffset.value.y
  
  // Apply boundary constraints
  const constrainedX = Math.max(0, Math.min(newX, 1700))
  const constrainedY = Math.max(0, Math.min(newY, 1700))
  
  appPositions.value[draggingApp.value] = {
    x: constrainedX,
    y: constrainedY
  }
}

function stopDrag() {
  if (draggingApp.value) {
    // Save positions to backend (will be implemented later)
    savePositionsToBackend()
  }
  draggingApp.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// Reset layout to auto-grid
async function resetLayout() {
  if (!props.projectId) return
  
  try {
    // Delete saved layout from backend
    const response = await LayoutService.resetLayout(props.projectId)
    
    if (response.success) {
      // Reset to auto-grid locally
      appPositions.value = calculateAutoGridPositions()
      connections.value = []
      
      showNotification({
        type: 'success',
        message: 'Layout reset to default.',
        duration: 2000
      })
    } else {
      console.error('Failed to reset layout:', response.error)
      showNotification({
        type: 'error',
        message: 'Failed to reset layout.',
        duration: 3000
      })
    }
  } catch (error) {
    console.error('Error resetting layout:', error)
    showNotification({
      type: 'error',
      message: 'Error resetting layout.',
      duration: 3000
    })
  }
}

// Connection path calculation for SVG lines
function getConnectionPath(connection: { from: string; to: string }): string {
  const fromPos = appPositions.value[connection.from]
  const toPos = appPositions.value[connection.to]
  
  if (!fromPos || !toPos) return ''
  
  // Calculate center points of app nodes (280px width, ~80px height)
  const fromX = fromPos.x + 140
  const fromY = fromPos.y + 40
  const toX = toPos.x + 140
  const toY = toPos.y + 40
  
  // Create a curved path using cubic bezier
  const controlPointOffset = Math.abs(toX - fromX) * 0.5
  return `M ${fromX} ${fromY} C ${fromX + controlPointOffset} ${fromY}, ${toX - controlPointOffset} ${toY}, ${toX} ${toY}`
}

// Backend integration functions
async function loadLayoutFromBackend() {
  // When no project is persisted yet, fall back to the auto-grid immediately
  if (!props.projectId) {
    appPositions.value = calculateAutoGridPositions()
    connections.value = []
    return
  }
  
  try {
    isLoadingLayout.value = true
    const response = await LayoutService.loadLayout(props.projectId)
    
    if (response.success && response.layout_data) {
      const { positions, connections: savedConnections } = response.layout_data
      
      // Only load positions for apps that actually exist
      const validPositions: Record<string, { x: number; y: number }> = {}
      apps.value.forEach(app => {
        if (positions[app.key]) {
          validPositions[app.key] = positions[app.key]
        }
      })
      
      // If we have saved positions, use them; otherwise use auto-grid
      if (Object.keys(validPositions).length > 0) {
        appPositions.value = validPositions
        connections.value = savedConnections || []
        return
      }
    }

    // No saved layout or no matches for current apps - use auto-grid
    appPositions.value = calculateAutoGridPositions()
    connections.value = []
  } catch (error) {
    console.error('Error loading layout:', error)
    // Fall back to auto-grid on error
    appPositions.value = calculateAutoGridPositions()
    connections.value = []
    showNotification({
      type: 'error',
      message: 'Failed to load saved layout. Using default layout.',
      duration: 3000
    })
  } finally {
    isLoadingLayout.value = false
  }
}

function savePositionsToBackend() {
  if (!props.projectId) return
  
  // Clear any existing timer
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
  
  // Debounce the save operation (wait 1 second after last change)
  saveTimer = setTimeout(async () => {
    try {
      const layoutData = {
        positions: appPositions.value,
        connections: connections.value
      }
      
      const response = await LayoutService.saveLayout(props.projectId!, layoutData)
      
      if (!response.success) {
        console.error('Failed to save layout:', response.error)
        showNotification({
          type: 'error',
          message: 'Failed to save layout changes.',
          duration: 3000
        })
      }
    } catch (error) {
      console.error('Error saving layout:', error)
      showNotification({
        type: 'error',
        message: 'Error saving layout changes.',
        duration: 3000
      })
    }
  }, 1000)
}

function handleAppClick(app: GalleryApp) {
  if (connectionMode.value) {
    handleConnectionClick(app)
  } else {
    openApp(app)
  }
}

function openApp(app: GalleryApp) {
  // Prioritize a view file; else first file
  const view = app.files.find((f) => /\/views\//i.test(f.path))
  const target = view || app.files[0]
  if (target) {
    emit('selectFile', target)
  }
}

// Connection mode functions
function toggleConnectionMode() {
  connectionMode.value = !connectionMode.value
  if (!connectionMode.value) {
    // Reset connection state when exiting mode
    connectionFromApp.value = null
  }
}

function handleConnectionClick(app: GalleryApp) {
  if (!connectionFromApp.value) {
    // First click - select source app
    connectionFromApp.value = app.key
  } else if (connectionFromApp.value === app.key) {
    // Clicked same app - deselect
    connectionFromApp.value = null
  } else {
    // Second click - create connection
    const newConnection = {
      from: connectionFromApp.value,
      to: app.key
    }
    // Check if connection already exists
    const exists = connections.value.some(
      c => c.from === newConnection.from && c.to === newConnection.to
    )
    if (!exists) {
      connections.value.push(newConnection)
      savePositionsToBackend()
    }
    // Reset for next connection
    connectionFromApp.value = null
  }
}

function onCreateAppClick(ev: MouseEvent) {
  (ev.currentTarget as HTMLElement | null)?.blur()
  emit('createApp')
}

function onPreviewClick(ev: MouseEvent) {
  (ev.currentTarget as HTMLElement | null)?.blur()
  emit('preview')
}

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  
  // Clear save timer if it exists
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
})
</script>
