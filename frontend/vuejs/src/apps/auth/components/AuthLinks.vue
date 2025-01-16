<template>
  <div class="mt-8 space-y-4">
    <p class="text-center text-gray-400">
      {{ mainText }}
      <router-link :to="mainLink.to" class="text-primary-400 hover:text-primary-300 font-medium">
        {{ mainLink.text }}
      </router-link>
    </p>
    <div class="flex flex-col items-center space-y-2">
      <div class="w-full border-t border-dark-700"></div>
      <slot name="additional-links"></slot>
      <router-link to="/" class="text-gray-400 hover:text-gray-300">
        Back to Home
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthLinks',
  props: {
    mainText: {
      type: String,
      required: true
    },
    mainLink: {
      type: Object,
      required: true,
      validator: prop => {
        return prop.to && prop.text
      }
    }
  }
}
</script> 