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
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">LEGAL & AGREEMENTS</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h1 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Terms of Service</span> 
                  <br class="hidden sm:block" />Our Agreement
                </h1>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Please read these terms carefully before using our services. By accessing our platform, you agree to be bound by these terms.
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
                          Welcome to Imagi Oasis. Our Terms of Service govern your use of our platform and services. By using Imagi Oasis, you agree to these terms in their entirety.
                        </p>
                        <p>
                          These terms were last updated on July 15, 2023. We may update these terms from time to time, so please check this page occasionally to ensure you're aware of any changes.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Acceptance of Terms Section -->
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
                        <span class="text-cyan-300 font-medium text-xs tracking-wide uppercase">Acceptance of Terms</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 flex items-center justify-center border border-cyan-400/20 flex-shrink-0">
                          <i class="fas fa-check-circle text-cyan-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Acceptance of Terms</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">By accessing or using Imagi's services, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.</p>
                        </div>
                      </div>
                      
                      <div class="space-y-4 text-gray-300 leading-relaxed">
                        <p>
                          By accessing or using Imagi's services, including our AI-powered website builder ("Imagi Oasis"), you acknowledge that you have read, understood, and agree to be bound by these Terms of Service. If you do not agree to these terms, you must not access or use our services.
                        </p>
                        <p>
                          By using our services, you represent that you have the legal capacity to enter into a binding agreement.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Prohibited Uses Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-red-400 via-orange-400 to-red-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-red-400/4 to-orange-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-red-500/15 to-orange-500/15 border border-red-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-red-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-red-300 font-medium text-xs tracking-wide uppercase">Prohibited Uses</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-red-400/20 to-orange-400/20 flex items-center justify-center border border-red-400/20 flex-shrink-0">
                          <i class="fas fa-ban text-red-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Prohibited Uses</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">You are strictly prohibited from using Imagi's services for any unlawful or unauthorized purposes.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Prohibited Activities List -->
                      <div class="space-y-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-red-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300">Creating any illegal products, services, applications, or content that violates applicable laws</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-red-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300">Developing applications that promote, facilitate, or enable illegal activities</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-red-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300">Building systems designed to harm, defraud, exploit, or harass others</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-red-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300">Attempting to reverse engineer, decompile, or access non-public parts of our services</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-red-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300">Using our services to spread malware, viruses, or other harmful code</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Service Description Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-emerald-400/4 to-teal-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-emerald-500/15 to-teal-500/15 border border-emerald-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-emerald-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-emerald-300 font-medium text-xs tracking-wide uppercase">Service Description</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-400/20 to-teal-400/20 flex items-center justify-center border border-emerald-400/20 flex-shrink-0">
                          <i class="fas fa-cube text-emerald-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Service Description and Limitations</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">Imagi provides an AI-powered platform for generating code and websites.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Service Limitations -->
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Our services are provided "as is" without warranties</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">We may modify, suspend, or discontinue services</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Generated code requires review and testing</span>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-emerald-400 mt-2.5 flex-shrink-0"></div>
                          <span class="text-gray-300 text-sm">Usage limits may apply to maintain quality</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- User Responsibilities Section -->
              <section>
                <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-1 w-full bg-gradient-to-r from-amber-400 via-orange-400 to-amber-400 opacity-80"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-amber-400/4 to-orange-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-amber-500/15 to-orange-500/15 border border-amber-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-amber-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-amber-300 font-medium text-xs tracking-wide uppercase">User Responsibilities</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center border border-amber-400/20 flex-shrink-0">
                          <i class="fas fa-user-shield text-amber-300 text-lg"></i>
                        </div>
                        <div class="flex-1">
                          <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">User Responsibilities and Conduct</h2>
                          <p class="text-gray-300 text-sm leading-relaxed">Users must adhere to our conduct guidelines and maintain responsible use of our platform.</p>
                        </div>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                      
                      <!-- Responsibilities List -->
                      <div class="space-y-4">
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Account Security:</span>
                            <span class="text-gray-300"> Maintain security and confidentiality of credentials</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Accurate Information:</span>
                            <span class="text-gray-300"> Provide complete and up-to-date information</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Legal Compliance:</span>
                            <span class="text-gray-300"> Comply with all applicable laws and regulations</span>
                          </div>
                        </div>
                        <div class="flex items-start gap-3 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div class="w-2 h-2 rounded-full bg-amber-400 mt-2.5 flex-shrink-0"></div>
                          <div>
                            <span class="text-white font-semibold">Security Measures:</span>
                            <span class="text-gray-300"> Implement appropriate security for your applications</span>
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
                    <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-rose-400/4 to-pink-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                    
                    <div class="relative z-10 p-8">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-rose-500/15 to-pink-500/15 border border-rose-400/20 rounded-full mb-6 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-rose-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-rose-300 font-medium text-xs tracking-wide uppercase">Contact Us</span>
                      </div>
                      
                      <!-- Icon and Content -->
                      <div class="flex items-start gap-4 mb-6 text-center">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-400/20 to-pink-400/20 flex items-center justify-center border border-rose-400/20 flex-shrink-0 mx-auto">
                          <i class="fas fa-file-contract text-rose-300 text-lg"></i>
                        </div>
                      </div>
                      
                      <div class="text-center">
                        <h2 class="text-2xl font-semibold text-white mb-3 leading-tight">Questions About Our Terms?</h2>
                        <p class="text-gray-300 text-sm leading-relaxed mb-6">We're here to help you understand our terms and conditions. Reach out with any questions.</p>
                        
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
  name: 'TermsOfService',
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