<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Quick Start Guide"
      description="Get up and running with Imagi Oasis in minutes with this step-by-step guide."
      badge-text="DOCUMENTATION"
    >
      <!-- Main content with step-by-step guide -->
      <div class="prose prose-invert prose-lg max-w-none">
        <!-- Step 1 -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-primary-500/20 rounded-full flex items-center justify-center mr-3">
                <span class="text-primary-400 font-bold">1</span>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Create a New Project</h2>
            </div>
            <div class="ml-11">
              <p>
                Start by creating a new project in Imagi Oasis. Navigate to the dashboard and click on the "New Project" button.
              </p>
              <div class="mt-4 border border-dark-700 rounded-lg overflow-hidden">
                <img src="@/assets/images/docs/create-project.jpg" alt="Create a new project" class="w-full">
              </div>
              <div class="mt-4 flex space-x-4">
                <router-link 
                  to="/products/oasis/builder/dashboard" 
                  class="inline-flex items-center px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 rounded-lg transition-all duration-300"
                >
                  <i class="fas fa-external-link-alt mr-2"></i>
                  Create New Project
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2 -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-green-500 to-emerald-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center mr-3">
                <span class="text-green-400 font-bold">2</span>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Describe Your Application</h2>
            </div>
            <div class="ml-11">
              <p>
                Enter a detailed description of the web application you want to build. Be as specific as possible about:
              </p>
              <ul class="space-y-2 mt-4">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-check text-green-400 text-xs"></i>
                  </div>
                  <span>The <strong>purpose</strong> of your application</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-check text-green-400 text-xs"></i>
                  </div>
                  <span>Key <strong>features</strong> and functionality</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-check text-green-400 text-xs"></i>
                  </div>
                  <span>Data models and <strong>user interactions</strong></span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-check text-green-400 text-xs"></i>
                  </div>
                  <span>Design preferences and <strong>inspirations</strong></span>
                </li>
              </ul>
              <div class="mt-6 bg-dark-800 p-4 rounded-lg">
                <h4 class="text-green-400 mt-0 mb-2 text-base font-medium">Example Description</h4>
                <p class="text-gray-300 text-sm mb-0">
                  "I need a task management application with user authentication. Users should be able to create projects, add tasks to projects, and mark tasks as complete. Each task should have a title, description, due date, and priority level. The app should have a dashboard showing task statistics and upcoming deadlines. The design should be minimal and modern, similar to Asana but with a darker theme."
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3 -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center mr-3">
                <span class="text-blue-400 font-bold">3</span>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Review and Customize</h2>
            </div>
            <div class="ml-11">
              <p>
                After Imagi generates your application, you'll be taken to the workspace where you can:
              </p>
              <ul class="space-y-2 mt-4">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-code text-blue-400 text-xs"></i>
                  </div>
                  <span><strong>Explore the codebase</strong> - View and edit generated files</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-eye text-blue-400 text-xs"></i>
                  </div>
                  <span><strong>Preview the application</strong> - See it in action in real-time</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-magic text-blue-400 text-xs"></i>
                  </div>
                  <span><strong>Make refinements</strong> - Ask Imagi to modify or add features</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-database text-blue-400 text-xs"></i>
                  </div>
                  <span><strong>Customize data models</strong> - Adjust database schema and relationships</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Step 4 -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-purple-500 to-violet-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center mr-3">
                <span class="text-purple-400 font-bold">4</span>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Export Your Application</h2>
            </div>
            <div class="ml-11">
              <p>
                When you're satisfied with your application:
              </p>
              <ul class="space-y-2 mt-4">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-download text-purple-400 text-xs"></i>
                  </div>
                  <span><strong>Export your source code</strong> - Download the complete application codebase</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-laptop-code text-purple-400 text-xs"></i>
                  </div>
                  <span><strong>Run locally</strong> - Follow the included instructions to run the app on your machine</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-code-branch text-purple-400 text-xs"></i>
                  </div>
                  <span><strong>Modify as needed</strong> - Make any final adjustments to the code for your specific needs</span>
                </li>
              </ul>
              <div class="mt-6 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
                <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
                  <i class="fas fa-lightbulb mr-2"></i>
                  Pro Tip
                </h4>
                <p class="text-gray-300 text-sm mb-0">
                  For a deeper understanding of your generated application, check out the 
                  <router-link to="/docs/project-structure" class="text-primary-400 hover:text-primary-300 transition-colors">Project Structure</router-link> 
                  documentation to learn about the organization and architecture.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Next steps -->
        <h2>What's Next?</h2>
        <p>
          Now that you've created your first project, explore these resources to get the most out of Imagi Oasis:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <router-link 
            to="/docs/building-ui" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-paint-brush text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Building UIs</h3>
                <p class="text-gray-400 text-sm">Learn how to customize and extend your application's user interface</p>
              </div>
            </div>
          </router-link>
          <router-link 
            to="/docs/backend" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-server text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Backend Logic</h3>
                <p class="text-gray-400 text-sm">Master the data models, API endpoints, and business logic</p>
              </div>
            </div>
          </router-link>
          <router-link 
            to="/docs/project-structure" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-sitemap text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Project Structure</h3>
                <p class="text-gray-400 text-sm">Understand the organization and architecture of your application</p>
              </div>
            </div>
          </router-link>
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
                <p class="text-gray-400 text-sm">Follow recommended patterns for efficient development</p>
              </div>
            </div>
          </router-link>
        </div>
        
        <!-- CTA Section -->
        <DocsCTASection 
          title="Ready to Build?" 
          icon="fas fa-rocket" 
          description="Start building your first AI-powered web application with Imagi Oasis."
          buttonText="Create a Project"
          buttonLink="/builder/dashboard"
          buttonIcon="fas fa-plus-circle"
        />
      </div>
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCTASection } from '../components'
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