import { ref } from 'vue'

// One settings panel per workspace, opened from either pane's header. Module
// scope so the pane that opens it and the view that hosts it share the flag
// without threading an event through the layout.
const open = ref(false)

export function useWorkspaceSettings() {
  return {
    open,
    openSettings: () => { open.value = true },
    closeSettings: () => { open.value = false },
  }
}
