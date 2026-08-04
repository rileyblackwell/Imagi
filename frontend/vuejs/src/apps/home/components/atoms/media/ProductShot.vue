<!--
  ProductShot — frames a real screenshot of the running app in a minimal window
  chrome so it reads as product rather than decoration.

  The screenshots in /public/product are captured from the dev app at 2x, so
  every instance passes intrinsic width/height and the browser reserves the box
  before the image lands (no layout shift on a page that is mostly imagery).
-->
<template>
  <figure class="shot">
    <div class="shot__frame">
      <div class="shot__bar">
        <span class="shot__dots" aria-hidden="true">
          <i></i><i></i><i></i>
        </span>
        <span v-if="label" class="shot__chip">{{ label }}</span>
      </div>
      <img
        class="shot__img"
        :src="src"
        :alt="alt"
        :width="width"
        :height="height"
        :loading="eager ? 'eager' : 'lazy'"
        :fetchpriority="eager ? 'high' : 'auto'"
        decoding="async"
      />
    </div>
    <figcaption v-if="caption" class="shot__caption">{{ caption }}</figcaption>
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

<style scoped>
.shot {
  margin: 0;
}

.shot__frame {
  position: relative;
  border-radius: 0.9rem;
  overflow: hidden;
  background: #0d0d10;
  border: 1px solid var(--rule-strong);
  box-shadow:
    0 1px 2px rgba(19, 26, 44, 0.08),
    0 8px 20px -8px rgba(19, 26, 44, 0.16),
    0 32px 64px -24px rgba(19, 26, 44, 0.26);
}

/* The screenshots are of a dark UI, so on a near-black page a shadow does
   nothing to separate them. Dark mode leans on a brighter edge and a faint
   inner highlight instead. */
.dark .shot__frame {
  border-color: rgba(255, 255, 255, 0.16);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 20px 48px -20px rgba(0, 0, 0, 0.9);
}

/* Window chrome: three dots and a quiet label, nothing else */
.shot__bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  height: 2.25rem;
  padding: 0 0.9rem;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.shot__dots {
  display: inline-flex;
  gap: 0.4rem;
  flex-shrink: 0;
}

.shot__dots i {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
}

.shot__chip {
  font-size: 0.68rem;
  letter-spacing: 0.06em;
  color: rgba(255, 255, 255, 0.42);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.shot__img {
  display: block;
  width: 100%;
  height: auto;
}

.shot__caption {
  margin-top: 1rem;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--ink-40);
  text-wrap: pretty;
}
</style>
