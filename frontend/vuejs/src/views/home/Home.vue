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
            Build Web Apps with
            <br />
            Natural Language
          </h1>
          <p class="text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed mb-12 animate-fade-in">
            Transform your ideas into fully functional web applications using simple English. 
            <span class="text-primary-400">No coding required.</span>
          </p>
          <div class="flex justify-center gap-6 animate-fade-in-up">
            <router-link 
              to="/builder" 
              class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-semibold 
                     hover:from-primary-400 hover:to-primary-500 transform hover:scale-105 transition-all duration-300
                     shadow-lg hover:shadow-primary-500/25"
            >
              Start Building
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
              <i class="fas fa-magic"></i>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">AI-Powered Generation</h3>
            <p class="text-gray-300 leading-relaxed">
              Our advanced AI understands your requirements and generates production-ready code instantly.
            </p>
          </div>
          <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
            <div class="text-primary-400 text-4xl mb-6 group-hover:scale-110 transition-transform duration-300">
              <i class="fas fa-bolt"></i>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">Lightning Fast</h3>
            <p class="text-gray-300 leading-relaxed">
              Create complete web applications in minutes instead of weeks or months.
            </p>
          </div>
          <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
            <div class="text-primary-400 text-4xl mb-6 group-hover:scale-110 transition-transform duration-300">
              <i class="fas fa-code"></i>
            </div>
            <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">Full-Stack Support</h3>
            <p class="text-gray-300 leading-relaxed">
              Generate both frontend and backend code with modern frameworks and best practices.
            </p>
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
            Ready to Build Your Web App?
          </h2>
          <p class="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Start creating your web application today with Imagi's AI-powered platform.
            Join thousands of developers who are building the future.
          </p>
          <router-link 
            to="/builder" 
            class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-semibold 
                   hover:from-primary-400 hover:to-primary-500 transform hover:scale-105 transition-all duration-300
                   shadow-lg hover:shadow-primary-500/25 inline-flex items-center"
          >
            Get Started
            <i class="fas fa-arrow-right ml-2"></i>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<style>
@keyframes gradient {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient 8s ease infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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
