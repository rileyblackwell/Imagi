<template>
  <div class="text-center mb-8">
    <div class="brand-header">
      <div class="logo-container">
        <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-12 w-auto mx-auto mb-4" />
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
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