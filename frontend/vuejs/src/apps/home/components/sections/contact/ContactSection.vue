<!-- Contact section component -->
<template>
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="text-center">
        <h2 class="text-3xl font-bold">
          <GradientText variant="accent" size="3xl">{{ title }}</GradientText>
        </h2>
        <p v-if="description" class="mt-4 text-xl text-gray-300 max-w-2xl mx-auto">
          {{ description }}
        </p>
      </div>

      <div class="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-12">
        <!-- Contact methods -->
        <div class="space-y-8">
          <div v-for="method in contactMethods" :key="method.title" 
            class="bg-dark-800 rounded-2xl p-8 border border-dark-700 hover:border-primary-500/20 transition-all">
            <div class="text-primary-400 mb-4">
              <i :class="['text-2xl', method.icon]"></i>
            </div>
            <h3 class="text-xl font-semibold text-white mb-4">{{ method.title }}</h3>
            <p class="text-gray-300 mb-2">{{ method.description }}</p>
            <a :href="method.link" class="text-primary-400 hover:text-primary-300">
              {{ method.linkText }}
            </a>
          </div>
        </div>

        <!-- Contact form -->
        <div class="bg-dark-800 rounded-2xl p-8 border border-dark-700">
          <ContactForm @submit="handleSubmit" />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import GradientText from '@/apps/home/components/shared/GradientText.vue'
import ContactForm from '@/apps/home/components/ui/ContactForm.vue'

export default {
  name: 'ContactSection',
  components: {
    GradientText,
    ContactForm
  },
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    contactMethods: {
      type: Array,
      required: true,
      validator: value => value.every(method => 
        method.icon && method.title && method.description && method.link && method.linkText
      )
    }
  },
  methods: {
    handleSubmit(formData) {
      this.$emit('submit', formData)
    }
  }
}
</script> 