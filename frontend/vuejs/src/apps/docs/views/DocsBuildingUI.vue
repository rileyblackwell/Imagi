<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Building UIs
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Learn how to create beautiful user interfaces with Imagi Oasis.
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
          <h2 class="text-2xl font-bold text-white mb-4">Understanding Imagi UI Building</h2>
          <p class="text-gray-300">
            Imagi Oasis makes creating beautiful user interfaces simple for anyone, regardless of technical experience. 
            Rather than writing code, you'll use our visual editor and natural language descriptions to bring your vision to life.
          </p>
          <div class="mt-6 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
            <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
              <i class="fas fa-lightbulb mr-2"></i>
              Why it matters
            </h4>
            <p class="text-gray-300 text-sm mb-0">
              A well-designed user interface creates a seamless experience for your users, making your application intuitive and enjoyable to use. With Imagi Oasis, you don't need design expertise to create professional-looking UIs.
            </p>
          </div>
        </div>

        <!-- Section 1: Describing your UI -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">1. Describing Your UI Vision</h2>
            <p class="text-gray-300">
              The first step in building your UI is clearly describing what you want. Imagi works best when you provide:
            </p>
            <ul class="space-y-2 mt-4">
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-check text-primary-400 text-xs"></i>
                </div>
                <span><strong>Visual style</strong>: Modern, minimalist, colorful, dark/light theme</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-check text-primary-400 text-xs"></i>
                </div>
                <span><strong>Layout preferences</strong>: Single page, multi-page, dashboard style</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-check text-primary-400 text-xs"></i>
                </div>
                <span><strong>Key components</strong>: Forms, tables, cards, navigation menus</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-check text-primary-400 text-xs"></i>
                </div>
                <span><strong>Inspirations</strong>: "Similar to Spotify's layout" or "Like Airbnb's booking flow"</span>
              </li>
            </ul>
            <div class="mt-6 bg-dark-800 p-4 rounded-lg">
              <h4 class="text-primary-400 mt-0 mb-2 text-base font-medium">Example Description</h4>
              <p class="text-gray-300 text-sm mb-0">
                "I need a modern task management interface with a dark theme. It should have a sidebar navigation, a dashboard showing task statistics, and a main area displaying tasks in a card format. Each task card should show the title, description, due date, and a color-coded priority indicator. Include a floating action button to add new tasks."
              </p>
            </div>
          </div>
        </div>

        <!-- Section 2: Reviewing and Customizing -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">2. Reviewing and Customizing Your UI</h2>
            <p class="text-gray-300">
              After Imagi generates your UI based on your description, you'll be able to:
            </p>
            <ul class="space-y-2 mt-4">
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-eye text-blue-400 text-xs"></i>
                </div>
                <span><strong>Preview your UI</strong> - See exactly how your application looks and feels</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-paint-brush text-blue-400 text-xs"></i>
                </div>
                <span><strong>Request design changes</strong> - "Make the header larger" or "Change the color scheme to blue tones"</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-plus-circle text-blue-400 text-xs"></i>
                </div>
                <span><strong>Add new elements</strong> - "Add a search bar to the top navigation" or "Include a user profile section"</span>
              </li>
              <li class="flex items-start">
                <div class="flex-shrink-0 w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-mobile-alt text-blue-400 text-xs"></i>
                </div>
                <span><strong>Check responsiveness</strong> - See how your UI adapts to different screen sizes</span>
              </li>
            </ul>
            <div class="mt-6 bg-primary-500/10 border border-primary-500/20 rounded-lg p-4">
              <h4 class="text-primary-400 mt-0 mb-2 flex items-center text-base font-medium">
                <i class="fas fa-lightbulb mr-2"></i>
                Pro Tip
              </h4>
              <p class="text-gray-300 text-sm mb-0">
                Be specific with your feedback when requesting changes. Instead of saying "I don't like the buttons," try "Make the buttons rounded with a blue gradient background."
              </p>
            </div>
          </div>
        </div>

        <!-- Section 3: Common UI Patterns -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-green-500 to-emerald-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">3. Common UI Patterns</h2>
            <p class="text-gray-300">
              Here are some popular UI patterns you can request when building your application:
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div class="bg-dark-800/50 p-4 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2 flex items-center">
                  <div class="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-2">
                    <i class="fas fa-th-large text-green-400 text-xs"></i>
                  </div>
                  Dashboard Layout
                </h4>
                <p class="text-gray-300 text-sm">
                  A central hub showing key metrics, statistics, and summaries with cards, charts, and widgets.
                </p>
              </div>
              
              <div class="bg-dark-800/50 p-4 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2 flex items-center">
                  <div class="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-2">
                    <i class="fas fa-list text-green-400 text-xs"></i>
                  </div>
                  List/Table View
                </h4>
                <p class="text-gray-300 text-sm">
                  Organized display of data in rows and columns with sorting, filtering, and pagination features.
                </p>
              </div>
              
              <div class="bg-dark-800/50 p-4 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2 flex items-center">
                  <div class="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-2">
                    <i class="fas fa-edit text-green-400 text-xs"></i>
                  </div>
                  Form Layout
                </h4>
                <p class="text-gray-300 text-sm">
                  Input fields, dropdowns, checkboxes, and submit buttons for collecting user information.
                </p>
              </div>
              
              <div class="bg-dark-800/50 p-4 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2 flex items-center">
                  <div class="w-6 h-6 rounded-full bg-green-500/20 flex items-center justify-center mr-2">
                    <i class="fas fa-columns text-green-400 text-xs"></i>
                  </div>
                  Split View
                </h4>
                <p class="text-gray-300 text-sm">
                  Two-panel layout showing a master list on one side and details on the other.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: UI Building Tips -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-purple-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">4. UI Building Tips for Non-Designers</h2>
            
            <ul class="space-y-4 mt-4">
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-palette text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Stick to a consistent color scheme</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Request a specific color palette or ask Imagi to create one that matches your brand. Consistency in colors creates a more professional look.
                  </p>
                </div>
              </li>
              
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-text-height text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Use a clear typographic hierarchy</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Ask for different text sizes to indicate importance: larger for headings, smaller for body text.
                  </p>
                </div>
              </li>
              
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-mobile-alt text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Think mobile-first</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Specify that your UI should work well on mobile devices. Imagi will create responsive layouts that adapt to all screen sizes.
                  </p>
                </div>
              </li>
              
              <li class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-universal-access text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Consider accessibility</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Request that your UI follows accessibility best practices to ensure everyone can use your application.
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- What's Next -->
        <h2>What's Next?</h2>
        <p>
          Now that you understand how to build UIs with Imagi Oasis, explore these related resources:
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
            to="/docs/backend" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-server text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Backend Logic</h3>
                <p class="text-gray-400 text-sm">Learn how data is stored and processed in your app</p>
              </div>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
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