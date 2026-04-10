<template>
  <div class="text-center mb-8">
    <div class="brand-header mb-6">
      <div class="logo-container inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-br from-primary-500/10 to-violet-500/10 border border-primary-500/20 mb-6">
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
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