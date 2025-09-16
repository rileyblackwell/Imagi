<template>
  <div class="flex h-full w-full">
    <!-- Apps list (left) -->
    <aside class="hidden md:flex md:w-64 flex-col border-r border-white/10 bg-dark-900/40">
      <div class="px-3 py-3 border-b border-white/10 flex items-center gap-2">
        <span class="w-7 h-7 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
          <i class="fas fa-cubes"></i>
        </span>
        <div class="text-sm font-semibold text-white">Apps</div>
      </div>
      <div class="p-2 overflow-auto space-y-2">
        <button
          v-for="app in apps"
          :key="app.key"
          type="button"
          class="w-full text-left px-2 py-2 rounded-lg border transition flex items-center gap-2"
          :class="[
            selectedApp && selectedApp.key === app.key
              ? 'border-primary-500/40 bg-primary-500/10'
              : 'border-white/10 bg-white/[0.03] hover:bg-white/10'
          ]"
          @click="selectApp(app)"
        >
          <span :class="['w-8 h-8 rounded-md flex items-center justify-center border text-base', app.color.bg, app.color.border, app.color.text]">
            <i :class="app.icon"></i>
          </span>
          <span class="min-w-0">
            <span class="block text-xs text-white truncate">{{ app.displayName }}</span>
            <span class="block text-xxs text-gray-400 truncate">{{ app.hint }}</span>
          </span>
        </button>
      </div>
    </aside>

    <!-- Main content (right) -->
    <section class="flex-1 min-w-0 flex flex-col">
      <!-- Toolbar -->
      <div class="px-4 py-3 flex items-center gap-3 border-b border-white/10 bg-dark-900/50">
        <div class="flex items-center gap-2 min-w-0">
          <span v-if="selectedApp" :class="['w-8 h-8 rounded-md flex items-center justify-center border text-base', selectedApp.color.bg, selectedApp.color.border, selectedApp.color.text]">
            <i :class="selectedApp.icon"></i>
          </span>
          <div class="min-w-0">
            <div class="text-sm font-semibold text-white truncate">
              {{ selectedApp ? selectedApp.displayName : 'Browse Apps' }}
            </div>
            <div class="text-xxs text-gray-400 truncate">
              {{ selectedApp ? 'Select a file to chat or build' : 'Choose an app to view its files' }}
            </div>
          </div>
        </div>
        <div class="ml-auto flex items-center gap-2">
          <!-- Search -->
          <div class="relative w-56">
            <i class="fas fa-search text-gray-500 absolute left-2.5 top-2.5 text-xs"></i>
            <input
              v-model="query"
              type="text"
              placeholder="Search files..."
              class="w-full pl-7 pr-3 py-2 text-xs bg-dark-900/80 border border-dark-700/60 rounded-md text-white placeholder-gray-500 outline-none focus:ring-0 focus:border-primary-500/40"
            />
          </div>
          <!-- View toggle -->
          <div class="inline-flex rounded-md border border-white/10 overflow-hidden">
            <button
              class="px-2 py-1 text-xs border-r border-white/10"
              :class="viewMode === 'grid' ? 'bg-white/10 text-white' : 'text-gray-300 hover:bg-white/5'"
              @click="viewMode = 'grid'"
              title="Grid view"
            >
              <i class="fas fa-th-large"></i>
            </button>
            <button
              class="px-2 py-1 text-xs"
              :class="viewMode === 'list' ? 'bg-white/10 text-white' : 'text-gray-300 hover:bg-white/5'"
              @click="viewMode = 'list'"
              title="List view"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 min-h-0 overflow-auto p-4">
        <!-- Files for selected app -->
        <div class="space-y-3">
          <div class="flex items-center gap-2 text-xxs text-gray-400">
            <span>{{ filteredFiles.length }} files</span>
          </div>

          <!-- Tabs by category -->
          <div class="flex items-center gap-1 border-b border-white/10">
            <button
              v-for="cat in categories"
              :key="cat.key"
              class="px-3 py-2 text-xs rounded-t-md border-b-2 -mb-px"
              :class="activeCategory === cat.key ? 'border-primary-400 text-white' : 'border-transparent text-gray-400 hover:text-gray-300'"
              @click="setCategory(cat.key)"
            >
              {{ cat.label }}
            </button>
          </div>

          <!-- Grid/List of files -->
          <template v-if="activeCategory === 'components'">
            <div v-for="group in subgroupOrder" :key="group.key" class="space-y-2" v-show="componentSubgroups[group.key].length">
              <div class="text-[11px] uppercase tracking-wide text-gray-400/90 px-1">{{ group.label }}</div>
              <div v-if="viewMode === 'grid'" class="grid gap-3 grid-cols-[repeat(auto-fill,minmax(220px,1fr))]">
                <button
                  v-for="file in componentSubgroups[group.key]"
                  :key="file.path"
                  type="button"
                  class="group rounded-xl border border-white/10 bg-dark-900/50 hover:bg-white/5 text-left p-3 transition"
                  @click="emit('select-file', file)"
                  :title="file.path"
                >
                  <div class="flex items-start gap-3">
                    <div :class="['w-9 h-9 rounded-lg flex items-center justify-center border text-base', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                      <i :class="fileIcon(file).icon"></i>
                    </div>
                    <div class="min-w-0">
                      <div class="text-xs font-medium text-white truncate">{{ fileName(file.path) }}</div>
                      <div class="text-xxs text-gray-400 truncate">{{ prettyPath(file.path) }}</div>
                    </div>
                  </div>
                </button>
              </div>
              <div v-else class="divide-y divide-white/10 rounded-xl border border-white/10 overflow-hidden">
                <button
                  v-for="file in componentSubgroups[group.key]"
                  :key="file.path"
                  type="button"
                  class="w-full text-left px-3 py-2 flex items-center gap-3 bg-dark-900/50 hover:bg-white/5 transition"
                  @click="emit('select-file', file)"
                  :title="file.path"
                >
                  <div :class="['w-7 h-7 rounded-md flex items-center justify-center border text-sm', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                    <i :class="fileIcon(file).icon"></i>
                  </div>
                  <div class="min-w-0">
                    <div class="text-xs text-white truncate">{{ fileName(file.path) }}</div>
                    <div class="text-xxs text-gray-400 truncate">{{ prettyPath(file.path) }}</div>
                  </div>
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <div v-if="viewMode === 'grid'" class="grid gap-3 grid-cols-[repeat(auto-fill,minmax(220px,1fr))]">
              <button
                v-for="file in categorizedFiles"
                :key="file.path"
                type="button"
                class="group rounded-xl border border-white/10 bg-dark-900/50 hover:bg-white/5 text-left p-3 transition"
                @click="emit('select-file', file)"
                :title="file.path"
              >
                <div class="flex items-start gap-3">
                  <div :class="['w-9 h-9 rounded-lg flex items-center justify-center border text-base', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                    <i :class="fileIcon(file).icon"></i>
                  </div>
                  <div class="min-w-0">
                    <div class="text-xs font-medium text-white truncate">{{ fileName(file.path) }}</div>
                    <div class="text-xxs text-gray-400 truncate">{{ prettyPath(file.path) }}</div>
                  </div>
                </div>
              </button>
            </div>
            <div v-else class="divide-y divide-white/10 rounded-xl border border-white/10 overflow-hidden">
              <button
                v-for="file in categorizedFiles"
                :key="file.path"
                type="button"
                class="w-full text-left px-3 py-2 flex items-center gap-3 bg-dark-900/50 hover:bg-white/5 transition"
                @click="emit('select-file', file)"
                :title="file.path"
              >
                <div :class="['w-7 h-7 rounded-md flex items-center justify-center border text-sm', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                  <i :class="fileIcon(file).icon"></i>
                </div>
                <div class="min-w-0">
                  <div class="text-xs text-white truncate">{{ fileName(file.path) }}</div>
                  <div class="text-xxs text-gray-400 truncate">{{ prettyPath(file.path) }}</div>
                </div>
              </button>
            </div>
          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import type { ProjectFile } from '../../../types/components'

