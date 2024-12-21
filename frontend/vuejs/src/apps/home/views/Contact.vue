<template>
  <base-layout>
    <!-- Hero Section -->
    <template #hero>
      <div class="absolute inset-0 bg-gradient-radial from-primary-500/10 via-transparent to-transparent"></div>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-5xl md:text-6xl font-extrabold tracking-tight text-white">
            Get in Touch
          </h1>
          <p class="mt-6 text-xl text-gray-300">
            We're here to help you bring your ideas to life
          </p>
        </div>
      </div>
    </template>

    <!-- Main Content -->
    <template #default>
      <div class="py-24">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Contact Methods -->
          <section class="mb-24">
            <h2 class="text-3xl font-bold text-white text-center mb-16">Contact Methods</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-envelope text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Email Support</h3>
                <p class="text-gray-300 mb-4">For general inquiries and support</p>
                <a href="mailto:rileyblackwell5@gmail.com" class="text-primary-400 hover:text-primary-300">rileyblackwell5@gmail.com</a>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-phone text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Phone Support</h3>
                <p class="text-gray-300 mb-4">Available during business hours</p>
                <a href="tel:6168813592" class="text-primary-400 hover:text-primary-300">616-881-3592</a>
              </div>
            </div>
          </section>

          <!-- Contact Form -->
          <section class="mb-24">
            <h2 class="text-3xl font-bold text-white text-center mb-16">Send Us a Message</h2>
            <div class="max-w-2xl mx-auto">
              <form @submit.prevent="handleSubmit" class="space-y-8">
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    <i class="fas fa-user mr-2 text-primary-400"></i>
                    Name
                  </label>
                  <input 
                    type="text" 
                    v-model="form.name" 
                    required
                    class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    <i class="fas fa-envelope mr-2 text-primary-400"></i>
                    Email
                  </label>
                  <input 
                    type="email" 
                    v-model="form.email" 
                    required
                    class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    <i class="fas fa-tag mr-2 text-primary-400"></i>
                    Subject
                  </label>
                  <input 
                    type="text" 
                    v-model="form.subject" 
                    required
                    class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    <i class="fas fa-comment mr-2 text-primary-400"></i>
                    Message
                  </label>
                  <textarea 
                    v-model="form.message" 
                    rows="5" 
                    required
                    class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
                  ></textarea>
                </div>
                <div class="text-center">
                  <button 
                    type="submit"
                    class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                  >
                    Send Message
                    <i class="fas fa-paper-plane ml-2"></i>
                  </button>
                </div>
              </form>
            </div>
          </section>

          <!-- Response Time -->
          <section>
            <h2 class="text-3xl font-bold text-white text-center mb-16">Response Time</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-clock text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">General Support</h3>
                <p class="text-gray-300">We typically respond within 24 hours during business days.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700 transition-all duration-300 hover:-translate-y-2 hover:border-primary-500/20 hover:shadow-glow">
                <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/10 flex items-center justify-center mb-6">
                  <i class="fas fa-exclamation-circle text-2xl text-primary-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Urgent Issues</h3>
                <p class="text-gray-300">For urgent matters, please use our phone support for immediate assistance.</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </template>
  </base-layout>
</template>

<script>
import { ref } from 'vue'
import BaseLayout from '@/shared/layouts/BaseLayout.vue'

export default {
  name: 'Contact',
  components: {
    BaseLayout
  },
  setup() {
    const form = ref({
      name: '',
      email: '',
      subject: '',
      message: ''
    })

    const handleSubmit = async () => {
      // TODO: Implement form submission logic
      console.log('Form submitted:', form.value)
    }

    return {
      form,
      handleSubmit
    }
  }
}
</script>

<style>
.shadow-glow {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 255, 204, 0.1);
}

.bg-gradient-radial {
  background: radial-gradient(circle at top right, var(--tw-gradient-from), var(--tw-gradient-to));
}
</style> 