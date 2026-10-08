<!--
  MarketingAdBuilder.vue - Plan a Google search ad.

  The form on the left covers what a Google Ads search campaign needs: a goal,
  where clicks go, the ad's headlines and descriptions (within Google's 30 and
  90 character limits), the searches it should show for, where, and a daily
  budget. The right column previews the ad as it would read on a results page.

  Plans are saved in Imagi only. Launching on Google from here isn't built yet,
  so the launch button stays off and says so: nothing is sent to Google and
  nothing is spent.

  Routes: campaigns/google/new, campaigns/google/:draftId
-->
<template>
  <div>
    <router-link
      :to="{ name: 'marketing-overview', params: { projectName: projectName } }"
      class="inline-flex items-center gap-2 text-sm font-medium text-ink/60 dark:text-bone/60 hover:text-ink dark:hover:text-white transition-colors duration-200 mb-5 rounded-md focus-ring"
    >
      <i class="fas fa-arrow-left text-xs" aria-hidden="true"></i>
      <span>All campaigns</span>
    </router-link>

    <LoadingSpinner v-if="loading" />
    <div v-else-if="loadError" :class="ui.errorBox">{{ loadError }}</div>

    <form v-else class="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start" @submit.prevent="save">
      <!-- The plan -->
      <div class="lg:col-span-3 p-6 sm:p-7" :class="ui.card">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 shrink-0" :class="ui.iconTile"><i class="fab fa-google" aria-hidden="true"></i></div>
          <div>
            <h2 :class="ui.headingText">{{ draftId ? 'Google search ad' : 'New Google search ad' }}</h2>
            <p :class="ui.hintText">Saved in Imagi as a draft</p>
          </div>
        </div>

        <!-- Campaign -->
        <fieldset class="step">
          <legend class="step__title">Campaign</legend>
          <div>
            <label :class="ui.label" for="ad-name">Campaign name</label>
            <input id="ad-name" v-model="form.name" type="text" required maxlength="255" placeholder="e.g. Fall espresso promo" :class="ui.input" />
          </div>
          <div>
            <span :class="ui.label">Goal</span>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                v-for="option in goalOptions"
                :key="option.value"
                type="button"
                class="flex items-start gap-3 p-3.5 rounded-xl border text-left transition-all duration-200 focus-ring"
                :class="form.goal === option.value
                  ? 'border-[color:var(--sl-warm-line)] bg-[color:var(--sl-chip-bg-hover)] ring-1 ring-[color:var(--sl-warm-line)]'
                  : 'border-ink/10 dark:border-white/[0.12] bg-white dark:bg-white/[0.04] hover:border-ink/25 dark:hover:border-white/25'"
                :aria-pressed="form.goal === option.value"
                @click="form.goal = option.value"
              >
                <div class="w-9 h-9 shrink-0" :class="ui.iconTile"><i :class="['fas', option.icon]" aria-hidden="true"></i></div>
                <div>
                  <p class="text-sm font-semibold text-ink dark:text-bone">{{ option.label }}</p>
                  <p class="text-xs text-ink/60 dark:text-bone/60 leading-snug mt-0.5">{{ option.hint }}</p>
                </div>
              </button>
            </div>
          </div>
          <div>
            <label :class="ui.label" for="ad-url">Landing page</label>
            <input id="ad-url" v-model="form.final_url" type="url" placeholder="https://yourbusiness.com/offer" :class="ui.input" />
            <p :class="ui.hintText" class="mt-1.5">Where people go when they click the ad. Usually a page of the app you built.</p>
          </div>
          <div v-if="form.goal === 'calls'">
            <label :class="ui.label" for="ad-phone">Phone number</label>
            <input id="ad-phone" v-model="form.phone_number" type="tel" maxlength="20" placeholder="+15551234567" :class="ui.input" />
          </div>
        </fieldset>

        <!-- The ad -->
        <fieldset class="step">
          <legend class="step__title">The ad</legend>
          <div>
            <span :class="ui.label">Headlines</span>
            <div class="space-y-2.5">
              <div v-for="(headline, i) in form.headlines" :key="`h${i}`" class="relative">
                <input
                  v-model="form.headlines[i]"
                  type="text"
                  :maxlength="HEADLINE_MAX"
                  :placeholder="headlinePlaceholders[i] || 'Another headline'"
                  :aria-label="`Headline ${i + 1}`"
                  class="pr-14"
                  :class="ui.input"
                />
                <span class="counter" :class="{ 'counter--full': headline.length >= HEADLINE_MAX }">
                  {{ headline.length }}/{{ HEADLINE_MAX }}
                </span>
              </div>
            </div>
            <button
              v-if="form.headlines.length < 6"
              type="button"
              :class="ui.textLink"
              class="mt-2.5"
              @click="form.headlines.push('')"
            >
              Add a headline
            </button>
            <p :class="ui.hintText" class="mt-1.5">Google mixes up to three at a time, so each should make sense on its own.</p>
          </div>
          <div>
            <span :class="ui.label">Descriptions</span>
            <div class="space-y-2.5">
              <div v-for="(description, i) in form.descriptions" :key="`d${i}`" class="relative">
                <textarea
                  v-model="form.descriptions[i]"
                  rows="2"
                  :maxlength="DESCRIPTION_MAX"
                  :placeholder="i === 0 ? 'What you offer and why someone should click.' : 'A second line: a detail, a promise or an offer.'"
                  :aria-label="`Description ${i + 1}`"
                  class="pr-14 resize-none"
                  :class="ui.input"
                ></textarea>
                <span class="counter counter--area" :class="{ 'counter--full': description.length >= DESCRIPTION_MAX }">
                  {{ description.length }}/{{ DESCRIPTION_MAX }}
                </span>
              </div>
            </div>
          </div>
        </fieldset>

        <!-- Who sees it -->
        <fieldset class="step">
          <legend class="step__title">Who sees it</legend>
          <div>
            <label :class="ui.label" for="ad-keywords">Searches to show up for</label>
            <div class="flex flex-wrap items-center gap-2 px-2.5 py-2 min-h-[2.75rem]" :class="ui.input">
              <span
                v-for="keyword in form.keywords"
                :key="keyword"
                class="inline-flex items-center gap-1.5 pl-3 pr-1.5 py-1 rounded-full border border-[color:var(--sl-line)] bg-[color:var(--sl-chip-bg)] text-xs text-ink dark:text-bone"
              >
                {{ keyword }}
                <button type="button" class="w-4 h-4 inline-flex items-center justify-center rounded-full hover:bg-ink/10 dark:hover:bg-white/10 focus-ring" :aria-label="`Remove ${keyword}`" @click="removeKeyword(keyword)">
                  <i class="fas fa-xmark text-[10px]" aria-hidden="true"></i>
                </button>
              </span>
              <input
                id="ad-keywords"
                v-model="keywordInput"
                type="text"
                class="flex-1 min-w-[10rem] bg-transparent border-0 outline-none text-sm py-1 placeholder-ink/40 dark:placeholder-bone/30"
                :placeholder="form.keywords.length ? 'Add another' : 'e.g. espresso near me'"
                @keydown.enter.prevent="addKeyword"
                @keydown.,.prevent="addKeyword"
                @blur="addKeyword"
              />
            </div>
            <p :class="ui.hintText" class="mt-1.5">Press Enter after each one. Think of what a customer would type.</p>
          </div>
          <div>
            <label :class="ui.label" for="ad-location">Where</label>
            <input id="ad-location" v-model="form.location" type="text" maxlength="255" placeholder="e.g. Portland, OR or United States" :class="ui.input" />
          </div>
        </fieldset>

        <!-- Budget -->
        <fieldset class="step">
          <legend class="step__title">Budget</legend>
          <div class="sm:max-w-xs">
            <label :class="ui.label" for="ad-budget">Daily budget (USD)</label>
            <div class="relative">
              <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-sm text-ink/50 dark:text-bone/50">$</span>
              <input id="ad-budget" v-model="form.daily_budget" type="number" min="1" step="1" placeholder="15" class="pl-7" :class="ui.input" />
            </div>
          </div>
          <p :class="ui.hintText" v-if="monthlyCap">
            At most about {{ monthlyCap }} a month. Google can spend more on a busy day, but never more than 30.4 times your daily budget in a month.
          </p>
        </fieldset>

        <div v-if="saveError" class="mt-6" :class="ui.errorBox">{{ saveError }}</div>

        <div class="mt-7 pt-6 border-t border-[color:var(--sl-line)] flex flex-wrap items-center gap-3">
          <button type="submit" :class="ui.primaryBtn" :disabled="saving || !form.name.trim()">
            <i v-if="saving" class="fas fa-circle-notch animate-spin motion-reduce:animate-none" aria-hidden="true"></i>
            {{ saved ? 'Saved' : 'Save draft' }}
          </button>
          <router-link :to="{ name: 'marketing-overview', params: { projectName } }" :class="ui.secondaryBtn">Cancel</router-link>
          <button v-if="draftId" type="button" :class="ui.dangerBtn" class="sm:ml-auto" :disabled="deleting" @click="remove">
            Delete draft
          </button>
        </div>
      </div>

      <!-- Preview and launch -->
      <aside class="lg:col-span-2 space-y-6 lg:sticky lg:top-24">
        <section class="p-6" :class="ui.card">
          <h3 :class="ui.label" class="!mb-4">Preview</h3>
          <GoogleAdPreview
            :headlines="form.headlines"
            :descriptions="form.descriptions"
            :final-url="form.final_url"
            :business-name="projectTitle"
            :goal="form.goal"
            :phone-number="form.phone_number"
          />
          <p :class="ui.hintText" class="mt-3">One way the ad can appear in Google results. Google picks the mix that performs best.</p>
        </section>

        <section class="p-6" :class="ui.card">
          <div class="flex items-center justify-between gap-3">
            <h3 :class="ui.panelHeading">Launch</h3>
            <BaseStatusBadge :tone="googleConnected ? 'success' : 'neutral'" :label="googleConnected ? 'Google Ads connected' : 'Not connected yet'" />
          </div>
          <ul class="mt-4 space-y-2 text-sm">
            <li v-for="check in checklist" :key="check.label" class="flex items-center gap-2.5" :class="check.done ? 'text-ink/80 dark:text-bone/80' : 'text-ink/50 dark:text-bone/50'">
              <span class="tick" :class="{ 'tick--done': check.done }" aria-hidden="true"></span>
              {{ check.label }}
            </li>
          </ul>
          <button type="button" class="mt-5 w-full" :class="ui.secondaryBtn" disabled>
            <i class="fas fa-lock text-xs" aria-hidden="true"></i>
            Launch on Google Ads
          </button>
          <p :class="ui.hintText" class="mt-3 leading-relaxed">
            Launching from Imagi isn't available yet. Your plan is saved here, nothing is sent to Google, and nothing is spent.
            <router-link v-if="!googleConnected" :to="{ name: 'marketing-settings', params: { projectName } }" :class="ui.inlineLink">Connect Google Ads</router-link>
          </p>
        </section>
      </aside>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LoadingSpinner, StatusBadge as BaseStatusBadge } from '@/shared/components'
