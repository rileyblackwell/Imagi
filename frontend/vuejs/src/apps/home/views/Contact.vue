<!-- Contact page -->
<template>
  <DefaultLayout>
    <HomeNavbar />
    <div>
      <!-- Hero Section -->
      <hero-section
        title="Get in Touch"
        description="We're here to help you bring your ideas to life"
      />

      <div class="max-w-4xl mx-auto px-4 py-16">
        <div class="space-y-16">
          <!-- Contact Methods -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Contact Methods</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-envelope text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Email Support</h3>
                <p class="text-gray-300 mb-2">For general inquiries and support</p>
                <a href="mailto:rileyblackwell5@gmail.com" class="text-primary-400 hover:text-primary-300">rileyblackwell5@gmail.com</a>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-phone text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">Phone Support</h3>
                <p class="text-gray-300 mb-2">Available during business hours</p>
                <a href="tel:6168813592" class="text-primary-400 hover:text-primary-300">616-881-3592</a>
              </div>
            </div>
          </section>

          <!-- Contact Form -->
          <section>
            <h2 class="text-3xl font-bold text-white mb-8">Send Us a Message</h2>
            <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
              <form class="space-y-6" @submit.prevent="handleSubmit">
                <div>
                  <label class="block text-white mb-2">
                    <i class="fas fa-user mr-2"></i>
                    Name
                  </label>
                  <input
                    type="text"
                    v-model="form.name"
                    required
                    class="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-400"
                  />
                </div>
                <div>
                  <label class="block text-white mb-2">
                    <i class="fas fa-envelope mr-2"></i>
                    Email
                  </label>
                  <input
                    type="email"
                    v-model="form.email"
                    required
                    class="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-400"
                  />
                </div>
                <div>
                  <label class="block text-white mb-2">
                    <i class="fas fa-tag mr-2"></i>
                    Subject
                  </label>
                  <input
                    type="text"
                    v-model="form.subject"
                    required
                    class="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-400"
                  />
                </div>
                <div>
                  <label class="block text-white mb-2">
                    <i class="fas fa-comment mr-2"></i>
                    Message
                  </label>
                  <textarea
                    v-model="form.message"
                    required
                    rows="5"
                    class="w-full bg-dark-900 border border-dark-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-400"
                  ></textarea>
                </div>
                <div>
                  <button
                    type="submit"
                    class="w-full bg-primary-600 hover:bg-primary-500 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
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
            <h2 class="text-3xl font-bold text-white mb-8">Response Time</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-clock text-2xl"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-4">General Support</h3>
                <p class="text-gray-300">We typically respond within 24 hours during business days.</p>
              </div>
              <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
                <div class="text-primary-400 mb-4">
                  <i class="fas fa-exclamation-circle text-2xl"></i>
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
import { ref } from 'vue'
import HomeNavbar from '../components/HomeNavbar.vue'

export default {
  name: 'Contact',
  components: {
    DefaultLayout,
    HeroSection,
    HomeNavbar
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