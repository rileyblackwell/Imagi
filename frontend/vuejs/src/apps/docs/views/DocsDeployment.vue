<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Deployment Guide
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Learn how to share your Imagi Oasis applications with the world.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content -->
      <div class="prose prose-invert prose-lg max-w-none">
        <!-- Introduction -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-4">What is Deployment?</h2>
          <p class="text-gray-300">
            Deployment is the process of making your application available online for others to use. 
            It's like moving from designing a house to actually building it so people can move in.
          </p>
          <p class="text-gray-300">
            With Imagi Oasis, we're working to make deployment simple so you can share your creation with the world without needing technical expertise.
          </p>
          <div class="mt-6 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
            <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
              <i class="fas fa-lightbulb mr-2"></i>
              Why deployment matters
            </h4>
            <p class="text-gray-300 text-sm mb-0">
              Until your app is deployed, it only exists in your Imagi workspace. Deployment makes your app available on the internet with its own address (URL) that anyone can access.
            </p>
          </div>
        </div>

        <!-- Coming Soon Section -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8">
          <div class="flex flex-col items-center text-center">
            <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mb-5">
              <i class="fas fa-rocket text-2xl text-primary-400"></i>
            </div>
            <h3 class="text-xl font-semibold text-white mb-2">Deployment Features Coming Soon</h3>
            <p class="text-gray-300 text-center max-w-md mb-6">
              We're currently building our deployment pipeline to make it easy for you to take your Imagi Oasis applications live. Soon you'll be able to deploy your applications with just a few clicks.
            </p>
            <div class="mt-6 bg-dark-800/50 p-6 rounded-lg w-full max-w-2xl">
              <h4 class="text-lg font-medium text-white mb-4">Planned Deployment Options</h4>
              <ul class="space-y-4 text-left">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-bolt text-primary-400 text-xs"></i>
                  </div>
                  <div>
                    <strong class="text-white">One-Click Deployment</strong>
                    <p class="text-gray-300 text-sm mt-1">
                      Deploy your application with minimal configuration to our secure cloud infrastructure.
                    </p>
                  </div>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-download text-primary-400 text-xs"></i>
                  </div>
                  <div>
                    <strong class="text-white">Code Export</strong>
                    <p class="text-gray-300 text-sm mt-1">
                      Download your application code to deploy it to your preferred hosting provider.
                    </p>
                  </div>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-globe text-primary-400 text-xs"></i>
                  </div>
                  <div>
                    <strong class="text-white">Custom Domains</strong>
                    <p class="text-gray-300 text-sm mt-1">
                      Use your own domain name for a professional touch.
                    </p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- What's Next -->
        <h2>What's Next?</h2>
        <p>
          While waiting for deployment features, explore these resources:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <router-link 
            to="/docs/best-practices" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-check-circle text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Best Practices</h3>
                <p class="text-gray-400 text-sm">Learn how to optimize your app for production</p>
              </div>
            </div>
          </router-link>
          <router-link 
            to="/docs/troubleshooting" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-bug text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Troubleshooting</h3>
                <p class="text-gray-400 text-sm">Solutions to common development issues</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Override Tailwind prose styling for lists with custom icons */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style> 