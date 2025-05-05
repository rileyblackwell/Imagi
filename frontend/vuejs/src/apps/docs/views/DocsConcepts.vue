<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Key Concepts
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Understanding fundamental concepts and principles of Imagi Oasis.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content -->
      <div class="prose prose-invert prose-lg max-w-none">
        <!-- Introduction -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-4">How Imagi Oasis Works</h2>
          <p class="text-gray-300">
            Imagi Oasis transforms the way web applications are built by using artificial intelligence to bridge the gap between your ideas and a functioning application. This page explains the core concepts that will help you make the most of the platform.
          </p>
        </div>

        <!-- Section 1: AI Generation -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">1. AI-Powered Generation</h2>
            <p class="text-gray-300">
              At the heart of Imagi Oasis is advanced AI that can understand natural language descriptions and convert them into working code.
            </p>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-primary-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-comment-alt text-primary-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Natural Language Processing</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    You describe what you want in plain English, and our AI interprets your intent, requirements, and preferences. The more detailed and clear your description, the better the AI can understand what you need.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-primary-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-code text-primary-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Code Generation</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    Based on your description, the AI creates a complete application with both frontend (what users see) and backend (how data is stored and processed). This includes database structures, user interfaces, and business logic.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-primary-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-sync-alt text-primary-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Iterative Refinement</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    You can review what the AI creates and request changes or improvements. The AI learns from your feedback to refine and enhance your application over time.
                  </p>
                </div>
              </div>
            </div>
            
            <div class="mt-8 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
              <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
                <i class="fas fa-lightbulb mr-2"></i>
                Pro Tip
              </h4>
              <p class="text-gray-300 text-sm mb-0">
                Think of the AI as a collaborative partner rather than just a tool. It works best when you provide context, examples, and clear requirements, just as you would when working with a human developer.
              </p>
            </div>
          </div>
        </div>

        <!-- Section 2: Project Structure -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">2. Project Architecture</h2>
            <p class="text-gray-300">
              Understanding the structure of your Imagi Oasis applications helps you communicate more effectively with the AI and make better use of the platform.
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-3 flex items-center">
                  <i class="fas fa-desktop text-blue-400 mr-3"></i>
                  Frontend
                </h4>
                <p class="text-gray-300 text-sm mb-3">
                  The frontend is what users see and interact with. It includes:
                </p>
                <ul class="text-sm text-gray-400 space-y-2">
                  <li class="flex items-start">
                    <i class="fas fa-check text-blue-400 mr-2 mt-1"></i>
                    <span><strong>User Interface (UI)</strong> - The visual elements users interact with</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-blue-400 mr-2 mt-1"></i>
                    <span><strong>Pages</strong> - Different screens in your application</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-blue-400 mr-2 mt-1"></i>
                    <span><strong>Forms</strong> - For collecting user input</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-blue-400 mr-2 mt-1"></i>
                    <span><strong>Navigation</strong> - How users move between different parts of your app</span>
                  </li>
                </ul>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-3 flex items-center">
                  <i class="fas fa-server text-green-400 mr-3"></i>
                  Backend
                </h4>
                <p class="text-gray-300 text-sm mb-3">
                  The backend handles data and processing behind the scenes:
                </p>
                <ul class="text-sm text-gray-400 space-y-2">
                  <li class="flex items-start">
                    <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                    <span><strong>Database</strong> - Where your application's data is stored</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                    <span><strong>API</strong> - How the frontend and backend communicate</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                    <span><strong>Business Logic</strong> - Rules that determine how your app behaves</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                    <span><strong>Authentication</strong> - Handling user accounts and login</span>
                  </li>
                </ul>
              </div>
            </div>
            
            <div class="mt-8">
              <h3 class="text-white font-medium text-lg">How They Work Together</h3>
              <p class="text-gray-300 text-sm mt-2">
                In a typical user interaction:
              </p>
              <ol class="text-gray-300 text-sm mt-3 space-y-2 list-decimal pl-5">
                <li>A user interacts with the frontend (e.g., fills out a form)</li>
                <li>The frontend sends this information to the backend via an API request</li>
                <li>The backend processes the information, applies business rules, and stores or retrieves data</li>
                <li>The backend sends a response back to the frontend</li>
                <li>The frontend updates what the user sees based on this response</li>
              </ol>
              <p class="text-gray-300 text-sm mt-3">
                Imagi Oasis handles all this complexity for you, creating both frontend and backend components that work together seamlessly.
              </p>
            </div>
          </div>
        </div>

        <!-- Section 3: AI Credits -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-amber-500 to-yellow-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">3. AI Credits System</h2>
            <p class="text-gray-300">
              Imagi Oasis uses an AI credits system to provide a fair and transparent way to pay for the computational resources used when generating and modifying applications.
            </p>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-amber-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-coins text-amber-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">What are AI Credits?</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    AI credits are the currency used within Imagi Oasis to pay for AI-powered operations. Different actions consume different amounts of credits based on their complexity and resource requirements.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-amber-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-shopping-cart text-amber-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">How to Get Credits</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    You can purchase AI credits directly from your account dashboard. New accounts typically receive some free credits to help you get started. We also offer subscription plans for regular users that provide better value than one-time purchases.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-amber-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-calculator text-amber-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Credit Usage</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    Different operations consume varying amounts of credits:
                  </p>
                  <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <p class="text-amber-300 font-medium text-xs">PROJECT CREATION</p>
                      <p class="text-white text-sm">10-30 credits</p>
                      <p class="text-gray-400 text-xs mt-1">Varies based on complexity</p>
                    </div>
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <p class="text-amber-300 font-medium text-xs">FEATURE ADDITION</p>
                      <p class="text-white text-sm">3-15 credits</p>
                      <p class="text-gray-400 text-xs mt-1">Depends on feature complexity</p>
                    </div>
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <p class="text-amber-300 font-medium text-xs">DESIGN CHANGES</p>
                      <p class="text-white text-sm">2-8 credits</p>
                      <p class="text-gray-400 text-xs mt-1">For UI refinements</p>
                    </div>
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <p class="text-amber-300 font-medium text-xs">DEPLOYMENT</p>
                      <p class="text-white text-sm">5 credits</p>
                      <p class="text-gray-400 text-xs mt-1">Per deployment</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mt-6 bg-amber-500/10 border border-amber-500/20 rounded-lg p-4">
                <h4 class="text-amber-400 mt-0 mb-2 flex items-center text-base font-medium">
                  <i class="fas fa-lightbulb mr-2"></i>
                  Credit-Saving Tips
                </h4>
                <ul class="text-gray-300 text-sm mb-0 space-y-2">
                  <li class="flex items-start">
                    <i class="fas fa-check text-amber-400 mr-2 mt-1"></i>
                    <span>Be specific and detailed in your initial project description to reduce the need for revisions</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-amber-400 mr-2 mt-1"></i>
                    <span>Group related changes together instead of making many small individual requests</span>
                  </li>
                  <li class="flex items-start">
                    <i class="fas fa-check text-amber-400 mr-2 mt-1"></i>
                    <span>Test thoroughly before deployment to avoid consuming credits on multiple deployments</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: Templates & Customization -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-green-500 to-emerald-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">4. Templates & Customization</h2>
            <p class="text-gray-300">
              Imagi Oasis offers a balance between pre-built templates and custom development to save time while still giving you the exact application you need.
            </p>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-copy text-green-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Templates</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    Templates are pre-designed application frameworks for common use cases like e-commerce sites, blogs, task managers, and more. Starting with a template can save credits and provide a solid foundation for your custom application.
                  </p>
                  <div class="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <div class="flex items-center">
                        <i class="fas fa-shopping-cart text-green-400 mr-2"></i>
                        <p class="text-white font-medium">E-Commerce</p>
                      </div>
                      <p class="text-gray-400 text-xs mt-1">Product catalog, cart, checkout</p>
                    </div>
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <div class="flex items-center">
                        <i class="fas fa-calendar-alt text-green-400 mr-2"></i>
                        <p class="text-white font-medium">Event Management</p>
                      </div>
                      <p class="text-gray-400 text-xs mt-1">Events, tickets, attendees</p>
                    </div>
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <div class="flex items-center">
                        <i class="fas fa-tasks text-green-400 mr-2"></i>
                        <p class="text-white font-medium">Project Management</p>
                      </div>
                      <p class="text-gray-400 text-xs mt-1">Tasks, projects, teams</p>
                    </div>
                    <div class="bg-dark-800 p-3 rounded-lg">
                      <div class="flex items-center">
                        <i class="fas fa-user-friends text-green-400 mr-2"></i>
                        <p class="text-white font-medium">Community Platform</p>
                      </div>
                      <p class="text-gray-400 text-xs mt-1">Profiles, posts, comments</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-paint-brush text-green-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Customization</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    Even when starting with a template, every aspect of your application can be customized:
                  </p>
                  <ul class="text-sm text-gray-400 space-y-2 mt-3">
                    <li class="flex items-start">
                      <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                      <span><strong>Branding</strong> - Colors, logos, fonts to match your brand identity</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                      <span><strong>Features</strong> - Add, remove, or modify functionality</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                      <span><strong>Data Models</strong> - Change what information your application stores</span>
                    </li>
                    <li class="flex items-start">
                      <i class="fas fa-check text-green-400 mr-2 mt-1"></i>
                      <span><strong>User Experience</strong> - Modify workflows and interactions</span>
                    </li>
                  </ul>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-9 h-9 rounded-full bg-green-500/20 flex items-center justify-center mr-4">
                  <i class="fas fa-code-branch text-green-400"></i>
                </div>
                <div>
                  <h3 class="text-white font-medium text-lg">Custom Development</h3>
                  <p class="text-gray-300 text-sm mt-1">
                    For unique requirements, you can describe your application from scratch. This gives you the most freedom but may require more credits and refinement iterations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- What's Next -->
        <h2>What's Next?</h2>
        <p>
          Now that you understand the key concepts of Imagi Oasis, explore these related resources:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <router-link 
            to="/docs/quickstart" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-rocket text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Quick Start Guide</h3>
                <p class="text-gray-400 text-sm">Get started with your first project</p>
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
                <p class="text-gray-400 text-sm">Tips for creating successful applications</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
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