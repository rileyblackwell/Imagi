<!--
  OperateDashboard.vue - Operate is a dashboard with two halves.

  Your app: is it up (uptime from Imagi's checks of the live address), is it
  fast (response time), and who is visiting (from the page-view tag). Your
  business: revenue (Sell payments plus income recorded in the ledger),
  expenses (the ledger) and profit. Three numbers a side, one chart under
  each, and an honest empty state wherever there is no data source yet.
-->
<template>
  <div>
    <LoadingSpinner v-if="store.dashboardLoading && !dashboard" />

    <div v-else-if="dashboard" class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
      <!-- ============================ Your app ============================ -->
      <section aria-labelledby="operate-app-heading" class="min-w-0 flex flex-col">
        <div class="flex items-center justify-between gap-3 mb-3 min-h-[1.75rem]">
          <h2 id="operate-app-heading" :class="halfLabel">Your app</h2>
          <!-- Up / down, in the status colours, never the coral of a button -->
          <p
            v-if="app.status"
            class="status-pill inline-flex items-center gap-[0.4rem] whitespace-nowrap rounded-[999px] border border-sl-line
              bg-sl-chip-bg px-[0.7rem] py-1 text-[0.6875rem] font-semibold text-sl-text"
          >
            <span
              class="h-[0.45rem] w-[0.45rem] rounded-[999px]"
              :class="app.status.is_up
                ? 'bg-sl-ok shadow-[0_0_0_3px_color-mix(in_srgb,var(--sl-ok)_22%,transparent)]'
                : 'bg-sl-bad shadow-[0_0_0_3px_color-mix(in_srgb,var(--sl-bad)_22%,transparent)]'"
              aria-hidden="true"
            ></span>
            <span>{{ app.status.is_up ? 'Up' : 'Down' }}</span>
            <span class="font-medium text-sl-muted">· checked {{ timeAgo(app.status.checked_at) }}</span>
          </p>
        </div>

        <div class="flex-1 flex flex-col" :class="ui.card">
          <!-- No live address yet: the one thing to do. -->
          <form v-if="!app.live_url || editing" class="p-6 border-b border-[color:var(--sl-line)]" @submit.prevent="saveLiveUrl">
            <label for="operate-live-url" :class="ui.panelHeading" class="block">Where does your app live?</label>
            <p :class="ui.bodyText" class="mt-1 mb-4">
              Add the address your customers visit. Imagi checks it for uptime and speed, and counts visitors once you add the page-view tag.
            </p>
            <div class="flex flex-col sm:flex-row gap-3">
              <input
                id="operate-live-url"
                v-model="liveUrlDraft"
                type="text"
                inputmode="url"
                autocomplete="url"
                placeholder="yourapp.com"
                :class="ui.input"
                :disabled="saving"
              />
              <button type="submit" :class="ui.primaryBtn" :disabled="saving || !liveUrlDraft.trim()">
                {{ saving ? 'Checking…' : (editing ? 'Save address' : 'Start monitoring') }}
              </button>
              <button v-if="editing" type="button" :class="ui.secondaryBtn" :disabled="saving" @click="editing = false">
                Cancel
              </button>
            </div>
            <p v-if="saveError" class="mt-3 text-sm text-[color:var(--sl-bad)]">{{ saveError }}</p>
          </form>

          <!-- Three numbers -->
          <!-- Three numbers across, split by hairlines rather than boxed -->
          <dl class="grid grid-cols-3 border-b border-b-sl-line">
            <div :class="statCell">
              <dt :class="statLabel">Uptime</dt>
              <dd :class="statValue">{{ app.uptime.percent === null ? '—' : formatPercent(app.uptime.percent) }}</dd>
              <dd :class="statCaption">{{ uptimeCaption }}</dd>
            </div>
            <div :class="[statCell, 'border-l border-l-sl-line']">
              <dt :class="statLabel">Response</dt>
              <dd :class="statValue">{{ app.response_ms.latest === null ? '—' : formatMs(app.response_ms.latest) }}</dd>
              <dd :class="statCaption">{{ responseCaption }}</dd>
            </div>
            <div :class="[statCell, 'border-l border-l-sl-line']">
              <dt :class="statLabel">Visitors</dt>
              <dd :class="statValue">{{ app.live_url ? app.traffic.visitors.toLocaleString() : '—' }}</dd>
              <dd :class="statCaption">
                {{ app.traffic.page_views ? `${app.traffic.page_views.toLocaleString()} page view${app.traffic.page_views === 1 ? '' : 's'}, 30 days` : 'last 30 days' }}
              </dd>
            </div>
          </dl>

          <div class="px-6 pt-5 pb-6 flex-1">
            <p :class="ui.hintText" class="mb-3">Visitors per day, last two weeks</p>
            <VisitorsChart
              :days="app.traffic.daily"
              :empty-text="app.live_url ? 'No visitors counted yet. Add the page-view tag below to your app.' : 'Visitors show up here once your app is live.'"
            />
          </div>

          <!-- Live address, check now, and the page-view tag -->
          <div v-if="app.live_url && !editing" class="px-6 py-4 border-t border-[color:var(--sl-line)] space-y-3">
            <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
              <a :href="app.live_url" target="_blank" rel="noopener noreferrer" :class="ui.textLink" class="truncate max-w-full">
                {{ displayUrl(app.live_url) }}
              </a>
              <span class="flex-1"></span>
              <button type="button" :class="ui.textLink" :disabled="checking" @click="checkNow">
                {{ checking ? 'Checking…' : 'Check now' }}
              </button>
              <button type="button" :class="ui.textLink" @click="editLiveUrl">Change address</button>
            </div>
            <p v-if="app.status && !app.status.is_up && app.status.error" class="text-sm text-[color:var(--sl-bad)]">
              {{ app.status.error }}
            </p>
            <p v-if="checkError" class="text-sm text-[color:var(--sl-bad)]">{{ checkError }}</p>

            <details :open="!app.traffic.page_views">
              <summary
                :class="ui.panelHeading"
                class="tag__summary inline-flex cursor-pointer items-center [list-style:none] gap-2 text-sm
                  before:h-[0.4rem] before:w-[0.4rem] before:[transform:rotate(45deg)] before:bg-sl-grad before:content-['']"
              >Page-view tag</summary>
              <p :class="ui.bodyText" class="mt-2">
                Paste this into your app's <code class="text-[0.8125rem]">index.html</code>, just before <code class="text-[0.8125rem]">&lt;/head&gt;</code>, or ask Build to add it. It sets no cookies and only counts visits to {{ displayHost(app.live_url) }}.
              </p>
              <div class="mt-3 relative">
                <pre
                  class="tag__code m-0 max-h-36 overflow-auto whitespace-pre-wrap break-all rounded-xl border border-sl-line bg-sl-chip-bg
                    py-[0.9rem] pl-4 pr-20 text-sl-text"
                ><code class="text-[0.75rem] leading-[1.55]">{{ trackingTag }}</code></pre>
                <button type="button" :class="ui.secondaryBtn" class="absolute right-[0.6rem] top-[0.6rem] !px-3 !py-1.5 text-xs" @click="copyTag">
                  {{ copied ? 'Copied' : 'Copy' }}
                </button>
              </div>
            </details>
          </div>
        </div>
      </section>

      <!-- ========================== Your business ========================== -->
      <section aria-labelledby="operate-business-heading" class="min-w-0 flex flex-col">
        <div class="flex items-center justify-between gap-3 mb-3 min-h-[1.75rem]">
          <h2 id="operate-business-heading" :class="halfLabel">Your business</h2>
          <p :class="ui.hintText">last 30 days</p>
        </div>

        <div class="flex-1 flex flex-col" :class="ui.card">
          <!-- Three numbers across, split by hairlines rather than boxed -->
          <dl class="grid grid-cols-3 border-b border-b-sl-line">
            <div :class="statCell">
              <dt :class="statLabel">Revenue</dt>
              <dd :class="statValue">{{ money(business.revenue_30d) }}</dd>
              <dd :class="statCaption">{{ revenueCaption }}</dd>
            </div>
            <div :class="[statCell, 'border-l border-l-sl-line']">
              <dt :class="statLabel">Expenses</dt>
              <dd :class="statValue">{{ money(business.expenses_30d) }}</dd>
              <dd :class="statCaption">from your ledger</dd>
            </div>
            <div :class="[statCell, 'border-l border-l-sl-line']">
              <dt :class="statLabel">Profit</dt>
              <dd :class="statValue">{{ money(business.profit_30d) }}</dd>
              <dd :class="statCaption">revenue minus expenses</dd>
            </div>
          </dl>

          <div class="px-6 pt-5 pb-6 flex-1">
            <p :class="ui.hintText" class="mb-3">Month by month</p>
            <CashflowChart
              :points="business.monthly"
              income-label="Revenue"
              net-label="Profit"
              :currency="business.currency"
              empty-text="Nothing yet. Take payments through Sell, or record income and expenses in the ledger."
            />
          </div>

          <div class="px-6 py-4 border-t border-[color:var(--sl-line)] flex flex-wrap items-center gap-x-4 gap-y-2">
            <p v-if="!business.sell_connected" :class="ui.bodyText" class="flex-1 min-w-[12rem]">
              Connect Stripe in Sell and payments count as revenue here.
            </p>
            <span v-else class="flex-1"></span>
            <router-link v-if="!business.sell_connected" :to="{ name: 'sell-overview', params: { projectName: route.params.projectName } }" :class="ui.textLink">
              Open Sell
            </router-link>
            <router-link :to="{ name: 'operate-finance', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.textLink">
              Record income or an expense
            </router-link>
          </div>
        </div>
      </section>
    </div>

    <div v-else-if="loadError" :class="ui.errorBox">{{ loadError }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { LoadingSpinner } from '@/shared/components'
import CashflowChart from '../components/CashflowChart.vue'
import VisitorsChart from '../components/VisitorsChart.vue'
import { extractError } from '../services/operateService'
import { useOperateStore } from '../stores/operate'
import { formatMoney, ui } from '../utils/ui'

const route = useRoute()
const store = useOperateStore()

// Each half is titled like the hub's eyebrows: small, tracked, uppercase.
const halfLabel = 'text-[0.75rem] font-semibold uppercase tracking-[0.18em] text-sl-muted'

// One of the three numbers across a half (`stat__value` is a test hook).
const statCell = 'min-w-0 px-6 pb-[1.35rem] pt-5 max-[520px]:px-[0.9rem] max-[520px]:pb-[1.1rem] max-[520px]:pt-4'
const statLabel = 'text-[0.75rem] font-semibold uppercase tracking-[0.14em] text-sl-muted'
const statValue =
  'stat__value mt-2 truncate text-[1.625rem] font-semibold leading-[1.15] tabular-nums text-sl-text max-[520px]:text-[1.25rem]'
const statCaption = 'mt-[0.3rem] text-[0.75rem] leading-[1.4] text-sl-muted'
const loadError = ref('')

const dashboard = computed(() => store.dashboard)
const app = computed(() => store.dashboard!.app)
const business = computed(() => store.dashboard!.business)

// -- The app half ------------------------------------------------------------------

const liveUrlDraft = ref('')
const editing = ref(false)
const saving = ref(false)
const saveError = ref('')
const checking = ref(false)
const checkError = ref('')
const copied = ref(false)

async function saveLiveUrl() {
  saving.value = true
  saveError.value = ''
  try {
    await store.setLiveUrl(liveUrlDraft.value)
    editing.value = false
  } catch (error) {
    saveError.value = extractError(error, 'Could not save that address.')
  } finally {
    saving.value = false
  }
}

function editLiveUrl() {
  liveUrlDraft.value = app.value.live_url
  saveError.value = ''
  editing.value = true
}

async function checkNow() {
  checking.value = true
  checkError.value = ''
  try {
    await store.checkApp()
  } catch (error) {
    checkError.value = extractError(error, 'Could not check your app right now.')
  } finally {
    checking.value = false
  }
}

const uptimeCaption = computed(() => {
  const { checks } = app.value.uptime
  if (!app.value.live_url) return 'add your live address'
  return `${checks.toLocaleString()} check${checks === 1 ? '' : 's'}, 30 days`
})

const responseCaption = computed(() => {
  const { median } = app.value.response_ms
  if (!app.value.live_url) return 'time to first byte'
  return median === null ? 'time to first byte' : `typical ${formatMs(median)}`
})

/** The tag a live app pastes in. Posts to this Imagi's own API origin. */
const trackingTag = computed(() => {
  const endpoint = `${window.location.origin}/api/v1/operate/beacon/${app.value.site_key}/`
  const close = '</' + 'script>'
  return `<script>(function(){var u="${endpoint}";function s(f){try{navigator.sendBeacon(u,JSON.stringify({p:location.pathname,r:f?document.referrer:""}))}catch(e){}}var h=history.pushState;history.pushState=function(){h.apply(this,arguments);s()};addEventListener("popstate",function(){s()});s(1)})()${close}`
})

async function copyTag() {
  try {
    await navigator.clipboard.writeText(trackingTag.value)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    copied.value = false
  }
}

// -- The business half ---------------------------------------------------------------

function money(value: number): string {
  return formatMoney(value, business.value.currency)
}

const revenueCaption = computed(() => {
  const { revenue_sell_30d: sell, revenue_recorded_30d: recorded } = business.value
  if (sell && recorded) return `${money(sell)} from Sell, ${money(recorded)} recorded`
  if (sell) return 'from Sell payments'
  if (recorded) return 'recorded in your ledger'
  return 'Sell payments and recorded income'
})

// -- Formatting -------------------------------------------------------------------------

function formatPercent(value: number): string {
  return `${value >= 99.995 ? '100' : value.toFixed(value >= 99 ? 2 : 1)}%`
}

function formatMs(value: number): string {
  return value >= 1000 ? `${(value / 1000).toFixed(1)} s` : `${value} ms`
}

function displayHost(url: string): string {
  try {
    return new URL(url).host
  } catch {
    return url
  }
}

function displayUrl(url: string): string {
  return url.replace(/^https?:\/\//, '').replace(/\/$/, '')
}

function timeAgo(iso: string): string {
  const seconds = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000))
  if (seconds < 60) return 'just now'
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours} h ago`
  const days = Math.round(hours / 24)
  return `${days} day${days === 1 ? '' : 's'} ago`
}

onMounted(async () => {
  try {
    const data = await store.fetchDashboard()
    // Re-check the live app when the last check is old, after the page is up.
    if (data.app.check_stale) {
      checking.value = true
      store.checkApp(true).catch(() => {}).finally(() => { checking.value = false })
    }
  } catch (error) {
    loadError.value = extractError(error, 'Could not load the operate dashboard.')
  }
})
</script>

<style scoped>
/* WebKit draws the summary's disclosure triangle unless it is hidden here. */
.tag__summary::-webkit-details-marker {
  display: none;
}
</style>
