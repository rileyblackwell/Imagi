<template>
  <div class="min-h-screen bg-dark-900">
    <!-- Navigation -->
    <nav class="bg-dark-900/80 backdrop-blur-lg border-b border-dark-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <!-- Logo -->
            <router-link to="/" class="flex-shrink-0 flex items-center">
              <img class="h-8 w-auto" src="@/shared/assets/images/logo.webp" alt="Imagi" />
              <span class="text-xl font-bold text-white ml-2">Imagi</span>
            </router-link>
          </div>
          
          <!-- Navigation Links -->
          <div class="flex items-center space-x-4">
            <router-link 
              to="/dashboard" 
              class="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium"
            >
              <i class="fas fa-arrow-left mr-2"></i>
              Back to Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="min-h-screen">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
export default {
  name: 'PaymentLayout',
  mounted() {
    // Load Stripe.js
    if (!window.Stripe) {
      const script = document.createElement('script')
      script.src = 'https://js.stripe.com/v3/'
      script.async = true
      document.head.appendChild(script)
    }
  }
}
</script>

<style scoped>
.min-h-screen {
  min-height: 100vh;
  background: radial-gradient(
    circle at top right,
    rgba(0, 255, 204, 0.05),
    transparent 50%
  );
}
</style> 