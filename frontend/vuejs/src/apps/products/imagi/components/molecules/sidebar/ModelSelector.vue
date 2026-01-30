<template>
  <div>
    <!-- Debug info (hidden in production) -->
    <div v-if="false" class="mb-2 p-2 bg-dark-800 rounded text-xs text-gray-400">
      Models: {{ models.length }}, Available: {{ availableModels.length }}
    </div>
    
    <!-- Modern Model Selection Dropdown -->
    <div class="relative" ref="containerEl">
      <!-- Compact Mode Trigger Button -->
      <button
        v-if="props.compact"
        @click="toggleDropdown"
        class="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg border transition-all duration-200 bg-white/[0.03] backdrop-blur-sm border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.1] group"
        :class="{ 'border-violet-500/30 bg-violet-500/5': isDropdownOpen }"
      >
        <div v-if="selectedModel" class="flex items-center gap-2 flex-1 min-w-0 overflow-hidden">
          <!-- Compact Model Icon -->
          <div 
            class="w-6 h-6 rounded-md flex items-center justify-center shrink-0"
            :class="[getModelTypeClass(selectedModel)]"
          >
            <i class="fas text-[10px]" :class="getModelTypeIcon(selectedModel)"></i>
          </div>
          
          <!-- Compact Model Info -->
          <div class="flex items-center gap-2 flex-1 min-w-0 overflow-hidden">
            <span class="text-xs font-medium text-white/70 truncate">{{ selectedModel.name }}</span>
            <span class="text-[10px] font-medium px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300/80 shrink-0 whitespace-nowrap">${{ formatPrice(selectedModel.costPerRequest) }}</span>
          </div>
        </div>
        <div v-else class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-md bg-white/[0.05] flex items-center justify-center text-white/30">
            <i class="fas fa-robot text-[10px]"></i>
          </div>
          <span class="text-xs text-white/40">Select model</span>
        </div>
        
        <!-- Compact Dropdown Arrow -->
        <i class="fas fa-chevron-down text-[8px] text-white/30 transition-transform duration-200 ml-1 shrink-0"
           :class="{ 'rotate-180 text-violet-400': isDropdownOpen }"></i>
      </button>
      
      <!-- Regular Mode Trigger Button -->
      <button
        v-else
        @click="toggleDropdown"
        class="w-full flex items-center justify-between p-2.5 rounded-lg border transition-all duration-200 bg-white/[0.03] backdrop-blur-sm border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.1] group"
        :class="{ 'border-violet-500/30 bg-violet-500/5': isDropdownOpen }"
      >
        <div v-if="selectedModel" class="relative flex items-center gap-2.5 flex-1 min-w-0 overflow-hidden">
          <!-- Selected Model Icon - compact -->
          <div 
            class="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
            :class="[getModelTypeClass(selectedModel)]"
          >
            <i class="fas text-xs" :class="getModelTypeIcon(selectedModel)"></i>
          </div>
          
          <!-- Selected Model Info - compact -->
          <div class="flex items-center gap-2.5 text-left flex-1 min-w-0 overflow-hidden">
            <span class="text-sm font-medium text-white/70 group-hover:text-white/90 transition-colors truncate">{{ selectedModel.name }}</span>
            <span class="text-[10px] font-medium px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300/80 border border-violet-500/20 shrink-0 whitespace-nowrap">${{ formatPrice(selectedModel.costPerRequest) }}</span>
          </div>
        </div>
        <div v-else class="relative flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-md bg-white/[0.05] flex items-center justify-center text-white/30 border border-white/[0.08]">
            <i class="fas fa-robot text-xs"></i>
          </div>
          <span class="text-sm text-white/40">Select model</span>
        </div>
        
        <!-- Dropdown Arrow with animation -->
        <i class="fas fa-chevron-down text-[10px] text-white/30 transition-transform duration-200 relative ml-1 shrink-0"
           :class="{ 'rotate-180 text-violet-400': isDropdownOpen }"></i>
      </button>
      
      <!-- Dropdown Menu positioned like the mode selector (default, always below). Disabled because we use portal for fixed positioning. -->
      <div 
        v-show="false && isDropdownOpen && !usePortal" 
        class="absolute z-[11000] w-full min-w-[280px] mt-2 bg-[#0c0c12]/98 backdrop-blur-xl border border-white/[0.08] rounded-xl shadow-2xl shadow-black/60 overflow-hidden"
        role="listbox"
        aria-label="Select model"
        :style="dropdownInlineStyle"
      >
        <!-- Compact header -->
        <div class="px-3 py-2 border-b border-white/[0.06] text-[10px] font-semibold uppercase tracking-wider text-white/30">
          Models
        </div>
        
        <div class="overflow-y-auto py-1" :style="{ maxHeight: scrollMaxHeight }">
          <button
            v-for="model in displayModels"
            :key="model.id"
            class="w-full flex items-center gap-2 px-3 py-2 hover:bg-white/[0.05] transition-all duration-200 group relative"
            :class="{ 'bg-violet-500/15 text-violet-300': modelId === model.id }"
            @click="handleModelSelect(model.id)"
            role="option"
            :aria-selected="modelId === model.id"
          >
            <!-- Model Icon - compact -->
            <div 
              class="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0"
              :class="[getModelTypeClass(model)]"
            >
              <i class="fas text-[10px]" :class="getModelTypeIcon(model)"></i>
            </div>
            
            <!-- Model Info - no truncation -->
            <div class="flex items-center text-left flex-1">
              <span class="text-xs font-medium transition-colors whitespace-nowrap"
                :class="modelId === model.id ? 'text-violet-300' : 'text-white/70 group-hover:text-white/90'">
                {{ model.name }}
              </span>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0">
              <span class="text-[10px] font-medium px-1.5 py-0.5 rounded bg-violet-500/10 border border-violet-500/20 whitespace-nowrap"
                :class="modelId === model.id ? 'text-violet-300' : 'text-violet-300/80'">
                ${{ formatPrice(model.costPerRequest) }}
              </span>
              <span v-if="modelId === model.id" class="text-violet-400 w-3"><i class="fas fa-check text-[10px]"></i></span>
            </div>
          </button>
        </div>
      </div>

      <!-- Overlay to close dropdown when clicking outside -->
      <div
        v-if="false && isDropdownOpen && !usePortal"
        class="fixed inset-0 z-[10999]"
        @click="closeDropdown"
      ></div>

      <!-- Portal fallback to avoid clipping by parent or footer (always below) -->
      <Teleport to="body">
        <div 
          v-show="isDropdownOpen && usePortal"
          class="fixed z-[12000] bg-[#0c0c12]/98 backdrop-blur-xl border border-white/[0.08] rounded-xl shadow-2xl shadow-black/60 overflow-hidden min-w-[280px]"
          :style="portalStyle"
          role="listbox"
          aria-label="Select model"
        >
          <!-- Compact header -->
          <div class="px-3 py-2 border-b border-white/[0.06] text-[10px] font-semibold uppercase tracking-wider text-white/30">
            Models
          </div>
          
          <div class="overflow-y-auto py-1" :style="{ maxHeight: scrollMaxHeight }">
            <button
              v-for="model in displayModels"
              :key="model.id"
              class="w-full flex items-center gap-2 px-3 py-2 hover:bg-white/[0.05] transition-all duration-200 group relative"
              :class="{ 'bg-violet-500/15 text-violet-300': modelId === model.id }"
              @click="handleModelSelect(model.id)"
              role="option"
              :aria-selected="modelId === model.id"
            >
              <!-- Model Icon - compact -->
              <div 
                class="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0"
                :class="[getModelTypeClass(model)]"
              >
                <i class="fas text-[10px]" :class="getModelTypeIcon(model)"></i>
              </div>
              
              <!-- Model Info - no truncation -->
              <div class="flex items-center text-left flex-1">
                <span class="text-xs font-medium transition-colors whitespace-nowrap"
                  :class="modelId === model.id ? 'text-violet-300' : 'text-white/70 group-hover:text-white/90'">
                  {{ model.name }}
                </span>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-[10px] font-medium px-1.5 py-0.5 rounded bg-violet-500/10 border border-violet-500/20 whitespace-nowrap"
                  :class="modelId === model.id ? 'text-violet-300' : 'text-violet-300/80'">
                  ${{ formatPrice(model.costPerRequest) }}
                </span>
                <span v-if="modelId === model.id" class="text-violet-400 w-3"><i class="fas fa-check text-[10px]"></i></span>
              </div>
            </button>
          </div>
        </div>
      </Teleport>
      <Teleport to="body">
        <div
          v-if="isDropdownOpen && usePortal"
          class="fixed inset-0 z-[11999]"
          @click="closeDropdown"
        ></div>
      </Teleport>
    </div>
    
    <!-- No Models Available Message with improved styling -->
    <div v-if="displayModels.length === 0" class="mt-2 p-3 bg-white/[0.03] backdrop-blur-sm rounded-lg text-center text-white/40 text-xs border border-white/[0.06]">
      <i class="fas fa-exclamation-circle mr-1 text-white/30 text-[10px]"></i>
      No AI models available
    </div>

    <!-- Model Details with enhanced styling -->
    <TransitionGroup 
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div 
        v-if="rateLimitWarning"
        class="mt-2 p-2.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-400 text-[11px] backdrop-blur-sm"
        :key="'warning'"
      >
        <i class="fas fa-exclamation-triangle mr-1 text-[10px]"></i>
        {{ rateLimitWarning }}
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { ModelsService } from '../../../services/modelsService'
import { AI_MODELS } from '../../../types/services'
import type { AIModel } from '../../../types/services'

