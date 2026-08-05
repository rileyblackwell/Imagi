<template>
  <div class="tier" :class="{ 'tier--featured': isPopular }">
    <!-- Name, and the one mark that distinguishes the recommended plan -->
    <div class="tier__head">
      <h3 class="tier__name">{{ name }}</h3>
      <span v-if="isPopular" class="tier__flag">Most popular</span>
    </div>

    <!-- Price -->
    <p class="tier__price display">
      {{ active.price === 0 ? 'Free' : `$${active.price}` }}<span
        v-if="active.price !== 0"
        class="tier__period"
      >/month</span>
    </p>

    <!-- Usage option selector (Max-style tiers pick between 5× and 20×) -->
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
        <dt>Every 5 hours</dt>
        <dd>{{ active.sessionLimit }}</dd>
      </div>
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
      :disabled="loading"
      @click="$emit('subscribe', active.lookupKey)"
    >
      <span v-if="loading" class="inline-flex items-center gap-2">
        <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        Processing…
      </span>
      <span v-else>{{ cta ?? 'Get started' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface TierOption {
  label: string
  price: number
  lookupKey: string
  sessionLimit: string
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
  sessionLimit?: string
  weeklyLimit?: string
  features?: string[]
  // …multi-option tiers (e.g. Max) pass these instead.
  options?: TierOption[]
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
    sessionLimit: props.sessionLimit ?? '',
    weeklyLimit: props.weeklyLimit ?? '',
    features: props.features ?? [],
  }
})
</script>

<style scoped>
/* A ruled column rather than a floating card — the plans read as one table of
   options, which is what they are. The featured plan is marked by a heavier
   top rule and a small label, not by a coloured border and a shadow. */
.tier {
  display: flex;
  flex-direction: column;
  padding: 2rem 0 0;
  border-top: 1px solid var(--rule);
}

.tier--featured {
  border-top-color: var(--accent);
}

@media (min-width: 768px) {
  .tier {
    padding: 2rem 2rem 0 0;
  }

  .tier + .tier {
    padding-left: 2rem;
    border-left: 1px solid var(--rule);
  }
}

.tier__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  min-height: 1.5rem;
}

.tier__name {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ink-55);
}

.tier__flag {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--accent);
  white-space: nowrap;
}

.tier__price {
  margin-top: 1rem;
  font-size: 2.75rem;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.tier__period {
  font-family: 'Instrument Sans', system-ui, sans-serif;
  font-size: 0.9rem;
  font-weight: 400;
  color: var(--ink-40);
  margin-left: 0.35rem;
}

.tier__options {
  display: flex;
  gap: 0.4rem;
  margin-top: 1.5rem;
}

.tier__option {
  flex: 1;
  padding: 0.45rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--rule-strong);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink-55);
  transition: color 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.tier__option:hover {
  color: var(--ink);
}

.tier__option.is-selected {
  background: var(--ink);
  border-color: var(--ink);
  color: var(--paper);
}

.tier__option:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.tier__limits {
  margin-top: 1.75rem;
  display: grid;
  gap: 0.85rem;
}

.tier__limits dt {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-40);
}

.tier__limits dd {
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
  color: var(--ink-70);
}

/* Two-selector form so this beats `.editorial .checklist`'s `margin-top: auto`
   — the CTA below owns the auto margin, so the buttons line up across plans
   regardless of how many features each one lists. */
.tier .tier__features {
  margin-top: 2rem;
  margin-bottom: 2rem;
}

.tier__cta {
  width: 100%;
  margin-top: auto;
}
</style>
