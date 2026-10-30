<template>
  <!-- A plan card on the Spotlight stage. The plans are quiet cards; the
       recommended one stands in the light, edged with the glowing gradient of
       the home page's prompt bar. -->
  <div
    class="tier relative flex min-w-0 flex-col rounded-[22px] border pt-[30px] px-7 pb-7
      [transition:border-color_0.25s_ease,transform_0.25s_ease] hover:-translate-y-0.5
      max-[560px]:pt-6 max-[560px]:px-[22px] max-[560px]:pb-[22px]
      motion-reduce:[transition:none] motion-reduce:hover:transform-none"
    :class="isPopular
      ? 'tier--featured border-transparent [background:var(--sl-prompt-bg)_padding-box,var(--sl-prompt-edge)_border-box] shadow-sl-prompt'
      : 'border-sl-line hover:border-sl-line-strong bg-sl-card-bg shadow-sl-card'"
  >
    <!-- Name, and the one mark that distinguishes the recommended plan -->
    <div class="flex min-h-7 items-center justify-between gap-4">
      <h3 class="tier__name m-0 font-sl-display text-[22px] font-bold tracking-[-0.02em] text-sl-text">{{ name }}</h3>
      <span
        v-if="isPopular"
        class="whitespace-nowrap rounded-[999px] border border-sl-warm-line bg-sl-grad bg-clip-text px-2.5 py-1
          text-[10.5px] font-[650] uppercase tracking-[0.14em] text-transparent"
      >{{ flag ?? 'Most popular' }}</span>
    </div>

    <!-- Price -->
    <p
      class="mt-[18px] font-sl-display text-[clamp(44px,4.6vw,56px)] font-extrabold leading-none tracking-[-0.04em]
        tabular-nums text-sl-text [font-variation-settings:'opsz'_96]"
      :class="{ '[filter:drop-shadow(0_0_26px_var(--sl-text-glow))]': isPopular }"
    >
      ${{ active.price }}<span class="ml-[0.4rem] font-sl-body text-[15px] font-medium tracking-normal text-sl-faint">/month</span>
    </p>

    <!-- Usage option selector (Max-style tiers pick between 5× and 10×) -->
    <div
      v-if="options && options.length> 1"
      class="mt-[22px] flex gap-1 rounded-[999px] border border-sl-line bg-sl-chip-bg p-1"
      role="tablist"
      aria-label="Usage amount"
    >
      <button
        v-for="(opt, i) in options"
        :key="opt.lookupKey"
        type="button"
        role="tab"
        :aria-selected="selected === i"
        class="tier__option flex-1 rounded-[999px] px-2 py-[0.45rem] text-[13px] font-semibold
          [transition:color_0.18s_ease,background_0.18s_ease,box-shadow_0.18s_ease]
          focus-visible:outline focus-visible:outline-2 focus-visible:outline-sl-focus focus-visible:!outline-offset-2"
        :class="selected === i
          ? 'is-selected bg-sl-surface text-sl-text shadow-[0_0_0_1px_var(--sl-line-strong),0_4px_14px_-6px_var(--sl-glow)]'
          : 'text-sl-muted hover:text-sl-text'"
        @click="selected = i"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- How the allowance is actually delivered -->
    <dl class="tier__limits mt-[22px] rounded-[14px] border border-sl-line bg-sl-chip-bg px-4 py-3.5">
      <div>
        <dt class="text-[11px] font-semibold uppercase tracking-[0.16em] text-sl-faint">Per week</dt>
        <dd class="mt-1 text-[15.5px] font-semibold text-sl-text">{{ active.weeklyLimit }}</dd>
      </div>
    </dl>

    <!-- `!mt-6` beats `.editorial .checklist`'s `margin-top: auto`: the CTA
         below owns the auto margin, so the buttons line up across plans
         regardless of how many features each one lists. -->
    <ul class="checklist !mt-6 mb-7 text-sl-muted">
      <li v-for="feature in active.features" :key="feature">
        <span class="checklist__tick" aria-hidden="true"></span>
        <span>{{ feature }}</span>
      </li>
    </ul>

    <button
      class="tier__cta mt-auto w-full justify-center"
      :class="isPopular ? 'btn-primary' : 'btn-outline'"
      :disabled="loading || isCurrent"
      @click="$emit('subscribe', active.lookupKey)"
    >
      <span v-if="loading" class="inline-flex items-center gap-2">
        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        Processing…
      </span>
      <span v-else>{{ ctaLabel }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TierOption {
  label: string
  price: number
  lookupKey: string
  weeklyLimit: string
  features: string[]
}

const props = defineProps<{
  name: string
  cta?: string
  isPopular?: boolean
  // The featured card's flag; "Most popular" unless the page names it.
  flag?: string
  loading?: boolean
  // Single-option tiers pass these directly…
  price?: number
  lookupKey?: string | null
  weeklyLimit?: string
  features?: string[]
  // …multi-option tiers (e.g. Max) pass these instead.
  options?: TierOption[]
  // The signed-in user's plan, as its lookup key: null is Free, undefined is
  // unknown (signed out, or not loaded yet). A subscriber switches plans
  // rather than starting a new one, so the buttons say so.
  currentPlanKey?: string | null
}>()

defineEmits<{
  subscribe: [lookupKey: string | null]
}>()

const selected = ref(0)

// What's currently shown: the selected option for multi-option tiers,
// otherwise the tier's own props.
const active = computed(() => {
  const opt = props.options?.[selected.value]
  if (opt) return opt
  return {
    price: props.price ?? 0,
    lookupKey: props.lookupKey ?? null,
    weeklyLimit: props.weeklyLimit ?? '',
    features: props.features ?? [],
  }
})

const isCurrent = computed(
  () => props.currentPlanKey !== undefined && active.value.lookupKey === props.currentPlanKey
)

const ctaLabel = computed(() => {
  if (isCurrent.value) return 'Current plan'
  // A paying subscriber changes plan on their subscription; going to Free is
  // cancelling it, which happens in the billing portal.
  if (props.currentPlanKey) return active.value.lookupKey ? 'Switch to this plan' : 'Manage billing'
  return props.cta ?? 'Get started'
})
</script>
