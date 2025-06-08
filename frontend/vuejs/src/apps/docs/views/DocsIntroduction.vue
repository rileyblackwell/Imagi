<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Welcome to Imagi Oasis"
      description="The AI-powered web application generator that turns your ideas into functional code."
      badge-text="DOCUMENTATION"
    >
      <!-- Enhanced Introduction -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="What is Imagi Oasis?" icon="fas fa-magic" color="primary" />
        <p class="text-gray-300 leading-relaxed">
          Imagi Oasis is an innovative platform that leverages the power of AI to help developers and technical users
          build full-stack web applications using natural language. It streamlines the development process by generating 
          code, designing UIs, and implementing business logic based on your specifications.
        </p>
      </DocsCard>

      <!-- Enhanced Key Features -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Key Features" icon="fas fa-bolt" color="violet" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-bolt text-violet-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm mb-1">AI-Powered Generation</h4>
                <p class="text-gray-300 text-xs leading-relaxed">Create fully functional web applications from natural language descriptions.</p>
              </div>
            </div>
            
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-paint-brush text-blue-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm mb-1">Beautiful UI Components</h4>
                <p class="text-gray-300 text-xs leading-relaxed">Access a rich library of pre-designed UI components for rapid development.</p>
              </div>
            </div>
          </div>
          
          <div class="space-y-4">
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-server text-cyan-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm mb-1">Full-Stack Integration</h4>
                <p class="text-gray-300 text-xs leading-relaxed">Seamlessly connect frontend and backend components with best practices.</p>
              </div>
            </div>
            
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <i class="fas fa-code text-emerald-300 text-sm"></i>
              </div>
              <div>
                <h4 class="text-white font-semibold text-sm mb-1">Code Ownership</h4>
                <p class="text-gray-300 text-xs leading-relaxed">You own all generated code, with no proprietary dependencies or lock-in.</p>
              </div>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Enhanced Target Audience -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="Who is it for?" icon="fas fa-users" color="cyan" />
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-laptop-code text-cyan-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Developers</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">Accelerate your workflow and focus on unique challenges rather than boilerplate code.</p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-rocket text-blue-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Technical Founders</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">Quickly build and iterate on MVPs without waiting months for development.</p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-users text-violet-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Product Teams</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">Rapidly prototype and validate ideas before committing significant resources.</p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-4 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-briefcase text-emerald-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Agencies</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">Deliver high-quality projects efficiently with faster turnaround times.</p>
          </div>
        </div>
      </DocsCard>

      <!-- Enhanced How It Works -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="How Imagi Works" icon="fas fa-cogs" color="blue" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Imagi Oasis combines Large Language Models, specialized code generation systems, and pre-built components into a seamless workflow:
        </p>
        
        <div class="space-y-4">
          <div class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-blue-300 font-bold text-sm">1</span>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Describe your application</h4>
              <p class="text-gray-300 text-sm leading-relaxed">Using natural language - from the broad concept to specific functionality.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-blue-300 font-bold text-sm">2</span>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">AI generates the architecture</h4>
              <p class="text-gray-300 text-sm leading-relaxed">Creating components, database models, and API endpoints.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-blue-300 font-bold text-sm">3</span>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Customize and refine</h4>
              <p class="text-gray-300 text-sm leading-relaxed">The generated code using the intuitive interface.</p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <span class="text-blue-300 font-bold text-sm">4</span>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Export and deploy</h4>
              <p class="text-gray-300 text-sm leading-relaxed">Your application to your preferred hosting environment.</p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Enhanced 3 Steps Section -->
      <DocsCard>
        <DocsCardHeader title="Building Your Web App in 3 Simple Steps" icon="fas fa-list-ol" />
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 text-center h-full flex flex-col">
              <div class="h-0.5 w-full bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-400 opacity-80 mb-4"></div>
              
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center mb-4 mx-auto">
                <span class="text-blue-300 font-bold text-xl">1</span>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Describe Your Vision</h3>
              <p class="text-gray-300 text-sm leading-relaxed flex-1">
                Tell Imagi what you want to build using natural language. Be specific about features, data models, and user flows.
              </p>
            </div>
          </div>
          
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 text-center h-full flex flex-col">
              <div class="h-0.5 w-full bg-gradient-to-r from-violet-400 via-purple-400 to-violet-400 opacity-80 mb-4"></div>
              
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center mb-4 mx-auto">
                <span class="text-violet-300 font-bold text-xl">2</span>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Review & Refine</h3>
              <p class="text-gray-300 text-sm leading-relaxed flex-1">
                Examine the generated code, UI components, and backend logic. Iterate by asking the AI to make specific changes.
              </p>
            </div>
          </div>
          
          <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
            <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-800/90 via-dark-800/80 to-dark-700/90 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden p-5 text-center h-full flex flex-col">
              <div class="h-0.5 w-full bg-gradient-to-r from-emerald-400 via-green-400 to-emerald-400 opacity-80 mb-4"></div>
              
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mb-4 mx-auto">
                <span class="text-emerald-300 font-bold text-xl">3</span>
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Export Your App</h3>
              <p class="text-gray-300 text-sm leading-relaxed flex-1">
                Download your complete application with all source code and assets for deployment on your preferred platform.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Enhanced Capabilities -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Current Capabilities" icon="fas fa-check-circle" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          With Imagi Oasis, you can currently:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-layer-group" color="violet" size="sm">
              Generate full-stack Django applications with beautiful Vue.js frontends
            </DocsListItem>
            <DocsListItem icon="fas fa-database" color="purple" size="sm">
              Create complex data models with proper relationships and validations
            </DocsListItem>
            <DocsListItem icon="fas fa-mobile-alt" color="violet" size="sm">
              Design responsive user interfaces using our component library
            </DocsListItem>
          </ul>
          
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-shield-alt" color="purple" size="sm">
              Implement authentication and authorization with secure practices
            </DocsListItem>
            <DocsListItem icon="fas fa-download" color="violet" size="sm">
              Export your code for local development or deployment
            </DocsListItem>
            <DocsListItem icon="fas fa-code" color="purple" size="sm">
              Full ownership of generated code with no vendor lock-in
            </DocsListItem>
          </ul>
        </div>
      </DocsCard>
      
      <!-- Enhanced Coming Soon Section -->
      <DocsCard color-variant="cyan">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center flex-shrink-0">
            <i class="fas fa-rocket text-cyan-300"></i>
          </div>
          <div>
            <h3 class="text-cyan-300 font-semibold text-lg mb-2">Coming Soon!</h3>
            <p class="text-gray-300 text-sm leading-relaxed mb-4">
              We're working on exciting new features to make Imagi Oasis even more powerful:
            </p>
            <ul class="space-y-2">
              <DocsListItem icon="fas fa-cloud" color="cyan" size="sm">
                Direct hosting and deployment features
              </DocsListItem>
              <DocsListItem icon="fas fa-users" color="blue" size="sm">
                Team collaboration and project sharing
              </DocsListItem>
              <DocsListItem icon="fas fa-chart-line" color="cyan" size="sm">
                Built-in analytics and monitoring
              </DocsListItem>
            </ul>
          </div>
        </div>
      </DocsCard>

      <!-- Enhanced CTA -->
      <DocsCTASection 
        title="Ready to Get Started?" 
        icon="fas fa-lightbulb" 
        description="Follow our step-by-step guide to create your first project and see Imagi Oasis in action."
        buttonText="Quick Start Guide"
        buttonLink="/docs/quickstart"
        buttonIcon="fas fa-rocket"
      />
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem, DocsCTASection } from '../components';
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-horizontal {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.animate-pulse-horizontal {
  animation: pulse-horizontal 1.5s ease-in-out infinite;
}

.shine-effect {
  position: relative;
  overflow: hidden;
}

.shine-effect::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.1) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transform: rotate(30deg);
  animation: shine 4s infinite linear;
}

@keyframes shine {
  from { transform: translateX(-100%) rotate(30deg); }
  to { transform: translateX(100%) rotate(30deg); }
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