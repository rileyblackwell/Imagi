<!--
  SidebarToggle — the canonical show/hide control for the global sidebar.

  Lives in the top bar (never inside the panel) so it can never disappear with
  the sidebar it controls. Draws a "panel" glyph: an app frame with a hinged
  left column that fills in when the sidebar is open, so the icon reads as a
  live picture of the current state rather than a generic hamburger.
-->
<template>
  <button
    type="button"
    class="sidebar-toggle group inline-flex items-center justify-center w-9 h-9 rounded-lg text-blue-950/55 dark:text-blue-100/55 hover:text-blue-950 dark:hover:text-white hover:bg-blue-950/[0.05] dark:hover:bg-white/[0.07] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
    :aria-pressed="open"
    :aria-label="open ? 'Hide sidebar' : 'Show sidebar'"
    :title="open ? 'Hide sidebar' : 'Show sidebar'"
    @click="$emit('toggle')"
  >
    <svg
      viewBox="0 0 24 24"
      fill="none"
      class="w-[18px] h-[18px]"
      aria-hidden="true"
    >
      <!-- App frame -->
      <rect
        x="3"
        y="4.5"
        width="18"
        height="15"
        rx="3.2"
        stroke="currentColor"
        stroke-width="1.6"
      />
      <!-- Sidebar column divider -->
      <line
        x1="9.5"
        y1="4.5"
        x2="9.5"
        y2="19.5"
        stroke="currentColor"
        stroke-width="1.6"
      />
      <!-- Filled column: present only when the sidebar is open, so the glyph
           mirrors the actual state. A short fade keeps the swap from popping. -->
      <path
        d="M6.2 4.5H7.3a2.2 2.2 0 0 1 2.2 2.2v10.6A2.2 2.2 0 0 1 7.3 19.5H6.2A3.2 3.2 0 0 1 3 16.3V7.7A3.2 3.2 0 0 1 6.2 4.5Z"
        fill="currentColor"
        class="toggle-fill"
        :class="open ? 'opacity-100' : 'opacity-0'"
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>()
defineEmits<{ (e: 'toggle'): void }>()
</script>

<style scoped>
.sidebar-toggle {
  -webkit-tap-highlight-color: transparent;
}

.toggle-fill {
  transition: opacity 0.22s cubic-bezier(0.22, 1, 0.36, 1);
}
</style>
