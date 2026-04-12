<template>
  <div>
    <!-- Mode Selection Dropdown -->
    <div class="relative" ref="containerEl">
      <!-- Mode Trigger Button -->
      <button
        @click="toggleDropdown"
        class="w-full flex items-center justify-between text-xs bg-gray-50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] text-gray-700 dark:text-white/70 rounded-lg px-3 py-1.5 pr-8 cursor-pointer shadow-sm font-medium hover:bg-gray-100 dark:hover:bg-white/[0.05] hover:border-gray-300 dark:hover:border-white/[0.1] transition-all duration-200"
        :class="{ 'border-gray-300 dark:border-white/[0.12] bg-gray-100 dark:bg-white/[0.05]': isDropdownOpen }"
      >
        <span class="flex items-center gap-2">
          <i class="fas text-[10px]" :class="modeIcon"></i>
          {{ modeLabel }}
        </span>
        <i class="fas fa-chevron-down text-[10px] transition-transform duration-200"
           :class="{ 'rotate-180': isDropdownOpen }"></i>
      </button>
      
      <!-- Portal for dropdown menu (always below) -->
      <Teleport to="body">
        <div 
          v-show="isDropdownOpen"
          class="fixed z-[12000] bg-white dark:bg-[#0c0c12]/98 backdrop-blur-xl border border-gray-200 dark:border-white/[0.08] rounded-xl shadow-2xl shadow-black/20 dark:shadow-black/60 overflow-hidden"
          :style="portalStyle"
          role="listbox"
          aria-label="Select mode"
        >
          <!-- Header -->
          <div class="px-3 py-2 border-b border-gray-200 dark:border-white/[0.06] text-[10px] font-semibold uppercase tracking-wider text-gray-500 dark:text-white/30">
            Mode
          </div>
          
          <div class="py-1">
            <button
              class="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-gray-50 dark:hover:bg-white/[0.05] transition-all duration-200 group"
              :class="{ 'bg-gray-100 dark:bg-white/[0.08] text-gray-900 dark:text-white': modelValue === 'chat' }"
              @click="handleModeSelect('chat')"
              role="option"
              :aria-selected="modelValue === 'chat'"
            >
              <div class="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 bg-gray-100 dark:bg-white/[0.08] text-gray-700 dark:text-white/70">
                <i class="fas fa-comments text-[10px]"></i>
              </div>
              <div class="flex items-center text-left flex-1">
                <span class="text-xs font-medium text-gray-700 dark:text-white/70 group-hover:text-gray-900 dark:group-hover:text-white/90">Chat</span>
              </div>
              <span v-if="modelValue === 'chat'" class="text-gray-700 dark:text-white/70 w-3"><i class="fas fa-check text-[10px]"></i></span>
            </button>
            
            <button
              class="w-full flex items-center gap-2.5 px-3 py-2 hover:bg-gray-50 dark:hover:bg-white/[0.05] transition-all duration-200 group"
              :class="{ 'bg-gray-100 dark:bg-white/[0.08] text-gray-900 dark:text-white': modelValue === 'build' }"
              @click="handleModeSelect('build')"
              role="option"
              :aria-selected="modelValue === 'build'"
            >
              <div class="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 bg-gray-100 dark:bg-white/[0.08] text-gray-700 dark:text-white/70">
                <i class="fas fa-code text-[10px]"></i>
              </div>
              <div class="flex items-center text-left flex-1">
                <span class="text-xs font-medium text-gray-700 dark:text-white/70 group-hover:text-gray-900 dark:group-hover:text-white/90">Agent</span>
              </div>
              <span v-if="modelValue === 'build'" class="text-gray-700 dark:text-white/70 w-3"><i class="fas fa-check text-[10px]"></i></span>
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
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import type { BuilderMode } from '../../../types/components'

const props = defineProps<{
  modelValue: BuilderMode
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: BuilderMode): void
}>()

// Local state
const isDropdownOpen = ref(false)
const containerEl = ref<HTMLElement | null>(null)
const portalStyle = ref<Record<string, string>>({})

// Computed properties
const modeLabel = computed(() => {
  return props.modelValue === 'chat' ? 'Chat' : 'Agent'
})

const modeIcon = computed(() => {
  return props.modelValue === 'chat' ? 'fa-comments' : 'fa-code'
})

// Methods
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}

const closeDropdown = () => {
  isDropdownOpen.value = false
}

const handleModeSelect = (mode: BuilderMode) => {
  emit('update:modelValue', mode)
  closeDropdown()
}

const computeDropdownPlacement = () => {
  const el = containerEl.value
  if (!el) return
  
  const rect = el.getBoundingClientRect()
  const left = Math.round(rect.left)
  const width = Math.max(200, Math.round(rect.width))
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
</script>

<style scoped>
/* Smooth transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
