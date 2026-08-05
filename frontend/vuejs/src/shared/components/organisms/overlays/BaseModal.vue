<!--
  BaseModal.vue — the one centred modal.

  MarketingModal, OperateModal and SellModal were the same 64-line file three
  times over, down to the comment. The only difference between them was the
  dark panel colour (#16161a in two, #141418 in the third), which nobody chose
  — it drifted. That colour is now `--app-paper-raised` from tokens.css.

  Escape closes it, which none of the three originals did.
-->
<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      <!-- Overlay -->
      <div
        class="absolute inset-0 bg-blue-950/40 dark:bg-black/60 backdrop-blur-sm"
        @click="$emit('close')"
      ></div>

      <!-- Panel -->
      <div
        class="relative w-full max-h-[88vh] overflow-y-auto crisp-card rounded-2xl bg-paper-raised border border-blue-200/70 dark:border-blue-300/[0.16] p-6"
        :class="wide ? 'max-w-2xl' : 'max-w-lg'"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
      >
        <div class="flex items-start justify-between gap-4 mb-5">
          <h3 class="text-lg font-semibold text-blue-950 dark:text-white transition-colors duration-300">
            {{ title }}
          </h3>
          <button
            type="button"
            class="w-8 h-8 -mt-1 -mr-1"
            :class="ui.iconBtn"
            aria-label="Close"
            @click="$emit('close')"
          >
            <i class="fas fa-xmark"></i>
          </button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { ui } from '@/shared/styles'

defineProps<{
  title: string
  /** Widen the panel for forms with two columns of fields. */
  wide?: boolean
}>()

const emit = defineEmits<{ (e: 'close'): void }>()

// Escape closes the dialog. Every one of the three originals left this out, so
// a modal opened by mistake could only be dismissed with the mouse.
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => document.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>
