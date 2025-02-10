<template>
  <router-link 
    to="/" 
    class="inline-block"
  >
    <span class="text-2xl font-extrabold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent hover:from-primary-300 hover:to-primary-500 transition-all duration-300">
      <slot>Imagi</slot>
    </span>
  </router-link>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'BrandLogo'
})
</script>
