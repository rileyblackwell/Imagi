<!-- Default layout for public pages -->
<template>
  <BaseLayout>
    <BaseNavbar />
    <div class="min-h-screen">
      <slot></slot>
    </div>
    <BaseFooter />
  </BaseLayout>
</template>

<script>
import BaseLayout from './BaseLayout.vue'
import BaseNavbar from '@/shared/components/BaseNavbar.vue'
import BaseFooter from '@/shared/components/BaseFooter.vue'

export default {
  name: 'DefaultLayout',
  components: {
    BaseLayout,
    BaseNavbar,
    BaseFooter
  }
}
</script> 