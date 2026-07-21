<!--
  SellModal.vue - Simple centered modal used across the sell views.
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
        class="relative w-full max-h-[88vh] overflow-y-auto crisp-card rounded-2xl bg-white dark:bg-[#141418] border border-blue-200/70 dark:border-blue-300/[0.14] p-6"
        :class="wide ? 'max-w-2xl' : 'max-w-lg'"
        role="dialog"
        aria-modal="true"
      >
        <div class="flex items-start justify-between gap-4 mb-5">
          <h3 class="text-lg font-semibold text-blue-950 dark:text-white transition-colors duration-300">{{ title }}</h3>
          <button
            type="button"
            class="w-8 h-8 -mt-1 -mr-1 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-blue-100/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#141418]"
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
defineProps<{
  title: string
  wide?: boolean
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>

<style scoped>
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
