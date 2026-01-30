<template>
  <div>
    <!-- Model Selection Dropdown -->
    <div class="relative" ref="containerEl">
      <!-- Model Trigger Button -->
      <button
        @click="toggleDropdown"
        class="w-full flex items-center justify-between text-xs bg-gray-50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] text-gray-700 dark:text-white/70 rounded-lg px-3 py-1.5 pr-8 cursor-pointer shadow-sm font-medium hover:bg-gray-100 dark:hover:bg-white/[0.05] hover:border-gray-300 dark:hover:border-white/[0.1] transition-all duration-200"
        :class="{ 'border-gray-300 dark:border-white/[0.12] bg-gray-100 dark:bg-white/[0.05]': isDropdownOpen }"
      >
        <span v-if="selectedModel" class="truncate">{{ selectedModel.name }}</span>
        <span v-else class="text-gray-500 dark:text-white/40">Select model</span>
        <i class="fas fa-chevron-down text-[10px] transition-transform duration-200 ml-auto"
           :class="{ 'rotate-180': isDropdownOpen }"></i>
      </button>
      
      <!-- Portal for dropdown menu (always below) -->
      <Teleport to="body">
        <div 
          v-show="isDropdownOpen"
          class="fixed z-[12000] bg-white dark:bg-[#0c0c12]/98 backdrop-blur-xl border border-gray-200 dark:border-white/[0.08] rounded-xl shadow-2xl shadow-black/20 dark:shadow-black/60 overflow-hidden min-w-[240px]"
          :style="portalStyle"
          role="listbox"
          aria-label="Select model"
        >
          <!-- Header -->
          <div class="px-3 py-2 border-b border-gray-200 dark:border-white/[0.06] text-[10px] font-semibold uppercase tracking-wider text-gray-500 dark:text-white/30">
            Models
          </div>
          
          <div class="overflow-y-auto py-1" style="max-height: 300px;">
            <button
              v-for="model in displayModels"
              :key="model.id"
              class="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-gray-50 dark:hover:bg-white/[0.05] transition-all duration-200 group"
              :class="{ 'bg-gray-100 dark:bg-white/[0.08] text-gray-900 dark:text-white': modelId === model.id }"
              @click="handleModelSelect(model.id)"
              role="option"
              :aria-selected="modelId === model.id"
            >
              <!-- Model Icon -->
              <div 
                class="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0"
                :class="getModelTypeClass(model)"
              >
                <i class="fas text-[10px]" :class="getModelTypeIcon(model)"></i>
              </div>
              
              <!-- Model Info -->
              <div class="flex items-center text-left flex-1 min-w-0">
                <span class="text-xs font-medium truncate"
                  :class="modelId === model.id ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-white/70 group-hover:text-gray-900 dark:group-hover:text-white/90'">
                  {{ model.name }}
                </span>
              </div>
              
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-[10px] font-medium px-1.5 py-0.5 rounded bg-violet-100 dark:bg-violet-500/10 border border-violet-200 dark:border-violet-500/20 whitespace-nowrap text-violet-700 dark:text-violet-300/80">
                  ${{ formatPrice(model.costPerRequest) }}
                </span>
                <span v-if="modelId === model.id" class="text-gray-700 dark:text-white/70 w-3"><i class="fas fa-check text-[10px]"></i></span>
              </div>
            </button>
          </div>
        </div>
      </Teleport>
      
      <!-- Overlay to close dropdown -->
      <Teleport to="body">
        <div
          v-if="isDropdownOpen"
          class="fixed inset-0 z-[11999]"
          @click="closeDropdown"
        ></div>
      </Teleport>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { ModelsService } from '../../../services/modelsService'
import { AI_MODELS } from '../../../types/services'
import type { AIModel } from '../../../types/services'
import { getModelTypeIcon, getModelTypeClass } from '@/apps/products/imagi/utils/modelIconUtils'

const props = defineProps<{
  modelId: string | null
  models: AIModel[]
  mode: 'chat' | 'build'
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

// Local state
const isDropdownOpen = ref(false)
const defaultModels = ref<AIModel[]>(AI_MODELS)
const containerEl = ref<HTMLElement | null>(null)
const portalStyle = ref<Record<string, string>>({})

// Methods
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleModelSelect = async (modelId: string) => {
  try {
    // Validate the model exists
    const modelExists = displayModels.value.some(m => m.id === modelId) || 
                       defaultModels.value.some(m => m.id === modelId)
    
    if (!modelExists) {
      throw new Error(`Model ${modelId} not found in available models`)
    }
    
    // Emit the update event
    emit('update:modelId', modelId)
    closeDropdown()
  } catch (err) {
    console.error('Error selecting model', err)
  }
}

const formatPrice = (price: number | undefined): string => {
  if (price === undefined || price === null) return '0.00'
  return price >= 0.01 ? price.toFixed(2) : price.toFixed(3)
}

const computeDropdownPlacement = () => {
  const el = containerEl.value
  if (!el) return
  
  const rect = el.getBoundingClientRect()
  const left = Math.round(rect.left)
  const width = Math.max(240, Math.round(rect.width))
  const triggerTop = rect.bottom + 8
  
  portalStyle.value = {
    top: `${triggerTop}px`,
    left: `${left}px`,
    width: `${width}px`,
  }
}

// Watch for dropdown open/close
watch(isDropdownOpen, (open) => {
  if (open) {
    computeDropdownPlacement()
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

// Computed properties
const availableModels = computed(() => {
  const filtered = props.models.filter(model => {
    if (props.mode === 'build') {
      return ModelsService.canGenerateCode(model)
    }
    return true
  })
  
  return filtered.length > 0 ? filtered : defaultModels.value
})

const displayModels = computed(() => {
  return availableModels.value.filter(model => {
    if (props.mode === 'build') {
      return ModelsService.canGenerateCode(model)
    }
    return true
  })
})

const selectedModel = computed(() => {
  if (!props.modelId) return null
  
  const model = displayModels.value.find(m => m.id === props.modelId)
  if (model) return model
  
  const defaultModel = defaultModels.value.find(m => m.id === props.modelId)
  return defaultModel || null
})
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.12) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 3px;
  transition: background 0.2s ease;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
