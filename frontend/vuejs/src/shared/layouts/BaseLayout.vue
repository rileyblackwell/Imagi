<!-- Base layout - Root wrapper for all layouts -->
<template>
  <div class="flex flex-col min-h-screen bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Custom scrollbar and focus styles using arbitrary values -->
    <div class="overflow-auto
                [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar]:h-2
                [&::-webkit-scrollbar-track]:bg-transparent
                [&::-webkit-scrollbar-thumb]:bg-gray-300 dark:[&::-webkit-scrollbar-thumb]:bg-dark-700 [&::-webkit-scrollbar-thumb]:rounded
                [&::-webkit-scrollbar-thumb:hover]:bg-gray-400 dark:[&::-webkit-scrollbar-thumb:hover]:bg-dark-600
                [&_*:focus-visible]:outline-2 [&_*:focus-visible]:outline-primary-500 [&_*:focus-visible]:outline-offset-2
                [scrollbar-width]:thin">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BaseLayout'
}
</script>