const props = defineProps<{
  modelId: string | null
  models: AIModel[]
  mode: 'chat' | 'build'
  compact?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

// Local state
const rateLimitWarning = ref<string | null>(null)
const isDropdownOpen = ref(false)
const defaultModels = ref<AIModel[]>(AI_MODELS)
const isLoadingModels = ref(false)

// Dropdown dynamic placement within container (always below)
const containerEl = ref<HTMLElement | null>(null)
const dropdownInlineStyle = ref<Record<string, string>>({})
const usePortal = ref(false)
const portalStyle = ref<Record<string, string>>({})

const computeDropdownPlacement = () => {
  const el = containerEl.value
  if (!el) return
  const rect = el.getBoundingClientRect()
  // Always use portal so dropdown is fixed while page scrolls
  usePortal.value = true
  const left = Math.round(rect.left)
  const width = Math.max(280, Math.round(rect.width)) // Ensure minimum width of 280px
  const triggerTop = rect.bottom + 8
  // Available space below the trigger within viewport
  const availBelow = Math.max(140, window.innerHeight - triggerTop - 8)
  const maxH = Math.min(480, availBelow)
  dropdownInlineStyle.value = { top: 'calc(100% + 8px)', bottom: 'auto', maxHeight: `${maxH}px` }
  portalStyle.value = {
    top: `${Math.min(window.innerHeight - 8, triggerTop)}px`,
    left: `${left}px`,
    width: `${width}px`,
    maxHeight: `${maxH}px`
  }
}

// Max height for inner scroll container, derived from computed placement styles
const scrollMaxHeight = computed(() => {
  return portalStyle.value.maxHeight || dropdownInlineStyle.value.maxHeight || '240px'
})

// Methods - defined before they're used in watchers
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleModelSelect = async (modelId: string) => {
  try {
    // Validate the model exists in either available models or default models
    const modelExists = displayModels.value.some(m => m.id === modelId) || 
                       defaultModels.value.some(m => m.id === modelId)
    
    if (!modelExists) {
      throw new Error(`Model ${modelId} not found in available models`)
    }
    
    // Check rate limit before allowing selection
    await ModelsService.checkRateLimit(modelId)
    rateLimitWarning.value = null
    
    // Emit the update event
    emit('update:modelId', modelId)
    
    // Force a DOM update to ensure the change is reflected
    setTimeout(() => {
      // Use window instead of document for event dispatching
      const event = new CustomEvent('model-changed', { 
        detail: modelId,
        bubbles: true,
        cancelable: true
      })
      window.dispatchEvent(event)
    }, 50)
    
    isDropdownOpen.value = false // Close dropdown after selection
  } catch (err) {
    console.error('Error selecting model', err)
    rateLimitWarning.value = err instanceof Error ? err.message : 'Error selecting model'
  }
}

// Utility functions are now imported from utils/modelIconUtils.ts
import { getModelTypeIcon, getModelTypeClass } from '@/apps/products/imagi/utils/modelIconUtils'


// Format price for display
const formatPrice = (price: number | undefined): string => {
  if (price === undefined || price === null) return '0.00';
  return price >= 0.01 ? price.toFixed(2) : price.toFixed(3);
}

// Fetch models from API on mount
const fetchModels = async () => {
  isLoadingModels.value = true
  try {
    const apiModels = await ModelsService.getAvailableModels()
    if (apiModels && apiModels.length > 0) {
      defaultModels.value = apiModels
    }
  } catch (err) {
    console.error('Error fetching models:', err)
    // Keep using the default models
  } finally {
    isLoadingModels.value = false
  }
}

onMounted(() => {
  // Fetch available models from API
  fetchModels()
})

// Watch for changes in models prop
watch(() => props.models, (newModels) => {
  // Models changed
}, { immediate: true })

// Recompute placement when dropdown opens/closes and on viewport changes
watch(isDropdownOpen, (open) => {
  if (open) {
    // Compute immediately
    computeDropdownPlacement()
    // Listen to scroll/resize while open
    window.addEventListener('scroll', computeDropdownPlacement, true)
    window.addEventListener('resize', computeDropdownPlacement)
  } else {
    window.removeEventListener('scroll', computeDropdownPlacement, true)
    window.removeEventListener('resize', computeDropdownPlacement)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', computeDropdownPlacement, true)
  window.removeEventListener('resize', computeDropdownPlacement)
})

const availableModels = computed(() => {
  // Ensure we're filtering and displaying all available models
  const filtered = props.models.filter(model => {
    // For build mode, only show models that can generate code
    if (props.mode === 'build') {
      return ModelsService.canGenerateCode(model)
    }
    // For chat mode, show all models
    return true
  })
  
  // If no models from props, use default models
  return filtered.length > 0 ? filtered : defaultModels.value
})

// Filter models based on mode
const displayModels = computed(() => {
  return availableModels.value.filter(model => {
    if (props.mode === 'build') {
      return ModelsService.canGenerateCode(model)
    }
    return true
  })
})

// Selected model
const selectedModel = computed(() => {
  if (!props.modelId) return null
  
  // First try to find the model in the available models
  const model = displayModels.value.find(m => m.id === props.modelId)
  if (model) return model
  
  // If not found, check in the default models
  const defaultModel = defaultModels.value.find(m => m.id === props.modelId)
  return defaultModel || null
})
</script>

<style scoped>
/* Custom scrollbar for dropdown - matching builder design */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
