<!-- Base layout - Root wrapper for all layouts -->
<template>
  <div class="flex flex-col min-h-screen bg-dark-900">
    <!-- Custom scrollbar and focus styles using arbitrary values -->
    <div class="overflow-auto
                [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar]:h-2 
                [&::-webkit-scrollbar-track]:bg-dark-900
                [&::-webkit-scrollbar-thumb]:bg-dark-700 [&::-webkit-scrollbar-thumb]:rounded
                [&::-webkit-scrollbar-thumb:hover]:bg-dark-800
                [&_*:focus-visible]:outline-2 [&_*:focus-visible]:outline-primary-500 [&_*:focus-visible]:outline-offset-2
                [scrollbar-width]:thin [scrollbar-color]:dark-700_dark-900">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>