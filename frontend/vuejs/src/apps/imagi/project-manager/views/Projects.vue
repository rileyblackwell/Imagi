<!--
  Projects.vue — the projects list.

  This component is responsible for:
  1. Creating new projects
  2. Deleting existing projects
  3. Listing all user projects
  4. Navigating to the project hub

  It should NOT be responsible for:
  - Project file editing (handled by the build workspace)

  Design: the editorial surface the rest of the site wears — paper and ink,
  hairline rules, one accent. The page is a header and two ruled columns:
  starting a business on the left, the ones you already have on the right.
  Everything visual comes from shared/styles/editorial.css.
-->
<template>
  <div>
    <!-- Confirm Modal (uses Teleport to body) -->
    <ConfirmModal
      :is-open="confirmModal.isModalOpen.value"
      :options="confirmModal.modalOptions.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />

    <DefaultLayout>
      <div class="editorial projects-page relative min-h-screen font-body">
        <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

        <main class="relative z-10">

          <!-- Opening statement -->
          <section class="relative pt-32 sm:pt-40 md:pt-44 pb-4">
            <div class="section-shell">
              <div class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
                <div class="rise-item max-w-[36rem]">
                  <p class="eyebrow">
                    <span class="eyebrow__rule" aria-hidden="true"></span>
                    <span>Your workspace</span>
                  </p>
                  <h1 class="display mt-7 text-[2.75rem] sm:text-6xl md:text-[3.9rem]">
                    Projects
                  </h1>
                </div>
                <p class="rise-item lede mt-7 md:mt-0 md:max-w-sm md:pb-3 text-lg" style="animation-delay: 90ms">
                  Every business you run on Imagi lives in a project &mdash; its app and the tools
                  behind it. Start a new one, or pick up where you left off.
                </p>
              </div>
            </div>
          </section>

          <!-- Signed out -->
          <section v-if="showAuthError" class="relative py-20 md:py-28">
            <div class="section-shell">
              <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>
              <div class="rise-item max-w-xl" style="animation-delay: 90ms">
                <p class="eyebrow">
                  <span class="eyebrow__mark" aria-hidden="true"></span>
                  <span class="eyebrow__rule" aria-hidden="true"></span>
                  <span>Signed out</span>
                </p>
                <h2 class="display mt-6 text-4xl sm:text-5xl">Sign in to see your projects</h2>
                <p class="lede mt-6 text-lg">
                  Your projects are tied to your account. Sign in to open them, or to start a new one.
                </p>
                <router-link to="/auth/signin" class="btn-primary group mt-9">
                  <span>Sign in</span>
                  <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </router-link>
              </div>
            </div>
          </section>

          <!-- Start one / continue one -->
          <section v-else class="relative pt-16 md:pt-20 pb-20 md:pb-28">
            <div class="section-shell">
              <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

              <div class="rule-cols rule-cols--2">

                <!-- 01 — Create -->
                <div class="rule-col rise-item" style="animation-delay: 90ms">
                  <p class="eyebrow">
                    <span class="eyebrow__num">01</span>
                    <span class="eyebrow__rule" aria-hidden="true"></span>
                    <span>New business</span>
                  </p>
                  <h2 class="display mt-6 text-3xl sm:text-4xl">Start a project</h2>
                  <p class="lede mt-5">
                    Describe the business. Imagi's agent writes the first version of its web app
                    from what you say here, so the more it knows the closer the first draft lands.
                  </p>

                  <form class="mt-10 grid gap-8" @submit.prevent="createProject">
                    <div class="field">
                      <label class="field__label" for="project-name">Business name</label>
                      <input
                        id="project-name"
                        v-model="newProjectName"
                        type="text"
                        class="field__input disabled:opacity-50 disabled:cursor-not-allowed"
                        placeholder="Ticker Insights"
                        :disabled="isCreating"
                      >
                    </div>

                    <div class="field">
                      <label class="field__label" for="project-description">What the business does</label>
                      <p class="field__hint">
                        What it sells, who its customers are, and how it reaches them.
                      </p>
                      <textarea
                        id="project-description"
                        v-model="newProjectDescription"
                        rows="5"
                        class="field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                        placeholder="A stock tracker for retail investors — portfolio snapshots with AI-written summaries, sold as a monthly subscription."
                        :disabled="isCreating"
                      ></textarea>
                    </div>

                    <div class="field">
                      <label class="field__label" for="project-design">
                        Design direction
                        <span class="field__optional">Optional</span>
                      </label>
                      <p class="field__hint">
                        Colours, mood, references. Leave it blank and Imagi picks a look that fits.
                      </p>
                      <textarea
                        id="project-design"
                        v-model="newProjectDesign"
                        rows="2"
                        class="field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                        placeholder="Warm and minimal, earthy palette, lots of whitespace."
                        :disabled="isCreating"
                      ></textarea>
                    </div>

                    <button
                      type="submit"
                      class="btn-primary group w-full"
                      :disabled="!canCreate || isCreating"
                    >
                      <template v-if="isCreating">
                        <span class="spinner" aria-hidden="true"></span>
                        <span>Creating&hellip;</span>
                      </template>
                      <template v-else>
                        <span>Create project</span>
                        <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </template>
                    </button>
                  </form>
                </div>

                <!-- 02 — Library -->
                <div class="rule-col rise-item" style="animation-delay: 180ms">
                  <div class="flex items-center justify-between gap-4">
                    <p class="eyebrow">
                      <span class="eyebrow__num">02</span>
                      <span class="eyebrow__rule" aria-hidden="true"></span>
                      <span>Your projects</span>
                    </p>
                    <span v-if="!isLoading && !error && displayedProjects.length > 0" class="count">
                      {{ searchQuery ? `${displayedProjects.length} found` : `${projects?.length || 0} total` }}
                    </span>
                  </div>

                  <h2 class="display mt-6 text-3xl sm:text-4xl">Pick up where you left off</h2>
                  <p class="lede mt-5">
                    Open a project to keep building its app &mdash; or to market, sell and run
                    the business around it.
                  </p>

                  <!-- Search. Nothing to search until there is something in the
                       list, and an empty field over an empty list is just a
                       second hairline saying nothing. -->
                  <div v-if="projects?.length" class="search mt-10">
                    <svg class="search__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <circle cx="11" cy="11" r="7" />
                      <path d="m20 20-3.5-3.5" />
                    </svg>
                    <label class="sr-only" for="project-search">Search projects</label>
                    <input
                      id="project-search"
                      v-model="searchQuery"
                      type="search"
                      class="field__input search__input"
                      placeholder="Search projects"
                    >
                  </div>

                  <!--
                    Deletion result, anchored in the library rather than a
                    bottom-right toast, so the confirmation reads as part of the
                    list the project was removed from.
                  -->
                  <Transition
                    enter-active-class="transition-all duration-300 ease-out"
                    enter-from-class="opacity-0 -translate-y-1"
                    enter-to-class="opacity-100 translate-y-0"
                    leave-active-class="transition-all duration-200 ease-in"
                    leave-from-class="opacity-100 translate-y-0"
                    leave-to-class="opacity-0 -translate-y-1"
                  >
                    <div
                      v-if="deleteBanner"
                      :key="deleteBanner.id"
                      role="status"
                      aria-live="polite"
                      class="notice"
                      :class="{ 'notice--alert': deleteBanner.type === 'error' }"
                    >
                      <span class="flex-1">{{ deleteBanner.message }}</span>
                      <button
                        type="button"
                        class="notice__dismiss"
                        aria-label="Dismiss notification"
                        @click="dismissDeleteBanner"
                      >
                        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" aria-hidden="true">
                          <path d="M18 6 6 18M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </Transition>

                  <!-- Loading -->
                  <p v-if="isLoading" class="state">
                    <span class="spinner spinner--ink" aria-hidden="true"></span>
                    <span>Loading your projects&hellip;</span>
                  </p>

                  <!-- Error -->
                  <div v-else-if="error" class="state state--block">
                    <p class="state__message">{{ error }}</p>
                    <button type="button" class="btn-outline mt-6" @click="retryFetch">Try again</button>
                  </div>

                  <!-- No search results -->
                  <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="state state--block">
                    <p class="state__message">No project matches &ldquo;{{ searchQuery }}&rdquo;.</p>
                  </div>

                  <!--
                    Empty state, keyed off what's actually shown rather than the
                    raw store list, so deleting the last project surfaces this
                    immediately instead of leaving a blank column.
                  -->
                  <div v-else-if="!displayedProjects.length" class="state state--block">
                    <p class="state__message">
                      No projects yet. Describe a business on the left and Imagi builds the first
                      version of its app.
                    </p>
                  </div>

                  <!-- The list -->
                  <ul v-else class="project-list">
                    <li v-for="project in displayedProjects" :key="project.id">
                      <ProjectCard :project="project" @delete="confirmDelete" />
                    </li>
                  </ul>
                </div>

              </div>
            </div>
          </section>
        </main>
      </div>
    </DefaultLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onBeforeUnmount, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { DefaultLayout } from '@/shared/layouts'
