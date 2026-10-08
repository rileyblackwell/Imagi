<!--
  Projects.vue — the projects list.

  This component is responsible for:
  1. Creating new projects
  2. Deleting existing projects
  3. Listing all user projects
  4. Navigating to the project hub

  It should NOT be responsible for:
  - Project file editing (handled by the build workspace)

  Design: "Brief" on the Spotlight stage. Starting an app is four numbered
  steps on a lit rail (name it, what the app is, what it does, set the look),
  written for people who are not technical. Picking a kind of app in step 2
  tailors what step 3 asks, and step 4 is a starter design system (see
  utils/projectBrief.ts and components/molecules/brief/StarterDesign.vue), with a card beside them
  showing the brief the agent will receive and the button that sends it. The
  copy is app-first: the business tools are mentioned as what the same project
  offers once someone wants to turn the app into a business. The projects you
  already have follow as a numbered list. The editorial
  markup is re-lit by the bridge in shared/styles/spotlight.css.
-->
<template>
  <div class="spotlight projects-root">
    <!-- Confirm Modal (uses Teleport to body) -->
    <ConfirmModal
      :is-open="confirmModal.isModalOpen.value"
      :options="confirmModal.modalOptions.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />

    <DefaultLayout>
      <div class="editorial projects-page relative min-h-screen">
        <main class="relative">

          <!-- Opening statement -->
          <section class="sl-opener projects-opener">
            <div class="sl-spot projects-spot" aria-hidden="true"></div>
            <div class="sl-dots" aria-hidden="true"></div>
            <div class="sl-wrap projects-opener__inner">
              <p class="rise-item sl-eyebrow sl-pill">
                <span class="sl-pip" aria-hidden="true"></span>
                <span>Your workspace</span>
              </p>
              <h1 v-if="showAuthError" class="rise-item sl-display projects-title" style="animation-delay: 60ms">
                Projects
              </h1>
              <h1 v-else class="rise-item sl-display projects-title" style="animation-delay: 60ms">
                Brief the agent on a <span class="sl-grad-text">new app</span>
              </h1>
              <p class="rise-item sl-lede" style="animation-delay: 120ms">
                <template v-if="showAuthError">
                  Every app you build on Imagi lives in a project, along with the tools to turn it
                  into a business when you want to.
                </template>
                <template v-else>
                  Answer a few questions in your own words and Imagi builds the first version of
                  your app. If you want it to become a business, the same project has the tools to
                  sell, market and run it. Your projects are further down.
                </template>
              </p>
            </div>
          </section>

          <!-- Signed out -->
          <section v-if="showAuthError" class="relative pb-20 md:pb-28">
            <div class="sl-wrap">
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

          <template v-else>
            <!-- The brief: three steps on a rail, and what the agent will get -->
            <section class="relative brief-section">
              <div class="sl-wrap brief-cols">

                <form id="create-project" class="steps rise-item" style="animation-delay: 90ms" @submit.prevent="createProject">
                  <!-- 01 — Name it -->
                  <div class="step" :class="stepClass(1)">
                    <span class="step__node" aria-hidden="true">
                      <svg v-if="nameDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                      <template v-else>01</template>
                    </span>
                    <label class="step__title" for="project-name">Name it</label>
                    <p class="step__hint">The name of your app. You can change it later.</p>
                    <input
                      id="project-name"
                      ref="projectNameInput"
                      v-model="newProjectName"
                      type="text"
                      class="field__input step__name disabled:opacity-50 disabled:cursor-not-allowed"
                      placeholder="Ticker Insights"
                      :disabled="isCreating"
                      @focus="focusedStep = 1"
                      @blur="focusedStep = null"
                    >
                  </div>

                  <!-- 02 — What the app is. Picking a kind is the form's one
                       branch: it changes what step 3 asks. -->
                  <div class="step" :class="stepClass(2)">
                    <span class="step__node" aria-hidden="true">
                      <svg v-if="descriptionDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                      <template v-else>02</template>
                    </span>
                    <label class="step__title" for="project-description">What is your app?</label>
                    <p id="project-description-hint" class="step__hint">
                      A sentence or two: what it is and who it&rsquo;s for. Pick the closest kind if one fits.
                    </p>
                    <div class="starters" role="group" aria-label="Kind of app">
                      <button
                        v-for="kind in APP_KINDS"
                        :key="kind.id"
                        type="button"
                        class="starter"
                        :class="{ 'is-on': appKind === kind.id }"
                        :aria-pressed="appKind === kind.id"
                        :disabled="isCreating"
                        @click="toggleKind(kind.id)"
                      >
                        {{ kind.label }}
                      </button>
                    </div>
                    <div class="lit-field">
                      <textarea
                        id="project-description"
                        v-model="newProjectDescription"
                        rows="3"
                        class="lit-field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                        placeholder="A stock tracker for retail investors. Later I'd like to sell it as a monthly subscription."
                        aria-describedby="project-description-hint project-description-meter"
                        :disabled="isCreating"
                        @focus="focusedStep = 2"
                        @blur="focusedStep = null"
                      ></textarea>
                    </div>
                    <div class="meter" :class="{ 'meter--done': descriptionDone }">
                      <span class="meter__track" aria-hidden="true">
                        <span class="meter__fill" :style="{ transform: `scaleX(${descriptionProgress})` }"></span>
                      </span>
                      <span id="project-description-meter" class="meter__label" aria-live="polite">
                        <svg v-if="descriptionDone" class="meter__check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        {{ descriptionMeterLabel }}
                      </span>
                    </div>
                  </div>

                  <!-- 03 — What the app does. Required: it is the spec the
                       first build plans every page from. Its questions follow
                       the kind picked in step 2. -->
                  <div class="step" :class="stepClass(3)">
                    <span class="step__node" aria-hidden="true">
                      <svg v-if="detailsDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                      <template v-else>03</template>
                    </span>
                    <label class="step__title" for="project-details">What does it do?</label>
                    <p id="project-details-hint" class="step__hint">
                      {{ activeKind.hint }} Imagi turns this into the plan for your app.
                    </p>
                    <div class="starters" role="group" aria-label="Sentence starters">
                      <button
                        v-for="starter in activeKind.starters"
                        :key="starter"
                        type="button"
                        class="starter"
                        :disabled="isCreating"
                        @click="addStarter(starter)"
                      >
                        <span aria-hidden="true">+</span> {{ starter }}&hellip;
                      </button>
                    </div>
                    <div class="lit-field">
                      <textarea
                        id="project-details"
                        ref="projectDetailsInput"
                        v-model="newProjectDetails"
                        rows="4"
                        class="lit-field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                        :placeholder="activeKind.example"
                        aria-describedby="project-details-hint project-details-meter"
                        :disabled="isCreating"
                        @focus="focusedStep = 3"
                        @blur="focusedStep = null"
                      ></textarea>
                    </div>
                    <div class="meter" :class="{ 'meter--done': detailsDone }">
                      <span class="meter__track" aria-hidden="true">
                        <span class="meter__fill" :style="{ transform: `scaleX(${detailsProgress})` }"></span>
                      </span>
                      <span id="project-details-meter" class="meter__label" aria-live="polite">
                        <svg v-if="detailsDone" class="meter__check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        {{ detailsMeterLabel }}
                      </span>
                    </div>
                  </div>

                  <!-- 04 — The starter design: the app's first design system -->
                  <div class="step step--last" :class="stepClass(4)">
                    <span class="step__node" aria-hidden="true">
                      <svg v-if="designDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                      <template v-else>04</template>
                    </span>
                    <p class="step__title">
                      Set the look
                      <span class="step__optional">Optional</span>
                    </p>
                    <p class="step__hint">
                      Your app&rsquo;s starter design. Tap what fits, add your own words, or skip it and
                      Imagi picks a look.
                    </p>
                    <StarterDesign
                      v-model="newProjectDesign"
                      :app-name="newProjectName.trim()"
                      :disabled="isCreating"
                      @focus="focusedStep = 4"
                      @blur="focusedStep = null"
                    />
                  </div>
                </form>

                <!-- What the agent receives, and the button that sends it -->
                <aside class="brief rise-item" style="animation-delay: 160ms" aria-label="Project brief">
                  <div class="brief__card">
                    <p class="brief__head">
                      <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.5c.5 4.6 2.4 6.9 7 7.5-4.6.6-6.5 2.9-7 7.5-.5-4.6-2.4-6.9-7-7.5 4.6-.6 6.5-2.9 7-7.5Z" /></svg>
                      <span>What the agent receives</span>
                    </p>
                    <div class="brief__body">
                      <p class="brief__name" :class="{ 'is-empty': !nameDone }">
                        {{ newProjectName.trim() || 'Your app' }}
                      </p>
                      <p class="brief__desc" :class="{ 'is-empty': !newProjectDescription.trim() }">
                        {{ newProjectDescription.trim() || 'What your app does shows up here as you describe it.' }}
                      </p>
                      <dl class="brief__facts">
                        <template v-if="appKind && appKind !== GENERIC_KIND.id">
                          <dt>Kind</dt>
                          <dd>{{ activeKind.label }}</dd>
                        </template>
                        <dt>What it does</dt>
                        <dd class="brief__clamp" :class="{ 'is-empty': !newProjectDetails.trim() }">{{ newProjectDetails.trim() || 'Shows up here as you describe it' }}</dd>
                        <dt>Look</dt>
                        <dd>{{ designSummary || 'Imagi picks one' }}</dd>
                        <dt>First build</dt>
                        <dd>A web app you can preview</dd>
                        <dt>Business tools</dt>
                        <dd>Sell, Market and Operate, ready when you want them</dd>
                      </dl>
                    </div>
                    <div class="brief__foot">
                      <button
                        type="submit"
                        form="create-project"
                        class="btn-primary group brief__submit"
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
                      <p class="brief__note">You can change everything later in the workspace.</p>
                    </div>
                  </div>
                </aside>

              </div>
            </section>

            <!-- Your projects -->
            <section class="relative library-section">
              <div class="sl-wrap">
                <div class="library-head rise-item" style="animation-delay: 200ms">
                  <div>
                    <p class="count">
                      Your projects<template v-if="!isLoading && !error && displayedProjects.length > 0">
                        &middot; {{ searchQuery ? `${displayedProjects.length} found` : `${projects?.length || 0}` }}
                      </template>
                    </p>
                    <h2 class="display library-title">Pick up where you left off</h2>
                  </div>

                  <!-- Search. Nothing to search until there is something in the
                       list, and an empty field over an empty list is just a
                       second line saying nothing. -->
                  <div v-if="projects?.length" class="search">
                    <svg class="search__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <circle cx="11" cy="11" r="7" />
                      <path d="m20 20-3.5-3.5" />
                    </svg>
                    <label class="sr-only" for="project-search">Search projects</label>
                    <input
                      id="project-search"
                      v-model="searchQuery"
                      type="search"
                      class="search__input"
                      placeholder="Search projects"
                    >
                  </div>
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
                  immediately instead of leaving an empty section.
                -->
                <div v-else-if="!displayedProjects.length" class="state state--block">
                  <p class="state__message">
                    No projects yet. Describe an app above and Imagi builds the first version of
                    it.
                  </p>
                </div>

                <!-- The list -->
                <ol v-else class="project-list">
                  <li v-for="(project, i) in displayedProjects" :key="project.id">
                    <ProjectCard :project="project" :index="i + 1" @delete="confirmDelete" />
                  </li>
                </ol>
              </div>
            </section>
          </template>
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
import { takePendingIdea } from '@/apps/home/utils/pendingIdea'
import StarterDesign from '../components/molecules/brief/StarterDesign.vue'
import {
  APP_KINDS,
  GENERIC_KIND,
  kindById,
  emptyDesign,
  designIsSet,
  summarizeDesign,
  composeAppDetails,
  composeDesignPreferences,
  type StarterDesign as StarterDesignValue,
} from '../utils/projectBrief'


