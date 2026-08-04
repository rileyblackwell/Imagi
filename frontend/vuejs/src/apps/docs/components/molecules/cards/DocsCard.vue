<!--
  A ruled column, not a card. Sits inside a `.rule-cols` grid on the docs
  pages so a row of these reads as one divided band.
-->
<template>
  <div class="rule-col">
    <h3 v-if="title" class="rule-col__title !mt-0">{{ title }}</h3>
    <div class="rule-col__body !mb-0">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
}>()
</script>
