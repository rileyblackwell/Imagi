<template>
  <footer class="bg-dark-800 border-t border-dark-700">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center">
        <!-- Copyright -->
        <div class="text-gray-400 text-sm">
          © {{ new Date().getFullYear() }} Imagi. All rights reserved.
        </div>

        <!-- Links -->
        <div class="flex space-x-6">
          <a 
            href="/terms" 
            class="text-gray-400 hover:text-white text-sm"
          >
            Terms
          </a>
          <a 
            href="/privacy" 
            class="text-gray-400 hover:text-white text-sm"
          >
            Privacy
          </a>
          <a 
            href="/support" 
            class="text-gray-400 hover:text-white text-sm"
          >
            Support
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'PaymentFooter'
}
</script> 