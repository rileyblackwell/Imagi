<template>
  <DocsLayout>
    <div class="max-w-5xl mx-auto">
      <DocsPageHeader
        badge-text="DOCUMENTATION"
        title="Welcome to Imagi"
        description="The AI-powered web application generator that turns your ideas into functional code."
      />

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
          <DocsCard title="Non-Technical Startup Founders">
            Quickly prototype and validate your startup ideas without needing to write code or hire developers upfront.
          </DocsCard>
          <DocsCard title="Technical Startup Founders">
            An easy-to-use platform for rapidly building and iterating on MVPs, so you can focus on validation instead of setup.
          </DocsCard>
          <DocsCard title="Non-Technical Employees">
            Prototype ideas within your company to test concepts and demonstrate value before committing major resources.
          </DocsCard>
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
          <DocsCard title="AI-Powered Chat Agent">
            Describe what you want to build in plain English. The AI agent helps you plan your application,
            writes code collaboratively with you, and answers questions along the way.
          </DocsCard>
          <DocsCard title="Visual Builder">
            Design your application's interface through a simple graphical interface. No need to understand
            complex frameworks or write UI code from scratch—just arrange, customize, and shape your vision visually.
          </DocsCard>
          <DocsCard title="One-Click Deployment">
            When you're ready to share your work, deploy your application to the web with a single click.
            No server configuration, no complex setup—just launch and share your URL.
          </DocsCard>
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
          <DocsCard title="Speed Without Sacrifice">
            Build and iterate quickly without creating technical debt. Every application Imagi generates
            uses clean, maintainable code that professional developers can easily understand and extend.
          </DocsCard>
          <DocsCard title="Affordable & Transparent">
            Get started for a fraction of the cost of hiring developers. No hidden fees, no vendor lock-in—
            just straightforward pricing that scales with your needs.
          </DocsCard>
          <DocsCard title="Purpose-Built for Prototyping">
            Unlike generic code generators, Imagi is designed specifically for rapid prototyping and early
            validation. Every feature focuses on helping you test ideas and gain traction quickly.
          </DocsCard>
          <DocsCard title="Room to Grow">
            When your project scales beyond a prototype, hand it off to engineering teams with confidence.
            Imagi generates standard Vue.js and Django code that any developer can work with.
          </DocsCard>
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
          <DocsNavigationCard
            to="/docs/quickstart"
            title="Quick Start Guide"
            description="Get up and running with Imagi in minutes with this step-by-step guide."
          />
          <DocsNavigationCard
            to="/docs/creating-projects"
            title="Creating Projects"
            description="Learn how to create and configure projects in detail."
          />
        </div>
      </section>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue';
import { DocsCard, DocsNavigationCard, DocsPageHeader } from '../components';
</script>
