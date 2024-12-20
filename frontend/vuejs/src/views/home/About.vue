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
        
        <div class="relative animate-fade-in">
          <h1 class="text-7xl font-bold mb-8 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text animate-gradient">
            About Imagi
          </h1>
          <p class="text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            Revolutionizing web development through the power of natural language and artificial intelligence.
          </p>
        </div>
      </section>

      <!-- Mission Section -->
      <section class="py-24">
        <div class="max-w-4xl mx-auto animate-fade-in">
          <h2 class="text-4xl font-bold mb-8 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            Our Mission
          </h2>
          <div class="space-y-6 text-lg">
            <p class="text-gray-300 leading-relaxed">
              At Imagi, we believe that creating web applications should be as simple as describing your vision. 
              Our mission is to democratize web development by removing technical barriers and empowering everyone 
              to bring their ideas to life.
            </p>
            <p class="text-gray-300 leading-relaxed">
              We're building a future where technical expertise is no longer a prerequisite for creating 
              sophisticated web applications. Through the power of AI, we're making web development accessible, 
              efficient, and enjoyable for everyone.
            </p>
          </div>
        </div>
      </section>

      <!-- Technology Section -->
      <section class="py-24 relative">
        <!-- Background decoration -->
        <div class="absolute inset-0 overflow-hidden">
          <div class="absolute -right-40 top-1/2 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
        </div>
        
        <div class="max-w-4xl mx-auto relative">
          <h2 class="text-4xl font-bold mb-12 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            Our Technology
          </h2>
          <div class="grid md:grid-cols-2 gap-8">
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-6 bg-gray-800/50 rounded-xl
                          group-hover:scale-110 transition-transform duration-300">
                <i class="fas fa-brain"></i>
              </div>
              <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
                Advanced AI Understanding
              </h3>
              <p class="text-gray-300 leading-relaxed">
                Our AI models are trained to understand context, user experience principles, and modern web development 
                practices, ensuring your vision is translated accurately into code.
              </p>
            </div>
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-6 bg-gray-800/50 rounded-xl
                          group-hover:scale-110 transition-transform duration-300">
                <i class="fas fa-code"></i>
              </div>
              <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
                Full-Stack Generation
              </h3>
              <p class="text-gray-300 leading-relaxed">
                We generate production-ready code for both frontend and backend, following best practices and 
                using modern frameworks and technologies.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Benefits Section -->
      <section class="py-24">
        <div class="max-w-4xl mx-auto">
          <h2 class="text-4xl font-bold mb-12 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            Why Choose Imagi
          </h2>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300 text-center">
              <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">Speed</h3>
              <p class="text-gray-300 leading-relaxed">
                Transform ideas into working applications in minutes instead of weeks or months.
              </p>
            </div>
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300 text-center">
              <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">Quality</h3>
              <p class="text-gray-300 leading-relaxed">
                Generate clean, maintainable code that follows industry best practices.
              </p>
            </div>
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300 text-center">
              <h3 class="text-2xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">Flexibility</h3>
              <p class="text-gray-300 leading-relaxed">
                Easily modify and iterate on your application as your needs evolve.
              </p>
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
                   shadow-lg hover:shadow-primary-500/25 inline-flex items-center gap-3"
          >
            Get Started
            <i class="fas fa-arrow-right"></i>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
// Component logic here
</script>

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

.card {
  @apply p-8 rounded-2xl bg-gray-800/30 border border-gray-700/50 backdrop-blur-sm;
}
</style> 