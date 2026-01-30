import { useAgentStore } from '../stores/agentStore'
import type { NavigationGuard } from 'vue-router'

export const builderGuard: NavigationGuard = async (to, from, next) => {
  const store = useAgentStore()

  // Check if leaving builder workspace
  if (from.name === 'builder' && to.name !== 'builder') {
    if (store.unsavedChanges) {
      const confirmed = window.confirm('You have unsaved changes. Leave anyway?')
      if (!confirmed) {
        return next(false)
      }
      // Reset store state when confirmed
      store.$reset()
    }
  }

  next()
}