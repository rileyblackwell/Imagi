<template>
  <div class="h-full flex flex-col bg-transparent overflow-hidden transition-colors duration-300">
    <!-- Header -->
    <div class="px-6 py-5 border-b border-gray-200 dark:border-white/[0.08] transition-colors duration-300">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white/90 transition-colors duration-300">Your Apps</h2>
          <p class="text-sm text-gray-600 dark:text-white/60 mt-1 transition-colors duration-300">Each app is a section of your website (Home, Checkout, Profile...)</p>
        </div>
        <button
          @click="$emit('create-app')"
          class="group relative cursor-pointer"
        >
          <!-- Card content -->
          <div class="relative px-6 py-3 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05]">
              <i class="fas fa-plus text-xs text-gray-700 dark:text-white/70"></i>
            </div>
            <span class="text-sm font-semibold text-gray-900 dark:text-white/90">New App</span>
          </div>
        </button>
      </div>
    </div>

    <!-- Apps List -->
    <div class="flex-1 overflow-y-auto px-6 py-6">
      <!-- Empty State -->
      <div v-if="apps.length === 0" class="flex flex-col items-center justify-center py-20">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 dark:bg-white/[0.05] border border-gray-200 dark:border-white/[0.08] mb-4 transition-colors duration-300">
          <i class="fas fa-cubes text-gray-700 dark:text-white/70 text-2xl"></i>
        </div>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white/90 mb-2 transition-colors duration-300">No apps yet</h3>
        <p class="text-gray-600 dark:text-white/60 text-center max-w-md mb-6 transition-colors duration-300">Add your first app to start building your website</p>
        <button
          @click="$emit('create-app')"
          class="group relative cursor-pointer"
        >
          <!-- Card content -->
          <div class="relative px-8 py-4 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05]">
              <i class="fas fa-plus text-sm text-gray-700 dark:text-white/70"></i>
            </div>
            <span class="text-base font-semibold text-gray-900 dark:text-white/90">New App</span>
          </div>
        </button>
      </div>

      <!-- Apps List (Vertical) -->
      <div v-else class="space-y-3">
        <div
          v-for="app in apps"
          :key="app.key"
          @click="$emit('select-app', app)"
          class="group relative cursor-pointer"
        >
          <!-- Card content -->
          <div class="relative p-4 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300">
            <!-- Icon and name -->
            <div class="flex items-center gap-4">
              <div
                :class="[
                  'w-12 h-12 rounded-xl flex items-center justify-center border shadow-sm flex-shrink-0',
                  app.color.bg,
                  app.color.border,
                  app.color.text
                ]"
              >
                <i :class="app.icon" class="text-lg"></i>
              </div>
              <div class="min-w-0 flex-1">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white/90 mb-1 truncate transition-colors duration-300">{{ app.displayName }}</h3>
                <p class="text-xs text-gray-600 dark:text-white/60 truncate transition-colors duration-300">{{ app.hint }}</p>
              </div>
              <!-- Arrow indicator -->
              <div class="w-8 h-8 rounded-full bg-gray-100 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] flex items-center justify-center text-gray-600 dark:text-white/60 group-hover:text-gray-900 dark:group-hover:text-white transition-all duration-300 flex-shrink-0">
                <i class="fas fa-arrow-right text-xs"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ProjectFile } from '../../../types/components'

const props = defineProps<{
  files: ProjectFile[]
}>()

const emit = defineEmits<{
  (e: 'select-app', app: any): void
  (e: 'create-app'): void
}>()

type GalleryApp = {
  key: string
  name: string
  displayName: string
  files: ProjectFile[]
  icon: string
  color: { bg: string; border: string; text: string }
  hint: string
  pagesCount: number
  blocksCount: number
  dataCount: number
}

const apps = computed(() => {
  const map: Record<string, GalleryApp> = {}
  // Use consistent grayscale colors for all app icons - matching homepage design
  const colorMap = [
    { bg: 'bg-gray-100 dark:bg-white/[0.05]', border: 'border-gray-200 dark:border-white/[0.08]', text: 'text-gray-700 dark:text-white/70' },
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

  // Helper to check if file is a barrel/index file (we exclude these from counts)
  const isBarrelFile = (path: string): boolean => {
    const filename = path.split('/').pop()?.toLowerCase() || ''
    return filename === 'index.ts' || filename === 'index.js' || filename === 'index.vue'
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
        displayName: `${displayName}`,
        files: [],
        icon: guessIcon(rawName),
        color,
        hint: hintFor(rawName),
        pagesCount: 0,
        blocksCount: 0,
        dataCount: 0,
      }
    }
    map[key].files.push(file)
  })

  // Compute counts for each app
  Object.values(map).forEach((app) => {
    app.pagesCount = app.files.filter(f => 
      /\/views\//i.test(f.path) && !isBarrelFile(f.path)
    ).length
    app.blocksCount = app.files.filter(f => 
      /\/components\//i.test(f.path) && !isBarrelFile(f.path)
    ).length
    app.dataCount = app.files.filter(f => 
      (/\/stores\//i.test(f.path) || /store\.(ts|js)$/i.test(f.path)) && !isBarrelFile(f.path)
    ).length
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

  return sortedApps
})
</script>
