<template>
  <div class="text-center mb-8">
    <div class="brand-header">
      <div class="logo-container">
        <h1 class="text-3xl font-bold text-white">
          Imagi
        </h1>
      </div>
      <h2 class="text-2xl font-bold text-white mb-2">{{ title }}</h2>
      <p class="text-gray-400">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      required: true
    }
  }
}
</script> 