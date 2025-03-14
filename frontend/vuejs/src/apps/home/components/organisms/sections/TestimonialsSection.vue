<!-- Testimonials Section Component -->
<template>
  <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 relative">
    <div class="max-w-7xl mx-auto">
      <SectionHeader
        :title="title"
        :subtitle="subtitle"
      />

      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
        <!-- Connecting line between testimonials -->
        <div class="absolute top-1/3 left-0 right-0 h-px bg-gradient-to-r from-primary-500/0 via-primary-500/20 to-primary-500/0 -z-10 hidden md:block"></div>
        
        <TestimonialCard 
          v-for="(testimonial, index) in testimonials" 
          :key="index"
          :quote="testimonial.quote"
          :avatar-initials="testimonial.avatarInitials"
          :name="testimonial.name"
          :position="testimonial.position"
          :color="testimonial.color"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import SectionHeader from '@/apps/home/components/molecules/containers/SectionHeader.vue'
import TestimonialCard from '@/apps/home/components/molecules/cards/TestimonialCard.vue'

export default defineComponent({
  name: 'TestimonialsSection',
  components: {
    SectionHeader,
    TestimonialCard
  },
  props: {
    title: {
      type: String,
      default: 'What Developers Say'
    },
    subtitle: {
      type: String,
      default: 'Join thousands of satisfied developers who trust Imagi'
    },
    testimonials: {
      type: Array,
      default: () => [
        {
          quote: 'Imagi has revolutionized how I build web applications. What used to take weeks now takes hours. The AI understands exactly what I need.',
          avatarInitials: 'JS',
          name: 'John Smith',
          position: 'Senior Developer',
          color: 'primary'
        },
        {
          quote: "The code quality is impressive. It's not just about speed - Imagi generates clean, maintainable code that follows best practices.",
          avatarInitials: 'AD',
          name: 'Alice Davis',
          position: 'Tech Lead',
          color: 'indigo'
        },
        {
          quote: "Perfect for startups and MVPs. We've cut our development time by 80% and can iterate much faster with customer feedback.",
          avatarInitials: 'MR',
          name: 'Mike Ross',
          position: 'Startup Founder',
          color: 'violet'
        }
      ]
    }
  }
})
</script> 