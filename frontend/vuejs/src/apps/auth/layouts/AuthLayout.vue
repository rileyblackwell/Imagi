<template>
  <div class="min-h-screen flex flex-col bg-dark-950">
    <!-- Navigation -->
    <nav class="fixed top-0 left-0 right-0 z-50 bg-dark-950 bg-opacity-80 backdrop-blur-lg border-b border-dark-800">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-3">
            <img src="@/shared/assets/images/logo.webp" alt="Imagi Logo" class="h-8 w-auto" />
            <span class="text-xl font-bold bg-gradient-to-r from-primary-300 to-primary-500 text-transparent bg-clip-text">
              Imagi
            </span>
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow flex items-center justify-center pt-16 px-4 bg-gradient-to-b from-dark-950 to-dark-900">
      <div class="w-full max-w-md">
        <div class="auth-form-container">
          <router-view v-slot="{ Component }">
            <transition 
              name="page" 
              mode="out-in"
              appear
            >
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AuthLayout'
}
</script>

<style scoped>
.auth-form-container {
  @apply w-full p-8 bg-dark-900 bg-opacity-50 backdrop-blur-sm border border-dark-700 rounded-2xl shadow-xl;
}

/* Page transition animations */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 