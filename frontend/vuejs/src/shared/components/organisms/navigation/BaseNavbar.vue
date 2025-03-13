<template>
  <nav class="bg-dark-900/80 backdrop-blur-sm fixed w-full z-50 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-20">
        <div class="flex items-center">
          <ImagiLogo size="md">
            <slot name="logo">Imagi</slot>
          </ImagiLogo>
          <slot name="left"></slot>
        </div>
        <div class="flex items-center h-full">
          <slot name="right"></slot>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { defineComponent } from 'vue'
import { ImagiLogo } from '@/shared/components/molecules'

export default defineComponent({
  name: 'BaseNavbar',
  components: {
    ImagiLogo
  }
})
</script>
