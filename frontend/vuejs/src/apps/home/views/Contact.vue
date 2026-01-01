<!-- Contact Page - Premium Design matching Home -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-[#050508] relative overflow-hidden">
      <!-- Premium Background System -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Base gradient mesh -->
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(120,119,198,0.15),transparent_50%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_80%_50%,rgba(78,68,206,0.08),transparent_40%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_10%_80%,rgba(167,139,250,0.06),transparent_35%)]"></div>
        
        <!-- Subtle grain texture -->
        <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
        
        <!-- Animated aurora effect -->
        <div class="absolute top-0 left-1/4 right-1/4 h-[600px] opacity-30">
          <div class="absolute inset-0 bg-gradient-to-b from-violet-500/20 via-fuchsia-500/10 to-transparent blur-[100px] animate-aurora"></div>
        </div>
        
        <!-- Floating orbs -->
        <div class="absolute top-[20%] right-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-600/8 to-violet-600/4 blur-[120px] animate-float-slow"></div>
        <div class="absolute bottom-[10%] left-[5%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-fuchsia-600/6 to-purple-600/3 blur-[100px] animate-float-delayed"></div>
        <div class="absolute top-[60%] right-[30%] w-[300px] h-[300px] rounded-full bg-gradient-to-bl from-emerald-500/4 to-teal-500/2 blur-[80px] animate-float-reverse"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative min-h-[50vh] flex items-center justify-center overflow-hidden pt-28 pb-16 sm:pt-32 sm:pb-20 md:pt-36 md:pb-24">
          <!-- Local background effects -->
          <div class="absolute inset-0 pointer-events-none">
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[80%] bg-[radial-gradient(ellipse_at_center,rgba(139,92,246,0.08)_0%,transparent_60%)]"></div>
          </div>

          <div class="relative w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
            <div class="text-center">
              <!-- Animated badge -->
              <div class="mb-8 inline-block animate-fade-in">
                <div class="group inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
                  </span>
                  <span class="text-sm font-medium text-white/70 tracking-wide">Support & Assistance</span>
                </div>
              </div>

              <!-- Hero title -->
              <h1 class="text-4xl sm:text-5xl md:text-6xl lg:text-[3.5rem] font-semibold tracking-tight mb-8 leading-[1.1] animate-fade-in-up" style="animation-delay: 100ms">
                <span class="block text-white/90">Get in Touch</span>
                <span class="block mt-3">
                  <span class="relative inline-block">
                    <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                      We're Here to Help
                    </span>
                    <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
                  </span>
                </span>
              </h1>

              <!-- Description -->
              <p class="text-lg sm:text-xl text-white/50 mb-10 max-w-2xl mx-auto leading-relaxed animate-fade-in-up" style="animation-delay: 200ms">
                Have questions or need assistance? We're here to help you bring your ideas to life with personalized support.
              </p>
            </div>
          </div>
        </section>

        <!-- Elegant Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative flex items-center justify-center">
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
            <div class="mx-6 flex items-center gap-2">
              <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
              <div class="w-1.5 h-1.5 rounded-full bg-violet-400/70"></div>
              <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
            </div>
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
          </div>
        </div>

        <!-- Contact Methods Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-7xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-headset text-xs text-violet-400/80"></i>
                <span class="text-sm font-medium text-white/60">Contact Options</span>
              </div>
              
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">How Can We Help?</h2>
              <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">
                Choose your preferred way to reach us and we'll get back to you as soon as possible.
              </p>
            </div>

            <!-- Contact cards grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-5 md:gap-6">
              <!-- Email Support Card -->
              <div class="group relative">
                <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-500 opacity-[0.03]"></div>
                  </div>
                  
                  <!-- Icon -->
                  <div class="relative mb-6">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/20 group-hover:bg-violet-500/15 group-hover:border-violet-500/30 transition-all duration-300">
                      <i class="fas fa-envelope text-lg text-violet-400"></i>
                    </div>
                  </div>
                  
                  <!-- Content -->
                  <h3 class="relative text-lg font-semibold text-white/90 mb-3">Email Support</h3>
                  <p class="relative text-white/50 text-sm leading-relaxed mb-6">For general inquiries and assistance with your projects. We typically respond within 24 hours.</p>
                  
                  <!-- Action -->
                  <a href="mailto:support@imagi-oasis.com" class="relative inline-flex items-center gap-2 px-5 py-2.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-violet-400/30 rounded-xl text-white font-medium text-sm transition-all duration-300">
                    <i class="fas fa-envelope text-violet-400"></i>
                    support@imagi-oasis.com
                  </a>

                  <!-- Bottom accent line on hover -->
                  <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                </div>
              </div>

              <!-- Live Chat Card -->
              <div class="group relative">
                <div class="relative h-full p-6 md:p-8 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 cursor-default overflow-hidden">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br from-blue-500 to-cyan-500 opacity-[0.03]"></div>
                  </div>
                  
                  <!-- Icon -->
                  <div class="relative mb-6">
                    <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 group-hover:bg-blue-500/15 group-hover:border-blue-500/30 transition-all duration-300">
                      <i class="fas fa-headset text-lg text-blue-400"></i>
                    </div>
                  </div>
                  
                  <!-- Content -->
                  <h3 class="relative text-lg font-semibold text-white/90 mb-3">Live Chat</h3>
                  <p class="relative text-white/50 text-sm leading-relaxed mb-6">Get real-time assistance from our support team. Available during business hours.</p>
                  
                  <!-- Action -->
                  <button class="relative inline-flex items-center gap-2 px-5 py-2.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-blue-400/30 rounded-xl text-white font-medium text-sm transition-all duration-300">
                    <i class="fas fa-comment text-blue-400"></i>
                    Start Chat
                  </button>

                  <!-- Bottom accent line on hover -->
                  <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Simple Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        </div>

        <!-- Contact Form Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-3xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-paper-plane text-xs text-emerald-400/80"></i>
                <span class="text-sm font-medium text-white/60">Send Message</span>
              </div>
              
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">Send Us a Message</h2>
              <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">
                Fill out the form below and we'll get back to you as soon as possible.
              </p>
            </div>

            <!-- Form Card -->
            <div class="group relative">
              <!-- Background glow -->
              <div class="absolute -inset-1 bg-gradient-to-r from-emerald-600/20 via-teal-600/20 to-emerald-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
              
              <div class="relative p-8 md:p-10 rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden">
                <!-- Accent line -->
                <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"></div>
                
                <form @submit.prevent="submitForm" class="space-y-6">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="relative">
                      <label for="name" class="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Your Name</label>
                      <input
                        type="text"
                        id="name"
                        v-model="formData.name"
                        class="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] focus:border-emerald-400/50 hover:border-white/[0.12] rounded-xl text-white placeholder-white/30 transition-all duration-300 backdrop-blur-sm focus:bg-white/[0.05]"
                        placeholder="Enter your name"
                        required
                      />
                    </div>
                    <div class="relative">
                      <label for="email" class="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Email Address</label>
                      <input
                        type="email"
                        id="email"
                        v-model="formData.email"
                        class="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] focus:border-emerald-400/50 hover:border-white/[0.12] rounded-xl text-white placeholder-white/30 transition-all duration-300 backdrop-blur-sm focus:bg-white/[0.05]"
                        placeholder="youremail@example.com"
                        required
                      />
                    </div>
                  </div>
                  
                  <div class="relative">
                    <label for="subject" class="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Subject</label>
                    <input
                      type="text"
                      id="subject"
                      v-model="formData.subject"
                      class="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] focus:border-emerald-400/50 hover:border-white/[0.12] rounded-xl text-white placeholder-white/30 transition-all duration-300 backdrop-blur-sm focus:bg-white/[0.05]"
                      placeholder="What is your message about?"
                      required
                    />
                  </div>
                  
                  <div class="relative">
                    <label for="message" class="block text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Message</label>
                    <textarea
                      id="message"
                      v-model="formData.message"
                      rows="5"
                      class="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] focus:border-emerald-400/50 hover:border-white/[0.12] rounded-xl text-white placeholder-white/30 transition-all duration-300 resize-none backdrop-blur-sm focus:bg-white/[0.05]"
                      placeholder="Tell us how we can help you..."
                      required
                    ></textarea>
                  </div>
                  
                  <div class="pt-2">
                    <button
                      type="submit"
                      :disabled="isSubmitting"
                      class="w-full group/btn inline-flex items-center justify-center gap-2 px-7 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl text-white font-medium shadow-lg shadow-emerald-500/25 hover:shadow-xl hover:shadow-emerald-500/30 transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <template v-if="isSubmitting">
                        <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Sending...
                      </template>
                      <template v-else>
                        <i class="fas fa-paper-plane"></i>
                        <span>Send Message</span>
                        <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                      </template>
                    </button>
                    
                    <p class="text-xs text-white/40 mt-4 text-center">
                      <i class="fas fa-clock mr-1.5"></i>
                      We'll respond within 24 hours during business days
                    </p>
                  </div>
                </form>
                
                <!-- Decorative elements -->
                <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-emerald-500/5 rounded-full blur-3xl"></div>
                <div class="absolute -top-20 -left-20 w-32 h-32 bg-teal-500/5 rounded-full blur-3xl"></div>
              </div>
            </div>
          </div>
        </section>

        <!-- Simple Divider -->
        <div class="relative py-8 md:py-12 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        </div>

        <!-- FAQ Section -->
        <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative">
          <div class="max-w-4xl mx-auto relative">
            <!-- Section header -->
            <div class="text-center mb-16 md:mb-20">
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-6">
                <i class="fas fa-circle-question text-xs text-amber-400/80"></i>
                <span class="text-sm font-medium text-white/60">FAQ</span>
              </div>
              
              <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">Frequently Asked Questions</h2>
              <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">
                Find quick answers to common questions about our services.
              </p>
            </div>

            <!-- FAQ cards -->
            <div class="space-y-4">
              <div v-for="(faq, index) in faqs" :key="index" class="group relative">
                <div class="relative p-6 rounded-2xl border border-white/[0.06] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.1] transition-all duration-500 overflow-hidden">
                  <!-- Subtle hover glow -->
                  <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                    <div class="absolute inset-0 bg-gradient-to-br from-amber-500 to-orange-500 opacity-[0.03]"></div>
                  </div>
                  
                  <div class="relative flex items-start gap-4">
                    <div class="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 mt-0.5">
                      <i class="fas fa-question text-xs text-amber-400"></i>
                    </div>
                    <div class="flex-1">
                      <h3 class="text-white/90 font-semibold mb-2 group-hover:text-amber-400 transition-colors duration-300">{{ faq.question }}</h3>
                      <p class="text-white/50 text-sm leading-relaxed">{{ faq.answer }}</p>
                    </div>
                  </div>

                  <!-- Bottom accent line on hover -->
                  <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-r from-transparent via-amber-500/50 to-transparent"></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
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
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    showNotification({
      type: 'success',
      message: 'Your message has been sent successfully! We\'ll get back to you soon.'
    })
    
    formData.value = {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
  } catch (error) {
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
/* Aurora animation */
@keyframes aurora {
  0%, 100% {
    transform: translateX(-10%) rotate(-2deg);
    opacity: 0.3;
  }
  50% {
    transform: translateX(10%) rotate(2deg);
    opacity: 0.4;
  }
}

.animate-aurora {
  animation: aurora 20s ease-in-out infinite;
}

/* Float animations */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-25px, -30px) scale(1.03);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, 15px);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 30s ease-in-out infinite;
  animation-delay: -5s;
}

.animate-float-reverse {
  animation: float-reverse 20s ease-in-out infinite;
  animation-delay: -10s;
}

/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out forwards;
}

/* Fade in up animation */
@keyframes fade-in-up {
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
  opacity: 0;
  animation: fade-in-up 0.8s ease-out forwards;
}

/* Gradient animation */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 4s ease infinite;
}

/* Form input styles */
input, textarea {
  outline: none !important;
}

input:focus, textarea:focus {
  outline: none !important;
}

/* Custom scrollbar */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(139, 92, 246, 0.5);
}
</style>
