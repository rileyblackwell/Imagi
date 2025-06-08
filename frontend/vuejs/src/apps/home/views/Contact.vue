<!-- Contact page -->
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
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">SUPPORT & ASSISTANCE</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h1 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Get in Touch</span> 
                  <br class="hidden sm:block" />We're Here to Help
                </h1>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Have questions or need assistance? We're here to help you bring your ideas to life with personalized support.
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
              <!-- Contact Methods Grid -->
              <section>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
                  <!-- Email Support Card -->
                  <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                    <!-- Modern glassmorphism container -->
                    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                      <!-- Sleek gradient header -->
                      <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
                      
                      <!-- Subtle background effects -->
                      <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                      
                      <div class="relative z-10 p-8">
                        <!-- Modern pill badge -->
                        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-6 backdrop-blur-sm">
                          <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
                          <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">Email Support</span>
                        </div>
                        
                        <!-- Icon and Content -->
                        <div class="flex items-start gap-4 mb-6">
                          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 flex items-center justify-center border border-indigo-400/20 flex-shrink-0">
                            <i class="fas fa-envelope text-indigo-300 text-lg"></i>
                          </div>
                          <div class="flex-1">
                            <h3 class="text-xl font-semibold text-white mb-3 leading-tight">Email Support</h3>
                            <p class="text-gray-300 text-sm leading-relaxed">For general inquiries and assistance with your projects.</p>
                          </div>
                        </div>
                        
                        <!-- Modern separator -->
                        <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                        
                        <!-- Contact Link -->
                        <a href="mailto:support@imagi-oasis.com" class="w-full inline-flex items-center justify-center px-4 py-3 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-indigo-400/30 text-white rounded-xl transition-all duration-300 text-sm font-medium group/button">
                          <i class="fas fa-envelope mr-2 group-hover/button:text-indigo-400 transition-colors duration-200"></i>
                          support@imagi-oasis.com
                        </a>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Live Chat Card -->
                  <div class="group relative transform transition-all duration-300 hover:-translate-y-1">
                    <!-- Modern glassmorphism container -->
                    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                      <!-- Sleek gradient header -->
                      <div class="h-1 w-full bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 opacity-80"></div>
                      
                      <!-- Subtle background effects -->
                      <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-cyan-400/4 to-blue-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                      
                      <div class="relative z-10 p-8">
                        <!-- Modern pill badge -->
                        <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-cyan-500/15 to-blue-500/15 border border-cyan-400/20 rounded-full mb-6 backdrop-blur-sm">
                          <div class="w-1.5 h-1.5 bg-cyan-400 rounded-full mr-2 animate-pulse"></div>
                          <span class="text-cyan-300 font-medium text-xs tracking-wide uppercase">Live Chat</span>
                        </div>
                        
                        <!-- Icon and Content -->
                        <div class="flex items-start gap-4 mb-6">
                          <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400/20 to-blue-400/20 flex items-center justify-center border border-cyan-400/20 flex-shrink-0">
                            <i class="fas fa-headset text-cyan-300 text-lg"></i>
                          </div>
                          <div class="flex-1">
                            <h3 class="text-xl font-semibold text-white mb-3 leading-tight">Live Chat</h3>
                            <p class="text-gray-300 text-sm leading-relaxed">Get real-time assistance from our support team.</p>
                          </div>
                        </div>
                        
                        <!-- Modern separator -->
                        <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                        
                        <!-- Chat Button -->
                        <button class="w-full inline-flex items-center justify-center px-4 py-3 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-cyan-400/30 text-white rounded-xl transition-all duration-300 text-sm font-medium group/button">
                          <i class="fas fa-comment mr-2 group-hover/button:text-cyan-400 transition-colors duration-200"></i>
                          Start Chat
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <!-- Contact Form Section -->
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
                        <span class="text-emerald-300 font-medium text-xs tracking-wide uppercase">Send Message</span>
                      </div>
                      
                      <!-- Section Header -->
                      <div class="mb-8 text-center">
                        <h2 class="text-2xl font-semibold text-white leading-tight mb-3">Send Us a Message</h2>
                        <p class="text-gray-400 text-sm leading-relaxed">Fill out the form below and we'll get back to you as soon as possible.</p>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8"></div>
                      
                      <!-- Contact Form -->
                      <form @submit.prevent="submitForm" class="space-y-6">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div class="relative group/input">
                            <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/12 to-teal-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                            <label for="name" class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Your Name</label>
                            <input
                              type="text"
                              id="name"
                              v-model="formData.name"
                              class="relative z-10 w-full px-4 py-3 bg-white/5 border border-white/10 focus:border-emerald-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-emerald-500/20"
                              style="outline: none !important; box-shadow: none !important;"
                              placeholder="Enter your name"
                              required
                            />
                          </div>
                          <div class="relative group/input">
                            <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/12 to-teal-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                            <label for="email" class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Email Address</label>
                            <input
                              type="email"
                              id="email"
                              v-model="formData.email"
                              class="relative z-10 w-full px-4 py-3 bg-white/5 border border-white/10 focus:border-emerald-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-emerald-500/20"
                              style="outline: none !important; box-shadow: none !important;"
                              placeholder="youremail@example.com"
                              required
                            />
                          </div>
                        </div>
                        
                        <div class="relative group/input">
                          <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/12 to-teal-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                          <label for="subject" class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Subject</label>
                          <input
                            type="text"
                            id="subject"
                            v-model="formData.subject"
                            class="relative z-10 w-full px-4 py-3 bg-white/5 border border-white/10 focus:border-emerald-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-emerald-500/20"
                            style="outline: none !important; box-shadow: none !important;"
                            placeholder="What is your message about?"
                            required
                          />
                        </div>
                        
                        <div class="relative group/input">
                          <div class="absolute inset-0 bg-gradient-to-r from-emerald-500/12 to-teal-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                          <label for="message" class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Message</label>
                          <textarea
                            id="message"
                            v-model="formData.message"
                            rows="5"
                            class="relative z-10 w-full px-4 py-3 bg-white/5 border border-white/10 focus:border-emerald-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 resize-none backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-emerald-500/20"
                            style="outline: none !important; box-shadow: none !important;"
                            placeholder="Tell us how we can help you..."
                            required
                          ></textarea>
                        </div>
                        
                        <div class="pt-2">
                          <button
                            type="submit"
                            :disabled="isSubmitting"
                            class="w-full px-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-medium rounded-xl shadow-lg shadow-emerald-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <span class="relative flex items-center justify-center">
                              <template v-if="isSubmitting">
                                <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                                Sending...
                              </template>
                              <template v-else>
                                <i class="fas fa-paper-plane mr-2"></i>
                                Send Message
                              </template>
                            </span>
                          </button>
                          
                          <p class="text-xs text-gray-500 mt-3 text-center leading-relaxed">
                            <svg class="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                            </svg>
                            We'll respond within 24 hours during business days
                          </p>
                        </div>
                      </form>
                    </div>
                  </div>
                </div>
              </section>

              <!-- FAQ Section -->
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
                        <span class="text-amber-300 font-medium text-xs tracking-wide uppercase">FAQ</span>
                      </div>
                      
                      <!-- Section Header -->
                      <div class="mb-8 text-center">
                        <h2 class="text-2xl font-semibold text-white leading-tight mb-3">Frequently Asked Questions</h2>
                        <p class="text-gray-400 text-sm leading-relaxed">Find quick answers to common questions about our services.</p>
                      </div>
                      
                      <!-- Modern separator -->
                      <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-8"></div>
                      
                      <!-- FAQ Items -->
                      <div class="space-y-6">
                        <div v-for="(faq, index) in faqs" :key="index" class="group/faq">
                          <div class="flex items-start gap-4 p-5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-amber-400/30 rounded-xl transition-all duration-300">
                            <!-- FAQ Icon -->
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400/20 to-orange-400/20 flex items-center justify-center border border-amber-400/20 flex-shrink-0 mt-1">
                              <i class="fas fa-question text-amber-300 text-xs"></i>
                            </div>
                            
                            <!-- FAQ Content -->
                            <div class="flex-1">
                              <h3 class="text-white font-semibold mb-2 leading-tight group-hover/faq:text-amber-400 transition-colors duration-200">{{ faq.question }}</h3>
                              <p class="text-gray-300 text-sm leading-relaxed">{{ faq.answer }}</p>
                            </div>
                          </div>
                        </div>
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

