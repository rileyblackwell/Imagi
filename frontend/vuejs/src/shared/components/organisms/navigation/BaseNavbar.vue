<template>
  <nav class="bg-dark-900/80 backdrop-blur-sm fixed w-full z-50 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-20">
        <div class="flex items-center">
          <BrandLogo>
            <slot name="logo">Imagi</slot>
          </BrandLogo>
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
import { BrandLogo } from '@/shared/components/molecules'

export default defineComponent({
  name: 'BaseNavbar',
  components: {
    BrandLogo
  }
})
</script>
