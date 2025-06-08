<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Deployment Guide"
      description="Learn how to share your Imagi Oasis applications with the world."
      badge-text="DEPLOYMENT"
    >
      <!-- What is Deployment -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="What is Deployment?" icon="fas fa-rocket" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-4">
          Deployment is the process of making your application available online for others to use. 
          It's like moving from designing a house to actually building it so people can move in.
        </p>
        <p class="text-gray-300 leading-relaxed mb-6">
          With Imagi Oasis, we're working to make deployment simple so you can share your creation with the world without needing technical expertise.
        </p>
        
        <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-lightbulb text-indigo-300 text-sm"></i>
            </div>
            <div>
              <h4 class="text-indigo-300 font-semibold mb-2">Why deployment matters</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Until your app is deployed, it only exists in your Imagi workspace. Deployment makes your app available on the internet with its own address (URL) that anyone can access.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Coming Soon Section -->
      <DocsCard color-variant="cyan">
        <div class="text-center">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-rocket text-2xl text-cyan-300"></i>
          </div>
          
          <DocsCardHeader title="Deployment Features Coming Soon!" icon="fas fa-clock" color="cyan" />
          <p class="text-gray-300 text-center max-w-md mx-auto mb-8 leading-relaxed">
            We're currently building our deployment pipeline to make it easy for you to take your Imagi Oasis applications live. Soon you'll be able to deploy your applications with just a few clicks.
          </p>
          
          <!-- Planned Features -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
            <h4 class="text-lg font-semibold text-white mb-6">Planned Deployment Options</h4>
            <div class="space-y-6">
              <div class="flex items-start gap-4 text-left">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0">
                  <i class="fas fa-bolt text-cyan-300"></i>
                </div>
                <div>
                  <h5 class="text-white font-semibold mb-1">One-Click Deployment</h5>
                  <p class="text-gray-300 text-sm leading-relaxed">
                    Deploy your application with minimal configuration to our secure cloud infrastructure.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start gap-4 text-left">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
                  <i class="fas fa-download text-violet-300"></i>
                </div>
                <div>
                  <h5 class="text-white font-semibold mb-1">Code Export</h5>
                  <p class="text-gray-300 text-sm leading-relaxed">
                    Download your application code to deploy it to your preferred hosting provider.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start gap-4 text-left">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center flex-shrink-0">
                  <i class="fas fa-globe text-emerald-300"></i>
                </div>
                <div>
                  <h5 class="text-white font-semibold mb-1">Custom Domains</h5>
                  <p class="text-gray-300 text-sm leading-relaxed">
                    Use your own domain name for a professional touch.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- What's Next -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="What's Next?" icon="fas fa-arrow-right" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          While waiting for deployment features, explore these resources to prepare your application:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <router-link 
            to="/docs/best-practices" 
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 hover:from-indigo-500/30 hover:to-violet-500/30 text-indigo-300 hover:text-indigo-200 rounded-xl transition-all duration-300 border border-indigo-400/20 hover:border-indigo-400/30 mr-4 mb-4"
          >
            <i class="fas fa-check-circle mr-2 text-sm"></i>
            Best Practices
          </router-link>
          
          <router-link 
            to="/docs/troubleshooting" 
            class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 hover:from-indigo-500/30 hover:to-violet-500/30 text-indigo-300 hover:text-indigo-200 rounded-xl transition-all duration-300 border border-indigo-400/20 hover:border-indigo-400/30 mb-4"
          >
            <i class="fas fa-bug mr-2 text-sm"></i>
            Troubleshooting
          </router-link>
        </div>
      </DocsCard>

      <!-- CTA -->
      <DocsCTASection 
        title="Get Notified When Deployment is Ready" 
        icon="fas fa-bell" 
        description="Want to be the first to know when one-click deployment is available? Start building your project now and we'll notify you when it's time to go live."
        buttonText="Start Building"
        buttonLink="/products/oasis/builder/dashboard"
        buttonIcon="fas fa-rocket"
      />
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsCTASection } from '../components'
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