const props = defineProps<{
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
  projectId: string
}>()

const emit = defineEmits<{
  (e: 'select-file', file: ProjectFile): void
  (e: 'create-file', data: { name: string; type: string; content?: string }): void
  (e: 'delete-file', file: ProjectFile): void
}>()

const query = ref('')
const viewMode = ref<'grid' | 'list'>('grid')

// Build app groups from files
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
  return Object.values(map).sort((a, b) => a.displayName.localeCompare(b.displayName))
})

const selectedApp = ref<null | (typeof apps.value)[number]>(null)
function selectApp(app: (typeof apps.value)[number]) {
  selectedApp.value = app
}

// Default to first app when available
watch(apps, (list) => {
  if (!selectedApp.value && list && list.length) {
    selectedApp.value = list[0]
  }
}, { immediate: true })
onMounted(() => {
  const list = apps.value
  if (!selectedApp.value && list && list.length) {
    selectedApp.value = list[0]
  }
})

// Categories
type CategoryKey = 'views' | 'components' | 'store' | 'services' | 'other'
const categories: ReadonlyArray<{ key: CategoryKey; label: string; match: RegExp | null }> = [
  { key: 'views', label: 'Views', match: /\/views\//i },
  { key: 'components', label: 'Components', match: /\/components\//i },
  { key: 'store', label: 'Store', match: /\/store\//i },
  { key: 'services', label: 'Services', match: /\/services\//i },
  { key: 'other', label: 'Other', match: null },
] as const
const activeCategory = ref<CategoryKey>('views')
function setCategory(k: CategoryKey) {
  activeCategory.value = k
}

const filteredFiles = computed(() => {
  const list = selectedApp.value ? selectedApp.value.files : []
  const q = query.value.trim().toLowerCase()
  if (!q) return list
  return list.filter((f) => f.path.toLowerCase().includes(q))
})

const categorizedFiles = computed(() => {
  const all = filteredFiles.value
  const cat = activeCategory.value
  const spec = categories.find((c) => c.key === cat)
  if (!spec) return all
  if (spec.match) return all.filter((f) => spec.match!.test(f.path))
  // other
  return all.filter((f) => !categories.some((c) => c.match && c.match.test(f.path)))
})

// Subgrouping for components: atoms, molecules, organisms
type SubKey = 'atoms' | 'molecules' | 'organisms' | 'other'
const subgroupOrder: Array<{ key: SubKey; label: string }> = [
  { key: 'atoms', label: 'Atoms' },
  { key: 'molecules', label: 'Molecules' },
  { key: 'organisms', label: 'Organisms' },
  { key: 'other', label: 'Other' },
]
const componentSubgroups = computed<Record<SubKey, ProjectFile[]>>(() => {
  const out: Record<SubKey, ProjectFile[]> = {
    atoms: [],
    molecules: [],
    organisms: [],
    other: [],
  }
  if (activeCategory.value !== 'components') return out
  const list = filteredFiles.value.filter((f) => /\/components\//i.test(f.path))
  list.forEach((f) => {
    const p = f.path.toLowerCase()
    if (/\/components\/atoms\//.test(p)) out.atoms.push(f)
    else if (/\/components\/molecules\//.test(p)) out.molecules.push(f)
    else if (/\/components\/organisms\//.test(p)) out.organisms.push(f)
    else out.other.push(f)
  })
  return out
})

function fileName(p: string): string {
  const parts = p.split('/')
  return parts[parts.length - 1]
}
function prettyPath(p: string): string {
  return p.replace(/^.*src\//, '')
}

function fileIcon(file: ProjectFile) {
  const ext = (file.path.split('.').pop() || '').toLowerCase()
  if (ext === 'vue') return { icon: 'fab fa-vuejs', bg: 'bg-emerald-600/15', border: 'border-emerald-400/30', text: 'text-emerald-300' }
  if (ext === 'ts') return { icon: 'fas fa-code', bg: 'bg-indigo-600/15', border: 'border-indigo-400/30', text: 'text-indigo-300' }
  if (ext === 'js') return { icon: 'fab fa-js', bg: 'bg-amber-600/15', border: 'border-amber-400/30', text: 'text-amber-300' }
  if (ext === 'css') return { icon: 'fas fa-paint-brush', bg: 'bg-rose-600/15', border: 'border-rose-400/30', text: 'text-rose-300' }
  if (ext === 'json') return { icon: 'fas fa-brackets-curly', bg: 'bg-cyan-600/15', border: 'border-cyan-400/30', text: 'text-cyan-300' }
  if (ext === 'md') return { icon: 'fas fa-file-alt', bg: 'bg-violet-600/15', border: 'border-violet-400/30', text: 'text-violet-300' }
  return { icon: 'fas fa-file', bg: 'bg-white/5', border: 'border-white/10', text: 'text-gray-300' }
}
</script>