const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()
const confirmModal = useConfirm()
const { confirm } = confirmModal

// State
const newProjectName = ref('')
const newProjectDescription = ref('')
// Optional: the starter design (style, colours, fonts, theme, notes). Nothing
// chosen is fine — the build carries strong default design direction.
const newProjectDesign = ref<StarterDesignValue>(emptyDesign())
const designSummary = computed(() => summarizeDesign(newProjectDesign.value))
// Optional: the kind of app. It tailors step 3's questions and leads the
// app_details the build reads.
const appKind = ref<string | null>(null)
const activeKind = computed(() => kindById(appKind.value) ?? GENERIC_KIND)
const toggleKind = (id: string) => { appKind.value = appKind.value === id ? null : id }
// Required: what the app does, in plain words. The initial build reads it as
// the app's functional brief.
const newProjectDetails = ref('')
const projectDetailsInput = ref<HTMLTextAreaElement | null>(null)
const isCreating = ref(false)
const projectNameInput = ref<HTMLInputElement | null>(null)

// The description and what the app does seed the initial AI build, so
// require enough signal to work with. Keep MIN_DESCRIPTION_LENGTH in sync with
// the backend (ProjectManager/api/serializers.py).
const MIN_DESCRIPTION_LENGTH = 20
const MIN_DETAILS_LENGTH = 20
const canCreate = computed(() =>
  Boolean(newProjectName.value.trim()) &&
  newProjectDescription.value.trim().length >= MIN_DESCRIPTION_LENGTH &&
  newProjectDetails.value.trim().length >= MIN_DETAILS_LENGTH
)

