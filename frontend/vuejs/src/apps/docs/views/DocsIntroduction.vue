<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Welcome to Imagi"
      description="The AI-powered web application generator that turns your ideas into functional code."
    >
      <!-- Enhanced Introduction -->
      <DocsCard>
        <DocsCardHeader title="What is Imagi?" />
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-300 mb-4">
          Imagi is a suite of AI tools that empowers non-technical developers to build web applications. 
          It gives you three simple tools that work together: design visually, chat with AI to plan and write code, 
          and launch to the web—all designed to be fast, affordable, and approachable.
        </p>
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-300">
          Whether you're prototyping a startup idea or validating a concept within your company, Imagi helps you 
          turn ideas into working applications without requiring extensive coding experience.
        </p>
      </DocsCard>

      <!-- Enhanced Target Audience -->
      <DocsCard>
        <DocsCardHeader title="Who is it for?" />
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Non-Technical Startup Founders</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">Quickly prototype and validate your startup ideas without needing to write code or hire developers upfront.</p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Technical Startup Founders</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">An easy-to-use platform for rapidly building and iterating on MVPs, so you can focus on validation instead of setup.</p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Non-Technical Employees</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">Prototype ideas within your company to test concepts and demonstrate value before committing major resources.</p>
          </div>
        </div>
      </DocsCard>

      <!-- How Does Imagi Work -->
      <DocsCard>
        <DocsCardHeader title="How Does Imagi Work?" />
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-300 mb-6">
          Imagi combines three powerful tools into one seamless platform, each designed to accelerate different parts 
          of your application development process:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">AI-Powered Chat Agent</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Describe what you want to build in plain English. The AI agent helps you plan your application, 
              writes code collaboratively with you, and answers questions along the way.
            </p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Visual Builder</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Design your application's interface through a simple graphical interface. No need to understand 
              complex frameworks or write UI code from scratch—just arrange, customize, and shape your vision visually.
            </p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">One-Click Deployment</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              When you're ready to share your work, deploy your application to the web with a single click. 
              No server configuration, no complex setup—just launch and share your URL.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- Why Choose Imagi -->
      <DocsCard>
        <DocsCardHeader title="Why Choose Imagi?" />
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed transition-colors duration-300 mb-6">
          Imagi is built on the principle that building software should be accessible to everyone, not just 
          experienced engineers. Here's what sets us apart:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Speed Without Sacrifice</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Build and iterate quickly without creating technical debt. Every application Imagi generates 
              uses clean, maintainable code that professional developers can easily understand and extend.
            </p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Affordable & Transparent</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Get started for a fraction of the cost of hiring developers. No hidden fees, no vendor lock-in—
              just straightforward pricing that scales with your needs.
            </p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Purpose-Built for Prototyping</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Unlike generic code generators, Imagi is designed specifically for rapid prototyping and early 
              validation. Every feature focuses on helping you test ideas and gain traction quickly.
            </p>
          </div>
          
          <div class="bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl p-4 backdrop-blur-sm transition-colors duration-300">
            <h4 class="text-gray-900 dark:text-white font-semibold mb-3 transition-colors duration-300">Room to Grow</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              When your project scales beyond a prototype, hand it off to engineering teams with confidence. 
              Imagi generates standard Vue.js and Django code that any developer can work with.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- Learn More Section -->
      <DocsCard>
        <DocsCardHeader title="Learn More" />
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed mb-6 transition-colors duration-300">
          Ready to dive deeper? Explore these guides to learn more about using Imagi:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <router-link 
            to="/docs/quickstart"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Quick Start Guide</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Get up and running with Imagi in minutes with this step-by-step guide.
            </p>
          </router-link>

          <router-link 
            to="/docs/creating-projects"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Creating Projects</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Learn how to create and configure projects in detail.
            </p>
          </router-link>

          <router-link 
            to="/docs/project-structure"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Project Structure</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Understand how Imagi projects are organized and structured.
            </p>
          </router-link>

          <router-link 
            to="/docs/deployment"
            class="group bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 rounded-xl p-4 backdrop-blur-sm transition-all duration-300"
          >
            <h4 class="text-gray-900 dark:text-white font-semibold mb-2 transition-colors duration-300">Deployment Guide</h4>
            <p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed transition-colors duration-300">
              Deploy your application to the web with detailed deployment instructions.
            </p>
          </router-link>
        </div>
      </DocsCard>
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsContentWrapper, DocsCard, DocsCardHeader } from '../components';
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