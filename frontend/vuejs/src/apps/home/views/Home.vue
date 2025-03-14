<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[90vh] md:min-h-[80vh] flex items-center justify-center overflow-hidden py-24 md:py-20 mt-16 sm:mt-0">
        <!-- Enhanced Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
          <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex flex-col lg:flex-row items-center gap-8 lg:gap-16">
            <!-- Left side - Main content -->
            <div class="flex-1 text-center lg:text-left">
              <div class="inline-block px-4 py-1 bg-dark-800/50 backdrop-blur-sm rounded-full border border-primary-500/50 mb-6">
                <span class="text-sm font-medium text-gray-300">
                  <i class="fas fa-sparkles text-primary-500 mr-2"></i>
                  AI-Powered Web Development
                </span>
              </div>

              <h1 class="text-3xl sm:text-4xl lg:text-6xl font-bold tracking-tight mb-6">
                <span class="text-white block mb-1">Transform Your</span>
                <span class="text-white block mb-1">Ideas Into</span>
                <GradientText variant="primary" class="font-bold block text-4xl sm:text-5xl lg:text-7xl">
                  Web Applications
                </GradientText>
              </h1>

              <p class="text-lg sm:text-xl text-gray-300 mb-8 max-w-xl">
                Create professional web applications using natural language. 
                Describe your vision, and watch as AI brings it to life.
              </p>

              <!-- Buttons -->
              <div class="flex flex-col sm:flex-row items-center gap-4 justify-center lg:justify-start">
                <HomeNavbarButton
                  :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                  class="group relative w-full sm:w-auto !h-14 px-8 rounded-xl border border-primary-500/30 hover:border-primary-500/50 bg-gradient-to-r from-primary-500/20 to-violet-500/20 hover:from-primary-500/30 hover:to-violet-500/30 backdrop-blur-sm transition-all duration-500"
                >
                  <span class="relative z-10 flex items-center justify-center text-lg font-medium text-white group-hover:text-white/90">
                    Start Building
                    <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform duration-500"></i>
                  </span>
                </HomeNavbarButton>

                <a 
                  href="#how-it-works" 
                  class="group flex items-center gap-3 text-gray-300 hover:text-white transition-all duration-300 px-6 py-3 rounded-xl border border-dark-700 hover:border-primary-500/30 bg-dark-800/50 hover:bg-dark-800/80 backdrop-blur-sm"
                >
                  <div class="w-8 h-8 rounded-full bg-dark-700 group-hover:bg-primary-500/20 flex items-center justify-center transition-all duration-300">
                    <i class="fas fa-play text-xs text-primary-400"></i>
                  </div>
                  <span class="font-medium">How It Works</span>
                </a>
              </div>
            </div>

            <!-- Right side - Interactive Demo -->
            <div class="flex-1">
              <AnimatedTerminal />
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 relative">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">Why Choose Imagi</h2>
            <p class="text-xl text-gray-300">Transform your ideas into reality with powerful AI-driven web development</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 relative">
            <!-- Connected cards with thin gradient line -->
            <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500/0 via-primary-500/50 to-primary-500/0 -z-10 hidden lg:block"></div>
            
            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 relative group overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <!-- Card glow effect -->
              <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-keyboard text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-primary-300 transition-colors">Natural Language Input</h3>
              <p class="text-gray-300">Describe your vision in plain English, and watch as it transforms into reality.</p>
              
              <!-- Border highlight effect -->
              <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500/0 via-primary-500 to-primary-500/0 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"></div>
            </div>

            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 relative group overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <div class="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-violet-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-bolt text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-indigo-300 transition-colors">Rapid Development</h3>
              <p class="text-gray-300">Build websites and applications in minutes, not months.</p>
              
              <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500/0 via-indigo-500 to-indigo-500/0 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"></div>
            </div>

            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 relative group overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <div class="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-code text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-violet-300 transition-colors">Professional Code</h3>
              <p class="text-gray-300">Generate clean, maintainable code that follows industry best practices.</p>
              
              <div class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-500/0 via-violet-500 to-violet-500/0 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-500"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- How It Works -->
      <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 bg-dark-800/50 relative">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">How It Works</h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 relative">
            <!-- Connected steps with gradient line -->
            <div class="absolute top-[4.5rem] left-[calc(12.5%-1px)] right-[calc(12.5%-1px)] h-0.5 bg-gradient-to-r from-primary-500 via-violet-500 to-fuchsia-500 hidden lg:block"></div>
            
            <div class="relative">
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 rounded-full bg-dark-800 border-2 border-primary-500 flex items-center justify-center text-primary-400 font-bold text-sm z-10">1</div>
                
                <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                  <i class="fas fa-pencil-alt text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-primary-300 transition-colors">Describe Your Vision</h3>
                <p class="text-gray-300">Tell us what you want to build using natural language. Describe your features, design preferences, and requirements.</p>
              </div>
            </div>

            <div class="relative">
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-indigo-500/50 transition-all duration-300 hover:-translate-y-1 group hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 rounded-full bg-dark-800 border-2 border-indigo-500 flex items-center justify-center text-indigo-400 font-bold text-sm z-10">2</div>
                
                <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                  <i class="fas fa-magic text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-indigo-300 transition-colors">AI Generation</h3>
                <p class="text-gray-300">Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic.</p>
              </div>
            </div>

            <div class="relative">
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-violet-500/50 transition-all duration-300 hover:-translate-y-1 group hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 rounded-full bg-dark-800 border-2 border-violet-500 flex items-center justify-center text-violet-400 font-bold text-sm z-10">3</div>
                
                <div class="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                  <i class="fas fa-sliders-h text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-violet-300 transition-colors">Customize & Refine</h3>
                <p class="text-gray-300">Review the generated application, make adjustments, and refine details using natural language commands.</p>
              </div>
            </div>

            <div class="relative">
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-fuchsia-500/50 transition-all duration-300 hover:-translate-y-1 group hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
                <div class="absolute -top-4 left-1/2 transform -translate-x-1/2 w-8 h-8 rounded-full bg-dark-800 border-2 border-fuchsia-500 flex items-center justify-center text-fuchsia-400 font-bold text-sm z-10">4</div>
                
                <div class="w-12 h-12 bg-gradient-to-br from-fuchsia-500 to-pink-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                  <i class="fas fa-rocket text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-fuchsia-300 transition-colors">Launch & Scale</h3>
                <p class="text-gray-300">Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Use Cases -->
      <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 relative">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">What You Can Build</h2>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 relative">
            <!-- Connected cards with thin gradient line -->
            <div class="absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500/10 via-primary-500/50 to-primary-500/10 -z-10 hidden lg:block"></div>
            
            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group relative overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <!-- Card glass reflection effect -->
              <div class="absolute -inset-0.5 bg-gradient-to-tr from-primary-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-store text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-primary-300 transition-colors">E-commerce Sites</h3>
              <p class="text-gray-300">Create full-featured online stores with product catalogs, shopping carts, and secure payment processing.</p>
            </div>

            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-indigo-500/50 transition-all duration-300 hover:-translate-y-1 group relative overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <div class="absolute -inset-0.5 bg-gradient-to-tr from-indigo-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-briefcase text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-indigo-300 transition-colors">Business Applications</h3>
              <p class="text-gray-300">Build custom CRM systems, inventory management tools, and other business-specific applications.</p>
            </div>

            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-violet-500/50 transition-all duration-300 hover:-translate-y-1 group relative overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <div class="absolute -inset-0.5 bg-gradient-to-tr from-violet-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-users text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-violet-300 transition-colors">Community Platforms</h3>
              <p class="text-gray-300">Develop social networks, forums, and community-driven websites with user management and content sharing.</p>
            </div>

            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-fuchsia-500/50 transition-all duration-300 hover:-translate-y-1 group relative overflow-hidden hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <div class="absolute -inset-0.5 bg-gradient-to-tr from-fuchsia-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
              
              <div class="w-12 h-12 bg-gradient-to-br from-fuchsia-500 to-pink-500 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 shadow-md">
                <i class="fas fa-chart-line text-white text-xl"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-4 group-hover:text-fuchsia-300 transition-colors">Analytics Dashboards</h3>
              <p class="text-gray-300">Create data visualization tools and interactive dashboards for business intelligence and reporting.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Stats Section -->
      <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 bg-dark-800/50 relative">
        <div class="max-w-7xl mx-auto">
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-8">
            <div class="text-center">
              <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">10K+</div>
              <p class="text-gray-300">Active Users</p>
            </div>
            <div class="text-center">
              <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">50K+</div>
              <p class="text-gray-300">Apps Generated</p>
            </div>
            <div class="text-center">
              <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">99%</div>
              <p class="text-gray-300">Success Rate</p>
            </div>
            <div class="text-center">
              <div class="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent mb-2">24/7</div>
              <p class="text-gray-300">AI Support</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Testimonials Section -->
      <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 relative">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">What Developers Say</h2>
            <p class="text-xl text-gray-300">Join thousands of satisfied developers who trust Imagi</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            <!-- Connecting line between testimonials -->
            <div class="absolute top-1/3 left-0 right-0 h-0.5 bg-gradient-to-r from-primary-500/0 via-primary-500/40 to-primary-500/0 -z-10 hidden md:block"></div>
            
            <!-- Testimonial 1 -->
            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-primary-500/40 transition-all duration-300 group relative hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <!-- Decorative corner accent -->
              <div class="absolute top-0 right-0 w-20 h-20 overflow-hidden">
                <div class="absolute -top-10 -right-10 w-20 h-20 bg-gradient-to-br from-primary-500/20 to-primary-500/5 rounded-full blur-md group-hover:opacity-100 opacity-0 transition-opacity duration-500"></div>
              </div>
              
              <div class="flex items-center mb-6">
                <div class="flex text-primary-400 group-hover:scale-105 transition-transform">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                </div>
              </div>
              <p class="text-gray-300 mb-6 relative">
                <span class="absolute -left-1 -top-1 text-4xl text-primary-500/20 font-serif">"</span>
                <span class="relative">Imagi has revolutionized how I build web applications. What used to take weeks now takes hours. The AI understands exactly what I need.</span>
                <span class="absolute -right-1 bottom-0 text-4xl text-primary-500/20 font-serif">"</span>
              </p>
              <div class="flex items-center">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-violet-500 flex items-center justify-center ring-2 ring-primary-500/20 shadow-md">
                  <span class="text-white font-semibold">JS</span>
                </div>
                <div class="ml-3">
                  <div class="text-white font-semibold group-hover:text-primary-300 transition-colors">John Smith</div>
                  <div class="text-gray-400 text-sm">Senior Developer</div>
                </div>
              </div>
            </div>

            <!-- Testimonial 2 -->
            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-indigo-500/40 transition-all duration-300 group relative mt-8 md:mt-0 hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <!-- Decorative corner accent -->
              <div class="absolute top-0 right-0 w-20 h-20 overflow-hidden">
                <div class="absolute -top-10 -right-10 w-20 h-20 bg-gradient-to-br from-indigo-500/20 to-indigo-500/5 rounded-full blur-md group-hover:opacity-100 opacity-0 transition-opacity duration-500"></div>
              </div>
              
              <div class="flex items-center mb-6">
                <div class="flex text-indigo-400 group-hover:scale-105 transition-transform">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                </div>
              </div>
              <p class="text-gray-300 mb-6 relative">
                <span class="absolute -left-1 -top-1 text-4xl text-indigo-500/20 font-serif">"</span>
                <span class="relative">The code quality is impressive. It's not just about speed - Imagi generates clean, maintainable code that follows best practices.</span>
                <span class="absolute -right-1 bottom-0 text-4xl text-indigo-500/20 font-serif">"</span>
              </p>
              <div class="flex items-center">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center ring-2 ring-indigo-500/20 shadow-md">
                  <span class="text-white font-semibold">AD</span>
                </div>
                <div class="ml-3">
                  <div class="text-white font-semibold group-hover:text-indigo-300 transition-colors">Alice Davis</div>
                  <div class="text-gray-400 text-sm">Tech Lead</div>
                </div>
              </div>
            </div>

            <!-- Testimonial 3 -->
            <div class="bg-dark-800/60 backdrop-blur-xl rounded-2xl p-8 border border-dark-700 hover:border-violet-500/40 transition-all duration-300 group relative mt-8 md:mt-0 hover:shadow-[0_15px_30px_-5px_rgba(99,102,241,0.2),0_5px_15px_-5px_rgba(124,58,237,0.15),0_0_0_1px_rgba(99,102,241,0.1)] shadow-[0_10px_25px_-5px_rgba(99,102,241,0.1),0_0_10px_-5px_rgba(124,58,237,0.1),0_0_0_1px_rgba(99,102,241,0.05)]">
              <!-- Decorative corner accent -->
              <div class="absolute top-0 right-0 w-20 h-20 overflow-hidden">
                <div class="absolute -top-10 -right-10 w-20 h-20 bg-gradient-to-br from-violet-500/20 to-violet-500/5 rounded-full blur-md group-hover:opacity-100 opacity-0 transition-opacity duration-500"></div>
              </div>
              
              <div class="flex items-center mb-6">
                <div class="flex text-violet-400 group-hover:scale-105 transition-transform">
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                  <i class="fas fa-star"></i>
                </div>
              </div>
              <p class="text-gray-300 mb-6 relative">
                <span class="absolute -left-1 -top-1 text-4xl text-violet-500/20 font-serif">"</span>
                <span class="relative">Perfect for startups and MVPs. We've cut our development time by 80% and can iterate much faster with customer feedback.</span>
                <span class="absolute -right-1 bottom-0 text-4xl text-violet-500/20 font-serif">"</span>
              </p>
              <div class="flex items-center">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center ring-2 ring-violet-500/20 shadow-md">
                  <span class="text-white font-semibold">MR</span>
                </div>
                <div class="ml-3">
                  <div class="text-white font-semibold group-hover:text-violet-300 transition-colors">Mike Ross</div>
                  <div class="text-gray-400 text-sm">Startup Founder</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA Section - Redesigned -->
      <section class="py-12 px-4 sm:px-6 lg:px-8 relative">
        <div class="max-w-4xl mx-auto relative">
          <!-- Main CTA Card - Redesigned with smoother effects -->
          <div class="relative rounded-2xl overflow-hidden bg-dark-800/80 backdrop-blur-md border border-dark-700 hover:border-primary-500/30 transition-all duration-500 shadow-lg">
            <!-- Subtle gradient background -->
            <div class="absolute inset-0 bg-gradient-to-br from-primary-600/20 via-violet-600/10 to-purple-600/20"></div>
            
            <!-- Subtle decorative elements -->
            <div class="absolute inset-0">
              <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-5"></div>
              <div class="absolute top-0 right-0 w-80 h-80 bg-primary-500/10 rounded-full blur-[120px] opacity-30"></div>
              <div class="absolute bottom-0 left-0 w-60 h-60 bg-violet-500/10 rounded-full blur-[100px] opacity-20"></div>
            </div>

            <!-- Content Container -->
            <div class="relative z-10 px-6 py-12 md:px-12">
              <div class="max-w-2xl mx-auto text-center">
                <!-- Main Text -->
                <h2 class="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">
                  Ready to Transform Your
                  <span class="bg-gradient-to-r from-primary-300 to-violet-300 bg-clip-text text-transparent">
                    Development Process?
                  </span>
                </h2>

                <p class="text-lg text-white/80 mb-8 max-w-xl mx-auto">
                  Join thousands of developers building amazing applications
                  <span class="font-semibold text-primary-300">10x faster</span> with AI.
                </p>

                <!-- Action Buttons -->
                <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <!-- Start Building Button with more subtle effects -->
                  <HomeNavbarButton
                    :to="{ name: isAuthenticated ? 'builder-dashboard' : 'login' }"
                    class="group relative w-full sm:w-auto min-w-[200px] !h-12 px-6 rounded-xl bg-primary-500/80 hover:bg-primary-500/90 border border-primary-500/50 hover:border-primary-400 transition-all duration-300 transform hover:-translate-y-1 shadow-md hover:shadow-primary-500/20"
                  >
                    <span class="relative z-10 flex items-center justify-center text-lg font-medium text-white">
                      Start Building Free
                      <i class="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                    </span>
                  </HomeNavbarButton>

                  <!-- Contact Sales Button with more subtle effects -->
                  <HomeNavbarButton
                    to="/contact"
                    class="group relative w-full sm:w-auto min-w-[200px] !h-12 px-6 rounded-xl bg-dark-700/50 hover:bg-dark-700/80 border border-dark-600 hover:border-primary-500/30 transition-all duration-300 transform hover:-translate-y-1 shadow-sm hover:shadow-lg"
                  >
                    <span class="relative z-10 flex items-center justify-center text-lg font-medium text-white">
                      Contact Sales
                      <i class="fas fa-arrow-up-right-from-square ml-2 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform"></i>
                    </span>
                  </HomeNavbarButton>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import { DefaultLayout } from '@/shared/layouts'
import { 
  GradientText, 
  HomeNavbarButton, 
  HeroSection,
  AnimatedTerminal 
} from '@/apps/home/components'

export default defineComponent({
  name: 'Home',
  components: {
    DefaultLayout,
    GradientText,
    HomeNavbarButton,
    HeroSection,
    AnimatedTerminal
  },
  setup() {
    const authStore = useAuthStore()
    
    return {
      isAuthenticated: computed(() => authStore.isAuthenticated)
    }
  }
})
</script>

<style scoped>
/* Removed the pulse-glow animation */

/* Gradient animation for connecting lines */
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.bg-gradient-to-r {
  background-size: 200% 100%;
  animation: gradient-shift 8s ease infinite;
}
</style>