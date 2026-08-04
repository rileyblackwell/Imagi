import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Tracks whether the viewport is below the workspace's mobile breakpoint.
 *
 * This lived in shared/composables and returned width, height, isMobile,
 * isTablet and isDesktop. It had one consumer — the build workspace — which
 * destructured `isMobile` and nothing else, so the other four refs updated on
 * every resize for no reader. If a second app needs breakpoints, promote this
 * back with the returns that caller actually uses.
 */
export function useIsMobile(breakpoint = 768) {
  const isMobile = ref(window.innerWidth < breakpoint)

  const update = () => {
    isMobile.value = window.innerWidth < breakpoint
  }

  onMounted(() => window.addEventListener('resize', update))
  onUnmounted(() => window.removeEventListener('resize', update))

  return { isMobile }
}
