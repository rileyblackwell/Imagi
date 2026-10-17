<!--
  Projects.vue — the projects list.

  This component is responsible for:
  1. Creating new projects
  2. Deleting existing projects
  3. Listing all user projects
  4. Navigating to the project hub

  It should NOT be responsible for:
  - Project file editing (handled by the build workspace)

  Design: "Studio" on the Spotlight stage. The app's name comes first, typed
  straight into the page's headline. Under it, three numbered steps on a lit
  rail (what the app is, how it works, set the look) run down the left, written
  for people who are not technical, while a live preview of the app stays
  pinned on the right with the Create app button beneath it. Set the look is
  the starter design (components/molecules/brief/StarterDesign.vue): a style
  and a colour scheme, drawn in the pinned preview. The copy is app-first: the
  business tools come with the same project once someone wants them. The
  projects you already have follow as a numbered list. The editorial markup is
  re-lit by the bridge in shared/styles/spotlight.css.
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

          <!-- Signed out: the page's own opening statement -->
          <section v-if="showAuthError" class="sl-opener projects-opener">
            <div class="sl-spot projects-spot" aria-hidden="true"></div>
            <div class="sl-dots" aria-hidden="true"></div>
            <div class="sl-wrap projects-opener__inner">
              <p class="rise-item sl-eyebrow sl-pill">
                <span class="sl-pip" aria-hidden="true"></span>
                <span>Your workspace</span>
              </p>
              <h1 class="rise-item sl-display projects-title" style="animation-delay: 60ms">
                Projects
              </h1>
              <p class="rise-item sl-lede" style="animation-delay: 120ms">
                Every app you build on Imagi lives in a project, along with the tools to turn it
                into a business when you want to.
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
            <form id="create-project" novalidate @submit.prevent="createProject">
              <!-- The name first: the page's headline, typed into directly,
                   and not one of the numbered steps. -->
              <section class="sl-opener projects-opener">
                <div class="sl-spot projects-spot" aria-hidden="true"></div>
                <div class="sl-dots" aria-hidden="true"></div>
                <div class="sl-wrap projects-opener__inner">
                  <h1 class="sr-only">Start a new app</h1>
                  <p class="rise-item sl-eyebrow sl-pill">
                    <span class="sl-pip" aria-hidden="true"></span>
                    <span>New app</span>
                  </p>
                  <div class="rise-item app-name" :class="{ 'is-filled': nameDone, 'is-invalid': fieldErrors.name }" style="animation-delay: 60ms">
                    <label class="sr-only" for="project-name">App name</label>
                    <input
                      id="project-name"
                      ref="projectNameInput"
                      v-model="newProjectName"
                      type="text"
                      class="app-name__input disabled:opacity-50 disabled:cursor-not-allowed"
                      placeholder="Name your app"
                      :aria-describedby="fieldErrors.name ? 'project-name-error project-name-hint' : 'project-name-hint'"
                      :aria-invalid="fieldErrors.name ? 'true' : undefined"
                      autocomplete="off"
                      :disabled="isCreating"
                    >
                  </div>
                  <p id="project-name-hint" class="rise-item app-name__hint" style="animation-delay: 90ms">
                    The name of your app. You can change it later.
                  </p>
                  <p v-if="fieldErrors.name" id="project-name-error" class="field-error">{{ fieldErrors.name }}</p>
                </div>
              </section>

              <!-- The steps on the left, the app pinned on the right -->
              <section class="relative brief-section">
                <div class="sl-wrap studio rise-item" style="animation-delay: 120ms">
                  <div class="steps">
                    <!-- 01 — What the app is: what, who for, and its goal. -->
                    <div class="step" :class="stepClass(1)">
                      <span class="step__node" aria-hidden="true">
                        <svg v-if="descriptionDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        <template v-else>01</template>
                      </span>
                      <label class="step__title" for="project-description">What is your app?</label>
                      <p id="project-description-hint" class="step__hint">
                        A few sentences: what your app is, who it&rsquo;s for, and what it should help them do.
                      </p>
                      <div class="lit-field" :class="{ 'is-invalid': fieldErrors.description }">
                        <textarea
                          id="project-description"
                          ref="projectDescriptionInput"
                          v-model="newProjectDescription"
                          rows="3"
                          class="lit-field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                          placeholder="A stock tracker for everyday investors. It helps them see how their portfolio is doing at a glance, without reading financial reports."
                          :aria-describedby="`project-description-hint project-description-meter${fieldErrors.description ? ' project-description-error' : ''}`"
                          :aria-invalid="fieldErrors.description ? 'true' : undefined"
                          :disabled="isCreating"
                          @focus="focusedStep = 1"
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
                      <p v-if="fieldErrors.description" id="project-description-error" class="field-error">{{ fieldErrors.description }}</p>
                    </div>

                    <!-- 02 — How the app works. Required: it is the functional
                         spec the first build plans every page from. -->
                    <div class="step" :class="stepClass(2)">
                      <span class="step__node" aria-hidden="true">
                        <svg v-if="detailsDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        <template v-else>02</template>
                      </span>
                      <label class="step__title" for="project-details">How does it work?</label>
                      <p id="project-details-hint" class="step__hint">
                        The details of how it works: what people can do on it, the steps they go through,
                        and what it needs to keep track of. Imagi turns this into the plan for your app.
                      </p>
                      <div class="lit-field" :class="{ 'is-invalid': fieldErrors.app_details }">
                        <textarea
                          id="project-details"
                          ref="projectDetailsInput"
                          v-model="newProjectDetails"
                          rows="4"
                          class="lit-field__input resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                          placeholder="People add the stocks they own and how many shares. It shows the total value, today's change and a chart for each stock. Each morning it writes a short summary of what moved and why."
                          :aria-describedby="`project-details-hint project-details-meter${fieldErrors.app_details ? ' project-details-error' : ''}`"
                          :aria-invalid="fieldErrors.app_details ? 'true' : undefined"
                          :disabled="isCreating"
                          @focus="focusedStep = 2"
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
                      <p v-if="fieldErrors.app_details" id="project-details-error" class="field-error">{{ fieldErrors.app_details }}</p>
                    </div>

                    <!-- 03 — The starter design: the app's first design system.
                         Its large preview is the pinned one beside the steps. -->
                    <div class="step step--last" :class="stepClass(3)">
                      <span class="step__node" aria-hidden="true">
                        <svg v-if="designDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        <template v-else>03</template>
                      </span>
                      <p class="step__title">
                        Set the look
                        <span class="step__optional">Optional</span>
                      </p>
                      <p class="step__hint">
                        Pick a style and a colour scheme and see your app take shape. Or
                        <button type="button" class="step__link" :disabled="isCreating" @click="newProjectDesign = emptyDesign()">let Imagi choose</button>.
                      </p>
                      <StarterDesign
                        v-model="newProjectDesign"
                        :app-name="newProjectName.trim()"
                        :app-description="newProjectDescription.trim()"
                        :disabled="isCreating"
                        hide-preview
                        compact
                        @focus="focusedStep = 3"
                        @blur="focusedStep = null"
                      />
                    </div>
                  </div>

                  <!-- The app as it's being described, and the button that
                       creates it -->
                  <aside class="studio__side">
                    <figure class="studio__preview">
                      <figcaption class="studio__label">
                        Your app, as you answer
                        <span v-if="!designDone" class="studio__label-note">Imagi picks the look if you skip it</span>
                      </figcaption>
                      <StarterPreview
                        :style-id="newProjectDesign.style"
                        :scheme="previewScheme"
                        :app-name="newProjectName.trim()"
                        :app-text="previewText"
                      />
                    </figure>

                    <div v-if="atProjectLimit" class="create-foot">
                      <router-link to="/payments/pricing" class="btn-primary group create-submit">
                        <span>See plans</span>
                        <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </router-link>
                      <p class="create-note create-note--limit">
                        Your {{ usageStore.plan?.name }} plan includes one project. Pro and Max include unlimited projects.
                      </p>
                    </div>
                    <div v-else class="create-foot">
                      <button
                        type="submit"
                        class="btn-primary group create-submit"
                        :disabled="isCreating"
                      >
                        <template v-if="isCreating">
                          <span class="spinner" aria-hidden="true"></span>
                          <span>Creating&hellip;</span>
                        </template>
                        <template v-else>
                          <span>Create app</span>
                          <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </svg>
                        </template>
                      </button>
                      <div v-if="errorFields.length" class="create-errors" role="alert">
                        <p class="create-errors__title">Your app can&rsquo;t be created yet. Check:</p>
                        <ul class="create-errors__list">
                          <li v-for="field in errorFields" :key="field">
                            <button type="button" class="create-errors__link" @click="focusField(field)">{{ FIELD_LABELS[field] }}</button>
                          </li>
                        </ul>
                      </div>
                      <p class="create-note">You can change everything later in the workspace.</p>
                    </div>
                  </aside>
                </div>
              </section>
            </form>

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
import { ref, computed, onBeforeUnmount, onMounted, onActivated, watch } from 'vue'
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
import StarterPreview from '../components/molecules/brief/StarterPreview.vue'
import { useUsageStore } from '@/shared/stores/usage'
import {
  emptyDesign,
  designIsSet,
  composeDesignPreferences,
  previewTextFor,
  schemeFor,
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
// Required: how the app works, in plain words. The initial build reads it as
// the app's functional brief.
const newProjectDetails = ref('')
const isCreating = ref(false)
const projectNameInput = ref<HTMLInputElement | null>(null)
const projectDescriptionInput = ref<HTMLTextAreaElement | null>(null)
const projectDetailsInput = ref<HTMLTextAreaElement | null>(null)

// The description and what the app does seed the initial AI build, so
// require enough signal to work with. Keep MIN_DESCRIPTION_LENGTH in sync with
// the backend (ProjectManager/api/serializers.py).
const MIN_DESCRIPTION_LENGTH = 20
const MIN_DETAILS_LENGTH = 20
// The plan's project limit (Free holds one). Once the projects list has
// loaded and the plan is full, the Create app button becomes a way to upgrade
// instead of a create that the server would refuse. The server still enforces
// the limit; this only says so before the form is sent.
const usageStore = useUsageStore()
const atProjectLimit = computed(() =>
  Array.isArray(projectStore.projects) &&
  !usageStore.canCreateProject(projectStore.projects.length)
)

// What still stops the app being created, field by field. Nothing shows until
// the first Create app press; after that the messages follow what is typed and
// clear as each field is fixed. A field the server refused (a name already in
// use) keeps its reason until that field is edited.
type Field = 'name' | 'description' | 'app_details'
const FIELD_LABELS: Record<Field, string> = {
  name: 'App name',
  description: 'What is your app?',
  app_details: 'How does it work?',
}
const showErrors = ref(false)
const serverErrors = ref<Partial<Record<Field, string>>>({})
watch(newProjectName, () => { delete serverErrors.value.name })
watch(newProjectDescription, () => { delete serverErrors.value.description })
watch(newProjectDetails, () => { delete serverErrors.value.app_details })

const missingText = (length: number, min: number, empty: string, short: string) => {
  if (!length) return empty
  if (length < min) return `${short} (at least ${min} characters, ${min - length} to go).`
  return ''
}
const clientErrors = computed<Partial<Record<Field, string>>>(() => {
  const errors: Partial<Record<Field, string>> = {}
  if (!newProjectName.value.trim()) errors.name = 'Give your app a name.'
  const description = missingText(
    newProjectDescription.value.trim().length, MIN_DESCRIPTION_LENGTH,
    'Say what your app is and who it\u2019s for. Imagi uses this to build the first version.',
    'Add a little more about what your app is and who it\u2019s for',
  )
  if (description) errors.description = description
  const details = missingText(
    newProjectDetails.value.trim().length, MIN_DETAILS_LENGTH,
    'Say how your app works: what people can do on it and what it keeps track of.',
    'Add a little more about how your app works',
  )
  if (details) errors.app_details = details
  return errors
})
const fieldErrors = computed<Partial<Record<Field, string>>>(() => ({
  ...(showErrors.value ? clientErrors.value : {}),
  ...serverErrors.value,
}))
const errorFields = computed(() =>
  (Object.keys(FIELD_LABELS) as Field[]).filter((field) => fieldErrors.value[field])
)
const focusField = (field?: Field) => {
  if (!field) return
  const input = {
    name: projectNameInput,
    description: projectDescriptionInput,
    app_details: projectDetailsInput,
  }[field].value
  input?.focus()
  input?.scrollIntoView?.({ block: 'center', behavior: 'smooth' })
}

// The name sits above the steps; the three steps below it are done once their
// answer is enough to build from. The current one is the field being typed
// in, or else the first that still needs an answer.
const nameDone = computed(() => Boolean(newProjectName.value.trim()))
const descriptionLength = computed(() => newProjectDescription.value.trim().length)
const descriptionDone = computed(() => descriptionLength.value >= MIN_DESCRIPTION_LENGTH)
const detailsLength = computed(() => newProjectDetails.value.trim().length)
const detailsDone = computed(() => detailsLength.value >= MIN_DETAILS_LENGTH)
const designDone = computed(() => designIsSet(newProjectDesign.value))
type Step = 1 | 2 | 3
const focusedStep = ref<Step | null>(null)
const currentStep = computed(() =>
  focusedStep.value ?? (!descriptionDone.value ? 1 : !detailsDone.value ? 2 : 3)
)
const stepDone = { 1: descriptionDone, 2: detailsDone, 3: designDone } as const
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

// The pinned preview: the app's own name and first sentence, in the picked
// style and colours (a quiet neutral app until something is picked).
const previewScheme = computed(() => schemeFor(newProjectDesign.value))
const previewText = computed(() => previewTextFor(newProjectDescription.value))

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

  // The name, what the app is and how it works all seed the first build.
  // Anything missing is said beside its field, and the first one gets focus.
  showErrors.value = true
  if (errorFields.value.length) {
    focusField(errorFields.value[0])
    return
  }

  isCreating.value = true

  try {
    // Create a properly formatted project data object with name and description
    const projectData = {
      name: newProjectName.value.trim(),
      description: newProjectDescription.value.trim(), // Use the description value
      app_details: newProjectDetails.value.trim(),
      design_preferences: composeDesignPreferences(newProjectDesign.value), // Optional
    }

    const newProject = await projectStore.createProject(projectData)

    // Clear the create form after successful creation
    newProjectName.value = ''
    newProjectDescription.value = ''
    newProjectDetails.value = ''
    newProjectDesign.value = emptyDesign()
    showErrors.value = false

    // Log project information to debug any ID issues
    console.debug('Created project details:', {
      project: newProject,
      id: newProject.id,
      idType: typeof newProject.id
    })

    // Straight into the build workspace: it shows the home page being built
    // and opens the app the moment it lands, while the other pages finish.
    router.push({
      name: 'builder-workspace',
      params: { projectName: projectSlug(newProject) }
    })

  } catch (error: any) {
    // A refusal may be the plan's project limit; refresh the plan so the
    // brief switches to its upgrade prompt.
    void usageStore.fetchUsage()
    // The form reports its own failure; the store's error is for the list,
    // which would otherwise swap the projects for a load error.
    projectStore.clearError()
    if (error?.fieldErrors) {
      serverErrors.value = { ...error.fieldErrors }
      if (errorFields.value.length) focusField(errorFields.value[0])
    } else {
      showNotification({
        message: error?.message || 'Failed to create project',
        type: 'error'
      })
    }
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
    void usageStore.fetchUsage()
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
   Left-aligned. Signed in, its headline is the app's name field. */

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

/* The app's name, typed into the headline. One hairline under it, lit from
   left to right once there is a name. */
.app-name {
  position: relative;
  width: 100%;
}

.app-name .app-name__input {
  display: block;
  width: 100%;
  padding: 0.1rem 0 0.75rem;
  border: 0;
  border-bottom: 1.5px solid var(--sl-line-strong);
  border-radius: 0;
  background: transparent;
  font-family: var(--sl-font-display);
  font-size: clamp(36px, 5vw, 58px);
  font-weight: 800;
  font-variation-settings: 'opsz' 96;
  line-height: 1.05;
  letter-spacing: -0.035em;
  color: var(--sl-text);
  transition: border-color 0.2s ease;
}

.app-name .app-name__input::placeholder {
  color: var(--sl-placeholder);
  opacity: 0.6;
}

.app-name .app-name__input:hover:not(:disabled) {
  border-bottom-color: var(--sl-muted);
}

.app-name .app-name__input:focus {
  outline: none;
}

.app-name::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 2px;
  border-radius: 2px;
  background: var(--sl-grad);
  transform: scaleX(0);
  transform-origin: left center;
  transition: transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
  pointer-events: none;
}

.app-name.is-filled::after,
.app-name:focus-within::after {
  transform: scaleX(1);
}

.app-name__hint {
  margin-top: -0.5rem;
  font-size: 0.9rem;
  color: var(--sl-muted);
}

/* --- Studio ---------------------------------------------------------------
   The three steps on the left; on the right, the app as it is being
   described, pinned under the navbar while the steps scroll, with the button
   that creates it. One column below 960px, the preview after the look. */

.brief-section {
  padding-bottom: clamp(72px, 9vw, 112px);
}

.studio {
  display: grid;
  gap: 3rem;
}

@media (min-width: 960px) {
  .studio {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.08fr);
    gap: clamp(2rem, 4vw, 3.5rem);
    align-items: start;
  }

  .studio__side {
    position: sticky;
    top: calc(57px + 1.5rem);
  }
}

