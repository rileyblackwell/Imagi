<template>
  <div class="h-full flex flex-col bg-[#0a0a0f] overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-5 border-b border-white/[0.08]">
      <div class="flex items-center gap-4 mb-4">
        <!-- Back button only shows when in a category view -->
        <button
          v-if="selectedCategory"
          @click="handleBack"
          class="w-10 h-10 rounded-xl border border-white/[0.08] bg-white/[0.03] hover:bg-white/[0.05] hover:border-white/[0.12] transition-all flex items-center justify-center text-white/60 hover:text-white"
        >
          <i class="fas fa-arrow-left"></i>
        </button>
        <div
          :class="[
            'w-12 h-12 rounded-xl flex items-center justify-center border shadow-inner flex-shrink-0',
            app.color.bg,
            app.color.border,
            app.color.text
          ]"
        >
          <i :class="app.icon" class="text-lg"></i>
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl font-semibold text-white/90 truncate">{{ app.displayName }}</h2>
          <p class="text-sm text-white/50 mt-1">
            <template v-if="selectedCategory">
              {{ selectedCategory.label }} in {{ app.displayName }}
            </template>
            <template v-else>
              {{ app.hint }}
            </template>
          </p>
        </div>
        <!-- Close button to deselect app (only shows when not in category view) -->
        <button
          v-if="!selectedCategory"
          @click="handleBack"
          class="w-10 h-10 rounded-xl border border-white/[0.08] bg-white/[0.03] hover:bg-white/[0.05] hover:border-white/[0.12] transition-all flex items-center justify-center text-white/60 hover:text-white"
          title="Close app"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <!-- Category Overview -->
      <div v-if="!selectedCategory" class="p-6">
        <!-- Primary Categories: Pages, Blocks, Data (always visible) -->
        <div class="mb-6">
          <h3 class="text-sm font-medium text-white/60 uppercase tracking-wider mb-4">What's in this app</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Pages Card -->
            <div
              @click="selectCategory(pagesCategory)"
              class="group relative cursor-pointer"
            >
              <div class="absolute -inset-0.5 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-violet-600/10 to-fuchsia-600/10"></div>
              <div class="relative p-6 rounded-xl border bg-[#0a0a0f]/80 backdrop-blur-xl transition-all duration-300 flex flex-col border-white/[0.08] hover:border-violet-500/30">
                <!-- Icon -->
                <div class="flex items-start justify-between mb-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center border bg-violet-500/10 border-violet-500/20">
                    <i class="fas fa-window-maximize text-xl text-violet-400"></i>
                  </div>
                </div>
                
                <!-- Category info -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-white/90 mb-1">Pages</h3>
                  <p class="text-xs text-white/50">Screens people visit in your app</p>
                </div>
                
                <!-- Footer -->
                <div class="flex items-center justify-end mt-4 pt-4 border-t border-white/[0.06]">
                  <i class="fas fa-arrow-right text-sm transition-all duration-300 group-hover:translate-x-1 text-violet-400"></i>
                </div>
              </div>
            </div>

            <!-- Blocks Card -->
            <div
              @click="selectCategory(blocksCategory)"
              class="group relative cursor-pointer"
            >
              <div class="absolute -inset-0.5 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-fuchsia-600/10 to-violet-600/10"></div>
              <div class="relative p-6 rounded-xl border bg-[#0a0a0f]/80 backdrop-blur-xl transition-all duration-300 flex flex-col border-white/[0.08] hover:border-fuchsia-500/30">
                <!-- Icon -->
                <div class="flex items-start justify-between mb-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center border bg-fuchsia-500/10 border-fuchsia-500/20">
                    <i class="fas fa-puzzle-piece text-xl text-fuchsia-400"></i>
                  </div>
                </div>
                
                <!-- Category info -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-white/90 mb-1">Blocks</h3>
                  <p class="text-xs text-white/50">Reusable pieces like headers, cards, forms</p>
                </div>
                
                <!-- Footer -->
                <div class="flex items-center justify-end mt-4 pt-4 border-t border-white/[0.06]">
                  <i class="fas fa-arrow-right text-sm transition-all duration-300 group-hover:translate-x-1 text-fuchsia-400"></i>
                </div>
              </div>
            </div>

            <!-- Data Card -->
            <div
              @click="dataCategory.count > 0 ? selectCategory(dataCategory) : null"
              :class="[
                'group relative',
                dataCategory.count > 0 ? 'cursor-pointer' : 'cursor-default opacity-60'
              ]"
            >
              <div v-if="dataCategory.count > 0" class="absolute -inset-0.5 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-emerald-600/10 to-cyan-600/10"></div>
              <div :class="[
                'relative p-6 rounded-xl border bg-[#0a0a0f]/80 backdrop-blur-xl transition-all duration-300 flex flex-col border-white/[0.08]',
                dataCategory.count > 0 ? 'hover:border-emerald-500/30' : ''
              ]">
                <!-- Icon -->
                <div class="flex items-start justify-between mb-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center border bg-emerald-500/10 border-emerald-500/20">
                    <i class="fas fa-database text-xl text-emerald-400"></i>
                  </div>
                </div>
                
                <!-- Category info -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-white/90 mb-1">Data</h3>
                  <p class="text-xs text-white/50">Information your app remembers</p>
                </div>
                
                <!-- Footer -->
                <div class="flex items-center justify-end mt-4 pt-4 border-t border-white/[0.06]">
                  <i v-if="dataCategory.count > 0" class="fas fa-arrow-right text-sm transition-all duration-300 group-hover:translate-x-1 text-emerald-400"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Advanced Section (collapsed by default) -->
        <div v-if="hasAdvancedFiles" class="mt-8">
          <button
            @click="showAdvanced = !showAdvanced"
            class="flex items-center gap-2 text-sm font-medium text-white/40 hover:text-white/60 transition-colors mb-4"
          >
            <i :class="['fas fa-chevron-right text-xs transition-transform duration-200', showAdvanced ? 'rotate-90' : '']"></i>
            <span>Advanced</span>
          </button>
          
          <div v-if="showAdvanced" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            <!-- Advanced Category Cards -->
            <div
              v-for="category in advancedCategories"
              :key="category.key"
              @click="selectCategory(category)"
              class="group relative cursor-pointer"
            >
              <div :class="[
                'absolute -inset-0.5 rounded-lg blur opacity-0 group-hover:opacity-100 transition-opacity duration-200',
                category.glowColor
              ]"></div>
              <div :class="[
                'relative p-4 rounded-lg border bg-[#0a0a0f]/80 backdrop-blur-xl transition-all duration-200 flex items-center gap-3',
                category.borderColor,
                category.hoverBorderColor
              ]">
                <div :class="[
                  'w-10 h-10 rounded-lg flex items-center justify-center border flex-shrink-0',
                  category.bgColor,
                  category.iconBorderColor
                ]">
                  <i :class="[category.icon, category.iconColor, 'text-sm']"></i>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-white/90 truncate">{{ category.label }}</div>
                </div>
                <i :class="['fas fa-chevron-right text-xs text-white/20 group-hover:text-white/40', category.iconColor]"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty state when no files at all -->
        <div v-if="pagesCategory.count === 0 && blocksCategory.count === 0 && dataCategory.count === 0 && !hasAdvancedFiles" class="flex flex-col items-center justify-center py-20">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-4">
            <i class="fas fa-folder-open text-violet-400 text-2xl"></i>
          </div>
          <h3 class="text-xl font-semibold text-white/90 mb-2">Start building {{ app.displayName }}</h3>
          <p class="text-white/50 text-center max-w-md mb-6">Create pages for screens people will visit, or blocks for reusable pieces.</p>
          <div class="flex gap-3">
            <button
              @click="handleCreatePage"
              class="relative group/btn"
            >
              <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 rounded-lg blur-md opacity-30 group-hover/btn:opacity-50 transition-opacity"></div>
              <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 rounded-lg"></div>
              <div class="absolute inset-[1px] bg-gradient-to-b from-white/[0.18] to-transparent rounded-lg opacity-90"></div>
              <span class="relative flex items-center gap-2 px-4 py-2.5 text-sm text-white font-semibold">
                <i class="fas fa-window-maximize text-xs"></i>
                <span>New Page</span>
              </span>
            </button>
            <button
              @click="handleCreateBlock"
              class="relative group/btn"
            >
              <div class="absolute -inset-0.5 bg-gradient-to-r from-fuchsia-600 via-violet-600 to-fuchsia-600 rounded-lg blur-md opacity-30 group-hover/btn:opacity-50 transition-opacity"></div>
              <div class="absolute inset-0 bg-gradient-to-r from-fuchsia-600 via-violet-600 to-fuchsia-600 rounded-lg"></div>
              <div class="absolute inset-[1px] bg-gradient-to-b from-white/[0.18] to-transparent rounded-lg opacity-90"></div>
              <span class="relative flex items-center gap-2 px-4 py-2.5 text-sm text-white font-semibold">
                <i class="fas fa-puzzle-piece text-xs"></i>
                <span>New Block</span>
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Item List View (when a category is selected) -->
      <div v-else class="p-6">
        <!-- Header for the list -->
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-white/90">
            {{ selectedCategory.label }} in {{ app.displayName }}
          </h3>
          <button
            v-if="selectedCategory.canCreate"
            @click="handleCreate(selectedCategory.key)"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] hover:bg-white/[0.08] hover:border-white/[0.12] transition-all text-sm text-white/70 hover:text-white"
          >
            <i class="fas fa-plus text-xs"></i>
            <span>New {{ selectedCategory.singularLabel }}</span>
          </button>
        </div>

        <!-- Items list -->
        <div class="space-y-2">
          <div
            v-for="file in selectedCategoryFiles"
            :key="file.path"
            @click="handleSelectFile(file)"
            class="group relative cursor-pointer"
          >
            <div :class="[
              'absolute -inset-0.5 rounded-lg blur opacity-0 group-hover:opacity-100 transition-opacity duration-200',
              selectedCategory.glowColor
            ]"></div>
            <div :class="[
              'relative p-4 rounded-lg border bg-[#0a0a0f]/80 transition-all duration-200 flex items-center gap-3',
              selectedCategory.borderColor,
              selectedCategory.hoverBorderColor
            ]">
              <div :class="[
                'w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 border',
                selectedCategory.bgColor,
                selectedCategory.iconBorderColor
              ]">
                <i :class="[getFileIcon(file.path), selectedCategory.iconColor, 'text-sm']"></i>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-white/90 truncate">{{ getDisplayName(file.path) }}</div>
                <div class="text-xs text-white/40 truncate">{{ getRelativePath(file.path) }}</div>
              </div>
              <i class="fas fa-chevron-right text-xs text-white/20 group-hover:text-white/40 transition-colors"></i>
            </div>
          </div>
        </div>

        <!-- Empty state for category -->
        <div v-if="selectedCategoryFiles.length === 0" class="flex flex-col items-center justify-center py-20">
          <div :class="[
            'inline-flex items-center justify-center w-16 h-16 rounded-2xl border mb-4',
            selectedCategory.bgColor,
            selectedCategory.iconBorderColor
          ]">
            <i :class="[selectedCategory.icon, selectedCategory.iconColor, 'text-2xl']"></i>
          </div>
          <h3 class="text-xl font-semibold text-white/90 mb-2">No {{ selectedCategory.label.toLowerCase() }} yet</h3>
          <p class="text-white/50 text-center max-w-md mb-6">
            {{ selectedCategory.emptyDescription }}
          </p>
          <button
            v-if="selectedCategory.canCreate"
            @click="handleCreate(selectedCategory.key)"
            class="relative group/btn"
          >
            <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 rounded-lg blur-md opacity-30 group-hover/btn:opacity-50 transition-opacity"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-violet-600 via-fuchsia-600 to-violet-600 rounded-lg"></div>
            <div class="absolute inset-[1px] bg-gradient-to-b from-white/[0.18] to-transparent rounded-lg opacity-90"></div>
            <span class="relative flex items-center gap-2 px-4 py-2.5 text-sm text-white font-semibold">
              <i :class="[selectedCategory.icon, 'text-xs']"></i>
              <span>New {{ selectedCategory.singularLabel }}</span>
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ProjectFile } from '../../../types/components'

