<!-- FAQ Section - Accordion design -->
<template>
  <section id="faq" class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden scroll-mt-20">
    <div class="max-w-4xl mx-auto relative z-10">
      <!-- Section header -->
      <div class="text-center mb-12 md:mb-16">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.08] rounded-full border border-white/20 mb-6">
          <i class="fas fa-question-circle text-xs text-blue-400"></i>
          <span class="text-sm font-medium text-white/90">FAQ</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white mb-5 tracking-tight">
          Frequently Asked Questions
        </h2>
        <p class="text-lg text-white/85 max-w-2xl mx-auto leading-relaxed">
          Everything you need to know about building apps with Imagi.
        </p>
      </div>

      <!-- FAQ Accordion -->
      <div class="space-y-4" role="region" aria-label="Frequently Asked Questions">
        <div 
          v-for="(faq, idx) in faqs" 
          :key="idx"
          class="group scroll-mt-24"
        >
            <div 
              class="rounded-xl border transition-all duration-300 overflow-hidden"
              :class="openIndex === idx 
                ? 'border-violet-500/50 bg-violet-500/15' 
                : 'border-white/15 bg-white/[0.07] hover:bg-white/[0.1] hover:border-white/25'"
            >
              <!-- Question button -->
              <button
                :ref="el => { if (el) accordionRefs[idx] = el }"
                @click="toggleFaq(idx)"
                @keydown="handleAccordionKeyNav($event, idx)"
                class="w-full flex items-center justify-between gap-4 p-5 text-left focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:ring-offset-2 focus:ring-offset-[#0f0f1a] rounded-xl"
                :aria-expanded="openIndex === idx"
                :aria-controls="`faq-answer-${idx}`"
                :id="`faq-question-${idx}`"
              >
                <div class="flex items-center gap-4">
                  <div 
                    class="flex-shrink-0 flex items-center justify-center w-9 h-9 rounded-lg transition-all duration-300"
                    :class="openIndex === idx 
                      ? 'bg-violet-500/30 border border-violet-500/50' 
                      : 'bg-white/[0.1] border border-white/20'"
                  >
                    <i 
                      :class="[faq.icon, 'text-sm transition-colors duration-300', openIndex === idx ? 'text-violet-400' : 'text-white/65']"
                    ></i>
                  </div>
                  <span 
                    class="font-medium transition-colors duration-300"
                    :class="openIndex === idx ? 'text-white' : 'text-white/90'"
                  >
                    {{ faq.question }}
                  </span>
                </div>
                
                <div 
                  class="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300"
                  :class="openIndex === idx 
                    ? 'bg-violet-500/30 rotate-180' 
                    : 'bg-white/[0.1]'"
                >
                  <i 
                    class="fas fa-chevron-down text-xs transition-colors duration-300"
                    :class="openIndex === idx ? 'text-violet-400' : 'text-white/65'"
                  ></i>
                </div>
              </button>
              
              <!-- Answer panel -->
              <div 
                :id="`faq-answer-${idx}`"
                :aria-labelledby="`faq-question-${idx}`"
                role="region"
                :hidden="openIndex !== idx"
                class="overflow-hidden transition-all duration-300 ease-in-out"
                :style="{ 
                  maxHeight: openIndex === idx ? '1000px' : '0px',
                  opacity: openIndex === idx ? '1' : '0'
                }"
              >
                <div class="px-5 pb-5 pt-2">
                  <div class="ml-4 md:ml-[52px] border-l border-white/10 pl-4 md:pl-6">
                    <p class="text-white/70 leading-relaxed text-sm">
                      {{ faq.answer }}
                    </p>
                  
                  <!-- Optional link -->
                  <router-link 
                    v-if="faq.link"
                    :to="faq.link.to"
                    class="inline-flex items-center gap-2 mt-4 text-sm text-violet-400 hover:text-violet-300 transition-colors"
                  >
                    {{ faq.link.text }}
                    <i class="fas fa-arrow-right text-xs"></i>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Bottom CTA -->
      <div class="mt-12 p-6 rounded-2xl border border-white/10 bg-white/[0.04] text-center">
        <div class="flex items-center justify-center gap-3 mb-3">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-violet-500/20 border border-violet-500/30">
            <i class="fas fa-headset text-violet-400"></i>
          </div>
          <h3 class="text-lg font-semibold text-white">Still have questions?</h3>
        </div>
        <p class="text-white/70 text-sm mb-4">
          Our team is here to help. Reach out and we'll get back to you within 24 hours.
        </p>
        <router-link 
          to="/contact"
          class="inline-flex items-center gap-2 px-5 py-2.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-lg text-white text-sm font-medium transition-all duration-300"
        >
          <i class="fas fa-envelope text-violet-400/80 text-xs"></i>
          Contact Support
        </router-link>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref, reactive } from 'vue'

