<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Building UIs"
      description="Learn how to create beautiful user interfaces with Imagi Oasis."
      badge-text="UI DESIGN"
    >
      <!-- Introduction -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Understanding Imagi UI Building" icon="fas fa-paint-brush" color="primary" />
        <p class="text-gray-300 leading-relaxed mb-4">
          Imagi Oasis makes creating beautiful user interfaces simple for anyone, regardless of technical experience. 
          Rather than writing code, you'll use our visual editor and natural language descriptions to bring your vision to life.
        </p>
        
        <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border border-indigo-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-lightbulb text-indigo-300 text-sm"></i>
            </div>
            <div>
              <h4 class="text-indigo-300 font-semibold mb-2">Why it matters</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                A well-designed user interface creates a seamless experience for your users, making your application intuitive and enjoyable to use. With Imagi Oasis, you don't need design expertise to create professional-looking UIs.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Step 1: Describing UI -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="1. Describing Your UI Vision" icon="fas fa-eye" color="violet" />
        <p class="text-gray-300 leading-relaxed mb-6">
          The first step in building your UI is clearly describing what you want. Imagi works best when you provide:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-palette" color="violet" size="sm">
              <strong>Visual style:</strong> Modern, minimalist, colorful, dark/light theme
            </DocsListItem>
            <DocsListItem icon="fas fa-th-large" color="purple" size="sm">
              <strong>Layout preferences:</strong> Single page, multi-page, dashboard style
            </DocsListItem>
          </ul>
          
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-cubes" color="violet" size="sm">
              <strong>Key components:</strong> Forms, tables, cards, navigation menus
            </DocsListItem>
            <DocsListItem icon="fas fa-lightbulb" color="purple" size="sm">
              <strong>Inspirations:</strong> "Similar to Spotify's layout" or "Like Airbnb's booking flow"
            </DocsListItem>
          </ul>
        </div>
        
        <div class="bg-dark-800/60 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
          <h4 class="text-violet-300 font-semibold mb-3">Example Description</h4>
          <p class="text-gray-300 text-sm leading-relaxed">
            "I need a modern task management interface with a dark theme. It should have a sidebar navigation, a dashboard showing task statistics, and a main area displaying tasks in a card format. Each task card should show the title, description, due date, and a color-coded priority indicator. Include a floating action button to add new tasks."
          </p>
        </div>
      </DocsCard>

      <!-- Step 2: Reviewing and Customizing -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="2. Reviewing and Customizing Your UI" icon="fas fa-magic" color="blue" />
        <p class="text-gray-300 leading-relaxed mb-6">
          After Imagi generates your UI based on your description, you'll be able to:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-eye" color="blue" size="sm">
              <strong>Preview your UI</strong> - See exactly how your application looks and feels
            </DocsListItem>
            <DocsListItem icon="fas fa-paint-brush" color="cyan" size="sm">
              <strong>Request design changes</strong> - "Make the header larger" or "Change the color scheme to blue tones"
            </DocsListItem>
          </ul>
          
          <ul class="space-y-3">
            <DocsListItem icon="fas fa-plus-circle" color="blue" size="sm">
              <strong>Add new elements</strong> - "Add a search bar to the top navigation" or "Include a user profile section"
            </DocsListItem>
            <DocsListItem icon="fas fa-mobile-alt" color="cyan" size="sm">
              <strong>Check responsiveness</strong> - See how your UI adapts to different screen sizes
            </DocsListItem>
          </ul>
        </div>
        
        <div class="mt-6 bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-lightbulb text-blue-300 text-sm"></i>
            </div>
            <div>
              <h4 class="text-blue-300 font-semibold mb-2">Pro Tip</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Be specific with your feedback when requesting changes. Instead of saying "I don't like the buttons," try "Make the buttons rounded with a blue gradient background."
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- Step 3: Common UI Patterns -->
      <DocsCard color-variant="cyan">
        <DocsCardHeader title="3. Common UI Patterns" icon="fas fa-th-large" color="cyan" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Here are some popular UI patterns you can request when building your application:
        </p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 border border-cyan-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-th-large text-cyan-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Dashboard Layout</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">
              A central hub showing key metrics, statistics, and summaries with cards, charts, and widgets.
            </p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-list text-emerald-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">List/Table View</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">
              Organized display of data in rows and columns with sorting, filtering, and pagination features.
            </p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-edit text-violet-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Form Layout</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">
              Input fields, dropdowns, checkboxes, and submit buttons for collecting user information.
            </p>
          </div>
          
          <div class="bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm">
            <div class="flex items-center mb-3">
              <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-orange-400/20 to-red-400/20 border border-orange-400/20 flex items-center justify-center mr-3">
                <i class="fas fa-columns text-orange-300 text-sm"></i>
              </div>
              <h4 class="text-white font-semibold">Split View</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">
              Two-panel layout showing a master list on one side and details on the other.
            </p>
          </div>
        </div>
      </DocsCard>

      <!-- Step 4: UI Building Tips -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="4. UI Building Tips for Non-Designers" icon="fas fa-magic" color="violet" />
        
        <div class="space-y-6">
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-400/20 to-purple-400/20 border border-violet-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-palette text-violet-300"></i>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Stick to a consistent color scheme</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Request a specific color palette or ask Imagi to create one that matches your brand. Consistency in colors creates a more professional look.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400/20 to-cyan-400/20 border border-blue-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-text-height text-blue-300"></i>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Use a clear typographic hierarchy</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Ask for different text sizes to indicate importance: larger for headings, smaller for body text.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400/20 to-green-400/20 border border-emerald-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-mobile-alt text-emerald-300"></i>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Think mobile-first</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Specify that your UI should work well on mobile devices. Imagi will create responsive layouts that adapt to all screen sizes.
              </p>
            </div>
          </div>
          
          <div class="flex items-start gap-4">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-400/20 to-red-400/20 border border-orange-400/20 flex items-center justify-center flex-shrink-0">
              <i class="fas fa-universal-access text-orange-300"></i>
            </div>
            <div>
              <h4 class="text-white font-semibold mb-1">Consider accessibility</h4>
              <p class="text-gray-300 text-sm leading-relaxed">
                Request that your UI follows accessibility best practices to ensure everyone can use your application.
              </p>
            </div>
          </div>
        </div>
      </DocsCard>

      <!-- What's Next -->
      <DocsCard>
        <DocsCardHeader title="What's Next?" icon="fas fa-arrow-right" />
        <p class="text-gray-300 leading-relaxed mb-6">
          Now that you understand how to build UIs with Imagi Oasis, explore these related resources:
        </p>
        
        <div class="flex flex-wrap gap-4">
          <router-link 
            to="/docs/project-structure" 
            class="group/btn inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
          >
            <i class="fas fa-sitemap text-sm"></i>
            <span>Project Structure</span>
          </router-link>
          
          <router-link 
            to="/docs/backend" 
            class="group/btn inline-flex items-center gap-2 px-5 py-2.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-xl text-white font-medium transition-all duration-300"
          >
            <i class="fas fa-server text-sm"></i>
            <span>Backend Logic</span>
          </router-link>
        </div>
      </DocsCard>

      <!-- CTA -->
      <DocsCTASection 
        title="Start Building Your UI" 
        icon="fas fa-paint-brush" 
        description="Ready to create a beautiful interface for your application? Start a new project and describe your UI vision to see Imagi's design capabilities in action."
        buttonText="Create Project"
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