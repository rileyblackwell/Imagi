<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Creating Projects
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Learn how to create and configure new projects in Imagi Oasis.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content -->
      <div class="prose prose-invert prose-lg max-w-none">
        <h2>Project Creation Process</h2>
        <p>
          Creating a new project in Imagi Oasis is simple, intuitive, and designed to get you from idea to working application quickly. 
          Here's a detailed guide on how to create and configure your projects.
        </p>

        <!-- Section 1: Starting a New Project -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-primary-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-rocket text-primary-400"></i>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Starting a New Project</h2>
            </div>
            <div class="ml-11">
              <p>
                To create a new project, navigate to the Imagi Oasis dashboard and follow these steps:
              </p>
              <ol class="space-y-4 mt-4">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-0.5">
                    <span class="text-primary-400 font-bold text-sm">1</span>
                  </div>
                  <div>
                    <strong>Click the "New Project" button</strong> on your dashboard homepage or from the projects list.
                  </div>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-0.5">
                    <span class="text-primary-400 font-bold text-sm">2</span>
                  </div>
                  <div>
                    <strong>Enter a project name</strong> - Choose something descriptive that reflects the purpose of your application.
                  </div>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-0.5">
                    <span class="text-primary-400 font-bold text-sm">3</span>
                  </div>
                  <div>
                    <strong>Select a project template</strong> (optional) - You can start from scratch or choose from pre-configured templates.
                  </div>
                </li>
              </ol>
              
              <div class="mt-6 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
                <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
                  <i class="fas fa-lightbulb mr-2"></i>
                  Pro Tip
                </h4>
                <p class="text-gray-300 text-sm mb-0">
                  Starting with a template can save time, but creating from scratch gives you more control over the architecture. 
                  Choose based on your specific needs and timeline.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Project Configuration -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-cogs text-blue-400"></i>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Project Configuration</h2>
            </div>
            <div class="ml-11">
              <p>
                After creating your project, you'll need to configure it with details about what you want to build:
              </p>
              
              <h3 class="text-blue-400 mt-6 mb-3">Describing Your Application</h3>
              <div class="bg-dark-800 p-4 rounded-lg mb-6">
                <p class="text-gray-300 text-sm mb-2">
                  Write a detailed description of your application, including:
                </p>
                <ul class="space-y-2 text-sm">
                  <li class="flex items-start">
                    <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-0.5">
                      <i class="fas fa-check text-blue-400 text-xs"></i>
                    </div>
                    <span><strong>Purpose and functionality</strong> - What problem does your app solve?</span>
                  </li>
                  <li class="flex items-start">
                    <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-0.5">
                      <i class="fas fa-check text-blue-400 text-xs"></i>
                    </div>
                    <span><strong>Key features</strong> - What are the main capabilities?</span>
                  </li>
                  <li class="flex items-start">
                    <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-0.5">
                      <i class="fas fa-check text-blue-400 text-xs"></i>
                    </div>
                    <span><strong>User roles</strong> - Who will use the application?</span>
                  </li>
                  <li class="flex items-start">
                    <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-0.5">
                      <i class="fas fa-check text-blue-400 text-xs"></i>
                    </div>
                    <span><strong>Data models</strong> - What information will be stored?</span>
                  </li>
                  <li class="flex items-start">
                    <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-0.5">
                      <i class="fas fa-check text-blue-400 text-xs"></i>
                    </div>
                    <span><strong>Design preferences</strong> - Any specific UI/UX requirements?</span>
                  </li>
                </ul>
              </div>
              
              <h3 class="text-blue-400 mt-6 mb-3">Technical Specifications</h3>
              <p>
                Define the technical aspects of your application:
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div class="bg-dark-800 p-4 rounded-lg">
                  <h4 class="text-white text-md font-medium mb-2">Frontend</h4>
                  <ul class="space-y-1 text-sm text-gray-300">
                    <li class="flex items-center">
                      <i class="fas fa-check-circle text-blue-400 mr-2 text-xs"></i>
                      UI framework preferences
                    </li>
                    <li class="flex items-center">
                      <i class="fas fa-check-circle text-blue-400 mr-2 text-xs"></i>
                      Responsive design requirements
                    </li>
                    <li class="flex items-center">
                      <i class="fas fa-check-circle text-blue-400 mr-2 text-xs"></i>
                      Authentication needs
                    </li>
                  </ul>
                </div>
                <div class="bg-dark-800 p-4 rounded-lg">
                  <h4 class="text-white text-md font-medium mb-2">Backend</h4>
                  <ul class="space-y-1 text-sm text-gray-300">
                    <li class="flex items-center">
                      <i class="fas fa-check-circle text-blue-400 mr-2 text-xs"></i>
                      API requirements
                    </li>
                    <li class="flex items-center">
                      <i class="fas fa-check-circle text-blue-400 mr-2 text-xs"></i>
                      Database complexity
                    </li>
                    <li class="flex items-center">
                      <i class="fas fa-check-circle text-blue-400 mr-2 text-xs"></i>
                      Integration needs
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Section 3: Generating Your Project -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-green-500 to-emerald-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-magic text-green-400"></i>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Generating Your Project</h2>
            </div>
            <div class="ml-11">
              <p>
                Once you've configured your project details, it's time to let Imagi Oasis work its magic:
              </p>
              <ul class="space-y-3 mt-4">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-0.5">
                    <span class="text-green-400 font-bold text-sm">1</span>
                  </div>
                  <div>
                    <strong>Click "Generate Project"</strong> to start the AI-powered creation process.
                  </div>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-0.5">
                    <span class="text-green-400 font-bold text-sm">2</span>
                  </div>
                  <div>
                    <strong>Wait for generation to complete</strong> - This typically takes 1-3 minutes depending on complexity.
                  </div>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-0.5">
                    <span class="text-green-400 font-bold text-sm">3</span>
                  </div>
                  <div>
                    <strong>Review the generated project</strong> - You'll be taken to the project workspace where you can explore the code and preview the application.
                  </div>
                </li>
              </ul>
              
              <div class="mt-6 bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <h4 class="text-green-400 mt-0 mb-2 flex items-center text-base font-medium">
                  <i class="fas fa-lightbulb mr-2"></i>
                  What to Expect
                </h4>
                <p class="text-gray-300 text-sm mb-0">
                  Imagi Oasis will generate a complete, working application with frontend and backend components, 
                  database models, API endpoints, authentication, and a responsive UI based on your specifications.
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Section 4: Project Management -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-purple-500 to-violet-500"></div>
          <div class="pl-4">
            <div class="flex items-center mb-4">
              <div class="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center mr-3">
                <i class="fas fa-tasks text-purple-400"></i>
              </div>
              <h2 class="text-2xl font-bold text-white m-0">Project Management</h2>
            </div>
            <div class="ml-11">
              <p>
                After your project is generated, you can manage it through the Imagi Oasis dashboard:
              </p>
              
              <h3 class="text-purple-400 mt-6 mb-3">Project Actions</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div class="bg-dark-800 p-4 rounded-lg">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-edit text-purple-400 mr-2"></i>
                    <h4 class="text-white text-md font-medium m-0">Edit Project</h4>
                  </div>
                  <p class="text-sm text-gray-300 mb-0">
                    Modify and extend your project with new features, UI changes, or backend enhancements.
                  </p>
                </div>
                <div class="bg-dark-800 p-4 rounded-lg">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-clone text-purple-400 mr-2"></i>
                    <h4 class="text-white text-md font-medium m-0">Duplicate Project</h4>
                  </div>
                  <p class="text-sm text-gray-300 mb-0">
                    Create a copy of your project as a starting point for a new application or for testing changes.
                  </p>
                </div>
                <div class="bg-dark-800 p-4 rounded-lg">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-download text-purple-400 mr-2"></i>
                    <h4 class="text-white text-md font-medium m-0">Export Project</h4>
                  </div>
                  <p class="text-sm text-gray-300 mb-0">
                    Download your project's source code for local development, hosting, or integration.
                  </p>
                </div>
                <div class="bg-dark-800 p-4 rounded-lg">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-trash-alt text-purple-400 mr-2"></i>
                    <h4 class="text-white text-md font-medium m-0">Delete Project</h4>
                  </div>
                  <p class="text-sm text-gray-300 mb-0">
                    Remove projects you no longer need. This action cannot be undone.
                  </p>
                </div>
              </div>
              
              <h3 class="text-purple-400 mt-6 mb-3">Project Collaboration</h3>
              <p>
                Imagi Oasis supports team collaboration on projects:
              </p>
              <ul class="space-y-2 mt-4">
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-users text-purple-400 text-xs"></i>
                  </div>
                  <span><strong>Share projects</strong> with team members for collaborative development</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-comment-alt text-purple-400 text-xs"></i>
                  </div>
                  <span><strong>Leave comments</strong> on specific files or features</span>
                </li>
                <li class="flex items-start">
                  <div class="flex-shrink-0 w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                    <i class="fas fa-history text-purple-400 text-xs"></i>
                  </div>
                  <span><strong>View revision history</strong> to track changes over time</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Next steps -->
        <h2>Next Steps</h2>
        <p>
          Now that you understand how to create and manage projects in Imagi Oasis, explore these related topics:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
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
                <p class="text-gray-400 text-sm">Understand how your application is organized</p>
              </div>
            </div>
          </router-link>
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
                <p class="text-gray-400 text-sm">Learn how to customize and extend your application's interface</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import { ref } from 'vue'
import DocsLayout from '../layouts/DocsLayout.vue'

// Component setup could include reactive variables for interactive examples
// For example:
const showExample = ref(false)
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