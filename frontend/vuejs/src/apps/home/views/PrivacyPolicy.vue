<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching dashboard pages -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10">
        <!-- Modern Welcome Header Section -->
        <div class="pt-32 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
              <div class="space-y-6 md:max-w-3xl">
                <!-- Enhanced Badge -->
                <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full">
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">PRIVACY & SECURITY</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h1 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Privacy Policy</span> 
                  <br class="hidden sm:block" />Your Privacy Matters
                </h1>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  We are committed to protecting your privacy and ensuring the security of your personal information.
                </p>
              </div>
            </div>
            
            <!-- Animated Divider Line -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent my-12 animate-pulse-slow"></div>
          </div>
        </div>

        <!-- Main Content with Modern Layout -->
        <div class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-7xl mx-auto">
            <div class="space-y-16">
              <!-- Introduction Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">Introduction</span>
                      </div>
                      
                      <div class="space-y-4 text-gray-300 leading-relaxed">
                        <p>
                          At Imagi Oasis, we value your privacy and are dedicated to maintaining the trust and confidence of all visitors to our website. This Privacy Policy explains how we collect, use, and protect your personal information.
                        </p>
                        <p>
                          This policy was last updated on July 15, 2023. We may update this policy from time to time, so please check this page occasionally to ensure you're happy with any changes.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Information Collection Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-cyan-400/4 to-blue-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-cyan-500/15 to-blue-500/15 border border-cyan-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-cyan-300 font-medium text-xs tracking-wide uppercase">Information Collection</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 flex items-center justify-center border border-cyan-400/20 flex-shrink-0">
                          <i class="fas fa-database text-cyan-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Information Collection and Use</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">We collect and process personal information necessary to provide our services. This information is handled with utmost care and in compliance with applicable data protection laws.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Information List -->
                      <div class="space-y-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-cyan-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Account Information:</span>
                            <span class="text-gray-300"> Name, email, password (encrypted), profile picture, and registration details</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-cyan-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Technical Data:</span>
                            <span class="text-gray-300"> IP address, browser type, device information, operating system, and cookies</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-cyan-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Usage Information:</span>
                            <span class="text-gray-300"> Interaction with our services, generated applications, API calls, and feature usage patterns</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-cyan-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Payment Details:</span>
                            <span class="text-gray-300"> Billing information, transaction history (stored securely via payment processors)</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-cyan-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Generated Content:</span>
                            <span class="text-gray-300"> Applications, code, and configurations created using our services</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-cyan-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Communication Data:</span>
                            <span class="text-gray-300"> Support tickets, feedback, and correspondence with our team</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Data Processing Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-emerald-400/4 to-teal-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-emerald-500/15 to-teal-500/15 border border-emerald-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-emerald-300 font-medium text-xs tracking-wide uppercase">Data Processing</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/20 to-teal-400/20 flex items-center justify-center border border-emerald-400/20 flex-shrink-0">
                          <i class="fas fa-microchip text-emerald-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Data Processing and Storage</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">We implement robust security measures to protect your data with industry-leading practices.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Security List -->
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">End-to-end encryption for sensitive data transmission</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Regular security audits and penetration testing</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Data backup and disaster recovery protocols</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Access controls and authentication mechanisms</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Regular updates to security infrastructure</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Compliance with industry security standards</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Use of Information Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-amber-400 via-orange-400 to-amber-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-amber-400/4 to-orange-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-amber-500/15 to-orange-500/15 border border-amber-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-amber-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-amber-300 font-medium text-xs tracking-wide uppercase">Use of Information</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center border border-amber-400/20 flex-shrink-0">
                          <i class="fas fa-cog text-amber-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Use of Information</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">Your information is used for the following purposes to enhance your experience.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Usage List -->
                      <div class="space-y-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Service Provision:</span>
                            <span class="text-gray-300"> Delivering and maintaining our AI-powered development platform</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Personalization:</span>
                            <span class="text-gray-300"> Customizing and optimizing your experience</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Analytics:</span>
                            <span class="text-gray-300"> Improving our services and understanding user needs</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Security:</span>
                            <span class="text-gray-300"> Protecting against fraud and unauthorized access</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Communication:</span>
                            <span class="text-gray-300"> Sending service updates, notifications, and support responses</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Legal Compliance:</span>
                            <span class="text-gray-300"> Meeting regulatory requirements and enforcing our terms</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Data Sharing Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-purple-400 via-fuchsia-400 to-purple-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-purple-400/4 to-fuchsia-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-purple-500/15 to-fuchsia-500/15 border border-purple-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-purple-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-purple-300 font-medium text-xs tracking-wide uppercase">Data Sharing</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-400/20 to-fuchsia-400/20 flex items-center justify-center border border-purple-400/20 flex-shrink-0">
                          <i class="fas fa-share-nodes text-purple-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Data Sharing and Third Parties</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">We may share your information with trusted partners under strict conditions.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Sharing List -->
                      <div class="space-y-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Service Providers:</span>
                            <span class="text-gray-300"> Cloud hosting, analytics, payment processing, and security services</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Legal Requirements:</span>
                            <span class="text-gray-300"> Court orders, law enforcement requests, or regulatory obligations</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Business Transfers:</span>
                            <span class="text-gray-300"> Mergers, acquisitions, or asset sales (with user notification)</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Aggregated Data:</span>
                            <span class="text-gray-300"> Anonymous, statistical data for research and analysis</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Privacy Rights Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-green-400 via-emerald-400 to-green-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-green-400/4 to-emerald-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-green-500/15 to-emerald-500/15 border border-green-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-green-300 font-medium text-xs tracking-wide uppercase">Your Rights</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-400/20 to-emerald-400/20 flex items-center justify-center border border-green-400/20 flex-shrink-0">
                          <i class="fas fa-user-shield text-green-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Your Privacy Rights</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">You have the following rights regarding your personal data.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Rights Grid -->
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Access:</span>
                            <span class="text-gray-300"> Request copies of your personal data</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Rectification:</span>
                            <span class="text-gray-300"> Correct inaccurate or incomplete information</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Deletion:</span>
                            <span class="text-gray-300"> Request erasure of your personal data</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Portability:</span>
                            <span class="text-gray-300"> Receive and transfer your data</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Restriction:</span>
                            <span class="text-gray-300"> Limit how we process your data</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Objection:</span>
                            <span class="text-gray-300"> Object to certain types of processing</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Contact Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-rose-400 via-pink-400 to-rose-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-rose-400/4 to-pink-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-rose-500/15 to-pink-500/15 border border-rose-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-rose-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-rose-300 font-medium text-xs tracking-wide uppercase">Contact Us</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6 text-center">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-400/20 to-pink-400/20 flex items-center justify-center border border-rose-400/20 flex-shrink-0 mx-auto">
                          <i class="fas fa-shield-halved text-rose-300 text-lg"></i>
                        </div>
                      </div>
                      
                      <div class="text-center">
                        <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Have Questions About Our Privacy Policy?</h2>
                        <p class="text-gray-300 text-sm leading-relaxed mb-6">We're committed to protecting your privacy and ensuring the security of your personal information.</p>
                        
                        <!-- Contact Button -->
                        <router-link 
                          to="/contact"
                          class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white font-medium rounded-xl shadow-lg shadow-rose-500/25 transition-all duration-200 transform hover:-translate-y-1"
                        >
                          <i class="fas fa-envelope mr-2"></i>
                          Contact Us
                        </router-link>
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

export default defineComponent({
  name: 'PrivacyPolicy',
  components: {
    DefaultLayout
  }
})
</script>

<style scoped>
/* Completely remove any browser default styling for form inputs */
input, textarea {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

.delay-700 {
  animation-delay: 700ms;
}
</style>