.studio__side {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}

.studio__preview {
  display: grid;
  gap: 0.65rem;
  margin: 0;
}

.studio__label {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.25rem 0.75rem;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.studio__label-note {
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
  color: var(--sl-faint);
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

/* "let Imagi choose": clears the look, so the build picks one itself. */
.step__link {
  padding: 0;
  border: 0;
  background: none;
  font: inherit;
  color: var(--sl-text);
  text-decoration: underline;
  text-decoration-color: var(--sl-line-strong);
  text-underline-offset: 3px;
  transition: text-decoration-color 0.2s ease;
}

.step__link:hover:not(:disabled) {
  text-decoration-color: currentColor;
}

.step__link:disabled {
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

/* Under the pinned preview. */
.create-foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1.25rem;
}

/* Two selectors so this beats `.editorial .btn-primary`'s padding. */
.create-foot .create-submit {
  padding: 0.8rem 1.6rem;
  font-size: 0.95rem;
}

/* Why the app can't be created yet: beside each field, and listed under the
   button. `bad`, not the light, so a problem never reads as a button. */
.field-error {
  margin-top: 0.6rem;
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--sl-bad);
}

.app-name.is-invalid .app-name__input {
  border-bottom-color: var(--sl-bad);
}

.app-name.is-invalid::after {
  background: var(--sl-bad);
}

/* Under the name's hint, in the opener's 20px column gap. */
.projects-opener__inner .field-error {
  margin-top: -0.85rem;
}

.lit-field.is-invalid {
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-bad) border-box;
}

.create-errors {
  padding-left: 0.85rem;
  border-left: 2px solid var(--sl-bad);
  font-size: 0.85rem;
  line-height: 1.5;
  color: var(--sl-text);
}

.create-errors__list {
  margin-top: 0.3rem;
}

.create-errors__link {
  color: var(--sl-bad);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.create-note {
  font-size: 0.78rem;
  color: var(--sl-faint);
}

/* The upgrade prompt is something to read, not a footnote: `faint` misses
   4.5:1, so it takes `muted`. */
.create-note--limit {
  max-width: 34ch;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--sl-muted);
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
