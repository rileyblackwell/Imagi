<!--
  SellPayments.vue - Gallery of prebuilt payment pages the user can drop
  into their generated app with one click. These are the safe path to
  taking payments: Stripe-hosted checkout, prices from the Sell catalog,
  no keys or card handling inside the user's app.
-->
<template>
  <div>
    <!-- Intro -->
    <div class="mb-6" :class="ui.infoBox">
      <div class="flex items-start gap-3">
      <i class="fas fa-shield-halved mt-0.5"></i>
        <p>
          Add payments to your app without writing any payment code. Pick a prebuilt page below and
          we'll drop it into your project — customers pay on Stripe's secure checkout page, and every
          sale shows up in this workspace. Card details never touch your app.
        </p>
      </div>
    </div>

    <!-- Stripe not connected yet -->
    <div
      v-if="!store.isConfigured"
      class="flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-2xl border border-amber-200/80 dark:border-amber-400/25 bg-amber-50/80 dark:bg-amber-400/10 mb-6 transition-colors duration-300"
    >
      <div class="flex items-center gap-3 flex-1 min-w-0">
        <i class="fas fa-plug-circle-bolt text-amber-600 dark:text-amber-300"></i>
        <p class="text-sm text-amber-900 dark:text-amber-100">
          You can add these pages now, but customers can't pay until Stripe is connected in Settings.
        </p>
      </div>
      <router-link
        :to="{ name: 'sell-settings', params: { projectName: route.params.projectName } }"
        class="shrink-0"
        :class="ui.secondaryBtn"
      >
        Connect Stripe
      </router-link>
    </div>

    <div v-if="actionError" class="mb-6" :class="ui.errorBox">{{ actionError }}</div>

    <!-- Install success -->
    <div v-if="installedNotice" class="mb-6" :class="ui.successBox">
      <div class="flex items-start gap-3">
        <i class="fas fa-circle-check mt-0.5"></i>
        <div>
          <p class="font-medium mb-1">{{ installedNotice.name }} added to your app</p>
          <p>
            It's live at the <code class="font-mono">{{ installedNotice.route }}</code> page of your app.
            <router-link
              :to="{ name: 'builder-workspace', params: { projectName: route.params.projectName } }"
              class="underline hover:no-underline"
            >
              Open the Build workspace
            </router-link>
            to preview it, or keep customizing the look with AI — the payment flow stays secure either way.
          </p>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.templatesLoading && !store.templates.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
    </div>

    <!-- Gallery -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="template in store.templates" :key="template.key" class="p-6 flex flex-col" :class="ui.card">
        <div class="flex items-start justify-between gap-3 mb-3">
          <div class="w-11 h-11 text-lg" :class="ui.iconTile">
            <i :class="['fas', template.icon]"></i>
          </div>
          <span
            v-if="template.installed"
            class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-[11px] font-semibold uppercase tracking-[0.1em] text-emerald-700 dark:text-emerald-300"
          >
            <i class="fas fa-check text-[9px]"></i>
            In your app
          </span>
        </div>

        <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-1">{{ template.name }}</h2>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">{{ template.description }}</p>

        <ul class="space-y-2 mb-6">
          <li
            v-for="feature in template.features"
            :key="feature"
            class="flex items-start gap-2.5 text-sm text-blue-950/70 dark:text-blue-100/70"
          >
            <i class="fas fa-check text-xs text-emerald-600 dark:text-emerald-300 mt-1"></i>
            {{ feature }}
          </li>
        </ul>

        <div class="flex items-center gap-3 mt-auto">
          <button
            type="button"
            :class="ui.primaryBtn"
            :disabled="installingKey !== null"
            @click="install(template)"
          >
            <i :class="['fas', installingKey === template.key ? 'fa-circle-notch animate-spin' : (template.installed ? 'fa-rotate' : 'fa-plus')]" class="text-xs"></i>
            {{ template.installed ? 'Reinstall' : 'Add to my app' }}
          </button>
          <span class="text-xs text-blue-950/50 dark:text-blue-100/50 font-mono">{{ template.route }}</span>
        </div>
      </div>

      <!-- No-code option: payment links -->
      <div class="p-6 flex flex-col" :class="ui.card">
        <div class="flex items-start justify-between gap-3 mb-3">
          <div class="w-11 h-11 text-lg" :class="ui.iconTile">
            <i class="fas fa-link"></i>
          </div>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full border border-blue-950/10 dark:border-white/15 bg-blue-950/[0.03] dark:bg-white/[0.04] text-[11px] font-semibold uppercase tracking-[0.1em] text-blue-950/60 dark:text-white/60">
            No code
          </span>
        </div>

        <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-1">Payment links</h2>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">
          No page needed — copy a secure Stripe Checkout link for any product and share it in a text,
          an email, or on social media.
        </p>

        <ul class="space-y-2 mb-6">
          <li
            v-for="feature in paymentLinkFeatures"
            :key="feature"
            class="flex items-start gap-2.5 text-sm text-blue-950/70 dark:text-blue-100/70"
          >
            <i class="fas fa-check text-xs text-emerald-600 dark:text-emerald-300 mt-1"></i>
            {{ feature }}
          </li>
        </ul>

        <div class="flex items-center gap-3 mt-auto">
          <router-link
            :to="{ name: 'sell-products', params: { projectName: route.params.projectName } }"
            :class="ui.secondaryBtn"
          >
            <i class="fas fa-box-open text-xs"></i>
            Go to products
          </router-link>
        </div>
      </div>
    </div>

    <!-- How it stays secure -->
    <section class="mt-8 p-6" :class="ui.card">
      <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-3">How these stay secure</h2>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div v-for="point in securityPoints" :key="point.title" class="flex items-start gap-3">
          <div class="w-9 h-9 shrink-0 text-sm" :class="ui.iconTile">
            <i :class="['fas', point.icon]"></i>
          </div>
          <div>
            <p class="text-sm font-medium text-blue-950 dark:text-white mb-0.5">{{ point.title }}</p>
            <p class="text-xs text-blue-950/60 dark:text-blue-100/60">{{ point.text }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { PaymentTemplate, TemplateInstallResult } from '../types'
import { ui } from '../utils/ui'

const route = useRoute()
const store = useSellStore()

const installingKey = ref<string | null>(null)
const installedNotice = ref<TemplateInstallResult | null>(null)
const actionError = ref('')

const paymentLinkFeatures = [
  'One click per product — the link is ready to share',
  'Works anywhere: texts, emails, Instagram bio',
  'Same secure Stripe checkout as the built-in pages',
]

const securityPoints = [
  {
    icon: 'fa-lock',
    title: 'Stripe handles the card',
    text: 'Customers pay on Stripe\'s hosted checkout page, so card numbers never touch your app.',
  },
  {
    icon: 'fa-key',
    title: 'No keys in your app',
    text: 'Your Stripe keys stay encrypted on Imagi\'s servers. The pages we add contain no secrets.',
  },
  {
    icon: 'fa-tag',
    title: 'Prices can\'t be tampered with',
    text: 'Checkout always charges your catalog price — a modified request can\'t change the amount.',
  },
]

async function install(template: PaymentTemplate) {
  installingKey.value = template.key
  installedNotice.value = null
  actionError.value = ''
  try {
    installedNotice.value = await store.installTemplate(template.key)
  } catch (error) {
    actionError.value = extractError(error, 'Could not add the template to your app.')
  } finally {
    installingKey.value = null
  }
}

onMounted(async () => {
  try {
    await store.fetchTemplates()
  } catch (error) {
    actionError.value = extractError(error, 'Could not load the payment templates.')
  }
})
</script>