import GoogleAdPreview from '../components/GoogleAdPreview.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { AdDraft, AdGoal } from '../types'
import { formatCurrency, ui } from '../utils/ui'

const HEADLINE_MAX = 30
const DESCRIPTION_MAX = 90

const route = useRoute()
const router = useRouter()
const store = useMarketingStore()

const projectName = computed(() => String(route.params.projectName))
const draftId = ref<number | null>(route.params.draftId ? Number(route.params.draftId) : null)

const form = reactive({
  name: '',
  goal: 'website' as AdGoal,
  final_url: '',
  phone_number: '',
  headlines: ['', '', ''],
  descriptions: ['', ''],
  keywords: [] as string[],
  location: '',
  daily_budget: '' as string | number,
})

const keywordInput = ref('')
const loading = ref(Boolean(draftId.value))
const loadError = ref('')
const saving = ref(false)
const saved = ref(false)
const saveError = ref('')
const deleting = ref(false)

const headlinePlaceholders = ['Fresh espresso downtown', 'Order ahead, skip the line', 'Open every day at 6am']

const goalOptions: { value: AdGoal; label: string; hint: string; icon: string }[] = [
  { value: 'website', label: 'Website visits', hint: 'Send people to a page of your app.', icon: 'fa-arrow-pointer' },
  { value: 'calls', label: 'Phone calls', hint: 'Let people call you from the ad.', icon: 'fa-phone' },
]

