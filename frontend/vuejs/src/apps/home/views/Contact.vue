<!-- Contact page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching other pages -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs -->
        <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-500/5 blur-[80px] sm:blur-[120px] animate-float"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-500/5 blur-[60px] sm:blur-[100px] animate-float-delay"></div>
        <!-- Grid pattern overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>

      <!-- Hero Section with improved styling -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pt-36 sm:pb-20">
        <!-- Content -->
        <div class="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <!-- Enhanced section header to match other pages -->
          <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
            <span class="text-primary-400 font-semibold text-sm tracking-wider">SUPPORT & ASSISTANCE</span>
          </div>
          
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block mb-2 sm:mb-3">Get in Touch</span>
            <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
              We're Here to Help
            </GradientText>
          </h1>
          
          <p class="text-xl text-gray-300 mb-12 sm:mb-16 max-w-3xl mx-auto leading-relaxed">
            Have questions or need assistance? We're here to help you bring your ideas to life.
          </p>
        </div>
      </section>

      <!-- Divider with animated line matching other pages -->
      <div class="relative h-16 max-w-7xl mx-auto">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main Content -->
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <!-- Contact Content -->
        <div class="space-y-16 relative z-10">
          <!-- Contact Methods -->
          <section>
            <SectionHeader 
              title="Contact Methods" 
              subtitle="Reach out to us through your preferred channel of communication."
            />
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mt-8">
              <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                  <div class="p-7">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20 shadow-lg shadow-primary-500/5 mb-6">
                      <i class="fas fa-envelope text-primary-400 text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-3">Email Support</h3>
                    <p class="text-gray-300 mb-4">For general inquiries and assistance with your projects.</p>
                    <a href="mailto:support@imagi-oasis.com" class="inline-flex items-center text-primary-400 hover:text-primary-300 transition-colors">
                      support@imagi-oasis.com
                      <i class="fas fa-arrow-right ml-2 text-xs"></i>
                    </a>
                  </div>
                </div>
              </div>
              
              <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-cyan-500/50 to-blue-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-cyan-500 to-blue-500"></div>
                  <div class="p-7">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-cyan-500/20 shadow-lg shadow-cyan-500/5 mb-6">
                      <i class="fas fa-headset text-cyan-400 text-xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-3">Live Chat</h3>
                    <p class="text-gray-300 mb-4">Get real-time assistance from our support team.</p>
                    <button class="inline-flex items-center text-cyan-400 hover:text-cyan-300 transition-colors">
                      Start Chat
                      <i class="fas fa-arrow-right ml-2 text-xs"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Contact Form Section -->
          <section>
            <SectionHeader 
              title="Send Us a Message" 
              subtitle="Fill out the form below and we'll get back to you as soon as possible."
            />
            
            <div class="group relative transform transition-all duration-300 hover:-translate-y-2 mt-8">
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>
                <div class="p-7">
                  <!-- Contact Form -->
                  <form @submit.prevent="submitForm" class="space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label for="name" class="block text-sm font-medium text-gray-300 mb-2">Your Name</label>
                        <input
                          type="text"
                          id="name"
                          v-model="formData.name"
                          class="w-full px-4 py-3 bg-dark-800/50 border border-dark-700 focus:border-primary-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500/25 transition-all duration-200"
                          placeholder="Enter your name"
                          required
                        />
                      </div>
                      <div>
                        <label for="email" class="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
                        <input
                          type="email"
                          id="email"
                          v-model="formData.email"
                          class="w-full px-4 py-3 bg-dark-800/50 border border-dark-700 focus:border-primary-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500/25 transition-all duration-200"
                          placeholder="youremail@example.com"
                          required
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label for="subject" class="block text-sm font-medium text-gray-300 mb-2">Subject</label>
                      <input
                        type="text"
                        id="subject"
                        v-model="formData.subject"
                        class="w-full px-4 py-3 bg-dark-800/50 border border-dark-700 focus:border-primary-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500/25 transition-all duration-200"
                        placeholder="What is your message about?"
                        required
                      />
                    </div>
                    
                    <div>
                      <label for="message" class="block text-sm font-medium text-gray-300 mb-2">Message</label>
                      <textarea
                        id="message"
                        v-model="formData.message"
                        rows="5"
                        class="w-full px-4 py-3 bg-dark-800/50 border border-dark-700 focus:border-primary-500/50 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500/25 transition-all duration-200 resize-none"
                        placeholder="Tell us how we can help you..."
                        required
                      ></textarea>
                    </div>
                    
                    <div>
                      <button
                        type="submit"
                        :disabled="isSubmitting"
                        class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 text-white rounded-xl hover:from-primary-600 hover:to-violet-600 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300"
                      >
                        <span v-if="isSubmitting">
                          <i class="fas fa-spinner fa-spin mr-2"></i>
                          Sending...
                        </span>
                        <span v-else>
                          <i class="fas fa-paper-plane mr-2"></i>
                          Send Message
                        </span>
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </section>

          <!-- FAQ Section -->
          <section>
            <SectionHeader 
              title="Frequently Asked Questions" 
              subtitle="Find quick answers to common questions about our services."
            />
            
            <div class="group relative transform transition-all duration-300 hover:-translate-y-2 mt-8">
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500/50 to-teal-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                <!-- Card header with gradient -->
                <div class="h-2 w-full bg-gradient-to-r from-emerald-500 to-teal-500"></div>
                <div class="p-7">
                  <div class="space-y-6">
                    <div v-for="(faq, index) in faqs" :key="index" class="border-b border-dark-700 pb-6 last:border-0 last:pb-0">
                      <h3 class="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                        <div class="w-6 h-6 rounded-full bg-emerald-500/15 flex items-center justify-center flex-shrink-0">
                          <i class="fas fa-question text-xs text-emerald-400"></i>
                        </div>
                        {{ faq.question }}
                      </h3>
                      <p class="text-gray-300">{{ faq.answer }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { GradientText, HeroBadge, SectionHeader } from '@/apps/home/components'
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
</style>