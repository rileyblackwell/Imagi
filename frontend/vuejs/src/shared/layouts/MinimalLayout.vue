<!-- Minimal layout without navbar or footer -->
<template>
  <BaseLayout>
    <div class="min-h-screen flex flex-col items-center justify-center bg-dark-950 px-4 sm:px-6 lg:px-8">
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