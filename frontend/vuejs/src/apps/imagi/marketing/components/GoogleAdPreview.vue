<!--
  GoogleAdPreview.vue - Roughly how a responsive search ad reads on a Google
  results page: the Sponsored label, the site, up to three headlines joined by
  pipes and the descriptions under them. Google mixes and matches headlines,
  so this is one likely arrangement, not a promise.
-->
<template>
  <div class="ad rounded-xl border border-[color:var(--sl-line)] bg-white dark:bg-white/[0.04] p-5">
    <p class="text-xs font-semibold text-ink dark:text-bone">Sponsored</p>
    <div class="mt-2.5 flex items-center gap-2.5 min-w-0">
      <span class="w-7 h-7 shrink-0 rounded-full border border-[color:var(--sl-line)] bg-[color:var(--sl-chip-bg)] flex items-center justify-center text-[11px] font-semibold uppercase text-ink/70 dark:text-bone/70">
        {{ initial }}
      </span>
      <div class="min-w-0 leading-tight">
        <p class="text-sm text-ink dark:text-bone truncate">{{ siteName }}</p>
        <p class="text-xs text-ink/55 dark:text-bone/55 truncate">{{ displayUrl }}</p>
      </div>
    </div>
    <p class="ad__headline mt-2.5 text-lg leading-snug text-[color:var(--sl-cool)]" :class="{ 'opacity-50': !headlineText }">
      {{ headlineText || 'Your headline appears here' }}
    </p>
    <p class="mt-1.5 text-sm leading-relaxed text-ink/70 dark:text-bone/70" :class="{ 'opacity-50': !descriptionText }">
      {{ descriptionText || 'Your description appears here. Say what you offer and why someone should click.' }}
    </p>
    <p v-if="goal === 'calls' && phoneNumber" class="mt-3 inline-flex items-center gap-2 text-sm text-[color:var(--sl-cool)]">
      <i class="fas fa-phone text-xs" aria-hidden="true"></i>
      Call {{ phoneNumber }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AdGoal } from '../types'

const props = defineProps<{
  headlines: string[]
  descriptions: string[]
  finalUrl: string
  /** Fallback for the site line when there's no landing page yet. */
  businessName: string
  goal: AdGoal
  phoneNumber?: string
}>()

const host = computed(() => {
  try {
    return new URL(props.finalUrl).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
})

const siteName = computed(() => props.businessName || host.value || 'Your business')
const initial = computed(() => siteName.value.charAt(0) || 'i')

const displayUrl = computed(() => {
  if (!host.value) return 'www.yourbusiness.com'
  try {
    const path = new URL(props.finalUrl).pathname.replace(/\/$/, '')
    return path ? `https://${host.value} › ${path.slice(1).split('/').join(' › ')}` : `https://${host.value}`
  } catch {
    return host.value
  }
})

const headlineText = computed(() =>
  props.headlines.map(h => h.trim()).filter(Boolean).slice(0, 3).join(' | ')
)

const descriptionText = computed(() =>
  props.descriptions.map(d => d.trim()).filter(Boolean).slice(0, 2).join(' ')
)
</script>
