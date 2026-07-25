<!--
  FoldTransition.vue — a section that opens and closes to its own height.

  Two places in the workspace hide a list behind a disclosure: the Subagents
  pane's History section and a settled activity feed's step list. Both were
  snapping open, which is the one thing that makes an otherwise smooth pane
  feel abrupt — the content below jumps by however tall the list happens to be.

  Height cannot be transitioned from `auto`, so this measures the element at
  the moment it enters and animates to that number, then hands height back to
  the layout once it lands (so a list that grows while open is not pinned to a
  stale pixel value). The content stays behind `v-if` in the caller, so a
  collapsed section costs nothing until it is first opened.

  Usage:
    <FoldTransition>
      <div v-if="open">…</div>
    </FoldTransition>
-->
<template>
  <Transition
    name="fold"
    @enter="onEnter"
    @after-enter="onAfterEnter"
    @enter-cancelled="onAfterEnter"
    @leave="onLeave"
    @after-leave="onAfterEnter"
    @leave-cancelled="onAfterEnter"
  >
    <slot />
  </Transition>
</template>

<script setup lang="ts">
/**
 * Opening: start at zero, then animate to the height the content actually
 * wants. The reflow read between the two writes is what makes the browser
 * treat them as two states rather than collapsing them into one.
 */
function onEnter(el: Element) {
  const node = el as HTMLElement
  node.style.overflow = 'hidden'
  node.style.height = '0px'
  void node.offsetHeight
  node.style.height = `${node.scrollHeight}px`
}

/** Landed (or interrupted): give height back to the layout. */
function onAfterEnter(el: Element) {
  const node = el as HTMLElement
  node.style.height = ''
  node.style.overflow = ''
}

/** Closing: pin the current height, then collapse from it. */
function onLeave(el: Element) {
  const node = el as HTMLElement
  node.style.overflow = 'hidden'
  node.style.height = `${node.scrollHeight}px`
  void node.offsetHeight
  node.style.height = '0px'
}
</script>

<style scoped>
.fold-enter-active,
.fold-leave-active {
  transition:
    height var(--iw-dur-3) var(--iw-ease-out),
    opacity var(--iw-dur-2) var(--iw-ease-out);
}

.fold-enter-from,
.fold-leave-to {
  opacity: 0;
}
</style>
