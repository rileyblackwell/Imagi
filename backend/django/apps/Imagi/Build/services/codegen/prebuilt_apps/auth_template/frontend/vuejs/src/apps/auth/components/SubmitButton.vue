<template>
  <button type="submit" class="auth-submit" :disabled="loading" :aria-busy="loading">
    <span v-if="loading" class="auth-spinner" aria-hidden="true"></span>
    <span>{{ loading ? loadingText : '' }}<slot v-if="!loading"></slot></span>
  </button>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ loading?: boolean; loadingText?: string }>(), {
  loading: false,
  loadingText: 'Working…'
})
</script>
