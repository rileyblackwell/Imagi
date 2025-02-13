<!-- Contact form component -->
<template>
  <form @submit.prevent="handleSubmit" class="space-y-8">
    <!-- Name field -->
    <div>
      <label class="block text-sm font-medium text-gray-300 mb-2">
        <i class="fas fa-user mr-2 text-primary-400"></i>
        Name
      </label>
      <input 
        type="text" 
        v-model="form.name"
        @input="updateField('name', $event.target.value)"
        required
        class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
      >
    </div>

    <!-- Email field -->
    <div>
      <label class="block text-sm font-medium text-gray-300 mb-2">
        <i class="fas fa-envelope mr-2 text-primary-400"></i>
        Email
      </label>
      <input 
        type="email" 
        v-model="form.email"
        @input="updateField('email', $event.target.value)"
        required
        class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
      >
    </div>

    <!-- Subject field -->
    <div>
      <label class="block text-sm font-medium text-gray-300 mb-2">
        <i class="fas fa-tag mr-2 text-primary-400"></i>
        Subject
      </label>
      <input 
        type="text" 
        v-model="form.subject"
        @input="updateField('subject', $event.target.value)"
        required
        class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
      >
    </div>

    <!-- Message field -->
    <div>
      <label class="block text-sm font-medium text-gray-300 mb-2">
        <i class="fas fa-comment mr-2 text-primary-400"></i>
        Message
      </label>
      <textarea 
        v-model="form.message"
        @input="updateField('message', $event.target.value)"
        rows="5" 
        required
        class="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
      ></textarea>
    </div>

    <!-- Submit button -->
    <div class="text-center">
      <button 
        type="submit"
        :disabled="!isValid || isLoading"
        class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span>Send Message</span>
        <i class="fas fa-paper-plane ml-2"></i>
      </button>
    </div>

    <!-- Error message -->
    <div v-if="error" class="text-red-500 text-center">
      {{ error }}
    </div>
  </form>
</template>

<script>
import { useHomeStore } from '@/apps/home/store/index'
import { computed } from 'vue'

export default {
  name: 'ContactForm',
  setup() {
    const store = useHomeStore()

    const form = computed(() => store.contactForm)
    const isLoading = computed(() => store.isLoading)
    const error = computed(() => store.error)
    const isValid = computed(() => store.isContactFormValid)

    const updateField = (field, value) => {
      store.updateContactForm(field, value)
    }

    const handleSubmit = async () => {
      if (await store.submitContactForm()) {
        // Handle successful submission (e.g., show success message)
      }
    }

    return {
      form,
      isLoading,
      error,
      isValid,
      updateField,
      handleSubmit
    }
  }
}
</script> 