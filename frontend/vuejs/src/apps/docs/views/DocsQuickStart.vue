<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Quick Start Guide"
      description="Get up and running with Imagi Oasis in minutes with this step-by-step guide."
      badge-text="GETTING STARTED"
    >
      <!-- Step 1 -->
      <DocsCard color-variant="primary">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
            <span class="text-indigo-300 font-bold text-lg">1</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Create a New Project" icon="fas fa-plus-circle" color="primary" />
            <p class="text-gray-300 leading-relaxed mb-4">
              Start by creating a new project in Imagi Oasis. Navigate to the dashboard and click on the "New Project" button.
            </p>
            
            <!-- Modern separator -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
            
            <router-link 
              to="/products/oasis/builder/dashboard" 
              class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 hover:from-indigo-500/30 hover:to-violet-500/30 text-indigo-300 rounded-xl transition-all duration-300 border border-indigo-400/20 hover:border-indigo-400/30"
            >
              <i class="fas fa-external-link-alt mr-2 text-sm"></i>
              Create New Project
            </router-link>
          </div>
        </div>
      </DocsCard>

      <!-- Step 2 -->
      <DocsCard color-variant="cyan">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0">
            <span class="text-cyan-300 font-bold text-lg">2</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Describe Your Application" icon="fas fa-edit" color="cyan" />
            <p class="text-gray-300 leading-relaxed mb-4">
              Enter a detailed description of the web application you want to build. Be as specific as possible about:
            </p>
            
            <ul class="space-y-3 mb-6">
              <DocsListItem icon="fas fa-bullseye" color="cyan">
                The <strong>purpose</strong> of your application
              </DocsListItem>
              <DocsListItem icon="fas fa-cogs" color="blue">
                Key <strong>features</strong> and functionality  
              </DocsListItem>
              <DocsListItem icon="fas fa-users" color="cyan">
                Data models and <strong>user interactions</strong>
              </DocsListItem>
              <DocsListItem icon="fas fa-palette" color="blue">
                Design preferences and <strong>inspirations</strong>
              </DocsListItem>
            </ul>
            
            <!-- Example card -->
            <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <h4 class="text-cyan-300 mt-0 mb-2 text-base font-medium flex items-center">
                <i class="fas fa-lightbulb mr-2"></i>
                Example Description
              </h4>
              <p class="text-gray-300 text-sm mb-0 leading-relaxed">
                "I need a task management application with user authentication. Users should be able to create projects, add tasks to projects, and mark tasks as complete. Each task should have a title, description, due date, and priority level. The app should have a dashboard showing task statistics and upcoming deadlines. The design should be minimal and modern, similar to Asana but with a darker theme."
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Step 3 -->
      <DocsCard color-variant="violet">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
            <span class="text-violet-300 font-bold text-lg">3</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Review and Customize" icon="fas fa-magic" color="violet" />
            <p class="text-gray-300 leading-relaxed mb-4">
              After Imagi generates your application, you'll be taken to the workspace where you can:
            </p>
            
            <ul class="space-y-3">
              <DocsListItem icon="fas fa-code" color="violet">
                <strong>Explore the codebase</strong> - View and edit generated files
              </DocsListItem>
              <DocsListItem icon="fas fa-eye" color="purple">
                <strong>Preview the application</strong> - See it in action in real-time
              </DocsListItem>
              <DocsListItem icon="fas fa-magic" color="violet">
                <strong>Make refinements</strong> - Ask Imagi to modify or add features
              </DocsListItem>
              <DocsListItem icon="fas fa-database" color="purple">
                <strong>Customize data models</strong> - Adjust database schema and relationships
              </DocsListItem>
            </ul>
          </div>
        </div>
      </DocsCard>

      <!-- Step 4 -->
      <DocsCard color-variant="blue">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
            <span class="text-blue-300 font-bold text-lg">4</span>
          </div>
          <div class="flex-1">
            <DocsCardHeader title="Export Your Application" icon="fas fa-download" color="blue" />
            <p class="text-gray-300 leading-relaxed mb-4">
              When you're satisfied with your application:
            </p>
            
            <ul class="space-y-3 mb-6">
              <DocsListItem icon="fas fa-download" color="blue">
                <strong>Export your source code</strong> - Download the complete application codebase
              </DocsListItem>
              <DocsListItem icon="fas fa-laptop-code" color="cyan">
                <strong>Run locally</strong> - Follow the included instructions to run the app on your machine
              </DocsListItem>
              <DocsListItem icon="fas fa-code-branch" color="blue">
                <strong>Modify as needed</strong> - Make any final adjustments to the code for your specific needs
              </DocsListItem>
            </ul>
            
            <!-- Pro tip card -->
            <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
              <h4 class="text-blue-300 mt-0 mb-2 flex items-center text-base font-medium">
                <i class="fas fa-lightbulb mr-2"></i>
                Pro Tip
              </h4>
              <p class="text-gray-300 text-sm mb-0 leading-relaxed">
                For a deeper understanding of your generated application, check out the 
                <router-link to="/docs/project-structure" class="text-blue-300 hover:text-blue-200 transition-colors font-medium">Project Structure</router-link> 
                documentation to learn about the organization and architecture.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <h2>What's Next?</h2>
      <p>
        Now that you've created your first project, explore these resources to get the most out of Imagi Oasis:
      </p>
      
      <!-- Next steps cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <router-link 
          to="/docs/building-ui" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 flex-shrink-0">
                <i class="fas fa-paint-brush text-xl text-indigo-300"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-indigo-300 transition-colors font-semibold text-lg mb-2">Building UIs</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Learn how to customize and extend your application's user interface</p>
              </div>
            </div>
          </div>
        </router-link>
        
        <router-link 
          to="/docs/backend" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 flex-shrink-0">
                <i class="fas fa-server text-xl text-cyan-300"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-cyan-300 transition-colors font-semibold text-lg mb-2">Backend Logic</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Master the data models, API endpoints, and business logic</p>
              </div>
            </div>
          </div>
        </router-link>
        
        <router-link 
          to="/docs/project-structure" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 flex-shrink-0">
                <i class="fas fa-sitemap text-xl text-violet-300"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-violet-300 transition-colors font-semibold text-lg mb-2">Project Structure</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Understand the organization and architecture of your application</p>
              </div>
            </div>
          </div>
        </router-link>
        
        <router-link 
          to="/docs/best-practices" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-emerald-400 via-green-400 to-emerald-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 flex-shrink-0">
                <i class="fas fa-check-circle text-xl text-emerald-300"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-emerald-300 transition-colors font-semibold text-lg mb-2">Best Practices</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Follow recommended patterns for efficient development</p>
              </div>
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
        buttonLink="/products/oasis/builder/dashboard"
        buttonIcon="fas fa-plus-circle"
      />
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem, DocsCTASection } from '../components'
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