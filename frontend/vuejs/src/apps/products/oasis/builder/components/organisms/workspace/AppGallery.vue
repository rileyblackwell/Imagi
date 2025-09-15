<template>
  <div class="flex h-full w-full flex-col">
    <!-- Header: title, search, simple/clear language -->
    <div class="px-4 py-3 flex items-center gap-3 border-b border-dark-700/50 bg-dark-850/60 rounded-t-2xl">
      <div class="flex items-center gap-2">
        <span class="w-7 h-7 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
          <i class="fas fa-cubes"></i>
        </span>
        <div class="flex flex-col">
          <span class="text-sm font-semibold text-white">Your Apps</span>
          <span class="text-xxs text-gray-400">Apps are the building blocks of your web application. Search, create, or open an app.</span>
        </div>
      </div>
      <div class="ml-auto flex items-center gap-2">
        <!-- Search apps -->
        <div class="relative">
          <i class="fas fa-search text-gray-500 absolute left-2.5 top-2.5 text-xs"></i>
          <input
            v-model="query"
            type="text"
            placeholder="Search apps..."
            class="pl-7 pr-3 py-2 text-xs bg-dark-900/80 border border-dark-700/60 rounded-md text-white placeholder-gray-500 outline-none focus:ring-0 focus:border-primary-500/40"
          />
        </div>

        <!-- New App -->
        <GlassButton
          size="sm"
          class="transition-none hover:!bg-white/5 hover:!border-white/10 active:!bg-white/5 active:!border-white/10 focus:!ring-0 focus:!ring-transparent focus:!outline-none focus:!border-white/10 focus-visible:!ring-0 focus-visible:!border-white/10"
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
          class="transition-none hover:!bg-white/5 hover:!border-white/10 active:!bg-white/5 active:!border-white/10 focus:!ring-0 focus:!ring-transparent focus:!outline-none focus:!border-white/10 focus-visible:!ring-0 focus-visible:!border-white/10"
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

    <!-- Apps grid -->
    <div v-else class="flex-1 min-h-0">
      <div class="h-full p-4 overflow-auto">
        <div class="grid grid-cols-1 gap-3">
          <div
            v-for="app in filteredApps"
            :key="app.key"
            class="group relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/70 to-dark-800/60 backdrop-blur-sm transition shadow hover:shadow-xl hover:-translate-y-0.5 ring-0 hover:ring-1 hover:ring-primary-500/30 overflow-hidden"
          >
            <!-- Decorative top overlay -->
            <div class="absolute inset-x-0 top-0 h-14 bg-gradient-to-b from-white/5 to-transparent pointer-events-none"></div>
            <!-- Top-right Open icon button -->
            <GlassButton
              class="absolute top-2 right-2 px-2 py-1"
              size="sm"
              @click="openApp(app)"
              aria-label="Open app"
              :title="`Open ${app.displayName}`"
            >
              <i class="fas fa-folder-open text-xs"></i>
              <span class="text-[10px] font-medium">Open</span>
            </GlassButton>

            <div class="pl-3 pr-16 pt-4 pb-3 flex items-start gap-3">
              <div :class="['w-10 h-10 rounded-xl flex items-center justify-center border text-lg shadow-inner', app.color.bg, app.color.border, app.color.text]">
                <i :class="app.icon"></i>
              </div>
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                  <div class="text-sm font-semibold text-white tracking-tight truncate">{{ app.displayName }}</div>
                </div>
                <div class="text-xs text-gray-400/90 mt-1 whitespace-normal break-words">{{ app.hint }}</div>
              </div>
            </div>
            <!-- Footer actions removed; open action moved to top-right -->
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

const query = ref('')

// Version dropdown state
const isDropdownOpen = ref(false)
const versionDropdownRef = ref<HTMLElement | null>(null)
const dropdownPanelRef = ref<HTMLElement | null>(null)
const activeIndex = ref<number>(-1)
const currentVersion = computed(() => props.versionHistory.find(v => (v.hash || v.commit_hash) === props.selectedVersionHash))
const currentVersionLabel = computed(() => {
  // If nothing is selected, return empty so the UI falls back to the placeholder 'Version history'
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
onMounted(() => document.addEventListener('click', onDocumentClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocumentClick))

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
    // Initialize to current selected index or 0
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
    // Set active to current selection
    activeIndex.value = props.versionHistory.findIndex(v => (v.hash || v.commit_hash) === props.selectedVersionHash)
    await nextTick()
    dropdownPanelRef.value?.focus()
  } else {
    activeIndex.value = -1
  }
})

// Extract apps from files
const apps = computed(() => {
  const map: Record<string, { key: string; name: string; displayName: string; files: ProjectFile[]; icon: string; color: { bg: string; border: string; text: string }; hint: string }> = {}
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
    // Sanitize out the word 'spacex' from display names
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
      }
    }
    map[key].files.push(file)
  })

  const priority = ['home', 'auth', 'payments', 'payment']
  return Object.values(map).sort((a, b) => {
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
})

const filteredApps = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return apps.value
  return apps.value.filter((a) => {
    const name = (a.name || '').toLowerCase()
    // Normalize display name by stripping a trailing ' App'
    const display = (a.displayName || '').toLowerCase().replace(/\s+app$/, '')
    return name.startsWith(q) || display.startsWith(q)
  })
})

function openApp(app: { name: string; files: ProjectFile[] }) {
  // Prioritize a view file; else first file
  const view = app.files.find((f) => /\/views\//i.test(f.path))
  const target = view || app.files[0]
  if (target) {
    emit('selectFile', target)
  }
}

// Suppress any lingering focus styles by blurring the clicked button
function onCreateAppClick(ev: MouseEvent) {
  (ev.currentTarget as HTMLElement | null)?.blur()
  emit('createApp')
}

function onPreviewClick(ev: MouseEvent) {
  (ev.currentTarget as HTMLElement | null)?.blur()
  emit('preview')
}
</script>
