<template>
  <div class="text-center mb-8">
    <div class="brand-header mb-6">
      <div class="logo-container inline-flex items-center justify-center p-3 rounded-2xl bg-white/85 dark:bg-white/[0.045] border border-blue-200/70 dark:border-blue-300/[0.14] backdrop-blur-sm mb-6 transition-colors duration-300">
        <h1 class="font-display text-3xl font-semibold tracking-[-0.02em] text-blue-950 dark:text-white transition-colors duration-300">
          Imagi
        </h1>
      </div>
      <h2 class="font-display text-2xl font-semibold tracking-[-0.02em] text-blue-950 dark:text-white mb-2 transition-colors duration-300">{{ title }}</h2>
      <p class="text-blue-950/65 dark:text-blue-100/65 transition-colors duration-300">{{ subtitle }}</p>
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