export default defineComponent({
  name: 'FAQSection',
  setup() {
    const openIndex = ref(0) // First one open by default
    const accordionRefs = reactive({})
    
    const toggleFaq = (idx) => {
      openIndex.value = openIndex.value === idx ? -1 : idx
    }
    
    const handleAccordionKeyNav = (e, currentIdx) => {
      const totalFaqs = faqs.length
      let newIndex = currentIdx
      
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        newIndex = Math.min(currentIdx + 1, totalFaqs - 1)
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        newIndex = Math.max(currentIdx - 1, 0)
      } else if (e.key === 'Home') {
        e.preventDefault()
        newIndex = 0
      } else if (e.key === 'End') {
        e.preventDefault()
        newIndex = totalFaqs - 1
      }
      
      if (newIndex !== currentIdx) {
        accordionRefs[newIndex]?.focus()
      }
    }
    
    const faqs = [
      {
        icon: 'fas fa-code',
        question: 'What does "no-code" mean? Do I own the code?',
        answer: 'No-code means you describe your app in plain English and our AI generates the code for you — no programming required. Yes, you own 100% of the generated code. It\'s standard Vue.js and Django that you can download, modify, and host anywhere you want.',
        link: { text: 'Learn more about ownership', to: '/docs' }
      },
      {
        icon: 'fas fa-layer-group',
        question: 'What kind of apps can I build?',
        answer: 'Imagi generates full-stack web applications with Vue.js frontends and Django backends. This includes dashboards, admin panels, customer portals, booking systems, e-commerce stores, CRMs, internal tools, and more. If it\'s a web app, you can likely build it with Imagi.',
        link: { text: 'See example templates', to: '/docs' }
      },
      {
        icon: 'fas fa-edit',
        question: 'How do I make changes to my app?',
        answer: 'Just chat with the AI! Describe what you want to change — "make the header blue", "add a search bar", "create a new page for user settings" — and Imagi updates your entire application. You can iterate as many times as you need.',
      },
      {
        icon: 'fas fa-dollar-sign',
        question: 'How does pricing work?',
        answer: 'Imagi uses a credit-based system. You purchase credits and spend them on AI requests. Building a complete app typically costs $5-15 in credits depending on complexity. There are no monthly fees — you only pay for what you build.',
        link: { text: 'View pricing details', to: '/payments/pricing' }
      },
      {
        icon: 'fas fa-rocket',
        question: 'When will deployment be available?',
        answer: 'Imagi-hosted deployment is coming in Q1 2026. You\'ll be able to publish your app to a .imagi.app domain with one click. Custom domains, SSL, and auto-scaling will be included. Join the waitlist to get early access.',
        link: { text: 'Join the waitlist', to: '/contact' }
      },
      {
        icon: 'fas fa-download',
        question: 'Can I export and self-host my app?',
        answer: 'Absolutely. You can download your complete application source code at any time. The generated code is clean, well-structured Vue.js and Django that follows best practices. Deploy it to any hosting provider you prefer.',
      },
      {
        icon: 'fas fa-database',
        question: 'Does Imagi support databases and authentication?',
        answer: 'Currently, Imagi generates Django backends with SQLite databases and basic data models. Full authentication systems and PostgreSQL support are in development and coming soon. The generated code is structured to easily add these features.',
      },
      {
        icon: 'fas fa-shield-alt',
        question: 'Is my data and code secure?',
        answer: 'Yes. Your projects are private and only accessible to you. We use industry-standard encryption for data in transit and at rest. Your generated code is never shared or used to train our models. You maintain full ownership and control.',
      }
    ]
    
    return {
      openIndex,
      toggleFaq,
      faqs,
      accordionRefs,
      handleAccordionKeyNav
    }
  }
})
</script>

<style scoped>
</style>
