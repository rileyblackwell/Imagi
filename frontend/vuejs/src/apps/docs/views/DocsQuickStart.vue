<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Quick Start Guide"
      description="Get up and running with Imagi in minutes with this step-by-step guide."
    >
      <!-- Step 1: Create a Project -->
      <div class="relative my-8">
        <div class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
          <div class="flex items-start gap-6">
            <div class="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-100 border-2 border-gray-200 dark:border-gray-300 flex items-center justify-center flex-shrink-0 shadow-sm">
              <span class="text-gray-900 dark:!text-gray-900 font-bold text-xl">1</span>
            </div>
            <div class="flex-1">
              <h3 class="text-2xl font-semibold text-gray-900 dark:!text-gray-900 mb-4 transition-colors duration-300">Create a Project</h3>
              <p class="text-gray-700 dark:text-black text-lg leading-relaxed mb-6 transition-colors duration-300">
                Navigate to the Builder Dashboard to get started. Click the "New Project" button to create your first project. Give it a name and description that reflects what you want to build.
              </p>
              
              <div class="w-full h-px bg-gray-200 dark:bg-gray-300 mb-6"></div>
              
              <router-link 
                to="/products/oasis/builder/dashboard" 
                class="btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 !text-white dark:!text-gray-900 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50 dark:border-gray-300/50"
              >
                <!-- Top edge highlight for 3D effect -->
                <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-white/60"></span>
                <!-- Bottom edge shadow for depth -->
                <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent dark:via-black/10"></span>
                <span class="relative !text-white dark:!text-gray-900">Create New Project</span>
                <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1 !text-white dark:!text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 2: Build Your Project -->
      <div class="relative my-8">
        <div class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
          <div class="flex items-start gap-6">
            <div class="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-100 border-2 border-gray-200 dark:border-gray-300 flex items-center justify-center flex-shrink-0 shadow-sm">
              <span class="text-gray-900 dark:!text-gray-900 font-bold text-xl">2</span>
            </div>
            <div class="flex-1">
              <h3 class="text-2xl font-semibold text-gray-900 dark:!text-gray-900 mb-4 transition-colors duration-300">Build Your Project</h3>
              <p class="text-gray-700 dark:text-black text-lg leading-relaxed mb-6 transition-colors duration-300">
                Once your project is created, you'll be taken to the AI agent interface. Here's where the magic happens—simply prompt the AI agent with what you want your project to be. The more specific you are, the better results you'll get.
              </p>
              
              <ul class="space-y-3 mb-6">
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Describe the <strong class="font-semibold text-gray-900 dark:text-black">purpose</strong> and functionality you need</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Specify key <strong class="font-semibold text-gray-900 dark:text-black">features</strong> and user interactions</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Mention any <strong class="font-semibold text-gray-900 dark:text-black">data models</strong> or structure requirements</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Share <strong class="font-semibold text-gray-900 dark:text-black">design preferences</strong> or style inspiration</span>
                </li>
              </ul>
              
              <!-- Example card -->
              <div class="bg-gray-50 dark:bg-gray-100 border border-gray-200 dark:border-gray-300 rounded-xl p-6 transition-colors duration-300">
                <h4 class="text-gray-900 dark:!text-gray-900 mt-0 mb-3 text-lg font-semibold transition-colors duration-300">
                  Example Prompt
                </h4>
                <p class="text-gray-700 dark:text-black text-lg mb-0 leading-relaxed transition-colors duration-300">
                  "I need a task management application with user authentication. Users should be able to create projects, add tasks to projects, and mark tasks as complete. Each task should have a title, description, due date, and priority level. The app should have a dashboard showing task statistics and upcoming deadlines. The design should be minimal and modern, similar to Asana but with a darker theme."
                </p>
              </div>
              
              <p class="text-gray-700 dark:text-black text-lg leading-relaxed mt-6 transition-colors duration-300">
                The AI agent will work with you to build out your application, generating code, creating views, and setting up your backend—all through natural conversation.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 3: Deploy Your Project -->
      <div class="relative my-8">
        <div class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
          <div class="flex items-start gap-6">
            <div class="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-100 border-2 border-gray-200 dark:border-gray-300 flex items-center justify-center flex-shrink-0 shadow-sm">
              <span class="text-gray-900 dark:!text-gray-900 font-bold text-xl">3</span>
            </div>
            <div class="flex-1">
              <h3 class="text-2xl font-semibold text-gray-900 dark:!text-gray-900 mb-4 transition-colors duration-300">Deploy Your Project</h3>
              <p class="text-gray-700 dark:text-black text-lg leading-relaxed mb-6 transition-colors duration-300">
                When you're happy with your application, it's time to share it with the world. Imagi makes deployment simple—just click the "Deploy" button in your project dashboard.
              </p>
              
              <ul class="space-y-3 mb-6">
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Review your application to ensure everything works as expected</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Click the <strong class="font-semibold text-gray-900 dark:text-black">"Deploy"</strong> button in your project dashboard</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Your app will be built and deployed to a live URL automatically</span>
                </li>
                <li class="flex items-start gap-3">
                  <div class="w-1.5 h-1.5 rounded-full bg-gray-900 dark:bg-black mt-2 flex-shrink-0"></div>
                  <span class="text-gray-700 dark:text-black text-lg leading-relaxed">Share your URL with users and start gathering feedback</span>
                </li>
              </ul>
              
              <p class="text-gray-700 dark:text-black text-lg leading-relaxed transition-colors duration-300">
                Your application will be live on the web, ready for users to access. You can continue to iterate and redeploy as your project evolves.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Next Steps Section -->
      <div class="relative my-8">
        <div class="relative p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 transition-colors duration-300 shadow-md">
          <h3 class="text-2xl font-semibold text-gray-900 dark:!text-gray-900 mb-4 transition-colors duration-300">Next Steps</h3>
          <p class="text-gray-700 dark:text-black text-lg leading-relaxed mb-8 transition-colors duration-300">
            Now that you've completed the quick start, continue learning with these guides:
          </p>
          <div class="grid grid-cols-1 gap-6">
            <router-link 
              to="/docs/creating-projects"
              class="bg-gray-50 dark:bg-gray-100 border border-gray-200 dark:border-gray-300 rounded-xl p-6"
            >
              <h4 class="text-gray-900 dark:!text-gray-900 font-semibold mb-3 text-lg transition-colors duration-300">Creating Projects</h4>
              <p class="text-gray-700 dark:text-black text-lg leading-relaxed transition-colors duration-300">
                Learn more about project creation options and best practices.
              </p>
            </router-link>
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
/* 3D Printed Button Effect - matching homepage */
.btn-3d {
  transform: translateZ(0);
  box-shadow: 
    /* Tight shadow for immediate depth */
    0 2px 3px -1px rgba(0, 0, 0, 0.4),
    /* Medium shadow for body lift */
    0 6px 12px -3px rgba(0, 0, 0, 0.35),
    /* Large diffuse shadow */
    0 16px 32px -8px rgba(0, 0, 0, 0.3),
    0 24px 48px -12px rgba(0, 0, 0, 0.2),
    /* Bottom edge thickness */
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    /* Inset highlights */
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.2),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}

.dark .btn-3d {
  box-shadow: 
    /* Tight shadow for immediate depth */
    0 2px 3px -1px rgba(0, 0, 0, 0.1),
    /* Medium shadow for body lift */
    0 6px 12px -3px rgba(0, 0, 0, 0.1),
    /* Large diffuse shadow */
    0 16px 32px -8px rgba(0, 0, 0, 0.1),
    0 24px 48px -12px rgba(0, 0, 0, 0.08),
    /* Bottom edge thickness */
    0 3px 0 -1px rgba(0, 0, 0, 0.15),
    /* Inset highlights */
    inset 0 3px 6px 0 rgba(255, 255, 255, 0.9),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.08);
}

/* Ensure button text is white/black, not purple */
.btn-3d {
  color: white !important;
}

.dark .btn-3d {
  color: rgb(17, 24, 39) !important; /* gray-900 */
}

.btn-3d span,
.btn-3d svg {
  color: inherit !important;
}
</style>