const googleConnected = computed(() =>
  store.adConnections.some(c => c.provider === 'google' && c.is_configured)
)

// The project's name stands in for the business on the preview's site line.
const projectTitle = computed(() => projectName.value.replace(/-/g, ' ').replace(/\b\w/g, ch => ch.toUpperCase()))

const monthlyCap = computed(() => {
  const daily = Number(form.daily_budget)
  return daily > 0 ? formatCurrency(Math.round(daily * 30.4), 'USD') : ''
})

const checklist = computed(() => [
  { label: 'Landing page', done: Boolean(form.final_url) },
  { label: 'Three headlines', done: form.headlines.filter(h => h.trim()).length >= 3 },
  { label: 'A description', done: form.descriptions.some(d => d.trim()) },
  { label: 'Keywords', done: form.keywords.length > 0 },
  { label: 'Daily budget', done: Number(form.daily_budget) > 0 },
  { label: 'Google Ads connected', done: googleConnected.value },
])

function addKeyword() {
  const words = keywordInput.value.split(',').map(w => w.trim()).filter(Boolean)
  for (const word of words) {
    if (!form.keywords.some(k => k.toLowerCase() === word.toLowerCase())) form.keywords.push(word)
  }
  keywordInput.value = ''
}

function removeKeyword(keyword: string) {
  form.keywords = form.keywords.filter(k => k !== keyword)
}