import { useProjectStore } from '@/apps/imagi/build/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { ProjectCard } from '../components/molecules/cards'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '@/apps/imagi/build/composables/useConfirm'
import { useNotificationStore } from '@/shared/stores/notificationStore'
import { useProjectSearch } from '../composables/useProjectSearch'
import type { Project } from '@/apps/imagi/build/types/components'
import { normalizeProject } from '@/apps/imagi/build/types/components'
import { projectSlug } from '@/apps/imagi/build/utils/slug'
import { ConfirmModal } from '@/apps/imagi/build/components/organisms/modals'


const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()
const confirmModal = useConfirm()
const { confirm } = confirmModal

// State
const newProjectName = ref('')
const newProjectDescription = ref('')
// Optional: extra design/style direction for the initial AI build. Empty is
// fine — the build carries strong default design direction on its own.
const newProjectDesign = ref('')
const isCreating = ref(false)

// The description seeds the initial AI build, so require enough signal to
// work with. Keep in sync with MIN_DESCRIPTION_LENGTH on the backend
// (ProjectManager/api/serializers.py).
const MIN_DESCRIPTION_LENGTH = 20
const canCreate = computed(() =>
  Boolean(newProjectName.value.trim()) &&
  newProjectDescription.value.trim().length >= MIN_DESCRIPTION_LENGTH
)
const isInitializing = ref(true)

