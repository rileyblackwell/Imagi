<!-- Auth Layout -->
<template>
  <DefaultLayout>
    <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-dark-950 to-dark-900">
      <div class="w-full max-w-md">
        <div class="w-full p-8 bg-dark-900/50 backdrop-blur-sm border border-dark-700 rounded-2xl shadow-xl">
          <!-- Header -->
          <div class="text-center">
            <h2 class="text-2xl font-bold text-white">{{ $route.meta.title }}</h2>
            <p class="mt-2 text-gray-400">{{ $route.meta.subtitle }}</p>
          </div>

          <!-- Main Content -->
          <div class="mt-8">
            <router-view />
          </div>

          <!-- Links -->
          <AuthLinks
            :main-text="$route.meta.mainText"
            :main-link="{
              to: $route.meta.mainLinkPath,
              text: $route.meta.mainLinkText
            }"
          />
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { DefaultLayout } from '@/shared/layouts'
import { AuthLinks, AuthHeader } from '@/apps/auth/components'
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>