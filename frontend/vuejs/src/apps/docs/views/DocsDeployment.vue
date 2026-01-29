<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Deployment Guide"
      description="Learn how to share your Imagi applications with the world."
      badge-text="DEPLOYMENT"
    >
      <!-- What is Deployment -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="What is Deployment?" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-4">
          Deployment is the process of making your application available online for others to use. 
          It's like moving from designing a house to actually building it so people can move in.
        </p>
        <p class="text-gray-300 leading-relaxed mb-6">
          With Imagi, we're working to make deployment simple so you can share your creation with the world without needing technical expertise.
        </p>
        
        <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
          <h4 class="text-white font-semibold mb-2">Why deployment matters</h4>
          <p class="text-gray-300 text-sm leading-relaxed">
            Until your app is deployed, it only exists in your Imagi workspace. Deployment makes your app available on the internet with its own address (URL) that anyone can access.
          </p>
        </div>
      </DocsCard>

      <!-- Coming Soon Section -->
      <DocsCard color-variant="cyan">
        <div class="text-center">
          <DocsCardHeader title="Deployment Features Coming Soon!" color="cyan" />
          <p class="text-gray-300 text-center max-w-md mx-auto mb-8 leading-relaxed">
            We're currently building our deployment pipeline to make it easy for you to take your Imagi applications live. Soon you'll be able to deploy your applications with just a few clicks.
          </p>
          
          <!-- Planned Features -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm">
            <h4 class="text-lg font-semibold text-white mb-6">Planned Deployment Options</h4>
            <div class="space-y-6">
              <div class="text-left">
                <h5 class="text-white font-semibold mb-1">One-Click Deployment</h5>
                <p class="text-gray-300 text-sm leading-relaxed">
                  Deploy your application with minimal configuration to our secure cloud infrastructure.
                </p>
              </div>
              
              <div class="text-left">
                <h5 class="text-white font-semibold mb-1">Code Export</h5>
                <p class="text-gray-300 text-sm leading-relaxed">
                  Download your application code to deploy it to your preferred hosting provider.
                </p>
              </div>
              
              <div class="text-left">
                <h5 class="text-white font-semibold mb-1">Custom Domains</h5>
                <p class="text-gray-300 text-sm leading-relaxed">
                  Use your own domain name for a professional touch.
                </p>
              </div>
            </div>
          </div>
        </div>
      </DocsCard>
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