// Deletion outcomes surface as an inline notice anchored in the project list
// (see template) rather than a bottom-right toast, so the confirmation reads as
// part of the list the project was removed from.
type DeleteBanner = { type: 'success' | 'error'; message: string; id: number }
const deleteBanner = ref<DeleteBanner | null>(null)
let deleteBannerTimer: ReturnType<typeof setTimeout> | null = null

const showDeleteBanner = (type: DeleteBanner['type'], message: string) => {
  if (deleteBannerTimer) clearTimeout(deleteBannerTimer)
  deleteBanner.value = { type, message, id: Date.now() }
  // Success auto-dismisses; errors stay until dismissed so they aren't missed.
  deleteBannerTimer = type === 'success'
    ? setTimeout(() => { deleteBanner.value = null; deleteBannerTimer = null }, 5000)
    : null
}

const dismissDeleteBanner = () => {
  if (deleteBannerTimer) { clearTimeout(deleteBannerTimer); deleteBannerTimer = null }
  deleteBanner.value = null
}

// Computed
const projects = computed(() => projectStore.projects)
const normalizedProjects = computed<Project[]>(() => {
  if (!projects.value) return [];
  return projects.value.map(project => {
    return normalizeProject(project);
  });
})
const isLoading = computed(() => projectStore.loading || isInitializing.value)
const error = computed(() => projectStore.error || '')
const showAuthError = computed(() => !authStore.isAuthenticated && !isLoading.value)

// Use project search composable
const { searchQuery, filteredProjects } = useProjectSearch(normalizedProjects, { includeDescription: true });

// Compute displayed projects
const displayedProjects = computed<Project[]>(() => {
  const hasSearchQuery = searchQuery.value?.trim().length > 0;

  if (hasSearchQuery) {
    return (filteredProjects.value || []).filter(project => project && project.id);
  }

  if (!normalizedProjects.value?.length) {
    return [];
  }

  return [...normalizedProjects.value]
    .filter(project => project && project.id)
    .sort((a, b) => {
      if (!a.updated_at) return 1;
      if (!b.updated_at) return -1;

      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    });
});

/**
 * Create a new project
 */
