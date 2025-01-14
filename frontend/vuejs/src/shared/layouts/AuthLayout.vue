<template>
  <div class="min-h-screen flex flex-col bg-dark-950">
    <!-- Auth Content -->
    <div class="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-md w-full space-y-8">
        <!-- Logo -->
        <div class="text-center">
          <router-link to="/" class="inline-flex items-center gap-3">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-12 w-auto" />
            <span class="text-2xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
              Imagi
            </span>
          </router-link>
        </div>

        <!-- Auth Form Container -->
        <div class="bg-dark-900/50 backdrop-blur-lg rounded-lg shadow-xl p-8 space-y-6 border border-dark-800">
          <router-view></router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthLayout'
}
</script> 