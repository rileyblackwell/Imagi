<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Welcome to Imagi Oasis"
      description="The AI-powered web application generator that turns your ideas into functional code."
      badge-text="DOCUMENTATION"
    >
      <h2>What is Imagi Oasis?</h2>
      <p>
        Imagi Oasis is an innovative platform that leverages the power of AI to help developers and technical users
        build full-stack web applications using natural language. It streamlines the development process by generating 
        code, designing UIs, and implementing business logic based on your specifications.
      </p>

      <DocsCard>
        <DocsCardHeader title="Key Features" icon="fas fa-bolt" />
        <ul class="mt-4 space-y-3">
          <DocsListItem icon="fas fa-bolt">
            <strong class="text-white">AI-Powered Generation:</strong> Create fully functional web applications from natural language descriptions.
          </DocsListItem>
          <DocsListItem icon="fas fa-paint-brush">
            <strong class="text-white">Beautiful UI Components:</strong> Access a rich library of pre-designed UI components for rapid development.
          </DocsListItem>
          <DocsListItem icon="fas fa-server">
            <strong class="text-white">Full-Stack Integration:</strong> Seamlessly connect frontend and backend components with best practices.
          </DocsListItem>
          <DocsListItem icon="fas fa-code">
            <strong class="text-white">Code Ownership:</strong> You own all generated code, with no proprietary dependencies or lock-in.
          </DocsListItem>
        </ul>
      </DocsCard>

      <h2>Who is it for?</h2>
      <p>
        Imagi Oasis is designed for:
      </p>
      <ul>
        <li><strong>Developers</strong> who want to accelerate their workflow and focus on unique challenges rather than boilerplate code.</li>
        <li><strong>Technical founders</strong> who need to quickly build and iterate on MVPs.</li>
        <li><strong>Product teams</strong> looking to rapidly prototype and validate ideas before committing resources.</li>
        <li><strong>Agencies</strong> that need to deliver high-quality projects efficiently.</li>
      </ul>

      <h2>How Imagi Works</h2>
      <p>
        Imagi Oasis combines Large Language Models, specialized code generation systems, and pre-built components into a seamless workflow:
      </p>

      <ol>
        <li><strong>Describe your application</strong> using natural language - from the broad concept to specific functionality.</li>
        <li><strong>AI generates the architecture</strong> - creating components, database models, and API endpoints.</li>
        <li><strong>Customize and refine</strong> the generated code using the intuitive interface.</li>
        <li><strong>Export and deploy</strong> your application to your preferred hosting environment.</li>
      </ol>

      <h2>Building Your Web App in 3 Simple Steps</h2>
      
      <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-6 my-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700 flex flex-col items-center text-center">
            <div class="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center mb-4">
              <span class="text-primary-400 font-bold text-xl">1</span>
            </div>
            <h3 class="text-lg font-bold text-white mb-2">Describe Your Vision</h3>
            <p class="text-gray-300 text-sm">
              Tell Imagi what you want to build using natural language. Be specific about features, data models, and user flows.
            </p>
          </div>
          
          <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700 flex flex-col items-center text-center">
            <div class="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center mb-4">
              <span class="text-primary-400 font-bold text-xl">2</span>
            </div>
            <h3 class="text-lg font-bold text-white mb-2">Review & Refine</h3>
            <p class="text-gray-300 text-sm">
              Examine the generated code, UI components, and backend logic. Iterate by asking the AI to make specific changes.
            </p>
          </div>
          
          <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700 flex flex-col items-center text-center">
            <div class="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center mb-4">
              <span class="text-primary-400 font-bold text-xl">3</span>
            </div>
            <h3 class="text-lg font-bold text-white mb-2">Export Your App</h3>
            <p class="text-gray-300 text-sm">
              Download your complete application with all source code and assets for deployment on your preferred platform.
            </p>
          </div>
        </div>
      </div>

      <h2>Current Capabilities</h2>
      <p>
        With Imagi Oasis, you can currently:
      </p>
      <ul>
        <li><strong>Generate full-stack Django applications</strong> with beautiful Vue.js frontends</li>
        <li><strong>Create complex data models</strong> with proper relationships and validations</li>
        <li><strong>Design responsive user interfaces</strong> using our component library</li>
        <li><strong>Implement authentication and authorization</strong> with secure practices</li>
        <li><strong>Export your code</strong> for local development or deployment</li>
      </ul>
      <p class="text-primary-400">
        <i class="fas fa-info-circle mr-1"></i> 
        Direct hosting/deployment features are coming soon! Currently, you can export your code for manual deployment.
      </p>

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