async function createProject() {
  if (!authStore.isAuthenticated) {
    showNotification({
      message: 'Please log in to create projects',
      type: 'error'
    })
    return
  }

  // Validate business name
  if (!newProjectName.value.trim()) {
    showNotification({
      message: 'Business name cannot be empty',
      type: 'error'
    })
    return
  }

  // Validate business description — it seeds the initial AI build
  if (newProjectDescription.value.trim().length < MIN_DESCRIPTION_LENGTH) {
    showNotification({
      message: 'Please describe your business — what it does, who its customers are, and how it will sell. Imagi uses this to build the first version of your app.',
      type: 'error'
    })
    return
  }

  isCreating.value = true

  try {
    // Create a properly formatted project data object with name and description
    const projectData = {
      name: newProjectName.value.trim(),
      description: newProjectDescription.value.trim(), // Use the description value
      design_preferences: newProjectDesign.value.trim() // Optional design direction
    }

    const newProject = await projectStore.createProject(projectData)

    // Clear the create form after successful creation
    newProjectName.value = ''
    newProjectDescription.value = ''
    newProjectDesign.value = ''

    // Log project information to debug any ID issues
    console.debug('Created project details:', {
      project: newProject,
      id: newProject.id,
      idType: typeof newProject.id
    })

    // Navigate immediately to the project hub for the newly created project
    router.push({
      name: 'project-hub',
      params: { projectName: projectSlug(newProject) }
    })

  } catch (error: any) {
    showNotification({
      message: error?.message || 'Failed to create project',
      type: 'error'
    })
  } finally {
    isCreating.value = false
  }
}

/**
 * Load/reload the projects list
 * This is the ONLY place that should handle loading the list of all projects
 */
const fetchProjects = async (force = false) => {
  if (!authStore.isAuthenticated) {
    isInitializing.value = false
    return
  }

  try {
    // First, ensure project store auth state is synchronized
    if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
      projectStore.setAuthenticated(authStore.isAuthenticated)
    }

    await projectStore.fetchProjects(force)

  } catch (error: any) {
    console.error('Error fetching projects:', error)
    showNotification({
      message: error?.message || 'Failed to load projects',
      type: 'error'
    })
  } finally {
    isInitializing.value = false
  }
}

/**
 * Retry fetching projects if there was an error
 */
const retryFetch = () => {
  projectStore.clearError()
  fetchProjects(true) // Force refresh when retrying
}

/**
 * Confirm and delete a project
 * This is the ONLY place in the application that should call projectStore.deleteProject
 */
const confirmDelete = async (project: Project) => {
  if (!authStore.isAuthenticated) {
    showNotification({
      message: 'Please log in to delete projects',
      type: 'error'
    })
    return
  }

  // Use confirm dialog
  const confirmed = await confirm({
    title: 'Delete Project',
    message: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })

  if (!confirmed) {
    return
  }

  // Capture the project name before deletion to ensure we have it for the notification
  const projectName = project.name || `Project ${project.id}` || 'Unknown Project'

  // Check if user is currently in the workspace for this project
  const isCurrentlyInWorkspace = router.currentRoute.value.name === 'builder-workspace' &&
                                 router.currentRoute.value.params.projectName === projectSlug(project)

  try {
    // The store owns the delete: it optimistically removes the project from the
    // list, records the deletion tombstone, clears the cache, and treats a 404
    // from the server as success. Because the list updates optimistically, the
    // UI reflects the deletion the moment this resolves — the remaining projects
    // (or the "No projects yet" empty state) render immediately without waiting
    // on a forced refetch that could hang or race and leave the panel spinning.
    await projectStore.deleteProject(String(project.id))

    // Confirm the deletion right away, independent of any background refresh.
    showDeleteBanner('success', `"${projectName}" deleted successfully`)

    // If the user was in the workspace for this project, navigate away from it.
    if (isCurrentlyInWorkspace) {
      await router.push({ name: 'projects' })
    }
  } catch (error: any) {
    console.error('Error deleting project:', error)

    // A real failure (the store already treats 404 as success). The optimistic
    // removal leaves the project missing from the list, so reconcile with the
    // server to bring it back, then report the error.
    showDeleteBanner('error', error?.message || `Failed to delete "${projectName}"`)

    try {
      await fetchProjects(true)
    } catch (refreshError) {
      console.warn('Failed to refresh projects after failed deletion:', refreshError)
    }
  }
}

