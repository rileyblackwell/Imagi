<template>
  <div class="flex h-full w-full bg-[#050508]">
    <!-- Apps list (left) -->
    <aside class="hidden md:flex md:w-56 flex-col border-r border-white/[0.06] bg-[#0a0a0f]/80 backdrop-blur-xl">
      <div class="px-3 py-3 border-b border-white/[0.06] flex items-center gap-2">
        <span class="w-7 h-7 rounded-lg flex items-center justify-center bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 text-violet-300 shadow-lg shadow-violet-500/10">
          <i class="fas fa-cubes text-xs"></i>
        </span>
        <div class="text-sm font-semibold text-white/90">Apps</div>
      </div>
      <div class="p-2 overflow-auto space-y-1.5">
        <button
          v-for="app in apps"
          :key="app.key"
          type="button"
          class="w-full text-left px-2.5 py-2 rounded-lg border transition-all duration-200 flex items-center gap-2.5 group"
          :class="[
            selectedApp && selectedApp.key === app.key
              ? 'border-violet-500/30 bg-gradient-to-r from-violet-500/15 to-fuchsia-500/15 shadow-lg shadow-violet-500/5'
              : 'border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/[0.08]'
          ]"
          @click="selectApp(app)"
        >
          <span :class="['w-8 h-8 rounded-lg flex items-center justify-center border text-sm transition-transform duration-200 group-hover:scale-105', app.color.bg, app.color.border, app.color.text]">
            <i :class="app.icon"></i>
          </span>
          <span class="min-w-0 flex-1">
            <span class="block text-xs font-medium text-white/90 truncate">{{ app.displayName }}</span>
            <span class="block text-[10px] text-white/40 truncate">{{ app.files.length }} files</span>
          </span>
        </button>
      </div>
    </aside>

    <!-- Main content (right) -->
    <section class="flex-1 min-w-0 flex flex-col bg-[#050508]">
      <!-- Toolbar -->
      <div class="px-4 py-3 flex items-center gap-3 border-b border-white/[0.06] bg-[#0a0a0f]/80 backdrop-blur-xl">
        <div class="flex items-center gap-3 min-w-0">
          <span v-if="selectedApp" :class="['w-9 h-9 rounded-xl flex items-center justify-center border text-base shadow-lg', selectedApp.color.bg, selectedApp.color.border, selectedApp.color.text]">
            <i :class="selectedApp.icon"></i>
          </span>
          <div class="min-w-0">
            <div class="text-sm font-semibold text-white/90 truncate">
              {{ selectedApp ? selectedApp.displayName : 'Browse Apps' }}
            </div>
            <div class="text-[11px] text-white/40 truncate">
              {{ selectedApp ? 'Select a file to chat or build' : 'Choose an app to view its files' }}
            </div>
          </div>
        </div>
        <div class="ml-auto flex items-center gap-3">
          <!-- Search -->
          <div class="relative">
            <i class="fas fa-search text-white/30 absolute left-3 top-1/2 -translate-y-1/2 text-xs"></i>
            <input
              v-model="query"
              type="text"
              placeholder="Search files..."
              class="w-48 pl-8 pr-3 py-2 text-xs bg-white/[0.03] border border-white/[0.08] rounded-lg text-white/90 placeholder-white/30 outline-none focus:ring-1 focus:ring-violet-500/30 focus:border-violet-500/30 transition-all"
            />
          </div>
          <!-- View toggle -->
          <div class="inline-flex rounded-lg border border-white/[0.08] overflow-hidden bg-white/[0.02]">
            <button
              class="px-2.5 py-1.5 text-xs border-r border-white/[0.08] transition-all"
              :class="viewMode === 'grid' ? 'bg-violet-500/20 text-violet-300' : 'text-white/40 hover:text-white/60 hover:bg-white/[0.03]'"
              @click="viewMode = 'grid'"
              title="Grid view"
            >
              <i class="fas fa-th-large"></i>
            </button>
            <button
              class="px-2.5 py-1.5 text-xs transition-all"
              :class="viewMode === 'list' ? 'bg-violet-500/20 text-violet-300' : 'text-white/40 hover:text-white/60 hover:bg-white/[0.03]'"
              @click="viewMode = 'list'"
              title="List view"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-1 min-h-0 overflow-auto p-4 bg-[#050508]">
        <!-- Files for selected app -->
        <div class="space-y-4">
          <!-- File count badge -->
          <div class="inline-flex items-center gap-2 px-3 py-1.5 bg-white/[0.03] rounded-full border border-white/[0.06]">
            <i class="fas fa-file text-[10px] text-violet-400/70"></i>
            <span class="text-[11px] text-white/50">{{ filteredFiles.length }} files</span>
          </div>

          <!-- Tabs by category -->
          <div class="flex items-center gap-1 border-b border-white/[0.06]">
            <button
              v-for="cat in categories"
              :key="cat.key"
              class="px-4 py-2.5 text-xs font-medium rounded-t-lg border-b-2 -mb-px transition-all"
              :class="activeCategory === cat.key 
                ? 'border-violet-400 text-white/90 bg-violet-500/10' 
                : 'border-transparent text-white/40 hover:text-white/60 hover:bg-white/[0.02]'"
              @click="setCategory(cat.key)"
            >
              {{ cat.label }}
            </button>
          </div>

          <!-- Grid/List of files -->
          <template v-if="activeCategory === 'components'">
            <div v-for="group in subgroupOrder" :key="group.key" class="space-y-3">
              <div class="flex items-center gap-2">
                <div class="text-[11px] uppercase tracking-wider font-medium text-white/40">{{ group.label }}</div>
                <div class="flex-1 h-px bg-gradient-to-r from-white/[0.06] to-transparent"></div>
                <button
                  @click="openNewComponentModal(group.key)"
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-violet-500/20 bg-violet-500/10 hover:bg-violet-500/20 text-violet-300 hover:text-violet-200 transition-all text-[10px] font-medium"
                  :title="`Create new ${group.label.toLowerCase()} component`"
                >
                  <i class="fas fa-plus text-[9px]"></i>
                  <span>New</span>
                </button>
              </div>
              
              <!-- Empty state when no files in this subgroup -->
              <div v-if="!componentSubgroups[group.key].length" class="py-4 text-center">
                <p class="text-xs text-white/30">No {{ group.label.toLowerCase() }} yet</p>
              </div>
              <!-- Grid view for components -->
              <div v-if="viewMode === 'grid' && componentSubgroups[group.key].length" class="grid gap-3 grid-cols-[repeat(auto-fill,minmax(160px,1fr))]">
                <div
                  v-for="file in componentSubgroups[group.key]"
                  :key="file.path"
                  class="group relative rounded-xl border border-white/[0.06] bg-gradient-to-br from-white/[0.03] to-transparent hover:from-white/[0.06] hover:border-white/[0.08] text-left p-3.5 transition-all duration-200 hover:shadow-lg hover:shadow-violet-500/5 hover:-translate-y-0.5 cursor-pointer"
                  @click="emit('select-file', file)"
                  @keydown.enter.prevent="emit('select-file', file)"
                  @keydown.space.prevent="emit('select-file', file)"
                  :title="file.path"
                  role="button"
                  tabindex="0"
                >
                  <!-- Delete button -->
                  <button
                    @click.stop="confirmDelete(file)"
                    class="absolute top-2 right-2 w-6 h-6 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center"
                    title="Delete file"
                  >
                    <i class="fas fa-trash text-[10px]"></i>
                  </button>
                  <div class="flex flex-col items-center text-center gap-2.5">
                    <div :class="['w-10 h-10 rounded-xl flex items-center justify-center border text-lg shadow-lg transition-transform duration-200 group-hover:scale-110', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                      <i :class="fileIcon(file).icon"></i>
                    </div>
                    <div class="text-xs font-medium text-white/90 truncate w-full">{{ fileName(file.path) }}</div>
                  </div>
                </div>
              </div>
              
              <!-- List view for components -->
              <div v-else-if="viewMode === 'list' && componentSubgroups[group.key].length" class="divide-y divide-white/[0.04] rounded-xl border border-white/[0.06] overflow-hidden bg-white/[0.01]">
                <div
                  v-for="file in componentSubgroups[group.key]"
                  :key="file.path"
                  class="w-full text-left px-3.5 py-2.5 flex items-center gap-3 hover:bg-white/[0.03] transition-all group cursor-pointer"
                  @click="emit('select-file', file)"
                  @keydown.enter.prevent="emit('select-file', file)"
                  @keydown.space.prevent="emit('select-file', file)"
                  :title="file.path"
                  role="button"
                  tabindex="0"
                >
                  <div :class="['w-8 h-8 rounded-lg flex items-center justify-center border text-sm transition-transform duration-200 group-hover:scale-105', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                    <i :class="fileIcon(file).icon"></i>
                  </div>
                  <div class="text-xs font-medium text-white/90 truncate flex-1">{{ fileName(file.path) }}</div>
                  <button
                    @click.stop="confirmDelete(file)"
                    class="w-7 h-7 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center"
                    title="Delete file"
                  >
                    <i class="fas fa-trash text-[10px]"></i>
                  </button>
                  <i class="fas fa-chevron-right text-[10px] text-white/30 opacity-0 group-hover:opacity-100 transition-opacity"></i>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <!-- New file button for current category -->
            <div v-if="activeCategory === 'views'" class="flex items-center gap-2 mb-3">
              <button
                @click="openNewViewModal()"
                class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-violet-500/20 bg-violet-500/10 hover:bg-violet-500/20 text-violet-300 hover:text-violet-200 transition-all text-xs font-medium"
              >
                <i class="fas fa-plus text-[10px]"></i>
                <span>New View</span>
              </button>
            </div>
            
            <div v-if="viewMode === 'grid'" class="grid gap-3 grid-cols-[repeat(auto-fill,minmax(160px,1fr))]">
              <div
                v-for="file in categorizedFiles"
                :key="file.path"
                class="group relative rounded-xl border border-white/[0.06] bg-gradient-to-br from-white/[0.03] to-transparent hover:from-white/[0.06] hover:border-white/[0.08] text-left p-3.5 transition-all duration-200 hover:shadow-lg hover:shadow-violet-500/5 hover:-translate-y-0.5 cursor-pointer"
                @click="emit('select-file', file)"
                @keydown.enter.prevent="emit('select-file', file)"
                @keydown.space.prevent="emit('select-file', file)"
                :title="file.path"
                role="button"
                tabindex="0"
              >
                <!-- Delete button for views -->
                <button
                  v-if="activeCategory === 'views'"
                  @click.stop="confirmDelete(file)"
                  class="absolute top-2 right-2 w-6 h-6 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center"
                  title="Delete file"
                >
                  <i class="fas fa-trash text-[10px]"></i>
                </button>
                <div class="flex flex-col items-center text-center gap-2.5">
                  <div :class="['w-10 h-10 rounded-xl flex items-center justify-center border text-lg shadow-lg transition-transform duration-200 group-hover:scale-110', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                    <i :class="fileIcon(file).icon"></i>
                  </div>
                  <div class="text-xs font-medium text-white/90 truncate w-full">{{ fileName(file.path) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="divide-y divide-white/[0.04] rounded-xl border border-white/[0.06] overflow-hidden bg-white/[0.01]">
              <div
                v-for="file in categorizedFiles"
                :key="file.path"
                class="w-full text-left px-3.5 py-2.5 flex items-center gap-3 hover:bg-white/[0.03] transition-all group cursor-pointer"
                @click="emit('select-file', file)"
                @keydown.enter.prevent="emit('select-file', file)"
                @keydown.space.prevent="emit('select-file', file)"
                :title="file.path"
                role="button"
                tabindex="0"
              >
                <div :class="['w-8 h-8 rounded-lg flex items-center justify-center border text-sm transition-transform duration-200 group-hover:scale-105', fileIcon(file).bg, fileIcon(file).border, fileIcon(file).text]">
                  <i :class="fileIcon(file).icon"></i>
                </div>
                <div class="text-xs font-medium text-white/90 truncate flex-1">{{ fileName(file.path) }}</div>
                <button
                  v-if="activeCategory === 'views'"
                  @click.stop="confirmDelete(file)"
                  class="w-7 h-7 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center"
                  title="Delete file"
                >
                  <i class="fas fa-trash text-[10px]"></i>
                </button>
                <i class="fas fa-chevron-right text-[10px] text-white/30 opacity-0 group-hover:opacity-100 transition-opacity"></i>
              </div>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- New File Modal -->
    <Teleport to="body">
      <div
        v-if="showNewFileModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="closeNewFileModal"
      >
        <div class="relative w-full max-w-md rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/95 backdrop-blur-xl shadow-2xl">
          <!-- Header -->
          <div class="px-6 py-4 border-b border-white/[0.06]">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 flex items-center justify-center">
                  <i class="fas fa-plus text-violet-300"></i>
                </div>
                <div>
                  <h3 class="text-base font-semibold text-white/90">
                    {{ newFileType === 'view' ? 'New View' : `New ${newFileSubtype.charAt(0).toUpperCase() + newFileSubtype.slice(1)} Component` }}
                  </h3>
                  <p class="text-xs text-white/40 mt-0.5">
                    {{ selectedApp ? `in ${selectedApp.displayName}` : '' }}
                  </p>
                </div>
              </div>
              <button
                @click="closeNewFileModal"
                class="w-8 h-8 rounded-lg hover:bg-white/[0.05] text-white/40 hover:text-white/90 transition-all flex items-center justify-center"
              >
                <i class="fas fa-times"></i>
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="px-6 py-5 space-y-4">
            <div>
              <label class="block text-sm font-medium text-white/60 mb-2">
                File Name
              </label>
              <input
                v-model="newFileName"
                type="text"
                placeholder="MyComponent"
                class="w-full px-4 py-2.5 bg-white/[0.03] border border-white/[0.08] rounded-lg text-white/90 placeholder-white/30 outline-none focus:ring-2 focus:ring-violet-500/30 focus:border-violet-500/30 transition-all"
                @keydown.enter="createNewFile"
                @keydown.escape="closeNewFileModal"
                autofocus
              />
              <p class="text-xs text-white/30 mt-2">
                .vue extension will be added automatically
              </p>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-white/[0.06] flex items-center justify-end gap-3">
            <button
              @click="closeNewFileModal"
              class="px-4 py-2 rounded-lg border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.05] text-white/60 hover:text-white/90 transition-all text-sm font-medium"
            >
              Cancel
            </button>
            <button
              @click="createNewFile"
              :disabled="!newFileName.trim()"
              class="px-4 py-2 rounded-lg bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white transition-all text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-violet-500/20"
            >
              Create File
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div
        v-if="showDeleteConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="closeDeleteConfirm"
      >
        <div class="relative w-full max-w-md rounded-2xl border border-red-500/20 bg-[#0a0a0f]/95 backdrop-blur-xl shadow-2xl">
          <!-- Header -->
          <div class="px-6 py-4 border-b border-white/[0.06]">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-red-500/20 border border-red-500/20 flex items-center justify-center">
                <i class="fas fa-exclamation-triangle text-red-400"></i>
              </div>
              <div>
                <h3 class="text-base font-semibold text-white/90">Delete File</h3>
                <p class="text-xs text-white/40 mt-0.5">This action cannot be undone</p>
              </div>
            </div>
          </div>

          <!-- Body -->
          <div class="px-6 py-5">
            <p class="text-sm text-white/60">
              Are you sure you want to delete 
              <span class="font-semibold text-white/90">{{ fileToDelete ? fileName(fileToDelete.path) : '' }}</span>?
            </p>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-white/[0.06] flex items-center justify-end gap-3">
            <button
              @click="closeDeleteConfirm"
              class="px-4 py-2 rounded-lg border border-white/[0.08] bg-white/[0.02] hover:bg-white/[0.05] text-white/60 hover:text-white/90 transition-all text-sm font-medium"
            >
              Cancel
            </button>
            <button
              @click="deleteFile"
              class="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-all text-sm font-medium shadow-lg shadow-red-500/20"
            >
              Delete File
            </button>
          </div>
        </div>
      </div>
    </Teleport>
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

// Modal states
const showNewFileModal = ref(false)
const newFileName = ref('')
const newFileType = ref<'view' | 'component'>('view')
const newFileSubtype = ref<'atoms' | 'molecules' | 'organisms' | 'other'>('atoms')
const showDeleteConfirm = ref(false)
const fileToDelete = ref<ProjectFile | null>(null)

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
type CategoryKey = 'views' | 'components' | 'store' | 'services'
const categories: ReadonlyArray<{ key: CategoryKey; label: string; match: RegExp }> = [
  { key: 'views', label: 'Views', match: /\/views\//i },
  { key: 'components', label: 'Components', match: /\/components\//i },
  { key: 'store', label: 'Store', match: /\/store\//i },
  { key: 'services', label: 'Services', match: /\/services\//i },
] as const
const activeCategory = ref<CategoryKey>('views')
function setCategory(k: CategoryKey) {
  activeCategory.value = k
}

const filteredFiles = computed(() => {
  const list = selectedApp.value ? selectedApp.value.files : []
  // Filter out index.ts barrel files
  const withoutBarrels = list.filter((f) => {
    const filename = f.path.split('/').pop()?.toLowerCase() || ''
    return filename !== 'index.ts'
  })
  const q = query.value.trim().toLowerCase()
  if (!q) return withoutBarrels
  return withoutBarrels.filter((f) => f.path.toLowerCase().includes(q))
})

const categorizedFiles = computed(() => {
  const all = filteredFiles.value
  const cat = activeCategory.value
  const spec = categories.find((c) => c.key === cat)
  if (!spec) return all
  return all.filter((f) => spec.match.test(f.path))
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

// Modal functions
function openNewViewModal() {
  newFileType.value = 'view'
  newFileName.value = ''
  showNewFileModal.value = true
}

function openNewComponentModal(subtype: 'atoms' | 'molecules' | 'organisms' | 'other') {
  newFileType.value = 'component'
  newFileSubtype.value = subtype
  newFileName.value = ''
  showNewFileModal.value = true
}

function closeNewFileModal() {
  showNewFileModal.value = false
  newFileName.value = ''
}

function createNewFile() {
  if (!newFileName.value.trim() || !selectedApp.value) return
  
  // Clean filename and ensure .vue extension
  let filename = newFileName.value.trim()
  if (!filename.endsWith('.vue')) {
    filename += '.vue'
  }
  
  // Build the file path based on type
  let filePath = ''
  if (newFileType.value === 'view') {
    filePath = `frontend/vuejs/src/apps/${selectedApp.value.name}/views/${filename}`
  } else {
    // Component path
    const subdir = newFileSubtype.value !== 'other' ? `${newFileSubtype.value}/` : ''
    filePath = `frontend/vuejs/src/apps/${selectedApp.value.name}/components/${subdir}${filename}`
  }
  
  emit('create-file', {
    name: filePath,
    type: 'vue',
    content: ''
  })
  
  closeNewFileModal()
}

function confirmDelete(file: ProjectFile) {
  fileToDelete.value = file
  showDeleteConfirm.value = true
}

function closeDeleteConfirm() {
  showDeleteConfirm.value = false
  fileToDelete.value = null
}

function deleteFile() {
  if (fileToDelete.value) {
    emit('delete-file', fileToDelete.value)
  }
  closeDeleteConfirm()
}
</script>
