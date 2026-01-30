<template>
  <div class="h-full flex flex-col bg-transparent overflow-hidden transition-colors duration-300">
    <!-- Header -->
    <div class="px-6 py-5 border-b border-gray-200 dark:border-white/[0.08] transition-colors duration-300">
      <div class="flex items-center gap-4 mb-4">
        <!-- Back button only shows when in a category view -->
        <button
          v-if="selectedCategory"
          @click="handleBack"
          class="w-10 h-10 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex items-center justify-center text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white"
        >
          <i class="fas fa-arrow-left"></i>
        </button>
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
        <div class="flex-1 min-w-0">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white/90 truncate transition-colors duration-300">{{ app.displayName }}</h2>
          <p class="text-sm text-gray-600 dark:text-white/60 mt-1 transition-colors duration-300">
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
          class="w-10 h-10 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex items-center justify-center text-gray-600 dark:text-white/60 hover:text-gray-900 dark:hover:text-white"
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
          <h3 class="text-sm font-medium text-gray-600 dark:text-white/60 uppercase tracking-wider mb-4 transition-colors duration-300">What's in this app</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Pages Card -->
            <div
              @click="selectCategory(pagesCategory)"
              class="group relative cursor-pointer"
            >
              <div class="relative p-6 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex flex-col">
                <!-- Icon -->
                <div class="flex items-start justify-between mb-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05]">
                    <i class="fas fa-window-maximize text-xl text-gray-700 dark:text-white/70"></i>
                  </div>
                </div>
                
                <!-- Category info -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white/90 mb-1 transition-colors duration-300">Pages</h3>
                  <p class="text-xs text-gray-600 dark:text-white/60 transition-colors duration-300">Screens people visit in your app</p>
                </div>
                
                <!-- Footer -->
                <div class="flex items-center justify-end mt-4 pt-4 border-t border-gray-200 dark:border-white/[0.06] transition-colors duration-300">
                  <i class="fas fa-arrow-right text-sm transition-all duration-300 group-hover:translate-x-1 text-gray-700 dark:text-white/70"></i>
                </div>
              </div>
            </div>

            <!-- Blocks Card -->
            <div
              @click="selectCategory(blocksCategory)"
              class="group relative cursor-pointer"
            >
              <div class="relative p-6 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex flex-col">
                <!-- Icon -->
                <div class="flex items-start justify-between mb-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05]">
                    <i class="fas fa-puzzle-piece text-xl text-gray-700 dark:text-white/70"></i>
                  </div>
                </div>
                
                <!-- Category info -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white/90 mb-1 transition-colors duration-300">Blocks</h3>
                  <p class="text-xs text-gray-600 dark:text-white/60 transition-colors duration-300">Reusable pieces like headers, cards, forms</p>
                </div>
                
                <!-- Footer -->
                <div class="flex items-center justify-end mt-4 pt-4 border-t border-gray-200 dark:border-white/[0.06] transition-colors duration-300">
                  <i class="fas fa-arrow-right text-sm transition-all duration-300 group-hover:translate-x-1 text-gray-700 dark:text-white/70"></i>
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
              <div :class="[
                'relative p-6 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] shadow-sm transition-all duration-300 flex flex-col',
                dataCategory.count > 0 ? 'hover:bg-gray-50 dark:hover:bg-white/[0.06] hover:shadow-md' : ''
              ]">
                <!-- Icon -->
                <div class="flex items-start justify-between mb-4">
                  <div class="w-14 h-14 rounded-xl flex items-center justify-center border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05]">
                    <i class="fas fa-database text-xl text-gray-700 dark:text-white/70"></i>
                  </div>
                </div>
                
                <!-- Category info -->
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white/90 mb-1 transition-colors duration-300">Data</h3>
                  <p class="text-xs text-gray-600 dark:text-white/60 transition-colors duration-300">Information your app remembers</p>
                </div>
                
                <!-- Footer -->
                <div class="flex items-center justify-end mt-4 pt-4 border-t border-gray-200 dark:border-white/[0.06] transition-colors duration-300">
                  <i v-if="dataCategory.count > 0" class="fas fa-arrow-right text-sm transition-all duration-300 group-hover:translate-x-1 text-gray-700 dark:text-white/70"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Advanced Section (collapsed by default) -->
        <div v-if="hasAdvancedFiles" class="mt-8">
          <button
            @click="showAdvanced = !showAdvanced"
            class="flex items-center gap-2 text-sm font-medium text-gray-500 dark:text-white/40 hover:text-gray-700 dark:hover:text-white/60 transition-colors duration-300 mb-4"
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
              <div class="relative p-4 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex items-center gap-3">
                <div :class="[
                  'w-10 h-10 rounded-lg flex items-center justify-center border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05] flex-shrink-0'
                ]">
                  <i :class="[category.icon, 'text-gray-700 dark:text-white/70', 'text-sm']"></i>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-900 dark:text-white/90 truncate transition-colors duration-300">{{ category.label }}</div>
                </div>
                <i class="fas fa-chevron-right text-xs text-gray-500 dark:text-white/40 group-hover:text-gray-700 dark:group-hover:text-white/60 transition-colors duration-300"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty state when no files at all -->
        <div v-if="pagesCategory.count === 0 && blocksCategory.count === 0 && dataCategory.count === 0 && !hasAdvancedFiles" class="flex flex-col items-center justify-center py-20">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 dark:bg-white/[0.05] border border-gray-200 dark:border-white/[0.08] mb-4 transition-colors duration-300">
            <i class="fas fa-folder-open text-gray-700 dark:text-white/70 text-2xl"></i>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white/90 mb-2 transition-colors duration-300">Start building {{ app.displayName }}</h3>
          <p class="text-gray-600 dark:text-white/60 text-center max-w-md mb-6 transition-colors duration-300">Create pages for screens people will visit, or blocks for reusable pieces.</p>
          <div class="flex gap-3">
            <button
              @click="handleCreatePage"
              class="relative px-6 py-3 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <span class="flex items-center gap-2 text-sm font-semibold">
                <i class="fas fa-window-maximize text-xs"></i>
                <span>New Page</span>
              </span>
            </button>
            <button
              @click="handleCreateBlock"
              class="relative px-6 py-3 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 shadow-lg hover:shadow-xl transition-all duration-300"
            >
              <span class="flex items-center gap-2 text-sm font-semibold">
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
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white/90 transition-colors duration-300">
            {{ selectedCategory.label }} in {{ app.displayName }}
          </h3>
          <button
            v-if="selectedCategory.canCreate"
            @click="handleCreate(selectedCategory.key)"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 text-sm text-gray-700 dark:text-white/70 hover:text-gray-900 dark:hover:text-white"
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
            <div class="relative p-4 rounded-lg border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] shadow-sm hover:shadow-md transition-all duration-300 flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05]">
                <i :class="[getFileIcon(file.path), 'text-gray-700 dark:text-white/70', 'text-sm']"></i>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 dark:text-white/90 truncate transition-colors duration-300">{{ getDisplayName(file.path) }}</div>
                <div class="text-xs text-gray-600 dark:text-white/50 truncate transition-colors duration-300">{{ getRelativePath(file.path) }}</div>
              </div>
              <i class="fas fa-chevron-right text-xs text-gray-500 dark:text-white/40 group-hover:text-gray-700 dark:group-hover:text-white/60 transition-colors duration-300"></i>
            </div>
          </div>
        </div>

        <!-- Empty state for category -->
        <div v-if="selectedCategoryFiles.length === 0" class="flex flex-col items-center justify-center py-20">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl border border-gray-200 dark:border-white/[0.08] bg-gray-100 dark:bg-white/[0.05] mb-4 transition-colors duration-300">
            <i :class="[selectedCategory.icon, 'text-gray-700 dark:text-white/70', 'text-2xl']"></i>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white/90 mb-2 transition-colors duration-300">No {{ selectedCategory.label.toLowerCase() }} yet</h3>
          <p class="text-gray-600 dark:text-white/60 text-center max-w-md mb-6 transition-colors duration-300">
            {{ selectedCategory.emptyDescription }}
          </p>
          <button
            v-if="selectedCategory.canCreate"
            @click="handleCreate(selectedCategory.key)"
            class="relative px-6 py-3 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <span class="flex items-center gap-2 text-sm font-semibold">
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

