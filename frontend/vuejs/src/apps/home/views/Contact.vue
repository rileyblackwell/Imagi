<!-- Contact page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[60vh] md:min-h-[50vh] flex items-center justify-center overflow-hidden py-12 md:py-20">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 class="text-3xl sm:text-4xl lg:text-6xl font-bold tracking-tight mb-4 md:mb-6">
            <span class="text-white block">Get in Touch</span>
            <GradientText variant="primary" class="font-bold block text-3xl sm:text-4xl lg:text-5xl">
              We're Here to Help
            </GradientText>
          </h1>
          <p class="text-base sm:text-lg lg:text-xl text-gray-300 mb-6 md:mb-8 max-w-2xl mx-auto">
            Have questions or need assistance? We're here to help you bring your ideas to life.
          </p>
        </div>
      </section>

      <div class="max-w-4xl mx-auto px-4 py-8 md:py-16 relative">
        <div class="space-y-8 md:space-y-16">
          <!-- Contact Methods -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Contact Methods</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-envelope text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Email Support</h3>
                <p class="text-gray-300 mb-2">For general inquiries and support</p>
                <a href="mailto:rileyblackwell5@gmail.com" class="text-primary-400 hover:text-primary-300 transition-colors">rileyblackwell5@gmail.com</a>
              </div>
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-phone text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Phone Support</h3>
                <p class="text-gray-300 mb-2">Available during business hours</p>
                <a href="tel:6168813592" class="text-primary-400 hover:text-primary-300 transition-colors">616-881-3592</a>
              </div>
            </div>
          </section>

          <!-- Contact Form -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Send Us a Message</h2>
            <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-6 md:p-8 border border-dark-700">
              <form class="space-y-4 md:space-y-6" @submit.prevent="handleSubmit">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="text-white mb-2 flex items-center">
                      <i class="fas fa-user text-primary-400 mr-2"></i>
                      Name
                    </label>
                    <input
                      type="text"
                      v-model="form.name"
                      required
                      class="w-full bg-dark-900/50 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all"
                    />
                  </div>
                  <div>
                    <label class="text-white mb-2 flex items-center">
                      <i class="fas fa-envelope text-primary-400 mr-2"></i>
                      Email
                    </label>
                    <input
                      type="email"
                      v-model="form.email"
                      required
                      class="w-full bg-dark-900/50 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all"
                    />
                  </div>
                </div>
                <div>
                  <label class="text-white mb-2 flex items-center">
                    <i class="fas fa-tag text-primary-400 mr-2"></i>
                    Subject
                  </label>
                  <input
                    type="text"
                    v-model="form.subject"
                    required
                    class="w-full bg-dark-900/50 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all"
                  />
                </div>
                <div>
                  <label class="text-white mb-2 flex items-center">
                    <i class="fas fa-comment text-primary-400 mr-2"></i>
                    Message
                  </label>
                  <textarea
                    v-model="form.message"
                    required
                    rows="5"
                    class="w-full bg-dark-900/50 border border-dark-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400/50 transition-all resize-none"
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

          <!-- Response Time -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8 text-center">Response Time</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-clock text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">General Support</h3>
                <p class="text-gray-300">We typically respond within 24 hours during business days.</p>
              </div>
              <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300 hover:-translate-y-1 group">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <i class="fas fa-exclamation-circle text-2xl text-primary-400"></i>
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
import { DefaultLayout } from '../../../shared/layouts'
import { HeroSection } from '../components'
import GradientText from '../components/shared/GradientText.vue'
import { ref } from 'vue'

export default {
  name: 'Contact',
  components: {
    DefaultLayout,
    HeroSection,
    GradientText
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
}
</script>