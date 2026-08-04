import { computed, onMounted, ref, watch, type Ref } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { useProjectStore } from '@/apps/imagi/build/stores/projectStore'
import { findProjectBySlug } from '@/apps/imagi/build/utils/slug'
import type { Project } from '@/apps/imagi/build/types/components'

/**
 * Resolve the project a workspace is showing, from the `:projectName` slug.
 *
 * The project hub and all three tool workspaces open the same way: make sure
 * the project list is loaded, then find the one whose slug matches the URL.
 * That loader was written out four times, identical apart from the string in
 * its console.error.
 *
 * Returns the resolved project (null while loading, or if the slug matches
 * nothing) and a loading flag that covers both the store's fetch and the first
 * resolution — so a view can tell "still looking" from "no such project".
 */
export function useProjectFromSlug(projectName: Ref<string> | (() => string), label: string) {
  const authStore = useAuthStore()
  const projectStore = useProjectStore()

  const slug = computed(() => (typeof projectName === 'function' ? projectName() : projectName.value))
  const isInitializing = ref(true)

  const isLoading = computed(() => projectStore.loading || isInitializing.value)
  const project = computed<Project | null>(
    () => findProjectBySlug(projectStore.projects, slug.value) || null
  )

  async function load() {
    isInitializing.value = true
    try {
      if (!authStore.isAuthenticated) return
      if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
        projectStore.setAuthenticated(authStore.isAuthenticated)
      }
      if (!projectStore.projects.length) {
        await projectStore.fetchProjects()
      }
    } catch (error) {
      console.error(`Failed to load project for ${label}:`, error)
    } finally {
      isInitializing.value = false
    }
  }

  onMounted(load)
  watch(slug, load)

  return { project, isLoading, reload: load }
}
