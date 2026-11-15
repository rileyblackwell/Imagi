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
      ${{ price }}<span class="ml-[0.4rem] font-sl-body text-[15px] font-medium tracking-normal text-sl-faint">/month</span>
    </p>

    <!-- How the allowance is actually delivered -->
    <dl class="tier__limits mt-[22px] rounded-[14px] border border-sl-line bg-sl-chip-bg px-4 py-3.5">
      <div>
        <dt class="text-[11px] font-semibold uppercase tracking-[0.16em] text-sl-faint">Per week</dt>
        <dd class="mt-1 text-[15.5px] font-semibold text-sl-text">{{ weeklyLimit }}</dd>
      </div>
    </dl>

    <!-- `!mt-6` beats `.editorial .checklist`'s `margin-top: auto`: the CTA
         below owns the auto margin, so the buttons line up across plans
         regardless of how many features each one lists. -->
    <ul class="checklist !mt-6 mb-7 text-sl-muted">
      <li v-for="feature in features" :key="feature">
        <span class="checklist__tick" aria-hidden="true"></span>
        <span>{{ feature }}</span>
      </li>
    </ul>

    <button
      class="tier__cta mt-auto w-full justify-center"
      :class="isPopular ? 'btn-primary' : 'btn-outline'"
      @click="$emit('start')"
    >
      {{ cta ?? 'Get started' }}
    </button>
  </div>
</template>

<script setup lang="ts">
// A plan card. Free is the only plan, so the card just shows it and starts
// building; the paid plans' option selector and checkout states went with
// them.
defineProps<{
  name: string
  price: number
  weeklyLimit: string
  features: string[]
  cta?: string
  isPopular?: boolean
  // The featured card's flag; "Most popular" unless the page names it.
  flag?: string
}>()

defineEmits<{
  start: []
}>()
</script>
