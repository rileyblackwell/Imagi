<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Best Practices
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Tips and strategies for creating successful applications with Imagi Oasis.
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
          <h2 class="text-2xl font-bold text-white mb-4">Creating Successful Applications</h2>
          <p class="text-gray-300">
            While Imagi Oasis makes building web applications incredibly simple, following these best practices will help you create more robust, user-friendly applications that achieve your goals.
          </p>
        </div>

        <!-- Section 1: Project Planning -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">1. Project Planning Best Practices</h2>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-bullseye text-primary-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Define clear goals and requirements</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Before starting your project, clearly define what your application needs to accomplish. What problem does it solve? Who will use it? What key features are essential? Having a clear vision will help Imagi generate exactly what you need.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-puzzle-piece text-primary-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Start with a Minimum Viable Product (MVP)</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Begin with core features that solve your primary need, then add more functionality later. This approach lets you test your application sooner and refine it based on real-world use.
                  </p>
                  <div class="mt-3 p-3 bg-dark-800 rounded-lg">
                    <p class="text-primary-300 text-xs font-medium">EXAMPLE</p>
                    <p class="text-gray-300 text-sm italic">Instead of "I need a full customer relationship management system," start with "I need an application to track customer contacts and communications."</p>
                  </div>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-sitemap text-primary-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Map out your data needs</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Identify what information your application needs to store and how different pieces of data relate to each other. This will help Imagi create the right data models for your application.
                  </p>
                  <div class="mt-3 p-3 bg-dark-800 rounded-lg">
                    <p class="text-primary-300 text-xs font-medium">EXAMPLE</p>
                    <p class="text-gray-300 text-sm italic">"My event management app needs to store information about events (name, date, location), attendees (name, email, phone), and registrations (which attendees are coming to which events)."</p>
                  </div>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-primary-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-users text-primary-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Consider your users' needs and abilities</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Think about who will use your application and what they need to accomplish. Consider their technical skill level, device preferences, and potential accessibility requirements.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 2: Effective Description Writing -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">2. Writing Effective Project Descriptions</h2>
            <p class="text-gray-300">
              The way you describe your project to Imagi directly affects the quality of the generated application. Here's how to communicate effectively:
            </p>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-list-ul text-blue-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Be specific and organized</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Structure your description with sections for features, data models, user roles, and design preferences. Use bullet points or numbered lists to separate different requirements.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-theater-masks text-blue-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Use user stories</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Frame features as user stories to clearly communicate functionality: "As a [type of user], I want to [action] so that [benefit]."
                  </p>
                  <div class="mt-3 p-3 bg-dark-800 rounded-lg">
                    <p class="text-blue-300 text-xs font-medium">EXAMPLE</p>
                    <p class="text-gray-300 text-sm italic">"As an event organizer, I want to send automatic email reminders to attendees one day before an event so that fewer people forget to attend."</p>
                  </div>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-paint-brush text-blue-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Reference familiar applications and designs</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Mentioning well-known applications helps Imagi understand your design goals. For example, "Dashboard layout similar to Trello" or "User profile page styled like LinkedIn."
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-blue-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-search text-blue-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Specify what to prioritize</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Let Imagi know what aspects of your application are most important (e.g., user experience, data security, mobile responsiveness, performance).
                  </p>
                </div>
              </div>
              
              <div class="mt-6 bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <h4 class="text-blue-400 mt-0 mb-2 flex items-center text-base font-medium">
                  <i class="fas fa-lightbulb mr-2"></i>
                  Example of an Effective Project Description
                </h4>
                <div class="text-gray-300 text-sm">
                  <p class="font-medium">Project: Event Management Application</p>
                  <p class="mt-2"><span class="font-medium">Purpose:</span> Create a web application for organizing and managing events, tracking attendees, and sending communications.</p>
                  <p class="mt-2"><span class="font-medium">Key Features:</span></p>
                  <ul class="list-disc pl-5 space-y-1 mt-1">
                    <li>Event creation with name, date, time, location, and description</li>
                    <li>Attendee registration form with custom fields</li>
                    <li>Automatic email confirmations and reminders</li>
                    <li>Dashboard showing event statistics and attendance</li>
                    <li>QR code check-in system for events</li>
                  </ul>
                  <p class="mt-2"><span class="font-medium">User Roles:</span></p>
                  <ul class="list-disc pl-5 space-y-1 mt-1">
                    <li>Admin (full access to all events and settings)</li>
                    <li>Event Manager (can create and manage specific events)</li>
                    <li>Attendee (can register for events and view their registrations)</li>
                  </ul>
                  <p class="mt-2"><span class="font-medium">Design Preferences:</span> Clean, minimal design with a dark theme. Dashboard layout similar to Eventbrite but more simplified. Mobile-responsive design is important as many users will access on phones.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Testing & Refinement -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-green-500 to-emerald-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">3. Testing & Refining Your Application</h2>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-tasks text-green-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Test all key user journeys</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Before deploying, walk through all important user paths in your application. For example, in an e-commerce app, test the entire process from browsing products to completing checkout.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-mobile-alt text-green-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Check mobile responsiveness</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Test your application on different devices and screen sizes. Use the preview mode's responsive design tools to see how your app looks on mobile, tablet, and desktop.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-user-friends text-green-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Get feedback from potential users</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Share your application with a small group of trusted users before full launch. Their feedback can help identify usability issues or missing features you might have overlooked.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-pencil-alt text-green-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Refine with iterative requests</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Use Imagi's refinement feature to make specific improvements to your application. For example, "Improve the navigation menu by adding dropdown submenus" or "Make the registration form more user-friendly."
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-green-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-shield-alt text-green-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Test edge cases and error handling</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Try various scenarios that might cause problems: submitting forms with invalid data, testing with very large quantities of data, or using special characters in text fields.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 4: Post-Deployment Best Practices -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-purple-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">4. Post-Deployment Best Practices</h2>
            
            <div class="space-y-6 mt-6">
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-chart-line text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Monitor performance and usage</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Regularly check your application's analytics to understand how people are using it. Look for potential bottlenecks or features that aren't being utilized.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-database text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Regularly back up your data</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Even though Imagi provides automatic backups, it's good practice to periodically export your data, especially before making significant changes to your application.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-sync-alt text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Update gradually</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    When making significant changes to your application, roll them out incrementally rather than all at once. This makes it easier to identify and fix any issues that arise.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-comments text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Collect and act on user feedback</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Create a simple way for users to provide suggestions or report issues. This feedback is invaluable for improving your application over time.
                  </p>
                </div>
              </div>
              
              <div class="flex items-start">
                <div class="flex-shrink-0 w-7 h-7 rounded-full bg-purple-500/20 flex items-center justify-center mr-3 mt-1">
                  <i class="fas fa-book text-purple-400 text-xs"></i>
                </div>
                <div>
                  <strong class="text-white">Document your application</strong>
                  <p class="text-gray-300 text-sm mt-1">
                    Create simple documentation explaining how to use your application. This can be especially helpful for new users or when onboarding team members.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- What's Next -->
        <h2>What's Next?</h2>
        <p>
          Now that you understand best practices for creating applications with Imagi Oasis, explore these related resources:
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <router-link 
            to="/docs/deployment" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-cloud-upload-alt text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Deployment Guide</h3>
                <p class="text-gray-400 text-sm">Learn how to take your application live</p>
              </div>
            </div>
          </router-link>
          <router-link 
            to="/docs/troubleshooting" 
            class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
          >
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                <i class="fas fa-bug text-xl text-primary-400"></i>
              </div>
              <div>
                <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">Troubleshooting</h3>
                <p class="text-gray-400 text-sm">Solutions to common issues</p>
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