function fill(draft: AdDraft) {
  form.name = draft.name
  form.goal = draft.goal
  form.final_url = draft.final_url
  form.phone_number = draft.phone_number
  form.headlines = [...draft.headlines, '', '', ''].slice(0, Math.max(3, draft.headlines.length))
  form.descriptions = [...draft.descriptions, '', ''].slice(0, Math.max(2, draft.descriptions.length))
  form.keywords = [...draft.keywords]
  form.location = draft.location
  form.daily_budget = draft.daily_budget ?? ''
}

async function save() {
  addKeyword()
  saving.value = true
  saveError.value = ''
  try {
    const draft = await store.saveAdDraft(draftId.value, {
      name: form.name,
      goal: form.goal,
      final_url: form.final_url.trim(),
      phone_number: form.goal === 'calls' ? form.phone_number.trim() : '',
      headlines: form.headlines,
      descriptions: form.descriptions,
      keywords: form.keywords,
      location: form.location.trim(),
      daily_budget: form.daily_budget === '' ? null : String(form.daily_budget),
    })
    saved.value = true
    if (draftId.value === null) {
      draftId.value = draft.id
      router.replace({ name: 'marketing-ad-draft', params: { projectName: projectName.value, draftId: draft.id } })
    }
  } catch (error) {
    saveError.value = extractError(error, 'Could not save the ad.')
  } finally {
    saving.value = false
  }
}

async function remove() {
  if (draftId.value === null || !window.confirm('Delete this ad draft?')) return
  deleting.value = true
  try {
    await store.deleteAdDraft(draftId.value)
    router.push({ name: 'marketing-overview', params: { projectName: projectName.value } })
  } catch (error) {
    saveError.value = extractError(error, 'Could not delete the ad.')
    deleting.value = false
  }
}

// Any edit after a save turns the button back into "Save draft".
watch(form, () => { saved.value = false }, { deep: true })

onMounted(async () => {
  store.fetchAdConnections().catch(() => { /* The launch panel just shows "not connected". */ })
  if (draftId.value === null) return
  try {
    fill(await store.getAdDraft(draftId.value))
  } catch (error) {
    loadError.value = extractError(error, 'Could not load this ad.')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.step {
  margin-top: 1.75rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--sl-line);
  display: grid;
  gap: 1.25rem;
}

.step__title {
  /* Floated so it lays out as an ordinary grid row, not on the border. */
  float: left;
  width: 100%;
  padding: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--sl-text);
}

.counter {
  position: absolute;
  right: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.6875rem;
  font-variant-numeric: tabular-nums;
  color: var(--sl-muted);
  pointer-events: none;
}

.counter--area {
  top: auto;
  bottom: 0.625rem;
  transform: none;
}

.counter--full {
  color: var(--sl-coral);
}

/* The design system's diamond tick: hollow until the step is done, then lit. */
.tick {
  width: 7px;
  height: 7px;
  flex-shrink: 0;
  transform: rotate(45deg);
  border: 1px solid var(--sl-line-strong);
}

.tick--done {
  border-color: transparent;
  background: var(--sl-grad);
}
</style>