const props = defineProps<{
  app: {
    key: string
    name: string
    displayName: string
    files: ProjectFile[]
    icon: string
    color: { bg: string; border: string; text: string }
    hint: string
  }
}>()

const emit = defineEmits<{
  (e: 'back'): void
  (e: 'select-file', file: ProjectFile): void
  (e: 'create-file', data: { name: string; type: string }): void
  (e: 'category-change', category: { key: string; label: string } | null): void
}>()

// State
const selectedCategory = ref<any>(null)
const showAdvanced = ref(false)

// Helper function to check if a file is a barrel file (index file)
function isBarrelFile(path: string): boolean {
  const filename = path.split('/').pop()?.toLowerCase() || ''
  return filename === 'index.ts' || filename === 'index.js' || filename === 'index.vue'
}

// Categorize files and filter out barrel files
const pages = computed(() => {
  return props.app.files.filter(file => 
    /\/views\//i.test(file.path) && !isBarrelFile(file.path)
  )
})

const blocks = computed(() => {
  return props.app.files.filter(file => 
    /\/components\//i.test(file.path) && !isBarrelFile(file.path)
  )
})

const stores = computed(() => {
  return props.app.files.filter(file => 
    (/\/stores\//i.test(file.path) || /store\.(ts|js)$/i.test(file.path)) && !isBarrelFile(file.path)
  )
})

const routers = computed(() => {
  return props.app.files.filter(file => 
    (/\/router\//i.test(file.path) || /router\.(ts|js)$/i.test(file.path)) && !isBarrelFile(file.path)
  )
})

const services = computed(() => {
  return props.app.files.filter(file => 
    (/\/services\//i.test(file.path) || /service\.(ts|js)$/i.test(file.path)) && !isBarrelFile(file.path)
  )
})

const composables = computed(() => {
  return props.app.files.filter(file => 
    (/\/composables\//i.test(file.path) || /use[A-Z].*\.(ts|js)$/i.test(file.path)) && !isBarrelFile(file.path)
  )
})

const types = computed(() => {
  return props.app.files.filter(file => 
    (/\/types\//i.test(file.path) || /\.d\.ts$/i.test(file.path) || /types?\.(ts|js)$/i.test(file.path)) && !isBarrelFile(file.path)
  )
})

const otherFiles = computed(() => {
  const categorized = new Set([
    ...pages.value,
    ...blocks.value,
    ...stores.value,
    ...routers.value,
    ...services.value,
    ...composables.value,
    ...types.value
  ])
  return props.app.files.filter(file => !categorized.has(file) && !isBarrelFile(file.path))
})

// Primary categories (always visible)
const pagesCategory = computed(() => ({
  key: 'pages',
  label: 'Pages',
  singularLabel: 'Page',
  description: 'Screens people visit in your app',
  emptyDescription: 'Create pages for the different screens in your app. Each page is a place users can visit.',
  icon: 'fas fa-window-maximize',
  count: pages.value.length,
  files: pages.value,
  canCreate: true,
  bgColor: 'bg-violet-500/10',
  borderColor: 'border-white/[0.08]',
  hoverBorderColor: 'hover:border-violet-500/30',
  iconBorderColor: 'border-violet-500/20',
  iconColor: 'text-violet-400',
  textColor: 'text-violet-400',
  glowColor: 'bg-gradient-to-r from-violet-600/10 to-fuchsia-600/10'
}))

const blocksCategory = computed(() => ({
  key: 'blocks',
  label: 'Blocks',
  singularLabel: 'Block',
  description: 'Reusable pieces like headers, cards, forms',
  emptyDescription: 'Create blocks for reusable pieces of your app, like headers, buttons, cards, or forms.',
  icon: 'fas fa-puzzle-piece',
  count: blocks.value.length,
  files: blocks.value,
  canCreate: true,
  bgColor: 'bg-fuchsia-500/10',
  borderColor: 'border-white/[0.08]',
  hoverBorderColor: 'hover:border-fuchsia-500/30',
  iconBorderColor: 'border-fuchsia-500/20',
  iconColor: 'text-fuchsia-400',
  textColor: 'text-fuchsia-400',
  glowColor: 'bg-gradient-to-r from-fuchsia-600/10 to-violet-600/10'
}))

const dataCategory = computed(() => ({
  key: 'data',
  label: 'Data',
  singularLabel: 'Data Store',
  description: 'Information your app remembers',
  emptyDescription: 'Data stores help your app remember information across pages.',
  icon: 'fas fa-database',
  count: stores.value.length,
  files: stores.value,
  canCreate: false,
  bgColor: 'bg-emerald-500/10',
  borderColor: 'border-white/[0.08]',
  hoverBorderColor: 'hover:border-emerald-500/30',
  iconBorderColor: 'border-emerald-500/20',
  iconColor: 'text-emerald-400',
  textColor: 'text-emerald-400',
  glowColor: 'bg-gradient-to-r from-emerald-600/10 to-cyan-600/10'
}))

// Advanced categories (hidden by default)
const advancedCategories = computed(() => {
  const cats = []
  
  if (routers.value.length > 0) {
    cats.push({
      key: 'navigation',
      label: 'Navigation',
      singularLabel: 'Route',
      description: 'How users move between pages',
      emptyDescription: 'Navigation settings control how users move between pages.',
      icon: 'fas fa-route',
      count: routers.value.length,
      files: routers.value,
      canCreate: false,
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-white/[0.08]',
      hoverBorderColor: 'hover:border-cyan-500/30',
      iconBorderColor: 'border-cyan-500/20',
      iconColor: 'text-cyan-400',
      textColor: 'text-cyan-400',
      glowColor: 'bg-gradient-to-r from-cyan-600/10 to-blue-600/10'
    })
  }
  
  if (services.value.length > 0) {
    cats.push({
      key: 'integrations',
      label: 'Integrations',
      singularLabel: 'Integration',
      description: 'Connections to external services',
      emptyDescription: 'Integrations connect your app to external services and APIs.',
      icon: 'fas fa-plug',
      count: services.value.length,
      files: services.value,
      canCreate: false,
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-white/[0.08]',
      hoverBorderColor: 'hover:border-amber-500/30',
      iconBorderColor: 'border-amber-500/20',
      iconColor: 'text-amber-400',
      textColor: 'text-amber-400',
      glowColor: 'bg-gradient-to-r from-amber-600/10 to-orange-600/10'
    })
  }
  
  if (composables.value.length > 0) {
    cats.push({
      key: 'helpers',
      label: 'Helpers',
      singularLabel: 'Helper',
      description: 'Reusable logic and utilities',
      emptyDescription: 'Helpers contain reusable logic that can be shared across your app.',
      icon: 'fas fa-magic',
      count: composables.value.length,
      files: composables.value,
      canCreate: false,
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-white/[0.08]',
      hoverBorderColor: 'hover:border-purple-500/30',
      iconBorderColor: 'border-purple-500/20',
      iconColor: 'text-purple-400',
      textColor: 'text-purple-400',
      glowColor: 'bg-gradient-to-r from-purple-600/10 to-pink-600/10'
    })
  }
  
  if (types.value.length > 0) {
    cats.push({
      key: 'types',
      label: 'Settings',
      singularLabel: 'Setting',
      description: 'Type definitions and configurations',
      emptyDescription: 'Settings and type definitions for your app.',
      icon: 'fas fa-cog',
      count: types.value.length,
      files: types.value,
      canCreate: false,
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-white/[0.08]',
      hoverBorderColor: 'hover:border-blue-500/30',
      iconBorderColor: 'border-blue-500/20',
      iconColor: 'text-blue-400',
      textColor: 'text-blue-400',
      glowColor: 'bg-gradient-to-r from-blue-600/10 to-indigo-600/10'
    })
  }
  
  if (otherFiles.value.length > 0) {
    cats.push({
      key: 'other',
      label: 'Other',
      singularLabel: 'File',
      description: 'Additional files',
      emptyDescription: 'Other files in this app.',
      icon: 'fas fa-folder',
      count: otherFiles.value.length,
      files: otherFiles.value,
      canCreate: false,
      bgColor: 'bg-gray-500/10',
      borderColor: 'border-white/[0.08]',
      hoverBorderColor: 'hover:border-gray-500/30',
      iconBorderColor: 'border-gray-500/20',
      iconColor: 'text-gray-400',
      textColor: 'text-gray-400',
      glowColor: 'bg-gradient-to-r from-gray-600/10 to-slate-600/10'
    })
  }
  
  return cats
})

const hasAdvancedFiles = computed(() => {
  return routers.value.length > 0 || 
         services.value.length > 0 || 
         composables.value.length > 0 || 
         types.value.length > 0 || 
         otherFiles.value.length > 0
})

const advancedFilesCount = computed(() => {
  return routers.value.length + 
         services.value.length + 
         composables.value.length + 
         types.value.length + 
         otherFiles.value.length
})

// Files for the selected category
const selectedCategoryFiles = computed(() => {
  if (!selectedCategory.value) return []
  return selectedCategory.value.files || []
})

// Functions
function selectCategory(category: any) {
  selectedCategory.value = category
  emit('category-change', { key: category.key, label: category.label })
}

function handleBack() {
  if (selectedCategory.value) {
    selectedCategory.value = null
    emit('category-change', null)
  } else {
    emit('back')
  }
}

function handleSelectFile(file: ProjectFile) {
  emit('select-file', file)
}

function handleCreate(categoryKey: string) {
  if (categoryKey === 'pages') {
    handleCreatePage()
  } else if (categoryKey === 'blocks') {
    handleCreateBlock()
  }
}

function handleCreatePage() {
  const appName = props.app.name
  emit('create-file', {
    name: `frontend/vuejs/src/apps/${appName}/views/NewPage.vue`,
    type: 'vue'
  })
}

function handleCreateBlock() {
  const appName = props.app.name
  emit('create-file', {
    name: `frontend/vuejs/src/apps/${appName}/components/NewBlock.vue`,
    type: 'vue'
  })
}

function getDisplayName(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  const filename = parts[parts.length - 1]
  // Remove extension and return friendly name
  return filename.replace(/\.(vue|ts|js|tsx|jsx)$/, '')
}

function getRelativePath(path: string): string {
  if (!path) return ''
  // Remove the redundant parts to show a cleaner path
  const appName = props.app.name
  const regex = new RegExp(`.*\\/apps\\/${appName}\\/`, 'i')
  return path.replace(regex, '')
}

function getFileIcon(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase()
  if (ext === 'vue') return 'fas fa-file-code'
  if (ext === 'ts' || ext === 'js') return 'fas fa-file-code'
  if (ext === 'css' || ext === 'scss') return 'fas fa-palette'
  if (ext === 'html') return 'fas fa-file-code'
  if (ext === 'json') return 'fas fa-file-code'
  if (ext === 'md') return 'fas fa-file-alt'
  return 'fas fa-file'
}
</script>
