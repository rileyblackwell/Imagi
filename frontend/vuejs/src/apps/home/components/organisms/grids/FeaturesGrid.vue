<!-- Features grid component -->
<template>
  <div class="grid grid-cols-1 gap-12"
    :class="{
      'sm:grid-cols-2': columns >= 2,
      'lg:grid-cols-3': columns >= 3,
      'xl:grid-cols-4': columns === 4
    }"
  >
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'FeaturesGrid',
  props: {
    columns: {
      type: Number,
      default: 3,
      validator: value => [1, 2, 3, 4].includes(value)
    }
  }
}
</script> 