// The brief's four steps. A step is done once its answer is enough to build
// from; the current one is the field being typed in, or else the first that
// still needs an answer.
const nameDone = computed(() => Boolean(newProjectName.value.trim()))
const descriptionLength = computed(() => newProjectDescription.value.trim().length)
const descriptionDone = computed(() => descriptionLength.value >= MIN_DESCRIPTION_LENGTH)
const detailsLength = computed(() => newProjectDetails.value.trim().length)
const detailsDone = computed(() => detailsLength.value >= MIN_DETAILS_LENGTH)
const designDone = computed(() => designIsSet(newProjectDesign.value))
type Step = 1 | 2 | 3 | 4
const focusedStep = ref<Step | null>(null)
const currentStep = computed(() =>
  focusedStep.value ?? (!nameDone.value ? 1 : !descriptionDone.value ? 2 : !detailsDone.value ? 3 : 4)
)
const stepDone = { 1: nameDone, 2: descriptionDone, 3: detailsDone, 4: designDone } as const
const stepClass = (step: Step) => ({
  'is-done': stepDone[step].value,
  'is-current': currentStep.value === step,
})
const descriptionProgress = computed(() =>
  Math.min(1, descriptionLength.value / MIN_DESCRIPTION_LENGTH)
)
const meterLabel = (length: number, min: number) => {
  if (length >= min) return 'Enough to start'
  if (!length) return `At least ${min} characters`
  const left = min - length
  return `${left} more character${left === 1 ? '' : 's'}`
}
const descriptionMeterLabel = computed(() => meterLabel(descriptionLength.value, MIN_DESCRIPTION_LENGTH))
const detailsProgress = computed(() => Math.min(1, detailsLength.value / MIN_DETAILS_LENGTH))
const detailsMeterLabel = computed(() => meterLabel(detailsLength.value, MIN_DETAILS_LENGTH))

