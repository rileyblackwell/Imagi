<template>
  <nav class="bg-dark-800 border-b border-dark-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Logo and Brand -->
        <div class="flex">
          <div class="flex-shrink-0 flex items-center">
            <router-link to="/" class="text-white text-xl font-bold">
              Imagi
            </router-link>
          </div>
        </div>

        <!-- Navigation Links -->
        <div class="flex items-center space-x-4">
          <router-link 
            to="/payments/credits" 
            class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
          >
            Credits
          </router-link>
          <router-link 
            to="/payments/history" 
            class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
          >
            History
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'PaymentNavbar'
}
</script>

<style scoped>
.router-link-active {
  color: #00ffc6;
}
</style> 