// Primary categories (always visible) - Using consistent grayscale design
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
  bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
  borderColor: 'border-gray-200 dark:border-white/[0.08]',
  hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
  iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
  iconColor: 'text-gray-700 dark:text-white/70',
  textColor: 'text-gray-700 dark:text-white/70',
  glowColor: ''
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
  bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
  borderColor: 'border-gray-200 dark:border-white/[0.08]',
  hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
  iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
  iconColor: 'text-gray-700 dark:text-white/70',
  textColor: 'text-gray-700 dark:text-white/70',
  glowColor: ''
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
  bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
  borderColor: 'border-gray-200 dark:border-white/[0.08]',
  hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
  iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
  iconColor: 'text-gray-700 dark:text-white/70',
  textColor: 'text-gray-700 dark:text-white/70',
  glowColor: ''
}))

// Advanced categories (hidden by default) - Using consistent grayscale design
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
      bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
      borderColor: 'border-gray-200 dark:border-white/[0.08]',
      hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
      iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
      iconColor: 'text-gray-700 dark:text-white/70',
      textColor: 'text-gray-700 dark:text-white/70',
      glowColor: ''
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
      bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
      borderColor: 'border-gray-200 dark:border-white/[0.08]',
      hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
      iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
      iconColor: 'text-gray-700 dark:text-white/70',
      textColor: 'text-gray-700 dark:text-white/70',
      glowColor: ''
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
      bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
      borderColor: 'border-gray-200 dark:border-white/[0.08]',
      hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
      iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
      iconColor: 'text-gray-700 dark:text-white/70',
      textColor: 'text-gray-700 dark:text-white/70',
      glowColor: ''
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
      bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
      borderColor: 'border-gray-200 dark:border-white/[0.08]',
      hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
      iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
      iconColor: 'text-gray-700 dark:text-white/70',
      textColor: 'text-gray-700 dark:text-white/70',
      glowColor: ''
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
      bgColor: 'bg-gray-100 dark:bg-white/[0.05]',
      borderColor: 'border-gray-200 dark:border-white/[0.08]',
      hoverBorderColor: 'hover:border-gray-300 dark:hover:border-white/[0.12]',
      iconBorderColor: 'border-gray-200 dark:border-white/[0.08]',
      iconColor: 'text-gray-700 dark:text-white/70',
      textColor: 'text-gray-700 dark:text-white/70',
      glowColor: ''
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
