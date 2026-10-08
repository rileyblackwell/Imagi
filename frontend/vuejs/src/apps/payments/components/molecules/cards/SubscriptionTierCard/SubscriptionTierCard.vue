<template>
  <div class="tier" :class="{ 'tier--featured': isPopular }">
    <!-- Name, and the one mark that distinguishes the recommended plan -->
    <div class="tier__head">
      <h3 class="tier__name">{{ name }}</h3>
      <span v-if="isPopular" class="tier__flag">Most popular</span>
    </div>

    <!-- Price -->
    <p class="tier__price">
      ${{ active.price }}<span class="tier__period">/month</span>
    </p>

    <!-- Usage option selector (Max-style tiers pick between 5× and 10×) -->
    <div
      v-if="options && options.length> 1"
      class="tier__options"
      role="tablist"
      aria-label="Usage amount"
    >
      <button
        v-for="(opt, i) in options"
        :key="opt.lookupKey"
        type="button"
        role="tab"
        :aria-selected="selected === i"
        class="tier__option"
        :class="{ 'is-selected': selected === i }"
        @click="selected = i"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- How the allowance is actually delivered -->
    <dl class="tier__limits">
      <div>
        <dt>Per week</dt>
        <dd>{{ active.weeklyLimit }}</dd>
      </div>
    </dl>

    <ul class="checklist tier__features">
      <li v-for="feature in active.features" :key="feature">
        <span class="checklist__tick" aria-hidden="true"></span>
        <span>{{ feature }}</span>
      </li>
    </ul>

    <button
      class="tier__cta"
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

<style scoped>
/* A plan card on the Spotlight stage (shared/styles/spotlight.css). The plans
   are quiet cards; the recommended one stands in the light, edged with the
   glowing gradient of the home page's prompt bar. Every colour is a --sl-*
   token, so both themes come from spotlight.css. */
.tier {
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 30px 28px 28px;
  border: 1px solid var(--sl-line);
  border-radius: 22px;
  background: var(--sl-card-bg);
  box-shadow: var(--sl-card-shadow);
  transition: border-color 0.25s ease, transform 0.25s ease;
}

.tier:hover {
  border-color: var(--sl-line-strong);
  transform: translateY(-2px);
}

.tier--featured,
.tier--featured:hover {
  border-color: transparent;
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-prompt-edge) border-box;
  box-shadow: var(--sl-prompt-shadow);
}

.tier__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  min-height: 1.75rem;
}

.tier__name {
  margin: 0;
  font-family: var(--sl-font-display);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--sl-text);
}

.tier__flag {
  padding: 4px 10px;
  border: 1px solid var(--sl-warm-line);
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 650;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  white-space: nowrap;
  background: var(--sl-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.tier__price {
  margin: 18px 0 0;
  font-family: var(--sl-font-display);
  font-size: clamp(44px, 4.6vw, 56px);
  font-weight: 800;
  font-variation-settings: 'opsz' 96;
  letter-spacing: -0.04em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  color: var(--sl-text);
}

.tier--featured .tier__price {
  filter: drop-shadow(0 0 26px var(--sl-text-glow));
}

.tier__period {
  margin-left: 0.4rem;
  font-family: var(--sl-font-body);
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0;
  color: var(--sl-faint);
}

.tier__options {
  display: flex;
  gap: 4px;
  margin-top: 22px;
  padding: 4px;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-chip-bg);
}

.tier__option {
  flex: 1;
  padding: 0.45rem 0.5rem;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  color: var(--sl-muted);
  transition: color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.tier__option:hover {
  color: var(--sl-text);
}

.tier__option.is-selected {
  background: var(--sl-surface);
  color: var(--sl-text);
  box-shadow: 0 0 0 1px var(--sl-line-strong), 0 4px 14px -6px var(--sl-glow);
}

.tier__option:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 2px;
}

.tier__limits {
  margin: 22px 0 0;
  padding: 14px 16px;
  border: 1px solid var(--sl-line);
  border-radius: 14px;
  background: var(--sl-chip-bg);
}

.tier__limits dt {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-faint);
}

.tier__limits dd {
  margin: 0.25rem 0 0;
  font-size: 15.5px;
  font-weight: 600;
  color: var(--sl-text);
}

/* Two-selector form so this beats `.editorial .checklist`'s `margin-top: auto`
   — the CTA below owns the auto margin, so the buttons line up across plans
   regardless of how many features each one lists. */
.tier .tier__features {
  margin-top: 24px;
  margin-bottom: 28px;
  color: var(--sl-muted);
}

.tier__cta {
  width: 100%;
  margin-top: auto;
  justify-content: center;
}

@media (max-width: 560px) {
  .tier {
    padding: 24px 22px 22px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .tier {
    transition: none;
  }
  .tier:hover {
    transform: none;
  }
}
</style>