// Sentence starters for "What does it do?" (they follow the kind of app).
// Most founders have never written a spec; a first few words gets them past
// the empty box.
const addStarter = (starter: string) => {
  const text = newProjectDetails.value.replace(/\s+$/, '')
  const sep = !text ? '' : /[.!?]$/.test(text) ? ' ' : '. '
  newProjectDetails.value = `${text}${sep}${starter} `
  requestAnimationFrame(() => {
    const el = projectDetailsInput.value
    if (!el) return
    el.focus()
    el.setSelectionRange(el.value.length, el.value.length)
  })
}

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

  // Validate app name
  if (!newProjectName.value.trim()) {
    showNotification({
      message: 'App name cannot be empty',
      type: 'error'
    })
    return
  }

  // Validate app description — it seeds the initial AI build
  if (newProjectDescription.value.trim().length < MIN_DESCRIPTION_LENGTH) {
    showNotification({
      message: 'Please say what your app is and who it\'s for. Imagi uses this to build the first version.',
      type: 'error'
    })
    return
  }

  // Validate what the app does — the first build plans its pages from it
  if (newProjectDetails.value.trim().length < MIN_DETAILS_LENGTH) {
    showNotification({
      message: 'Please say what your app does — what people can do on it and what it keeps track of.',
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
      app_details: composeAppDetails(appKind.value, newProjectDetails.value),
      design_preferences: composeDesignPreferences(newProjectDesign.value), // Optional
    }

    const newProject = await projectStore.createProject(projectData)

    // Clear the create form after successful creation
    newProjectName.value = ''
    newProjectDescription.value = ''
    newProjectDetails.value = ''
    newProjectDesign.value = emptyDesign()
    appKind.value = null

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

  // An idea typed into the home page's prompt arrives here as the app
  // description; the visitor only has to name it. Signed-out visitors keep it
  // until they come back signed in, since the form only renders for them.
  if (authStore.isAuthenticated) {
    const idea = takePendingIdea()
    if (idea && !newProjectDescription.value) {
      newProjectDescription.value = idea
      requestAnimationFrame(() => projectNameInput.value?.focus())
    }
  }

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

/* --- Opener ---------------------------------------------------------------
   Left-aligned, so the title reads as the first line of the brief below it. */

.sl-opener.projects-opener {
  padding-bottom: clamp(36px, 5vw, 56px);
}

.projects-spot {
  left: 30%;
}

.projects-opener__inner {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 20px;
}

.projects-title {
  font-size: clamp(40px, 6vw, 68px);
  line-height: 1.02;
  letter-spacing: -0.035em;
  max-width: 18ch;
}

@media (min-width: 1024px) {
  .projects-title {
    max-width: none;
  }
}

/* --- Brief ----------------------------------------------------------------
   The steps on the left, the card that sums them up on the right. */

.brief-section {
  padding-bottom: clamp(72px, 9vw, 112px);
}

.brief-cols {
  display: grid;
  gap: 48px;
}

@media (min-width: 1024px) {
  .brief-cols {
    grid-template-columns: minmax(0, 1fr) 380px;
    gap: 56px;
    align-items: start;
  }
}

/* The rail: a line down the left that each step's node sits on. The segment
   below a node lights once that step has its answer. */
.steps {
  display: grid;
  min-width: 0;
}

.step {
  position: relative;
  padding: 0 0 2.25rem 3.5rem;
}

.step::before {
  content: '';
  position: absolute;
  left: 19px;
  top: 2.75rem;
  bottom: 0.25rem;
  width: 2px;
  border-radius: 2px;
  background: var(--sl-line-strong);
  transition: background 0.3s ease;
}

.step.is-done::before {
  background: linear-gradient(180deg, var(--sl-coral), var(--sl-amber));
}

.step--last {
  padding-bottom: 0;
}

.step--last::before {
  display: none;
}

.step__node {
  position: absolute;
  left: 0;
  top: 0;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 999px;
  border: 1.5px solid var(--sl-line-strong);
  background: var(--sl-bg);
  color: var(--sl-faint);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.8rem;
  transition: background 0.25s ease, border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}

.step__node svg {
  width: 17px;
  height: 17px;
}

.step.is-current .step__node {
  border-color: var(--sl-amber);
  color: var(--sl-amber);
  box-shadow: 0 0 0 5px color-mix(in srgb, var(--sl-amber) 14%, transparent), 0 0 24px var(--sl-glow);
}

.step.is-done .step__node {
  border-color: transparent;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
}

.step__title {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  padding-top: 0.35rem;
  font-family: var(--sl-font-display);
  font-size: 1.375rem;
  font-weight: 650;
  letter-spacing: -0.015em;
  color: var(--sl-text);
}

.step__optional {
  font-family: var(--sl-font-body);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-faint);
}

.step__hint {
  margin: 0.25rem 0 0.9rem;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--sl-muted);
}

