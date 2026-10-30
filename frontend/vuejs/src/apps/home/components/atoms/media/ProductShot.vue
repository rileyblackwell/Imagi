<!--
  ProductShot — frames a real screenshot of the running app in a minimal window
  chrome so it reads as product rather than decoration.

  The screenshots in /public/product are captured from the dev app at 2x, so
  every instance passes intrinsic width/height and the browser reserves the box
  before the image lands (no layout shift on a page that is mostly imagery).

  It only renders on Spotlight pages (home, About), so the frame is always the
  lit one: a thin gradient edge, a deep shadow, and the caption centered below.
-->
<template>
  <figure class="relative z-[1] m-0">
    <!-- Gradient edge as a border-box background, so one element keeps one radius -->
    <div
      class="relative overflow-hidden rounded-2xl border border-transparent shadow-sl-win
        [background:linear-gradient(var(--sl-surface),var(--sl-surface))_padding-box,var(--sl-win-edge)_border-box]"
    >
      <!-- Window chrome: three dots and a quiet label, nothing else -->
      <div
        class="flex h-10 items-center gap-3 border-b border-b-sl-line bg-sl-chrome-bg px-4
          max-[560px]:h-8 max-[560px]:px-[10px]"
      >
        <span class="inline-flex shrink-0 gap-[0.4rem]" aria-hidden="true">
          <i
            v-for="n in 3"
            :key="n"
            class="h-[11px] w-[11px] rounded-[999px] border border-sl-chrome-dot-edge bg-sl-chrome-dot
              max-[560px]:h-2 max-[560px]:w-2"
          ></i>
        </span>
        <!-- translateX centres the chip on the bar, not on the space after the dots -->
        <span
          v-if="label"
          class="shot__chip mx-auto -translate-x-[23px] truncate rounded-lg border border-sl-line bg-sl-chip-bg
            px-[14px] py-[6px] text-[12.5px] tracking-[0] text-sl-muted
            max-[560px]:transform-none max-[560px]:px-[10px] max-[560px]:py-1 max-[560px]:text-[11px]"
        >{{ label }}</span>
      </div>
      <img
        class="block h-auto w-full"
        :src="src"
        :alt="alt"
        :width="width"
        :height="height"
        :loading="eager ? 'eager' : 'lazy'"
        :fetchpriority="eager ? 'high' : 'auto'"
        decoding="async"
      />
    </div>
    <figcaption
      v-if="caption"
      class="mx-auto mb-0 mt-7 max-w-[64ch] text-center text-[15px] leading-[1.5] text-sl-muted text-pretty
        max-[560px]:mt-5 max-[560px]:text-[14px]"
    >{{ caption }}</figcaption>
  </figure>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ProductShot',
  props: {
    src: { type: String, required: true },
    alt: { type: String, required: true },
    width: { type: [Number, String], required: true },
    height: { type: [Number, String], required: true },
    label: { type: String, default: '' },
    caption: { type: String, default: '' },
    // Above-the-fold shots should not be lazy — they are the hero visual.
    eager: { type: Boolean, default: false }
  }
})
</script>
