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
  <div class="spotlight">
    <!-- Confirm Modal (uses Teleport to body) -->
    <ConfirmModal
      :is-open="confirmModal.isModalOpen.value"
      :options="confirmModal.modalOptions.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />

    <DefaultLayout>
      <div class="editorial relative min-h-screen">
        <main class="relative">

          <!-- Signed out: the page's own opening statement -->
          <section v-if="showAuthError" :class="OPENER">
            <div class="sl-spot" aria-hidden="true"></div>
            <div class="sl-dots" aria-hidden="true"></div>
            <div class="sl-wrap flex flex-col items-start gap-[20px]">
              <p class="rise-item sl-eyebrow sl-pill">
                <span class="sl-pip" aria-hidden="true"></span>
                <span>Your workspace</span>
              </p>
              <h1 class="rise-item sl-display max-w-[18ch] text-[clamp(40px,6vw,68px)] leading-[1.02] tracking-[-0.035em] lg:max-w-none" style="animation-delay: 60ms">
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
              <section :class="OPENER">
                <div class="sl-spot" aria-hidden="true"></div>
                <div class="sl-dots" aria-hidden="true"></div>
                <div class="sl-wrap flex flex-col items-start gap-[20px]">
                  <h1 class="sr-only">Start a new app</h1>
                  <p class="rise-item sl-eyebrow sl-pill">
                    <span class="sl-pip" aria-hidden="true"></span>
                    <span>New app</span>
                  </p>
                  <!-- The app's name, typed into the headline. One hairline under it, lit
                       from left to right (::after) once there is a name. -->
                  <div
                    class="rise-item app-name relative w-full after:pointer-events-none after:absolute after:bottom-0 after:left-0 after:right-0 after:h-[2px] after:rounded-[2px]
                      after:origin-[left_center] after:content-[''] after:[transition:transform_0.5s_cubic-bezier(0.22,1,0.36,1)]"
                    :class="[
                      { 'is-filled': nameDone, 'is-invalid': fieldErrors.name },
                      fieldErrors.name ? 'after:bg-sl-bad' : 'after:bg-sl-grad',
                      nameDone ? 'after:scale-x-100' : 'after:scale-x-0 focus-within:after:scale-x-100',
                    ]"
                    style="animation-delay: 60ms"
                  >
                    <label class="sr-only" for="project-name">App name</label>
                    <input
                      id="project-name"
                      ref="projectNameInput"
                      v-model="newProjectName"
                      type="text"
                      class="block w-full appearance-none rounded-none bg-transparent px-0 pb-[0.75rem] pt-[0.1rem] font-sl-display text-[clamp(36px,5vw,58px)] font-extrabold leading-[1.05] tracking-[-0.035em] text-sl-text
                        [border-style:none_none_solid] [border-width:0_0_1.5px] [font-variation-settings:'opsz'_96] [transition:border-color_0.2s_ease]
                        placeholder:text-sl-placeholder placeholder:opacity-60 enabled:hover:border-b-sl-muted focus:![outline:none] disabled:opacity-50 disabled:cursor-not-allowed"
                      :class="fieldErrors.name
                        ? '[border-color:currentcolor_currentcolor_var(--sl-bad)]'
                        : '[border-color:currentcolor_currentcolor_var(--sl-line-strong)]'"
                      placeholder="Name your app"
                      :aria-describedby="fieldErrors.name ? 'project-name-error project-name-hint' : 'project-name-hint'"
                      :aria-invalid="fieldErrors.name ? 'true' : undefined"
                      autocomplete="off"
                      :disabled="isCreating"
                    >
                  </div>
                  <p id="project-name-hint" class="rise-item -mt-[0.5rem] text-[0.9rem] text-sl-muted" style="animation-delay: 90ms">
                    The name of your app. You can change it later.
                  </p>
                  <p v-if="fieldErrors.name" id="project-name-error" class="field-error -mt-[0.85rem]" :class="FIELD_ERROR">{{ fieldErrors.name }}</p>
                </div>
              </section>

              <!-- The steps on the left, the app pinned on the right -->
              <section class="relative pb-[clamp(72px,9vw,112px)]">
                <!-- The three steps on the left; on the right, the app as it is being
                     described, pinned under the navbar while the steps scroll,
                     with the button that creates it. One column below 960px,
                     the preview after the look. -->
                <div
                  class="sl-wrap rise-item grid gap-[3rem] min-[960px]:grid-cols-[minmax(0,1fr)_minmax(0,1.08fr)] min-[960px]:[align-items:start] min-[960px]:gap-[clamp(2rem,4vw,3.5rem)]"
                  style="animation-delay: 120ms"
                >
                  <!-- The rail: a line down the left (each step's ::before) that
                       each step's node sits on. The segment below a node lights
                       once that step has its answer. -->
                  <div class="grid min-w-0">
                    <!-- 01 — What the app is: what, who for, and its goal. -->
                    <div class="step" :class="[stepClass(1), stepRail(1), 'pb-[2.25rem]']">
                      <span class="step__node" :class="stepNode(1)" aria-hidden="true">
                        <svg v-if="descriptionDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        <template v-else>01</template>
                      </span>
                      <label :class="STEP_TITLE" for="project-description">What is your app?</label>
                      <p id="project-description-hint" :class="STEP_HINT">
                        A few sentences: what your app is, who it&rsquo;s for, and what it should help them do.
                      </p>
                      <div :class="litField(fieldErrors.description)">
                        <textarea
                          id="project-description"
                          ref="projectDescriptionInput"
                          v-model="newProjectDescription"
                          rows="3"
                          :class="LIT_INPUT"
                          class="resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                          placeholder="A stock tracker for everyday investors. It helps them see how their portfolio is doing at a glance, without reading financial reports."
                          :aria-describedby="`project-description-hint project-description-meter${fieldErrors.description ? ' project-description-error' : ''}`"
                          :aria-invalid="fieldErrors.description ? 'true' : undefined"
                          :disabled="isCreating"
                          @focus="focusedStep = 1"
                          @blur="focusedStep = null"
                        ></textarea>
                      </div>
                      <div class="mt-[0.85rem] flex items-center gap-[0.85rem]">
                        <span class="relative h-[4px] flex-1 overflow-hidden rounded-[4px] bg-sl-line-strong" aria-hidden="true">
                          <span class="absolute inset-0 origin-[left_center] bg-sl-grad [transition:transform_0.3s_ease] motion-reduce:[transition:none]" :style="{ transform: `scaleX(${descriptionProgress})` }"></span>
                        </span>
                        <span id="project-description-meter" class="meter__label" :class="meterLabelClass(descriptionDone)" aria-live="polite">
                          <svg v-if="descriptionDone" class="h-[0.85rem] w-[0.85rem]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                          {{ descriptionMeterLabel }}
                        </span>
                      </div>
                      <p v-if="fieldErrors.description" id="project-description-error" class="field-error mt-[0.6rem]" :class="FIELD_ERROR">{{ fieldErrors.description }}</p>
                    </div>

                    <!-- 02 — How the app works. Required: it is the functional
                         spec the first build plans every page from. -->
                    <div class="step" :class="[stepClass(2), stepRail(2), 'pb-[2.25rem]']">
                      <span class="step__node" :class="stepNode(2)" aria-hidden="true">
                        <svg v-if="detailsDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        <template v-else>02</template>
                      </span>
                      <label :class="STEP_TITLE" for="project-details">How does it work?</label>
                      <p id="project-details-hint" :class="STEP_HINT">
                        The details of how it works: what people can do on it, the steps they go through,
                        and what it needs to keep track of. Imagi turns this into the plan for your app.
                      </p>
                      <div :class="litField(fieldErrors.app_details)">
                        <textarea
                          id="project-details"
                          ref="projectDetailsInput"
                          v-model="newProjectDetails"
                          rows="4"
                          :class="LIT_INPUT"
                          class="resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                          placeholder="People add the stocks they own and how many shares. It shows the total value, today's change and a chart for each stock. Each morning it writes a short summary of what moved and why."
                          :aria-describedby="`project-details-hint project-details-meter${fieldErrors.app_details ? ' project-details-error' : ''}`"
                          :aria-invalid="fieldErrors.app_details ? 'true' : undefined"
                          :disabled="isCreating"
                          @focus="focusedStep = 2"
                          @blur="focusedStep = null"
                        ></textarea>
                      </div>
                      <div class="mt-[0.85rem] flex items-center gap-[0.85rem]">
                        <span class="relative h-[4px] flex-1 overflow-hidden rounded-[4px] bg-sl-line-strong" aria-hidden="true">
                          <span class="absolute inset-0 origin-[left_center] bg-sl-grad [transition:transform_0.3s_ease] motion-reduce:[transition:none]" :style="{ transform: `scaleX(${detailsProgress})` }"></span>
                        </span>
                        <span id="project-details-meter" class="meter__label" :class="meterLabelClass(detailsDone)" aria-live="polite">
                          <svg v-if="detailsDone" class="h-[0.85rem] w-[0.85rem]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                          {{ detailsMeterLabel }}
                        </span>
                      </div>
                      <p v-if="fieldErrors.app_details" id="project-details-error" class="field-error mt-[0.6rem]" :class="FIELD_ERROR">{{ fieldErrors.app_details }}</p>
                    </div>

                    <!-- 03 — The starter design: the app's first design system.
                         Its large preview is the pinned one beside the steps. -->
                    <div class="step" :class="[stepClass(3), stepRail(3), 'pb-0 before:hidden']">
                      <span class="step__node" :class="stepNode(3)" aria-hidden="true">
                        <svg v-if="designDone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5" /></svg>
                        <template v-else>03</template>
                      </span>
                      <p :class="STEP_TITLE">
                        Set the look
                        <span class="font-sl-body text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-sl-faint">Optional</span>
                      </p>
                      <!-- "let Imagi choose" clears the look, so the build picks one itself. -->
                      <p :class="STEP_HINT">
                        Pick a style and a colour scheme and see your app take shape. Or
                        <button
                          type="button"
                          class="step__link p-0 [border:0] [font:inherit] text-sl-text underline decoration-sl-line-strong underline-offset-[3px] [transition:text-decoration-color_0.2s_ease]
                            enabled:hover:decoration-current disabled:cursor-not-allowed disabled:opacity-50"
                          :disabled="isCreating" @click="newProjectDesign = emptyDesign()">let Imagi choose</button>.
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
                  <aside class="studio__side grid min-w-0 gap-6 min-[960px]:sticky min-[960px]:top-[calc(57px+1.5rem)]">
                    <figure class="studio__preview m-0 grid gap-[0.65rem]">
                      <figcaption class="flex flex-wrap justify-between gap-x-[0.75rem] gap-y-[0.25rem] text-[0.72rem] font-semibold uppercase tracking-[0.16em] text-sl-muted">
                        Your app, as you answer
                        <span v-if="!designDone" class="font-medium normal-case tracking-[0] text-sl-faint">Imagi picks the look if you skip it</span>
                      </figcaption>
                      <StarterPreview
                        :style-id="newProjectDesign.style"
                        :scheme="previewScheme"
                        :app-name="newProjectName.trim()"
                        :app-text="previewText"
                      />
                    </figure>

                    <!-- Under the pinned preview. The button's size beats .btn-primary's. -->
                    <div v-if="atProjectLimit" :class="CREATE_FOOT">
                      <router-link to="/payments/pricing" class="btn-primary group create-submit !px-[1.6rem] !py-[0.8rem] !text-[0.95rem]">
                        <span>See plans</span>
                        <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </router-link>
                      <!-- The upgrade prompt is something to read, not a footnote: `faint`
                           misses 4.5:1, so it takes `muted`. -->
                      <p class="create-note--limit max-w-[34ch] text-[0.82rem] leading-[1.5] text-sl-muted">
                        Your {{ usageStore.plan?.name }} plan includes one project. Pro and Max include unlimited projects.
                      </p>
                    </div>
                    <div v-else :class="CREATE_FOOT">
                      <button
                        type="submit"
                        class="btn-primary group create-submit !px-[1.6rem] !py-[0.8rem] !text-[0.95rem]"
                        :disabled="isCreating"
                      >
                        <template v-if="isCreating">
                          <span class="spinner h-4 w-4 flex-none rounded-[999px] border-[1.5px] border-current border-t-transparent opacity-60" aria-hidden="true"></span>
                          <span>Creating&hellip;</span>
                        </template>
                        <template v-else>
                          <span>Create app</span>
                          <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </svg>
                        </template>
                      </button>
                      <!-- Why the app can't be created yet: beside each field, and listed
                           here. `bad`, not the light, so a problem never reads as a button. -->
                      <div v-if="errorFields.length" class="create-errors border-l-2 border-l-sl-bad pl-[0.85rem] text-[0.85rem] leading-[1.5] text-sl-text" role="alert">
                        <p>Your app can&rsquo;t be created yet. Check:</p>
                        <ul class="mt-[0.3rem]">
                          <li v-for="field in errorFields" :key="field">
                            <button type="button" class="create-errors__link text-sl-bad underline underline-offset-2" @click="focusField(field)">{{ FIELD_LABELS[field] }}</button>
                          </li>
                        </ul>
                      </div>
                      <p class="text-[0.78rem] text-sl-faint">You can change everything later in the workspace.</p>
                    </div>
                  </aside>
                </div>
              </section>
            </form>

            <!-- Your projects -->
            <section class="relative pb-[clamp(80px,10vw,128px)]">
              <div class="sl-wrap">
                <div
                  class="rise-item flex flex-wrap items-end justify-between gap-x-8 gap-y-[1.25rem] border-b border-b-sl-line-strong pb-[1.1rem]"
                  style="animation-delay: 200ms"
                >
                  <div>
                    <p class="whitespace-nowrap text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-sl-faint">
                      Your projects<template v-if="!isLoading && !error && displayedProjects.length > 0">
                        &middot; {{ searchQuery ? `${displayedProjects.length} found` : `${projects?.length || 0}` }}
                      </template>
                    </p>
                    <h2 class="display mt-2 text-[clamp(1.75rem,3.2vw,2.25rem)]">Pick up where you left off</h2>
                  </div>

                  <!-- Search. Nothing to search until there is something in the
                       list, and an empty field over an empty list is just a
                       second line saying nothing. -->
                  <div v-if="projects?.length" class="relative w-full max-w-[17rem]">
                    <svg class="pointer-events-none absolute left-[0.95rem] top-1/2 h-4 w-4 -translate-y-1/2 text-sl-faint" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <circle cx="11" cy="11" r="7" />
                      <path d="m20 20-3.5-3.5" />
                    </svg>
                    <label class="sr-only" for="project-search">Search projects</label>
                    <input
                      id="project-search"
                      v-model="searchQuery"
                      type="search"
                      class="w-full appearance-none rounded-[999px] border border-sl-line bg-sl-chip-bg py-[0.6rem] pl-[2.4rem] pr-4 text-[0.9rem] text-sl-text
                        [transition:border-color_0.18s_ease,background_0.18s_ease] placeholder:text-sl-placeholder
                        focus:border-sl-amber focus:bg-sl-chip-bg-hover focus:![outline:none] [&::-webkit-search-cancel-button]:appearance-none"
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
                    class="mt-6 flex items-start gap-3 border-l-2 py-3 pl-4 pr-0 text-[0.875rem] leading-[1.5]"
                    :class="deleteBanner.type === 'error' ? 'border-l-ed-accent text-ed-ink' : 'border-l-ed-rule-strong text-ed-ink-70'"
                  >
                    <span class="flex-1">{{ deleteBanner.message }}</span>
                    <button
                      type="button"
                      class="mt-[0.1rem] flex-none text-ed-ink-40 [transition:color_0.18s_ease] hover:text-ed-ink"
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
                <p v-if="isLoading" class="flex" :class="STATE">
                  <span class="spinner h-4 w-4 flex-none rounded-[999px] border-[1.5px] border-current border-t-transparent text-ed-accent opacity-100" aria-hidden="true"></span>
                  <span>Loading your projects&hellip;</span>
                </p>

                <!-- Error -->
                <div v-else-if="error" class="block pt-2" :class="STATE">
                  <p :class="STATE_MESSAGE">{{ error }}</p>
                  <button type="button" class="btn-outline mt-6" @click="retryFetch">Try again</button>
                </div>

                <!-- No search results -->
                <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="block pt-2" :class="STATE">
                  <p :class="STATE_MESSAGE">No project matches &ldquo;{{ searchQuery }}&rdquo;.</p>
                </div>

                <!--
                  Empty state, keyed off what's actually shown rather than the
                  raw store list, so deleting the last project surfaces this
                  immediately instead of leaving an empty section.
                -->
                <div v-else-if="!displayedProjects.length" class="block pt-2" :class="STATE">
                  <p :class="STATE_MESSAGE">
                    No projects yet. Describe an app above and Imagi builds the first version of
                    it.
                  </p>
                </div>

                <!-- The list -->
                <!-- Numbered ruled rows (ProjectCard), most recently updated first. -->
                <ol v-else class="project-list m-0 list-none pl-0">
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

// Shared class lists. The opener is left-aligned; signed in, its headline is
// the app's name field.
const OPENER = 'sl-opener !pb-[clamp(36px,5vw,56px)]'
const FIELD_ERROR = 'text-[0.85rem] leading-[1.5] text-sl-bad'
const CREATE_FOOT = 'flex flex-wrap items-center gap-x-[1.25rem] gap-y-[0.75rem]'
const STATE = 'mt-10 items-center gap-[0.7rem] text-[0.9375rem] text-ed-ink-55'
const STATE_MESSAGE = 'text-pretty text-[0.9375rem] leading-[1.65] text-ed-ink-55'

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
// The rail segment under each step's node (::before), lit once it's done.
const stepRail = (step: Step) => [
  "relative pl-[3.5rem] before:absolute before:bottom-[0.25rem] before:left-[19px] before:top-[2.75rem] before:w-[2px] before:rounded-[2px] before:content-[''] before:[transition:background_0.3s_ease] motion-reduce:before:[transition:none]",
  stepDone[step].value ? 'before:bg-[image:linear-gradient(180deg,var(--sl-coral),var(--sl-amber))]' : 'before:bg-sl-line-strong',
]
// The node: lit by the gradient once done, ringed in amber while current.
const stepNode = (step: Step) => [
  'absolute left-0 top-0 grid h-10 w-10 place-items-center rounded-[999px] border-[1.5px] font-[ui-monospace,SFMono-Regular,Menlo,monospace] text-[0.8rem] [&_svg]:h-[17px] [&_svg]:w-[17px] [transition:background_0.25s_ease,border-color_0.25s_ease,color_0.25s_ease,box-shadow_0.25s_ease] motion-reduce:[transition:none]',
  stepDone[step].value
    ? 'border-transparent bg-sl-grad text-sl-on-accent'
    : currentStep.value === step ? 'border-sl-amber bg-sl-bg text-sl-amber' : 'border-sl-line-strong bg-sl-bg text-sl-faint',
  currentStep.value === step && 'shadow-[0_0_0_5px_color-mix(in_srgb,var(--sl-amber)_14%,transparent),0_0_24px_var(--sl-glow)]',
]
const STEP_TITLE = 'flex items-baseline gap-3 pt-[0.35rem] font-sl-display text-[1.375rem] font-[650] tracking-[-0.015em] text-sl-text'
const STEP_HINT = 'mx-0 mb-[0.9rem] mt-[0.25rem] text-[0.9rem] leading-[1.55] text-sl-muted'
// The description gets the home page's glowing prompt sheet: it is the answer
// the first build leans on most. A problem turns its lit edge `bad`.
const litField = (invalid?: string) => [
  'rounded-2xl border border-transparent [box-shadow:var(--sl-prompt-shadow)] [transition:box-shadow_0.25s_ease] focus-within:[box-shadow:var(--sl-prompt-shadow-focus)]',
  invalid
    ? '[background:var(--sl-prompt-bg)_padding-box,var(--sl-bad)_border-box]'
    : '[background:var(--sl-prompt-bg)_padding-box,var(--sl-prompt-edge)_border-box]',
]
const LIT_INPUT = 'block min-h-[8rem] w-full rounded-2xl bg-transparent px-[1.15rem] py-4 text-[1rem] leading-[1.65] text-sl-text [border:0] placeholder:text-sl-placeholder focus:![outline:none]'
// How close an answer is to enough to build from.
const meterLabelClass = (done: boolean) => [
  'inline-flex items-center gap-[0.35rem] whitespace-nowrap text-[0.8rem]',
  done ? 'font-semibold text-sl-ok' : 'text-sl-muted',
]
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
/* The spinner's turn. Keyframes stay CSS: scoped keyframe names are hashed,
   so a utility can't reference them. */
.spinner {
  animation: spin 0.8s linear infinite;
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
</style>