/* Two selectors so these beat `.editorial .field__input`. */
.step .step__name {
  font-family: var(--sl-font-display);
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  padding: 0.5rem 0 0.75rem;
}

.step .field__input:focus {
  border-bottom-color: var(--sl-amber);
}

/* Sentence starters and moods: small pills that write into the field below,
   so a blank box never has to be faced cold. */
.starters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.starter {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.8rem;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-chip-bg);
  font-size: 0.8125rem;
  color: var(--sl-muted);
  transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}

.starter span {
  color: var(--sl-amber);
  font-weight: 600;
}

.starter:hover:not(:disabled) {
  background: var(--sl-chip-bg-hover);
  border-color: var(--sl-line-strong);
  color: var(--sl-text);
}

.starter:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 2px;
}

.starter.is-on,
.starter.is-on:hover:not(:disabled) {
  border-color: transparent;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
  font-weight: 600;
}

.starter:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* The description gets the home page's glowing prompt sheet: it is the answer
   the first build leans on most. */
.lit-field {
  border: 1px solid transparent;
  border-radius: 1rem;
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-prompt-edge) border-box;
  box-shadow: var(--sl-prompt-shadow);
  transition: box-shadow 0.25s ease;
}

.lit-field:focus-within {
  box-shadow: var(--sl-prompt-shadow-focus);
}

.lit-field__input {
  display: block;
  width: 100%;
  min-height: 8rem;
  padding: 1rem 1.15rem;
  border: 0;
  border-radius: 1rem;
  background: transparent;
  font-size: 1rem;
  line-height: 1.65;
  color: var(--sl-text);
}

