<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Hero Section -->
      <section class="py-24 text-center">
        <h1 class="text-6xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
          About Imagi
        </h1>
        <p class="text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
          Revolutionizing web development through the power of natural language and artificial intelligence.
        </p>
      </section>

      <!-- Mission Section -->
      <section class="py-16">
        <div class="max-w-4xl mx-auto">
          <h2 class="text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
            Our Mission
          </h2>
          <p class="text-gray-300 mb-8 leading-relaxed">
            At Imagi, we believe that creating web applications should be as simple as describing your vision. 
            Our mission is to democratize web development by removing technical barriers and empowering everyone 
            to bring their ideas to life.
          </p>
          <p class="text-gray-300 mb-8 leading-relaxed">
            We're building a future where technical expertise is no longer a prerequisite for creating 
            sophisticated web applications. Through the power of AI, we're making web development accessible, 
            efficient, and enjoyable for everyone.
          </p>
        </div>
      </section>

      <!-- Technology Section -->
      <section class="py-16">
        <div class="max-w-4xl mx-auto">
          <h2 class="text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
            Our Technology
          </h2>
          <div class="grid md:grid-cols-2 gap-8">
            <div class="card hover:bg-gradient-to-r hover:from-primary-500/5 hover:to-primary-600/5">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-4 bg-gray-800 rounded-lg">
                <i class="fas fa-brain"></i>
              </div>
              <h3 class="text-xl font-bold mb-3 text-white">Advanced AI Understanding</h3>
              <p class="text-gray-300 leading-relaxed">
                Our AI models are trained to understand context, user experience principles, and modern web development 
                practices, ensuring your vision is translated accurately into code.
              </p>
            </div>
            <div class="card hover:bg-gradient-to-r hover:from-primary-500/5 hover:to-primary-600/5">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-4 bg-gray-800 rounded-lg">
                <i class="fas fa-code"></i>
              </div>
              <h3 class="text-xl font-bold mb-3 text-white">Full-Stack Generation</h3>
              <p class="text-gray-300 leading-relaxed">
                We generate production-ready code for both frontend and backend, following best practices and 
                using modern frameworks and technologies.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Benefits Section -->
      <section class="py-16">
        <div class="max-w-4xl mx-auto">
          <h2 class="text-3xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
            Why Choose Imagi
          </h2>
          <div class="grid md:grid-cols-3 gap-6">
            <div class="card text-center">
              <h3 class="text-xl font-bold mb-3 text-white">Speed</h3>
              <p class="text-gray-300">
                Transform ideas into working applications in minutes instead of weeks or months.
              </p>
            </div>
            <div class="card text-center">
              <h3 class="text-xl font-bold mb-3 text-white">Quality</h3>
              <p class="text-gray-300">
                Generate clean, maintainable code that follows industry best practices.
              </p>
            </div>
            <div class="card text-center">
              <h3 class="text-xl font-bold mb-3 text-white">Flexibility</h3>
              <p class="text-gray-300">
                Easily modify and iterate on your application as your needs evolve.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="py-24 text-center">
        <h2 class="text-4xl font-bold mb-4 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
          Ready to Build Your Web App?
        </h2>
        <p class="text-xl text-gray-300 mb-8">
          Start creating your web application today with Imagi's AI-powered platform.
        </p>
        <router-link to="/builder" class="btn btn-primary inline-flex items-center gap-3">
          Get Started
          <i class="fas fa-arrow-right"></i>
        </router-link>
      </section>
    </div>
  </div>
</template>

<script setup>
// Component logic here
</script> 