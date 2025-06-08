<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Key Concepts"
      description="Understanding fundamental concepts and principles of Imagi Oasis."
      badge-text="CONCEPTS"
    >
      <!-- Introduction -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="How Imagi Oasis Works" icon="fas fa-cogs" color="primary" />
        <p class="text-gray-300 leading-relaxed">
          Imagi Oasis transforms the way web applications are built by using artificial intelligence to bridge the gap between your ideas and a functioning application. This page explains the core concepts that will help you make the most of the platform.
        </p>
      </DocsCard>

      <!-- Section 1: AI Generation -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="AI-Powered Generation" icon="fas fa-brain" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          At the heart of Imagi Oasis is advanced AI that can understand natural language descriptions and convert them into working code.
        </p>
        
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-comment-alt text-violet-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Natural Language Processing</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                You describe what you want in plain English, and our AI interprets your intent, requirements, and preferences. The more detailed and clear your description, the better the AI can understand what you need.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-code text-violet-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Code Generation</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                Based on your description, the AI creates a complete application with both frontend (what users see) and backend (how data is stored and processed). This includes database structures, user interfaces, and business logic.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-sync-alt text-violet-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Iterative Refinement</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                You can review what the AI creates and request changes or improvements. The AI learns from your feedback to refine and enhance your application over time.
              </p>
            </div>
          </div>
        </div>
        
        <!-- Pro tip -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm mt-6">
          <h4 class="text-violet-300 mt-0 mb-2 flex items-center text-base font-medium">
            <i class="fas fa-lightbulb mr-2"></i>
            Pro Tip
          </h4>
          <p class="text-gray-300 text-sm mb-0 leading-relaxed">
            Think of the AI as a collaborative partner rather than just a tool. It works best when you provide context, examples, and clear requirements, just as you would when working with a human developer.
          </p>
        </div>
      </DocsCard>

      <!-- Section 2: Project Structure -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Project Architecture" icon="fas fa-sitemap" color="cyan" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Understanding the structure of your Imagi Oasis applications helps you communicate more effectively with the AI and make better use of the platform.
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Frontend card -->
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
              <!-- Header -->
              <div class="h-0.5 w-full bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80 mb-4"></div>
              
              <h4 class="text-white font-semibold mb-3 flex items-center">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-desktop text-blue-300 text-sm"></i>
                </div>
                Frontend
              </h4>
              <p class="text-gray-300 text-sm mb-3 leading-relaxed">
                The frontend is what users see and interact with. It includes:
              </p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-eye" color="blue">
                  <strong>User Interface (UI)</strong> - The visual elements users interact with
                </DocsListItem>
                <DocsListItem icon="fas fa-file-alt" color="cyan">
                  <strong>Pages</strong> - Different screens in your application
                </DocsListItem>
                <DocsListItem icon="fas fa-edit" color="blue">
                  <strong>Forms</strong> - For collecting user input
                </DocsListItem>
                <DocsListItem icon="fas fa-compass" color="cyan">
                  <strong>Navigation</strong> - How users move between different parts of your app
                </DocsListItem>
              </ul>
            </div>
          </div>
          
          <!-- Backend card -->
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
              <!-- Header -->
              <div class="h-0.5 w-full bg-gradient-to-r from-emerald-400 via-green-400 to-emerald-400 opacity-80 mb-4"></div>
              
              <h4 class="text-white font-semibold mb-3 flex items-center">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                  <i class="fas fa-server text-emerald-300 text-sm"></i>
                </div>
                Backend
              </h4>
              <p class="text-gray-300 text-sm mb-3 leading-relaxed">
                The backend handles data and processing behind the scenes:
              </p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-database" color="green">
                  <strong>Database</strong> - Where your application's data is stored
                </DocsListItem>
                <DocsListItem icon="fas fa-plug" color="cyan">
                  <strong>API</strong> - How the frontend and backend communicate
                </DocsListItem>
                <DocsListItem icon="fas fa-cogs" color="green">
                  <strong>Business Logic</strong> - Rules that determine how your app behaves
                </DocsListItem>
                <DocsListItem icon="fas fa-lock" color="cyan">
                  <strong>Authentication</strong> - Handling user accounts and login
                </DocsListItem>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- How they work together -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-sm mt-6">
          <h3 class="text-white font-semibold text-lg mb-3 flex items-center">
            <i class="fas fa-link text-cyan-300 mr-2"></i>
            How They Work Together
          </h3>
          <p class="text-gray-300 text-sm mb-3 leading-relaxed">
            In a typical user interaction:
          </p>
          <ol class="text-gray-300 text-sm space-y-2 list-decimal pl-5">
            <li>A user interacts with the frontend (e.g., fills out a form)</li>
            <li>The frontend sends this information to the backend via an API request</li>
            <li>The backend processes the information, applies business rules, and stores or retrieves data</li>
            <li>The backend sends a response back to the frontend</li>
            <li>The frontend updates what the user sees based on this response</li>
          </ol>
          <p class="text-gray-300 text-sm mt-3 leading-relaxed">
            Imagi Oasis handles all this complexity for you, creating both frontend and backend components that work together seamlessly.
          </p>
        </div>
      </DocsCard>

      <!-- Section 3: AI Credits -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="AI Credits System" icon="fas fa-coins" color="blue" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Imagi Oasis uses an AI credits system to provide a fair and transparent way to pay for the computational resources used when generating and modifying applications.
        </p>
        
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-coins text-blue-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">What are AI Credits?</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                AI credits are the currency used within Imagi Oasis to pay for AI-powered operations. Different actions consume different amounts of credits based on their complexity and resource requirements.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-shopping-cart text-blue-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">How to Get Credits</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                You can purchase AI credits directly from your account dashboard. New accounts typically receive some free credits to help you get started. We also offer subscription plans for regular users that provide better value than one-time purchases.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-calculator text-blue-300"></i>
            </div>
            <div class="flex-1">
              <h3 class="text-white font-semibold text-lg mb-2">Credit Usage</h3>
              <p class="text-gray-300 text-sm mb-4 leading-relaxed">
                Different operations consume varying amounts of credits:
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="bg-white/5 border border-white/10 rounded-xl p-3 backdrop-blur-sm">
                  <p class="text-blue-300 font-medium text-xs uppercase tracking-wider">Project Creation</p>
                  <p class="text-white text-sm font-semibold">10-30 credits</p>
                  <p class="text-gray-400 text-xs mt-1">Varies based on complexity</p>
                </div>
                <div class="bg-white/5 border border-white/10 rounded-xl p-3 backdrop-blur-sm">
                  <p class="text-blue-300 font-medium text-xs uppercase tracking-wider">Feature Addition</p>
                  <p class="text-white text-sm font-semibold">3-15 credits</p>
                  <p class="text-gray-400 text-xs mt-1">Depends on feature complexity</p>
                </div>
                <div class="bg-white/5 border border-white/10 rounded-xl p-3 backdrop-blur-sm">
                  <p class="text-blue-300 font-medium text-xs uppercase tracking-wider">Design Changes</p>
                  <p class="text-white text-sm font-semibold">2-8 credits</p>
                  <p class="text-gray-400 text-xs mt-1">For UI refinements</p>
                </div>
                <div class="bg-white/5 border border-white/10 rounded-xl p-3 backdrop-blur-sm">
                  <p class="text-blue-300 font-medium text-xs uppercase tracking-wider">Deployment</p>
                  <p class="text-white text-sm font-semibold">5 credits</p>
                  <p class="text-gray-400 text-xs mt-1">Per deployment</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Credit saving tips -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm mt-6">
          <h4 class="text-blue-300 mt-0 mb-3 flex items-center text-base font-medium">
            <i class="fas fa-lightbulb mr-2"></i>
            Credit-Saving Tips
          </h4>
          <ul class="space-y-2">
            <DocsListItem icon="fas fa-check" color="blue">
              Be specific and detailed in your initial project description to reduce the need for revisions
            </DocsListItem>
            <DocsListItem icon="fas fa-layer-group" color="cyan">
              Group related changes together instead of making many small individual requests
            </DocsListItem>
            <DocsListItem icon="fas fa-vial" color="blue">
              Test thoroughly before deployment to avoid consuming credits on multiple deployments
            </DocsListItem>
          </ul>
        </div>
      </DocsCard>

      <!-- Section 4: Templates & Customization -->
      <DocsCard>
        <DocsCardHeader title="Templates & Customization" icon="fas fa-paint-brush" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Imagi Oasis offers a balance between pre-built templates and custom development to save time while still giving you the exact application you need.
        </p>
        
        <div class="space-y-8">
          <!-- Templates -->
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-copy text-indigo-300"></i>
            </div>
            <div class="flex-1">
              <h3 class="text-white font-semibold text-lg mb-2">Templates</h3>
              <p class="text-gray-300 text-sm mb-4 leading-relaxed">
                Templates are pre-designed application frameworks for common use cases like e-commerce sites, blogs, task managers, and more. Starting with a template can save credits and provide a solid foundation for your custom application.
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-shopping-cart text-indigo-300 mr-3"></i>
                    <p class="text-white font-medium">E-Commerce</p>
                  </div>
                  <p class="text-gray-400 text-xs">Product catalog, cart, checkout</p>
                </div>
                <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-calendar-alt text-indigo-300 mr-3"></i>
                    <p class="text-white font-medium">Event Management</p>
                  </div>
                  <p class="text-gray-400 text-xs">Events, tickets, attendees</p>
                </div>
                <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-tasks text-indigo-300 mr-3"></i>
                    <p class="text-white font-medium">Project Management</p>
                  </div>
                  <p class="text-gray-400 text-xs">Tasks, projects, teams</p>
                </div>
                <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
                  <div class="flex items-center mb-2">
                    <i class="fas fa-user-friends text-indigo-300 mr-3"></i>
                    <p class="text-white font-medium">Community Platform</p>
                  </div>
                  <p class="text-gray-400 text-xs">Profiles, posts, comments</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Customization -->
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-palette text-indigo-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Customization</h3>
              <p class="text-gray-300 text-sm mb-4 leading-relaxed">
                Even when starting with a template, every aspect of your application can be customized:
              </p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-swatchbook" color="primary">
                  <strong>Branding</strong> - Colors, logos, fonts to match your brand identity
                </DocsListItem>
                <DocsListItem icon="fas fa-cogs" color="violet">
                  <strong>Features</strong> - Add, remove, or modify functionality
                </DocsListItem>
                <DocsListItem icon="fas fa-database" color="primary">
                  <strong>Data Models</strong> - Change what information your application stores
                </DocsListItem>
                <DocsListItem icon="fas fa-users" color="violet">
                  <strong>User Experience</strong> - Modify workflows and interactions
                </DocsListItem>
              </ul>
            </div>
          </div>
          
          <!-- Custom Development -->
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-code-branch text-indigo-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Custom Development</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                For unique requirements, you can describe your application from scratch. This gives you the most freedom but may require more credits and refinement iterations.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <h2>What's Next?</h2>
      <p>
        Now that you understand the key concepts of Imagi Oasis, explore these related resources:
      </p>
      
      <!-- Next steps cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <router-link 
          to="/docs/quickstart" 
          class="group block transform transition-all duration-300 hover:-translate-y-1"
        >
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 flex-shrink-0">
                <i class="fas fa-rocket text-xl text-indigo-300"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-indigo-300 transition-colors font-semibold text-lg mb-2">Quick Start Guide</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Get started with your first project</p>
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
                <p class="text-gray-400 text-sm leading-relaxed">Tips for creating successful applications</p>
              </div>
            </div>
          </div>
        </router-link>
      </div>
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem } from '../components';
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