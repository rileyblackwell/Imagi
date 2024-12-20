<script setup>
// Component logic here
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
    <div class="max-w-7xl mx-auto px-4">
      <!-- Hero Section -->
      <section class="py-24 text-center">
        <h1 class="text-6xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
          Build Web Apps with Natural Language
        </h1>
        <p class="text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed mb-12">
          Transform your ideas into fully functional web applications using simple English. 
          No coding required.
        </p>
        <div class="flex justify-center gap-6">
          <router-link to="/builder" class="btn btn-primary">
            Start Building
          </router-link>
          <router-link to="/about" class="btn btn-secondary">
            Learn More
          </router-link>
        </div>
      </section>

      <!-- Feature Section -->
      <section class="py-16">
        <div class="grid md:grid-cols-3 gap-8">
          <div class="card">
            <div class="text-primary-500 text-4xl mb-4">
              <i class="fas fa-magic"></i>
            </div>
            <h3 class="text-xl font-bold mb-3">AI-Powered Generation</h3>
            <p class="text-gray-300">
              Our advanced AI understands your requirements and generates production-ready code.
            </p>
          </div>
          <div class="card">
            <div class="text-primary-500 text-4xl mb-4">
              <i class="fas fa-bolt"></i>
            </div>
            <h3 class="text-xl font-bold mb-3">Lightning Fast</h3>
            <p class="text-gray-300">
              Create complete web applications in minutes instead of weeks or months.
            </p>
          </div>
          <div class="card">
            <div class="text-primary-500 text-4xl mb-4">
              <i class="fas fa-code"></i>
            </div>
            <h3 class="text-xl font-bold mb-3">Full-Stack Support</h3>
            <p class="text-gray-300">
              Generate both frontend and backend code with modern frameworks and best practices.
            </p>
          </div>
        </div>
      </section>

      <!-- CTA Section -->
      <section class="py-24 text-center">
        <h2 class="text-4xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-primary-600 text-transparent bg-clip-text">
          Ready to Build Your Web App?
        </h2>
        <p class="text-xl text-gray-300 mb-8">
          Start creating your web application today with Imagi's AI-powered platform.
        </p>
        <router-link to="/builder" class="btn btn-primary">
          Get Started
          <i class="fas fa-arrow-right ml-2"></i>
        </router-link>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(to bottom, #121212, #1a1a1a);
}
</style>