// Set up watchers and lifecycle hooks
onMounted(async () => {
  console.debug('Projects mounted')

  // Always force refresh projects when the dashboard loads to ensure we have the latest data
  try {
    console.debug('Forcing refresh of projects on dashboard load')
    // Force refresh to always get the latest projects from API
    await fetchProjects(true)
  } catch (error) {
    console.error('Initial project fetch failed:', error)

    // Wait a moment and try again if authentication is confirmed
    if (authStore.isAuthenticated) {
      setTimeout(async () => {
        try {
          console.debug('Retrying project fetch after initial failure')
          await fetchProjects(true) // Force on retry after failure
        } catch (retryError) {
          console.error('Retry fetch also failed:', retryError)
        }
      }, 2000)
    }
  }
})

// Add support for keep-alive to refresh when component is re-activated
onActivated(async () => {
  console.debug('Projects activated - refreshing projects from API')
  if (authStore.isAuthenticated) {
    // Always force refresh projects when the component is activated (tab switch, navigation back, etc.)
    try {
      await fetchProjects(true) // Always force refresh to get latest state from API
    } catch (error) {
      console.error('Failed to refresh projects on activation:', error)
    }
  }
})

// Clean up resources when leaving the dashboard
onBeforeUnmount(() => {
  // Clear dashboard-specific notifications when leaving
  const notificationStore = useNotificationStore()
  notificationStore.clear()
  // Drop any pending deletion-banner auto-dismiss timer.
  if (deleteBannerTimer) clearTimeout(deleteBannerTimer)
})
</script>

<style scoped>
/* Quiet the native search field's own decorations — the browser's clear button
   is a grey chip that has nothing to do with this page. */
input {
  -webkit-appearance: none;
  appearance: none;
}

input[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}

/* Grid items default to `min-width: auto`, so the truncated project names —
   which never wrap — would set the library column's minimum width and squeeze
   the form beside it down to a third of the measure. */
.rule-col {
  min-width: 0;
}

/* The project count, sitting opposite the eyebrow it annotates. */
.count {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-40);
  white-space: nowrap;
}

/* --- Search ---------------------------------------------------------------
   The editorial field, with room made for a mark in the underline. */

.search {
  position: relative;
}

.search__icon {
  position: absolute;
  left: 0;
  top: 0.85rem;
  width: 1rem;
  height: 1rem;
  color: var(--ink-40);
  pointer-events: none;
}

/* Two selectors so this beats `.editorial .field__input`'s padding. */
.search .search__input {
  padding-left: 1.6rem;
}

/* --- Notice ---------------------------------------------------------------
   Deletion feedback. A hairline strip rather than a tinted box: quiet for the
   expected outcome, accented when something actually went wrong. */

.notice {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding: 0.75rem 0 0.75rem 1rem;
  border-left: 2px solid var(--rule-strong);
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--ink-70);
}

.notice--alert {
  border-left-color: var(--accent);
  color: var(--ink);
}

.notice__dismiss {
  flex: none;
  margin-top: 0.1rem;
  color: var(--ink-40);
  transition: color 0.18s ease;
}

.notice__dismiss:hover {
  color: var(--ink);
}

/* --- States --------------------------------------------------------------- */

.state {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-top: 2.5rem;
  font-size: 0.9375rem;
  color: var(--ink-55);
}

/* The column has to hold its shape whether it is showing eight projects or a
   sentence explaining why it is showing none. */
.state--block {
  display: block;
  padding-top: 2.5rem;
  border-top: 1px solid var(--rule);
}

.state__message {
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--ink-55);
  text-wrap: pretty;
}

.spinner {
  flex: none;
  width: 1rem;
  height: 1rem;
  border: 1.5px solid currentColor;
  border-top-color: transparent;
  border-radius: 999px;
  opacity: 0.6;
  animation: spin 0.8s linear infinite;
}

.spinner--ink {
  color: var(--accent);
  opacity: 1;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }
}

/* --- The list -------------------------------------------------------------
   Ruled rows, not floating cards: the library reads as one list of businesses,
   which is what it is. */

.project-list {
  /* No rule of its own at the top: the search field's underline sits right
     above it and is already the line that opens the list. */
  margin-top: 1.75rem;
  list-style: none;
  padding-left: 0;
  max-height: 30rem;
  overflow-y: auto;
}
</style>
