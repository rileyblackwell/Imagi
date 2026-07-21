<!-- Minimal layout without navbar or footer - warm porcelain canvas -->
<template>
  <BaseLayout>
    <div class="minimal-canvas min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 font-body transition-colors duration-500">
      <slot></slot>
    </div>
  </BaseLayout>
</template>

<script>
import BaseLayout from './BaseLayout.vue'

export default {
  name: 'MinimalLayout',
  components: {
    BaseLayout
  }
}
</script>

<style scoped>
/* Short-page porcelain canvas: starts porcelain, ends on the footer white */
.minimal-canvas {
  background: linear-gradient(180deg, #fdf9f2 0%, #ffffff 100%);
}

:root.dark .minimal-canvas,
.dark .minimal-canvas {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0a0a 100%);
}
</style>
