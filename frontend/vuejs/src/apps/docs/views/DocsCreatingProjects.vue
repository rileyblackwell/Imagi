<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Creating Projects"
      description="Learn how to create and configure new projects in Imagi Oasis."
      badge-text="PROJECTS"
    >
      <h2>Project Creation Process</h2>
      <p>
        Creating a new project in Imagi Oasis is simple, intuitive, and designed to get you from idea to working application quickly. 
        Here's a detailed guide on how to create and configure your projects.
      </p>

      <!-- Section 1: Starting a New Project -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Starting a New Project" icon="fas fa-rocket" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-6">
          To create a new project, navigate to the Imagi Oasis dashboard and follow these steps:
        </p>
        
        <ol class="space-y-4">
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-indigo-300 font-bold text-sm">1</span>
            </div>
            <div>
              <strong class="text-white">Click the "New Project" button</strong> on your dashboard homepage or from the projects list.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-indigo-300 font-bold text-sm">2</span>
            </div>
            <div>
              <strong class="text-white">Enter a project name</strong> - Choose something descriptive that reflects the purpose of your application.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-indigo-300 font-bold text-sm">3</span>
            </div>
            <div>
              <strong class="text-white">Select a project template</strong> (optional) - You can start from scratch or choose from pre-configured templates.
            </div>
          </li>
        </ol>
        
        <!-- Pro tip -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm mt-6">
          <h4 class="text-indigo-300 mt-0 mb-2 flex items-center text-base font-medium">
            <i class="fas fa-lightbulb mr-2"></i>
            Pro Tip
          </h4>
          <p class="text-gray-300 text-sm mb-0 leading-relaxed">
            Starting with a template can save time, but creating from scratch gives you more control over the architecture. 
            Choose based on your specific needs and timeline.
          </p>
        </div>
      </DocsCard>

      <!-- Section 2: Project Configuration -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Project Configuration" icon="fas fa-cogs" color="cyan" />
        <p class="text-gray-300 leading-relaxed mb-6">
          After creating your project, you'll need to configure it with details about what you want to build:
        </p>
        
        <!-- Describing Your Application -->
        <div class="mb-8">
          <h3 class="text-cyan-300 text-lg font-semibold mb-4 flex items-center">
            <i class="fas fa-edit mr-2"></i>
            Describing Your Application
          </h3>
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <p class="text-gray-300 text-sm mb-4 leading-relaxed">
              Write a detailed description of your application, including:
            </p>
            <ul class="space-y-3">
              <DocsListItem icon="fas fa-bullseye" color="cyan">
                <strong>Purpose and functionality</strong> - What problem does your app solve?
              </DocsListItem>
              <DocsListItem icon="fas fa-star" color="blue">
                <strong>Key features</strong> - What are the main capabilities?
              </DocsListItem>
              <DocsListItem icon="fas fa-users" color="cyan">
                <strong>User roles</strong> - Who will use the application?
              </DocsListItem>
              <DocsListItem icon="fas fa-database" color="blue">
                <strong>Data models</strong> - What information will be stored?
              </DocsListItem>
              <DocsListItem icon="fas fa-palette" color="cyan">
                <strong>Design preferences</strong> - Any specific UI/UX requirements?
              </DocsListItem>
            </ul>
          </div>
        </div>
        
        <!-- Technical Specifications -->
        <div>
          <h3 class="text-cyan-300 text-lg font-semibold mb-4 flex items-center">
            <i class="fas fa-code mr-2"></i>
            Technical Specifications
          </h3>
          <p class="text-gray-300 text-sm mb-4 leading-relaxed">
            Define the technical aspects of your application:
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Frontend card -->
            <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
              <h4 class="text-white text-md font-semibold mb-3 flex items-center">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-desktop text-blue-300 text-sm"></i>
                </div>
                Frontend
              </h4>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-palette" color="blue" size="sm">
                  UI framework preferences
                </DocsListItem>
                <DocsListItem icon="fas fa-mobile-alt" color="cyan" size="sm">
                  Responsive design requirements
                </DocsListItem>
                <DocsListItem icon="fas fa-lock" color="blue" size="sm">
                  Authentication needs
                </DocsListItem>
              </ul>
            </div>
            
            <!-- Backend card -->
            <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
              <h4 class="text-white text-md font-semibold mb-3 flex items-center">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-server text-emerald-300 text-sm"></i>
                </div>
                Backend
              </h4>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-plug" color="green" size="sm">
                  API requirements
                </DocsListItem>
                <DocsListItem icon="fas fa-database" color="cyan" size="sm">
                  Database complexity
                </DocsListItem>
                <DocsListItem icon="fas fa-link" color="green" size="sm">
                  Integration needs
                </DocsListItem>
              </ul>
            </div>
          </div>
        </div>
      </DocsCard>
      
      <!-- Section 3: Generating Your Project -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Generating Your Project" icon="fas fa-magic" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Once you've configured your project details, it's time to let Imagi Oasis work its magic:
        </p>
        
        <ol class="space-y-4 mb-6">
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-violet-300 font-bold text-sm">1</span>
            </div>
            <div>
              <strong class="text-white">Review your configuration</strong> - Make sure all details are accurate and complete.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-violet-300 font-bold text-sm">2</span>
            </div>
            <div>
              <strong class="text-white">Click "Generate Project"</strong> - The AI will begin creating your application based on your specifications.
            </div>
          </li>
          <li class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-violet-300 font-bold text-sm">3</span>
            </div>
            <div>
              <strong class="text-white">Wait for generation to complete</strong> - This typically takes 2-5 minutes depending on complexity.
            </div>
          </li>
        </ol>
        
        <!-- Generation info -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
          <h4 class="text-violet-300 mt-0 mb-2 flex items-center text-base font-medium">
            <i class="fas fa-info-circle mr-2"></i>
            What Happens During Generation?
          </h4>
          <p class="text-gray-300 text-sm mb-0 leading-relaxed">
            The AI analyzes your requirements, designs the database schema, creates API endpoints, generates UI components, 
            implements authentication logic, and sets up the project structure. You'll see progress updates as each component is created.
          </p>
        </div>
      </DocsCard>

      <!-- Section 4: Project Templates -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Available Project Templates" icon="fas fa-copy" color="blue" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Imagi Oasis provides several pre-built templates to help you get started quickly:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
              <!-- Header -->
              <div class="h-0.5 w-full bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80 mb-4"></div>
              
              <div class="flex items-center mb-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-shopping-cart text-blue-300"></i>
                </div>
                <h4 class="text-white font-semibold">E-Commerce Store</h4>
              </div>
              <p class="text-gray-300 text-sm leading-relaxed">
                Complete online store with product catalog, shopping cart, checkout, and order management.
              </p>
            </div>
          </div>
          
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
              <!-- Header -->
              <div class="h-0.5 w-full bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80 mb-4"></div>
              
              <div class="flex items-center mb-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-tasks text-violet-300"></i>
                </div>
                <h4 class="text-white font-semibold">Task Manager</h4>
              </div>
              <p class="text-gray-300 text-sm leading-relaxed">
                Project and task management system with teams, deadlines, and progress tracking.
              </p>
            </div>
          </div>
          
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
              <!-- Header -->
              <div class="h-0.5 w-full bg-gradient-to-r from-emerald-400 via-green-400 to-emerald-400 opacity-80 mb-4"></div>
              
              <div class="flex items-center mb-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-blog text-emerald-300"></i>
                </div>
                <h4 class="text-white font-semibold">Blog Platform</h4>
              </div>
              <p class="text-gray-300 text-sm leading-relaxed">
                Content management system with posts, categories, comments, and author management.
              </p>
            </div>
          </div>
          
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
              <!-- Header -->
              <div class="h-0.5 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80 mb-4"></div>
              
              <div class="flex items-center mb-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-users text-indigo-300"></i>
                </div>
                <h4 class="text-white font-semibold">Social Platform</h4>
              </div>
              <p class="text-gray-300 text-sm leading-relaxed">
                Community platform with user profiles, posts, messaging, and social features.
              </p>
            </div>
          </div>
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
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 flex-shrink-0">
                <i class="fas fa-sitemap text-xl text-violet-300"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-violet-300 transition-colors font-semibold text-lg mb-2">Project Structure</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Understand how your generated project is organized</p>
              </div>
            </div>
          </div>
        </router-link>
        
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
                <p class="text-gray-400 text-sm leading-relaxed">Learn to customize and enhance your application's interface</p>
              </div>
            </div>
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