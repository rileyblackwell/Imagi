<!-- Contact page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pt-36 sm:pb-20">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
          <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <HeroBadge text="Support & Assistance" />
          
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block mb-2 sm:mb-3">Get in Touch</span>
            <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
              We're Here to Help
            </GradientText>
          </h1>
          
          <p class="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto">
            Have questions or need assistance? We're here to help you bring your ideas to life.
          </p>
        </div>
      </section>

      <!-- Main Content -->
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-500 rounded-full blur-[100px] opacity-20 transform rotate-45"></div>
          <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-500 rounded-full blur-[100px] opacity-20 transform -rotate-45"></div>
        </div>

        <!-- Contact Content -->
        <div class="space-y-16 relative">
          <!-- Contact Methods -->
          <section>
            <SectionHeader 
              title="Contact Methods" 
              subtitle="Reach out to us through your preferred channel of communication."
            />
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mt-8">
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)] p-7">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-500 flex items-center justify-center shadow-md mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-envelope text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Email Support</h3>
                <p class="text-gray-300 mb-2">For general inquiries and support</p>
                <a href="mailto:rileyblackwell5@gmail.com" class="text-primary-400 hover:text-primary-300 transition-colors">rileyblackwell5@gmail.com</a>
              </div>
              
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-violet-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)] p-7">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-phone text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Phone Support</h3>
                <p class="text-gray-300 mb-2">Available during business hours</p>
                <a href="tel:6168813592" class="text-primary-400 hover:text-primary-300 transition-colors">616-881-3592</a>
              </div>
            </div>
          </section>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-dark-700"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="bg-dark-900 px-4 text-sm text-gray-400">Contact Form</span>
            </div>
          </div>

          <!-- Contact Form -->
          <section>
            <SectionHeader 
              title="Send Us a Message" 
              subtitle="Fill out the form below and we'll get back to you as soon as possible."
            />
            
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)] p-7 mt-8">
              <form class="space-y-6" @submit.prevent="handleSubmit">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="text-white mb-2 flex items-center text-sm font-medium">
                      <i class="fas fa-user text-primary-400 mr-2"></i>
                      Name
                    </label>
                    <input
                      type="text"
                      v-model="form.name"
                      required
                      class="w-full bg-dark-900/70 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all"
                    />
                  </div>
                  <div>
                    <label class="text-white mb-2 flex items-center text-sm font-medium">
                      <i class="fas fa-envelope text-primary-400 mr-2"></i>
                      Email
                    </label>
                    <input
                      type="email"
                      v-model="form.email"
                      required
                      class="w-full bg-dark-900/70 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all"
                    />
                  </div>
                </div>
                <div>
                  <label class="text-white mb-2 flex items-center text-sm font-medium">
                    <i class="fas fa-tag text-primary-400 mr-2"></i>
                    Subject
                  </label>
                  <input
                    type="text"
                    v-model="form.subject"
                    required
                    class="w-full bg-dark-900/70 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all"
                  />
                </div>
                <div>
                  <label class="text-white mb-2 flex items-center text-sm font-medium">
                    <i class="fas fa-comment text-primary-400 mr-2"></i>
                    Message
                  </label>
                  <textarea
                    v-model="form.message"
                    required
                    rows="5"
                    class="w-full bg-dark-900/70 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all resize-none"
                  ></textarea>
                </div>
                <div>
                  <button
                    type="submit"
                    class="w-full bg-gradient-to-r from-primary-600 to-primary-400 hover:from-primary-500 hover:to-primary-300 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-300 transform hover:scale-[1.02] flex items-center justify-center"
                  >
                    <span>Send Message</span>
                    <i class="fas fa-paper-plane ml-2"></i>
                  </button>
                </div>
              </form>
            </div>
          </section>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-dark-700"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="bg-dark-900 px-4 text-sm text-gray-400">Response Times</span>
            </div>
          </div>

          <!-- Response Time -->
          <section>
            <SectionHeader 
              title="Response Time" 
              subtitle="We strive to respond to all inquiries as quickly as possible."
            />
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 mt-8">
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)] p-7">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-500 flex items-center justify-center shadow-md mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-clock text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">General Support</h3>
                <p class="text-gray-300">We typically respond within 24 hours during business days.</p>
              </div>
              
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-violet-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)] p-7">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-exclamation-circle text-white text-xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Urgent Issues</h3>
                <p class="text-gray-300">For urgent matters, please use our phone support for immediate assistance.</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { 
  GradientText, 
  HeroBadge,
  SectionHeader 
} from '@/apps/home/components'
import { ref } from 'vue'

export default defineComponent({
  name: 'Contact',
  components: {
    DefaultLayout,
    GradientText,
    HeroBadge,
    SectionHeader
  },
  setup() {
    const form = ref({
      name: '',
      email: '',
      subject: '',
      message: ''
    })

    const handleSubmit = async () => {
      // TODO: Implement form submission
      console.log('Form submitted:', form.value)
    }

    return {
      form,
      handleSubmit
    }
  }
})
</script>

<style scoped>
/* Styles for form elements */
input:focus, textarea:focus {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

/* Input hover effects */
input:hover, textarea:hover {
  border-color: rgba(99, 102, 241, 0.3);
}
</style>