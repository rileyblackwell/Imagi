<script setup>
// Component logic here
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Hero Section -->
      <section class="py-32 text-center relative">
        <!-- Background decoration -->
        <div class="absolute inset-0 overflow-hidden">
          <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
          <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-600/10 rounded-full blur-3xl"></div>
        </div>
        
        <div class="relative">
          <h1 class="text-7xl font-bold mb-8 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text animate-gradient">
            Your Words to
            <br />
            Working Web Apps
          </h1>
          <p class="text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed mb-12 animate-fade-in">
            Describe your dream web application in plain English, and watch as Imagi's AI transforms your vision into 
            a fully functional website. <span class="text-primary-400">From concept to code in minutes.</span>
          </p>
          <div class="flex justify-center gap-6 animate-fade-in-up">
            <router-link 
              to="/builder" 
              class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-semibold 
                     hover:from-primary-400 hover:to-primary-500 transform hover:scale-105 transition-all duration-300
                     shadow-lg hover:shadow-primary-500/25"
            >
              Start Creating
              <i class="fas fa-arrow-right ml-2"></i>
            </router-link>
            <router-link 
              to="/about" 
              class="px-8 py-4 bg-gray-800/50 text-white rounded-xl font-semibold border border-gray-700
                     hover:bg-gray-700/50 transform hover:scale-105 transition-all duration-300"
            >
              Learn More
            </router-link>
          </div>
        </div>
      </section>

      <!-- Feature Section -->
      <section class="py-24">
        <div class="grid md:grid-cols-3 gap-8">
          <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
            <div class="text-primary-400 text-4xl mb-6 group-hover:scale-110 transition-transform duration-300">
              <i class="fas fa-wand-magic-sparkles"></i>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
              Natural Language to Code
            </h3>
            <p class="text-gray-300 leading-relaxed">
              Simply describe what you want to build in everyday language. Our AI understands your requirements and 
              generates professional-grade code instantly.
            </p>
          </div>
          <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
            <div class="text-primary-400 text-4xl mb-6 group-hover:scale-110 transition-transform duration-300">
              <i class="fas fa-layer-group"></i>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
              Complete Web Solutions
            </h3>
            <p class="text-gray-300 leading-relaxed">
              Get everything you need: beautiful UI, robust backend, database setup, API integrations, and user authentication - 
              all from a simple conversation.
            </p>
          </div>
          <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
            <div class="text-primary-400 text-4xl mb-6 group-hover:scale-110 transition-transform duration-300">
              <i class="fas fa-rocket"></i>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
              Instant Deployment
            </h3>
            <p class="text-gray-300 leading-relaxed">
              Your web app is ready to launch immediately. We handle hosting, SSL, and domain setup, so you can focus on 
              bringing your ideas to life.
            </p>
          </div>
        </div>
      </section>

      <!-- Workflow Section -->
      <section class="py-24 relative">
        <div class="max-w-5xl mx-auto">
          <h2 class="text-4xl font-bold mb-12 text-center bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            How It Works
          </h2>
          <div class="grid md:grid-cols-4 gap-8">
            <div class="card text-center">
              <div class="text-primary-400 text-3xl mb-4">
                <i class="fas fa-comment-dots"></i>
              </div>
              <h3 class="text-xl font-bold mb-2">Describe</h3>
              <p class="text-gray-300 text-sm">Tell us about your web app in plain English</p>
            </div>
            <div class="card text-center">
              <div class="text-primary-400 text-3xl mb-4">
                <i class="fas fa-robot"></i>
              </div>
              <h3 class="text-xl font-bold mb-2">Generate</h3>
              <p class="text-gray-300 text-sm">AI creates your custom code and design</p>
            </div>
            <div class="card text-center">
              <div class="text-primary-400 text-3xl mb-4">
                <i class="fas fa-sliders"></i>
              </div>
              <h3 class="text-xl font-bold mb-2">Customize</h3>
              <p class="text-gray-300 text-sm">Refine and adjust through conversation</p>
            </div>
            <div class="card text-center">
              <div class="text-primary-400 text-3xl mb-4">
                <i class="fas fa-paper-plane"></i>
              </div>
              <h3 class="text-xl font-bold mb-2">Launch</h3>
              <p class="text-gray-300 text-sm">Deploy your app with one click</p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="py-32 text-center relative">
        <!-- Background decoration -->
        <div class="absolute inset-0 overflow-hidden">
          <div class="absolute -bottom-40 -right-40 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
        </div>
        
        <div class="relative">
          <h2 class="text-5xl font-bold mb-6 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            Ready to Build Something Amazing?
          </h2>
          <p class="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Join the future of web development. Create stunning, functional web applications without writing a single line of code.
            Start building your next big idea today.
          </p>
          <router-link 
            to="/builder" 
            class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-semibold 
                   hover:from-primary-400 hover:to-primary-500 transform hover:scale-105 transition-all duration-300
                   shadow-lg hover:shadow-primary-500/25 inline-flex items-center gap-3"
          >
            Start Free Trial
            <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<style>
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient 8s ease infinite;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-fade-in {
  animation: fadeIn 1s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  animation: fadeInUp 1s ease-out;
}

.card {
  @apply p-8 rounded-2xl bg-gray-800/30 border border-gray-700/50 backdrop-blur-sm;
}
</style>