<script setup>
import { ref } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { useNotification } from '@/shared/composables/useNotification'

const { showNotification } = useNotification()

const formData = ref({
  name: '',
  email: '',
  subject: '',
  message: ''
})

const isSubmitting = ref(false)

const faqs = ref([
  {
    question: 'How quickly will I receive a response to my inquiry?',
    answer: 'We strive to respond to all inquiries within 24 hours during business days. For urgent matters, please use the live chat feature for immediate assistance.'
  },
  {
    question: 'Do you offer technical support for all plans?',
    answer: 'Yes, all plans include technical support. Premium plans receive priority support with faster response times and dedicated support specialists.'
  },
  {
    question: 'Can I schedule a demo of the platform?',
    answer: 'Absolutely! You can schedule a personalized demo with our team by sending us a message through the contact form or emailing support@imagi-oasis.com.'
  },
  {
    question: 'How do I report a bug or suggest a feature?',
    answer: 'You can report bugs or suggest features through our support email or by using the contact form. We appreciate your feedback and continuously work to improve our platform.'
  }
])

async function submitForm() {
  isSubmitting.value = true
  
  try {
    // Simulate API call with a delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Show success notification
    showNotification({
      type: 'success',
      message: 'Your message has been sent successfully! We\'ll get back to you soon.'
    })
    
    // Reset form
    formData.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
  } catch (error) {
    // Show error notification
    showNotification({
      type: 'error',
      message: 'There was an error sending your message. Please try again.'
    })
  } finally {
    isSubmitting.value = false
  }
}
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