<template>
  <DocsLayout>
    <!-- Hero Section matching home page -->
    <div class="max-w-5xl mx-auto">
      <!-- Hero Title and Description -->
      <div class="text-center mb-16 pt-8">
        <h1 class="text-5xl sm:text-6xl md:text-7xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
          Welcome to Imagi
        </h1>
        <p class="text-lg sm:text-xl text-gray-700 dark:text-white/80 tracking-wide font-medium max-w-3xl mx-auto transition-colors duration-300">
          The AI-powered web application generator that turns your ideas into functional code.
        </p>
      </div>

      <!-- What is Imagi -->
      <section class="mb-16">
        <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          What is Imagi?
        </h2>
        <div class="space-y-4 text-gray-700 dark:text-white/70 text-lg leading-relaxed transition-colors duration-300">
          <p>
            Imagi is a suite of AI tools that empowers non-technical developers to build web applications. 
            It gives you three simple tools that work together: design visually, chat with AI to plan and write code, 
            and launch to the web—all designed to be fast, affordable, and approachable.
          </p>
          <p>
            Whether you're prototyping a startup idea or validating a concept within your company, Imagi helps you 
            turn ideas into working applications without requiring extensive coding experience.
          </p>
        </div>
      </section>

      <!-- Who is it for -->
      <section class="mb-16">
        <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-8 tracking-tight transition-colors duration-300">
          Who is it for?
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Non-Technical Startup Founders
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Quickly prototype and validate your startup ideas without needing to write code or hire developers upfront.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Technical Startup Founders
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              An easy-to-use platform for rapidly building and iterating on MVPs, so you can focus on validation instead of setup.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Non-Technical Employees
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Prototype ideas within your company to test concepts and demonstrate value before committing major resources.
            </p>
          </div>
        </div>
      </section>

      <!-- How Does Imagi Work -->
      <section class="mb-16">
        <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          How Does Imagi Work?
        </h2>
        <p class="text-gray-700 dark:text-white/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Imagi combines three powerful tools into one seamless platform, each designed to accelerate different parts 
          of your application development process:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              AI-Powered Chat Agent
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Describe what you want to build in plain English. The AI agent helps you plan your application, 
              writes code collaboratively with you, and answers questions along the way.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Visual Builder
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Design your application's interface through a simple graphical interface. No need to understand 
              complex frameworks or write UI code from scratch—just arrange, customize, and shape your vision visually.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              One-Click Deployment
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              When you're ready to share your work, deploy your application to the web with a single click. 
              No server configuration, no complex setup—just launch and share your URL.
            </p>
          </div>
        </div>
      </section>

      <!-- Why Choose Imagi -->
      <section class="mb-16">
        <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Why Choose Imagi?
        </h2>
        <p class="text-gray-700 dark:text-white/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Imagi is built on the principle that building software should be accessible to everyone, not just 
          experienced engineers. Here's what sets us apart:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Speed Without Sacrifice
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Build and iterate quickly without creating technical debt. Every application Imagi generates 
              uses clean, maintainable code that professional developers can easily understand and extend.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Affordable & Transparent
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Get started for a fraction of the cost of hiring developers. No hidden fees, no vendor lock-in—
              just straightforward pricing that scales with your needs.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Purpose-Built for Prototyping
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Unlike generic code generators, Imagi is designed specifically for rapid prototyping and early 
              validation. Every feature focuses on helping you test ideas and gain traction quickly.
            </p>
          </div>
          
          <div class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">
              Room to Grow
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              When your project scales beyond a prototype, hand it off to engineering teams with confidence. 
              Imagi generates standard Vue.js and Django code that any developer can work with.
            </p>
          </div>
        </div>
      </section>

      <!-- Learn More Section -->
      <section class="mb-16">
        <h2 class="text-3xl sm:text-4xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Learn More
        </h2>
        <p class="text-gray-700 dark:text-white/70 text-lg leading-relaxed mb-8 transition-colors duration-300">
          Ready to dive deeper? Explore these guides to learn more about using Imagi:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <router-link 
            to="/docs/quickstart"
            class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300"
          >
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-2 transition-colors duration-300">
              Quick Start Guide
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Get up and running with Imagi in minutes with this step-by-step guide.
            </p>
          </router-link>

          <router-link 
            to="/docs/creating-projects"
            class="group relative p-8 rounded-2xl border border-gray-200 dark:border-gray-300 bg-white dark:bg-white shadow-md transition-all duration-300"
          >
            <h3 class="text-xl font-semibold text-gray-900 dark:text-black mb-2 transition-colors duration-300">
              Creating Projects
            </h3>
            <p class="text-gray-600 dark:text-black leading-relaxed transition-colors duration-300">
              Learn how to create and configure projects in detail.
            </p>
          </router-link>
        </div>
      </section>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
</script>

<style scoped>
/* Clean, minimal styling matching home page */
section {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

</style> 