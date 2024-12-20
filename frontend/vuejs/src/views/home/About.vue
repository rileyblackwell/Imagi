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
            Reimagining Web Development
          </h1>
          <p class="text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            We're bridging the gap between imagination and implementation, making web development accessible to everyone 
            through the power of conversational AI.
          </p>
        </div>
      </section>

      <!-- Vision Section -->
      <section class="py-24">
        <div class="max-w-4xl mx-auto animate-fade-in">
          <h2 class="text-4xl font-bold mb-8 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            Our Vision
          </h2>
          <div class="space-y-6 text-lg">
            <p class="text-gray-300 leading-relaxed">
              At Imagi, we envision a world where creating web applications is as natural as having a conversation. 
              We believe that technology should adapt to humans, not the other way around. That's why we've built a 
              platform that understands your ideas and transforms them into reality, no coding required.
            </p>
            <p class="text-gray-300 leading-relaxed">
              Our mission is to democratize web development by removing technical barriers and empowering everyone - 
              entrepreneurs, creators, small business owners, and innovators - to bring their digital ideas to life 
              without learning complex programming languages or hiring expensive development teams.
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
                Our AI models are trained on millions of web applications and design patterns. They understand not just code, 
                but user experience, accessibility, and modern web development best practices. This ensures your vision is 
                translated into professional, production-ready applications.
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
                From responsive frontends built with Vue.js and Tailwind CSS to robust Django backends with RESTful APIs, 
                our platform generates complete, scalable web applications. We handle everything from database design to 
                user authentication.
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-24">
        <div class="max-w-4xl mx-auto">
          <h2 class="text-4xl font-bold mb-12 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-500 text-transparent bg-clip-text">
            Key Features
          </h2>
          <div class="grid md:grid-cols-3 gap-8">
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-6 bg-gray-800/50 rounded-xl
                          group-hover:scale-110 transition-transform duration-300">
                <i class="fas fa-comments"></i>
              </div>
              <h3 class="text-xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
                Conversational Interface
              </h3>
              <p class="text-gray-300 leading-relaxed">
                Build your web app through natural conversation. Describe features, make changes, and refine your application 
                just by chatting with our AI.
              </p>
            </div>
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-6 bg-gray-800/50 rounded-xl
                          group-hover:scale-110 transition-transform duration-300">
                <i class="fas fa-paint-brush"></i>
              </div>
              <h3 class="text-xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
                Beautiful Design
              </h3>
              <p class="text-gray-300 leading-relaxed">
                Get stunning, responsive designs that look great on all devices. Our AI understands modern design trends 
                and user experience principles.
              </p>
            </div>
            <div class="card group hover:bg-gray-800/50 transform hover:-translate-y-1 transition-all duration-300">
              <div class="w-12 h-12 flex items-center justify-center text-2xl text-primary-400 mb-6 bg-gray-800/50 rounded-xl
                          group-hover:scale-110 transition-transform duration-300">
                <i class="fas fa-rocket"></i>
              </div>
              <h3 class="text-xl font-bold mb-4 text-white group-hover:text-primary-400 transition-colors">
                Instant Deployment
              </h3>
              <p class="text-gray-300 leading-relaxed">
                Deploy your application with one click. We handle hosting, SSL certificates, and domain setup automatically.
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
            Join the Future of Web Development
          </h2>
          <p class="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Experience the power of AI-driven web development. Create your first project today and see how Imagi 
            can transform your ideas into reality.
          </p>
          <router-link 
            to="/builder" 
            class="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-xl font-semibold 
                   hover:from-primary-400 hover:to-primary-500 transform hover:scale-105 transition-all duration-300
                   shadow-lg hover:shadow-primary-500/25 inline-flex items-center gap-3"
          >
            Start Building
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

.card {
  @apply p-8 rounded-2xl bg-gray-800/30 border border-gray-700/50 backdrop-blur-sm;
}
</style> 