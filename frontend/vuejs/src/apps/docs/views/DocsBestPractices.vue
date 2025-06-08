<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Best Practices"
      description="Follow these recommended patterns and tips for successful project development with Imagi Oasis."
      badge-text="BEST PRACTICES"
    >
      <h2>Development Guidelines</h2>
      <p>
        Following these best practices will help you create better applications, save AI credits, and get the most out of Imagi Oasis.
      </p>

      <!-- Project Planning -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Project Planning" icon="fas fa-map" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Proper planning is essential for successful project development. Start with a clear vision of what you want to build.
        </p>
        
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-lightbulb text-indigo-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Define Clear Requirements</h3>
              <p class="text-gray-300 text-sm leading-relaxed mb-3">
                Before creating your project, write down what your application should do, who will use it, and what problems it solves.
              </p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-users" color="primary" size="sm">
                  Identify your target users and their needs
                </DocsListItem>
                <DocsListItem icon="fas fa-list" color="violet" size="sm">
                  List essential features vs. nice-to-have features
                </DocsListItem>
                <DocsListItem icon="fas fa-mobile-alt" color="primary" size="sm">
                  Consider device types and screen sizes
                </DocsListItem>
              </ul>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-sitemap text-indigo-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Plan Your Data Structure</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                Think about what information your application needs to store and how different pieces of data relate to each other.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Writing Effective Descriptions -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Writing Effective Descriptions" icon="fas fa-edit" color="cyan" />
        <p class="text-gray-300 leading-relaxed mb-6">
          The quality of your project description directly impacts the quality of the generated application.
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Do's -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-emerald-300 font-semibold mb-4 flex items-center">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-check text-emerald-300 text-sm"></i>
              </div>
              Do's
            </h4>
            <ul class="space-y-3">
              <DocsListItem icon="fas fa-check" color="green" size="sm">
                Be specific about functionality
              </DocsListItem>
              <DocsListItem icon="fas fa-check" color="cyan" size="sm">
                Include example user workflows
              </DocsListItem>
              <DocsListItem icon="fas fa-check" color="green" size="sm">
                Mention design inspirations
              </DocsListItem>
              <DocsListItem icon="fas fa-check" color="cyan" size="sm">
                Specify data relationships
              </DocsListItem>
              <DocsListItem icon="fas fa-check" color="green" size="sm">
                Include authentication requirements
              </DocsListItem>
            </ul>
          </div>
          
          <!-- Don'ts -->
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-red-300 font-semibold mb-4 flex items-center">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-red-400/20 to-pink-400/20 border border-red-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-times text-red-300 text-sm"></i>
              </div>
              Don'ts
            </h4>
            <ul class="space-y-3">
              <DocsListItem icon="fas fa-times" color="red" size="sm">
                Use vague terms like "simple" or "basic"
              </DocsListItem>
              <DocsListItem icon="fas fa-times" color="pink" size="sm">
                Assume the AI knows your industry
              </DocsListItem>
              <DocsListItem icon="fas fa-times" color="red" size="sm">
                Skip user role definitions
              </DocsListItem>
              <DocsListItem icon="fas fa-times" color="pink" size="sm">
                Forget to mention key integrations
              </DocsListItem>
              <DocsListItem icon="fas fa-times" color="red" size="sm">
                Rush the description process
              </DocsListItem>
            </ul>
          </div>
        </div>
        
        <!-- Example -->
        <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm mt-6">
          <h4 class="text-cyan-300 mt-0 mb-2 flex items-center text-base font-medium">
            <i class="fas fa-star mr-2"></i>
            Example: Good Description
          </h4>
          <p class="text-gray-300 text-sm mb-0 leading-relaxed italic">
            "Create a project management application for small teams (3-10 people). Users can create projects, add tasks with due dates and priorities, assign tasks to team members, and track progress. Include a dashboard showing overdue tasks and project completion statistics. The design should be clean and minimal, similar to Asana, with a dark theme option. Need user authentication with roles: Admin (can create projects and manage users) and Member (can view and update assigned tasks)."
          </p>
        </div>
      </DocsCard>

      <!-- Credit Optimization -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Optimizing AI Credits" icon="fas fa-coins" color="blue" />
        <p class="text-gray-300 leading-relaxed mb-6">
          AI credits are valuable, so use them efficiently to get the best results for your investment.
        </p>
        
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-rocket text-blue-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Start with Templates</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                Using templates as starting points can save 30-50% of your credits compared to building from scratch, while still allowing full customization.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-layer-group text-blue-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Batch Your Changes</h3>
              <p class="text-gray-300 text-sm leading-relaxed mb-3">
                Instead of making many small changes, group related modifications together in a single request.
              </p>
              <div class="bg-white/5 border border-white/10 rounded-lg p-3 text-sm">
                <strong class="text-blue-300">Example:</strong> Instead of "Add a button" then "Change button color" then "Add click handler", 
                say "Add a blue submit button that validates the form and shows a success message."
              </div>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-vial text-blue-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Test Before Deploying</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                Use the preview feature extensively before deploying to avoid consuming deployment credits on broken builds.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Performance & Quality -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Performance & Quality" icon="fas fa-tachometer-alt" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Ensure your applications are fast, reliable, and provide excellent user experiences.
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Performance Tips -->
          <div>
            <h4 class="text-violet-300 font-semibold mb-4 flex items-center">
              <i class="fas fa-bolt mr-2"></i>
              Performance Tips
            </h4>
            <ul class="space-y-2">
              <DocsListItem icon="fas fa-images" color="violet" size="sm">
                Optimize images and media files
              </DocsListItem>
              <DocsListItem icon="fas fa-database" color="purple" size="sm">
                Design efficient database queries
              </DocsListItem>
              <DocsListItem icon="fas fa-mobile-alt" color="violet" size="sm">
                Implement responsive design patterns
              </DocsListItem>
              <DocsListItem icon="fas fa-code" color="purple" size="sm">
                Keep component hierarchies shallow
              </DocsListItem>
            </ul>
          </div>
          
          <!-- Quality Checks -->
          <div>
            <h4 class="text-violet-300 font-semibold mb-4 flex items-center">
              <i class="fas fa-check-circle mr-2"></i>
              Quality Checks
            </h4>
            <ul class="space-y-2">
              <DocsListItem icon="fas fa-universal-access" color="violet" size="sm">
                Test accessibility features
              </DocsListItem>
              <DocsListItem icon="fas fa-lock" color="purple" size="sm">
                Verify security implementations
              </DocsListItem>
              <DocsListItem icon="fas fa-bug" color="violet" size="sm">
                Test error handling scenarios
              </DocsListItem>
              <DocsListItem icon="fas fa-users" color="purple" size="sm">
                Validate user workflows
              </DocsListItem>
            </ul>
          </div>
        </div>
      </DocsCard>

      <!-- Security Best Practices -->
      <DocsCard>
        <DocsCardHeader title="Security Considerations" icon="fas fa-shield-alt" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Security should be considered from the beginning of your project, not as an afterthought.
        </p>
        
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-user-lock text-indigo-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Authentication & Authorization</h3>
              <p class="text-gray-300 text-sm leading-relaxed mb-3">
                Clearly define user roles and permissions in your project description.
              </p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-key" color="primary" size="sm">
                  Implement strong password requirements
                </DocsListItem>
                <DocsListItem icon="fas fa-users-cog" color="violet" size="sm">
                  Define role-based access controls
                </DocsListItem>
                <DocsListItem icon="fas fa-clock" color="primary" size="sm">
                  Consider session management needs
                </DocsListItem>
              </ul>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-database text-indigo-300"></i>
            </div>
            <div>
              <h3 class="text-white font-semibold text-lg mb-2">Data Protection</h3>
              <p class="text-gray-300 text-sm leading-relaxed">
                Specify what sensitive data your application handles and how it should be protected.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <h2>Common Pitfalls to Avoid</h2>
      <p>
        Learn from these common mistakes to save time and credits:
      </p>
      
      <!-- Common Pitfalls -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-red-400 via-pink-400 to-red-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-400/20 to-pink-400/20 border border-red-400/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-xl text-red-300"></i>
              </div>
              <div>
                <h3 class="text-white font-semibold text-lg mb-2">Scope Creep</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Continuously adding features without clear requirements leads to increased costs and complexity.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
          <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 h-full">
            <!-- Header -->
            <div class="h-0.5 w-full bg-gradient-to-r from-orange-400 via-yellow-400 to-orange-400 opacity-80 mb-4"></div>
            
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-400/20 to-yellow-400/20 border border-orange-400/20 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-edit text-xl text-orange-300"></i>
              </div>
              <div>
                <h3 class="text-white font-semibold text-lg mb-2">Insufficient Planning</h3>
                <p class="text-gray-400 text-sm leading-relaxed">Rushing into development without proper requirements leads to multiple revisions and wasted credits.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <DocsCTASection 
        title="Ready to Build Better Apps?" 
        icon="fas fa-rocket" 
        description="Apply these best practices to your next project and create amazing applications with Imagi Oasis."
        buttonText="Start a New Project"
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