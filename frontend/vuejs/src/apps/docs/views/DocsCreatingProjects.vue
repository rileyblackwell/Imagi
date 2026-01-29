<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Creating Projects"
      description="Learn how to create and configure new projects in Imagi."
      badge-text="PROJECTS"
    >
      <h2>Project Creation Process</h2>
      <p>
        Creating a new project in Imagi is simple, intuitive, and designed to get you from idea to working application quickly. 
        Here's a detailed guide on how to create and configure your projects.
      </p>

      <!-- Section 1: Starting a New Project -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Starting a New Project" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-6">
          To create a new project, navigate to the Imagi dashboard and follow these steps: 
        </p>
        
        <ol class="space-y-4">
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
              <span class="text-white font-bold text-sm">1</span>
            </div>
            <div>
              <strong class="text-white">Click the "New Project" button</strong> on your dashboard homepage or from the projects list.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
              <span class="text-white font-bold text-sm">2</span>
            </div>
            <div>
              <strong class="text-white">Enter a project name</strong> - Choose something descriptive that reflects the purpose of your application.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
              <span class="text-white font-bold text-sm">3</span>
            </div>
            <div>
              <strong class="text-white">Select a project template</strong> (optional) - You can start from scratch or choose from pre-configured templates.
            </div>
          </li>
        </ol>
        
        <!-- Pro tip -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm mt-6">
          <h4 class="text-white mt-0 mb-2 text-base font-medium">
            Pro Tip
          </h4>
          <p class="text-gray-300 text-sm mb-0 leading-relaxed">
            Starting with a template can save time, but creating from scratch gives you more control over the architecture. 
            Choose based on your specific needs and timeline.
          </p>
        </div>
      </DocsCard>

      <h2>Next Steps</h2>
      <p>
        Once your project is created, explore these guides to make the most of your application:
      </p>
      
      <!-- Next steps cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <router-link 
          to="/docs/project-structure" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <h3 class="text-white transition-colors font-semibold text-lg mb-2">Project Structure</h3>
            <p class="text-gray-400 text-sm leading-relaxed">Understand how your generated project is organized</p>
          </div>
        </router-link>
        
        <router-link 
          to="/docs/deployment" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <h3 class="text-white transition-colors font-semibold text-lg mb-2">Deployment</h3>
            <p class="text-gray-400 text-sm leading-relaxed">Learn how to deploy your application to production</p>
          </div>
        </router-link>
      </div>
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem } from '../components'
</script>

<style scoped>
/* Style for code blocks */
:deep(pre) {
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
}

/* Animation for page elements */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 0.6;
  }
}

.animate-pulse-slow {
  animation: pulse-slow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style> 