<template>
  <div class="min-h-screen flex items-center justify-center bg-dark-900">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-primary-500 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-300 mb-6">Page Not Found</h2>
      <p class="text-gray-400 mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <router-link
        to="/"
        class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200"
      >
        Return Home
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script> 