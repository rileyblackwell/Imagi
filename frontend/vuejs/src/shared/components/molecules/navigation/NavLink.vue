<template>
  <router-link 
    :to="to" 
    class="group flex items-center text-gray-400/90 hover:text-gray-200 transition-colors duration-150 w-full"
  >
    <span class="flex items-center min-w-[20px]">
      <i class="fas fa-chevron-right text-[8px] opacity-0 -translate-x-2 group-hover:opacity-50 group-hover:translate-x-0 transition-all duration-150 ease-out"></i>
    </span>
    <span class="text-sm"><slot></slot></span>
  </router-link>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'NavLink',
  props: {
    to: {
      type: String,
      required: true
    }
  }
})
</script>