.lit-field__input::placeholder {
  color: var(--sl-placeholder);
}

.lit-field__input:focus {
  outline: none;
}

/* How close the description is to enough to build from. */
.meter {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-top: 0.85rem;
}

.meter__track {
  position: relative;
  flex: 1;
  height: 4px;
  border-radius: 4px;
  background: var(--sl-line-strong);
  overflow: hidden;
}

.meter__fill {
  position: absolute;
  inset: 0;
  background: var(--sl-grad);
  transform-origin: left center;
  transition: transform 0.3s ease;
}

.meter__label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--sl-muted);
  white-space: nowrap;
}

.meter--done .meter__label {
  color: var(--sl-ok);
  font-weight: 600;
}

.meter__check {
  width: 0.85rem;
  height: 0.85rem;
}

/* The brief card. It stays in view while the steps are filled in. */
.brief {
  min-width: 0;
}

@media (min-width: 1024px) {
  .brief {
    position: sticky;
    top: 5.5rem;
  }
}

.brief__card {
  border: 1px solid var(--sl-line);
  border-radius: 1.25rem;
  background: var(--sl-card-bg);
  box-shadow: var(--sl-card-shadow);
  overflow: hidden;
}

.brief__head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.9rem 1.25rem;
  border-bottom: 1px solid var(--sl-line);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-faint);
}

.brief__head svg {
  width: 0.85rem;
  height: 0.85rem;
  color: var(--sl-amber);
}

.brief__body {
  padding: 1.25rem 1.4rem 1.35rem;
}

.brief__name {
  font-family: var(--sl-font-display);
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

.brief__desc {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  line-height: 1.6;
  color: var(--sl-muted);
  overflow-wrap: anywhere;
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.brief__name.is-empty,
.brief__desc.is-empty {
  color: var(--sl-faint);
}

.brief__facts {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.5rem 1rem;
  margin-top: 1.1rem;
  font-size: 0.8rem;
}

.brief__facts dt {
  color: var(--sl-faint);
}

.brief__facts dd {
  margin: 0;
  color: var(--sl-text);
  overflow-wrap: anywhere;
}

.brief__facts .brief__clamp {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.brief__foot {
  padding: 1rem 1.25rem 1.1rem;
  border-top: 1px solid var(--sl-line);
}

/* Two selectors so this beats `.editorial .btn-primary`'s padding. */
.brief .brief__submit {
  width: 100%;
  justify-content: center;
  padding: 0.8rem 1.35rem;
  font-size: 0.95rem;
}

.brief__note {
  margin-top: 0.75rem;
  text-align: center;
  font-size: 0.78rem;
  color: var(--sl-faint);
}

/* --- Library -------------------------------------------------------------- */

.library-section {
  padding-bottom: clamp(80px, 10vw, 128px);
}

.library-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.25rem 2rem;
  padding-bottom: 1.1rem;
  border-bottom: 1px solid var(--sl-line-strong);
}

.library-title {
  margin-top: 0.5rem;
  font-size: clamp(1.75rem, 3.2vw, 2.25rem);
}

.count {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-faint);
  white-space: nowrap;
}

/* --- Search --------------------------------------------------------------- */

.search {
  position: relative;
  width: 100%;
  max-width: 17rem;
}

.search__icon {
  position: absolute;
  left: 0.95rem;
  top: 50%;
  width: 1rem;
  height: 1rem;
  transform: translateY(-50%);
  color: var(--sl-faint);
  pointer-events: none;
}

.search__input {
  width: 100%;
  padding: 0.6rem 1rem 0.6rem 2.4rem;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-chip-bg);
  font-size: 0.9rem;
  color: var(--sl-text);
  transition: border-color 0.18s ease, background 0.18s ease;
}

.search__input::placeholder {
  color: var(--sl-placeholder);
}

.search__input:focus {
  outline: none;
  border-color: var(--sl-amber);
  background: var(--sl-chip-bg-hover);
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

.state--block {
  display: block;
  padding-top: 0.5rem;
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

  .meter__fill,
  .step::before,
  .step__node {
    transition: none;
  }
}

/* --- The list -------------------------------------------------------------
   Numbered ruled rows (ProjectCard), most recently updated first. */

.project-list {
  list-style: none;
  padding-left: 0;
  margin: 0;
}
</style>
