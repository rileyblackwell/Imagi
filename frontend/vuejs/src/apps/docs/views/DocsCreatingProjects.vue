<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Creating Projects"
      description="Learn how to create and configure new projects in Imagi."
      badge-text="PROJECTS"
    >
      <div class="not-prose">
      <!-- Introduction -->
      <div class="relative my-8">
        <div class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
          <h3 class="text-2xl font-semibold text-gray-900 dark:!text-gray-900 mb-4 transition-colors duration-300">Project Creation Process</h3>
          <p class="text-gray-600 dark:text-black text-lg leading-relaxed transition-colors duration-300">
            Creating a new project in Imagi is simple, intuitive, and designed to get you from idea to working application quickly. 
            Here's a detailed guide on how to create and configure your projects.
          </p>
        </div>
      </div>

      <!-- Section 1: Starting a New Project -->
      <div class="relative my-8">
        <div class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
          <h3 class="text-2xl font-semibold text-gray-900 dark:!text-gray-900 mb-4 transition-colors duration-300">Starting a New Project</h3>
          <p class="text-gray-600 dark:text-black text-lg leading-relaxed mb-6 transition-colors duration-300">
            To create a new project, navigate to the Imagi dashboard and follow these steps: 
          </p>
          
          <ol class="space-y-4 mb-6">
            <li class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-100 border-2 border-gray-200 dark:border-gray-300 flex items-center justify-center flex-shrink-0 shadow-sm">
                <span class="text-gray-900 dark:!text-gray-900 font-bold text-base">1</span>
              </div>
              <div class="text-gray-600 dark:text-black text-lg leading-relaxed transition-colors duration-300">
                <strong class="text-gray-900 dark:text-black font-semibold transition-colors duration-300">Click the "New Project" button</strong> on your dashboard homepage or from the projects list.
              </div>
            </li>
            <li class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-100 border-2 border-gray-200 dark:border-gray-300 flex items-center justify-center flex-shrink-0 shadow-sm">
                <span class="text-gray-900 dark:!text-gray-900 font-bold text-base">2</span>
              </div>
              <div class="text-gray-600 dark:text-black text-lg leading-relaxed transition-colors duration-300">
                <strong class="text-gray-900 dark:text-black font-semibold transition-colors duration-300">Enter a project name</strong> - Choose something descriptive that reflects the purpose of your application.
              </div>
            </li>
            <li class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-100 border-2 border-gray-200 dark:border-gray-300 flex items-center justify-center flex-shrink-0 shadow-sm">
                <span class="text-gray-900 dark:!text-gray-900 font-bold text-base">3</span>
              </div>
              <div class="text-gray-600 dark:text-black text-lg leading-relaxed transition-colors duration-300">
                <strong class="text-gray-900 dark:text-black font-semibold transition-colors duration-300">Select a project template</strong> (optional) - You can start from scratch or choose from pre-configured templates.
              </div>
            </li>
          </ol>
          
          <!-- Pro tip -->
          <div class="bg-gray-50 dark:bg-gray-100 border border-gray-200 dark:border-gray-300 rounded-xl p-6 transition-colors duration-300">
            <h4 class="text-gray-900 dark:!text-gray-900 mt-0 mb-3 text-lg font-semibold transition-colors duration-300">
              Pro Tip
            </h4>
            <p class="text-gray-600 dark:text-black text-lg mb-0 leading-relaxed transition-colors duration-300">
              Starting with a template can save time, but creating from scratch gives you more control over the architecture. 
              Choose based on your specific needs and timeline.
            </p>
          </div>
        </div>
      </div>
      </div>

    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper } from '../components'
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