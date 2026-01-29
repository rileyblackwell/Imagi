<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Quick Start Guide"
      description="Get up and running with Imagi in minutes with this step-by-step guide."
    >
      <!-- Step 1: Create a Project -->
      <DocsCard>
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 flex items-center justify-center flex-shrink-0">
            <span class="text-gray-700 dark:text-white/70 font-bold text-lg">1</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Create a Project" />
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed mb-4 transition-colors duration-300">
              Navigate to the Builder Dashboard to get started. Click the "New Project" button to create your first project. Give it a name and description that reflects what you want to build.
            </p>
            
            <div class="w-full h-px bg-gray-200 dark:bg-white/10 mb-4"></div>
            
            <router-link 
              to="/products/oasis/builder/dashboard" 
              class="inline-flex items-center justify-center gap-3 px-7 py-3.5 bg-transparent text-gray-900 dark:text-white rounded-full font-medium text-base border border-gray-300 dark:border-white/20"
            >
              <span>Create New Project</span>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </div>
      </DocsCard>

      <!-- Step 2: Build Your Project -->
      <DocsCard>
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 flex items-center justify-center flex-shrink-0">
            <span class="text-gray-700 dark:text-white/70 font-bold text-lg">2</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Build Your Project" />
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed mb-4 transition-colors duration-300">
              Once your project is created, you'll be taken to the AI agent interface. Here's where the magic happens—simply prompt the AI agent with what you want your project to be. The more specific you are, the better results you'll get.
            </p>
            
            <ul class="space-y-3 mb-6">
              <DocsListItem>
                Describe the <strong>purpose</strong> and functionality you need
              </DocsListItem>
              <DocsListItem>
                Specify key <strong>features</strong> and user interactions  
              </DocsListItem>
              <DocsListItem>
                Mention any <strong>data models</strong> or structure requirements
              </DocsListItem>
              <DocsListItem>
                Share <strong>design preferences</strong> or style inspiration
              </DocsListItem>
            </ul>
            
            <!-- Example card -->
            <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
              <h4 class="text-gray-900 dark:text-white mt-0 mb-2 text-base font-medium transition-colors duration-300">
                Example Prompt
              </h4>
              <p class="text-gray-600 dark:text-gray-300 text-sm mb-0 leading-relaxed transition-colors duration-300">
                "I need a task management application with user authentication. Users should be able to create projects, add tasks to projects, and mark tasks as complete. Each task should have a title, description, due date, and priority level. The app should have a dashboard showing task statistics and upcoming deadlines. The design should be minimal and modern, similar to Asana but with a darker theme."
              </p>
            </div>
            
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed mt-4 transition-colors duration-300">
              The AI agent will work with you to build out your application, generating code, creating views, and setting up your backend—all through natural conversation.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- Step 3: Deploy Your Project -->
      <DocsCard>
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-full bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 flex items-center justify-center flex-shrink-0">
            <span class="text-gray-700 dark:text-white/70 font-bold text-lg">3</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Deploy Your Project" />
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed mb-4 transition-colors duration-300">
              When you're happy with your application, it's time to share it with the world. Imagi makes deployment simple—just click the "Deploy" button in your project dashboard.
            </p>
            
            <ul class="space-y-3 mb-4">
              <DocsListItem>
                Review your application to ensure everything works as expected
              </DocsListItem>
              <DocsListItem>
                Click the <strong>"Deploy"</strong> button in your project dashboard  
              </DocsListItem>
              <DocsListItem>
                Your app will be built and deployed to a live URL automatically
              </DocsListItem>
              <DocsListItem>
                Share your URL with users and start gathering feedback
              </DocsListItem>
            </ul>
            
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-300">
              Your application will be live on the web, ready for users to access. You can continue to iterate and redeploy as your project evolves.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- Next Steps Section -->
      <DocsCard>
        <DocsCardHeader title="Next Steps" />
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
          Now that you've completed the quick start, continue learning with these guides:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <router-link 
            to="/docs/creating-projects"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Creating Projects</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Learn more about project creation options and best practices.
            </p>
          </router-link>

          <router-link 
            to="/docs/project-structure"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Project Structure</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Understand the organization and structure of your Imagi projects.
            </p>
          </router-link>

          <router-link 
            to="/docs/deployment"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Deployment Guide</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Explore advanced deployment options and configuration.
            </p>
          </router-link>
        </div>
      </DocsCard>
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem } from '../components'
</script>

<style scoped>
/* Override Tailwind prose styling for lists */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style>
