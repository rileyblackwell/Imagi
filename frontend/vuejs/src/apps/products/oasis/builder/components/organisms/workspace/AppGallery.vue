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
          <span class="text-xxs text-gray-400">Apps are groups of pages and components. Pick one to start.</span>
        </div>
      </div>
      <div class="ml-auto flex items-center gap-2">
        <div class="relative">
          <i class="fas fa-search text-gray-500 absolute left-2.5 top-2.5 text-xs"></i>
          <input
            v-model="query"
            type="text"
            placeholder="Search apps..."
            class="pl-7 pr-3 py-2 text-xs bg-dark-900/80 border border-dark-700/60 rounded-md text-white placeholder-gray-500 outline-none focus:ring-0 focus:border-primary-500/40"
          />
        </div>
        <button
          class="text-xs px-3 py-2 rounded-md border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-white/20 transition"
          @click="$emit('createApp')"
        >
          <i class="fas fa-plus mr-1"></i> New App
        </button>
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
        <button class="px-4 py-2 rounded-md bg-gradient-to-r from-indigo-500 to-violet-500 text-white text-xs" @click="$emit('createApp')">
          <i class="fas fa-plus mr-1"></i> Create App
        </button>
      </div>
    </div>

    <!-- Apps grid -->
    <div v-else class="p-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 overflow-auto">
      <div
        v-for="app in filteredApps"
        :key="app.key"
        class="group rounded-xl border border-dark-700/50 bg-dark-900/60 hover:bg-dark-800/60 transition shadow-sm overflow-hidden"
      >
        <div class="p-3 flex items-start gap-2">
          <div :class="['w-9 h-9 rounded-lg flex items-center justify-center border text-lg', app.color.bg, app.color.border, app.color.text]">
            <i :class="app.icon"></i>
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <div class="text-sm font-semibold text-white truncate">{{ app.displayName }}</div>
              <span class="text-[10px] px-1.5 py-0.5 rounded-full border bg-dark-800/60 border-dark-700/50 text-gray-300">{{ app.files.length }} files</span>
            </div>
            <div class="text-xxs text-gray-400 mt-0.5 truncate">{{ app.hint }}</div>
          </div>
        </div>
        <div class="px-3 pb-3">
          <div class="grid grid-cols-2 gap-1.5">
            <button
              class="text-xxs px-2 py-1.5 rounded-md border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-white/20 transition text-left"
              @click="openApp(app)"
            >
              <i class="fas fa-folder-open mr-1"></i> Open
            </button>
            <button
              class="text-xxs px-2 py-1.5 rounded-md border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-white/20 transition text-left"
              @click="$emit('addView', app.name)"
            >
              <i class="fas fa-file-alt mr-1"></i> Add Page
            </button>
            <button
              class="text-xxs px-2 py-1.5 rounded-md border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-white/20 transition text-left"
              @click="$emit('addComponent', app.name)"
            >
              <i class="fas fa-puzzle-piece mr-1"></i> Add Component
            </button>
            <button
              class="text-xxs px-2 py-1.5 rounded-md border border-white/10 bg-white/5 text-gray-300 hover:text-white hover:border-white/20 transition text-left"
              @click="$emit('preview')"
            >
              <i class="fas fa-play mr-1"></i> Preview
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ProjectFile } from '../../../types/components'

const props = defineProps<{
  files: ProjectFile[]
}>()

const emit = defineEmits<{
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createApp'): void
  (e: 'addView', appName: string): void
  (e: 'addComponent', appName: string): void
  (e: 'preview'): void
}>()

const query = ref('')

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
    if (n.includes('home')) return 'Homepage and marketing pages'
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
    const displayName = rawName.charAt(0).toUpperCase() + rawName.slice(1)
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

  return Object.values(map).sort((a, b) => a.displayName.localeCompare(b.displayName))
})

const filteredApps = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return apps.value
  return apps.value.filter((a) => a.displayName.toLowerCase().includes(q) || a.name.toLowerCase().includes(q))
})

function openApp(app: { name: string; files: ProjectFile[] }) {
  // Prioritize a view file; else first file
  const view = app.files.find((f) => /\/views\//i.test(f.path))
  const target = view || app.files[0]
  if (target) {
    emit('selectFile', target)
  }
}
</script>
