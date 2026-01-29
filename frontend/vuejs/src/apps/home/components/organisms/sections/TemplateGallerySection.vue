<!-- Template Gallery Section - Carousel/scroll-snap gallery -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-7xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-10 md:mb-14">
        <SectionPill
          class="mb-7"
          tone="fuchsia"
          icon="fas fa-th-large"
          label="App Templates"
        />
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-5 tracking-[-0.02em]">
          Start with a Template
        </h2>
        <p class="text-lg text-white/70 max-w-2xl mx-auto leading-relaxed font-light">
          Jump-start your project with pre-built templates. Customize everything through conversation.
        </p>
      </div>

      <!-- Gallery container -->
      <div class="relative">
        <!-- Navigation arrows -->
        <button 
          @click="scrollPrev"
          class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 hidden md:flex items-center justify-center w-12 h-12 rounded-full bg-[#0f0f1a]/90 border border-white/[0.2] text-white/75 hover:text-white hover:border-white/[0.3] transition-all duration-300 shadow-xl backdrop-blur-sm"
          :class="{ 'opacity-50 cursor-not-allowed': !canScrollPrev }"
          :disabled="!canScrollPrev"
          aria-label="Previous templates"
        >
          <i class="fas fa-chevron-left"></i>
        </button>
        
        <button 
          @click="scrollNext"
          class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 hidden md:flex items-center justify-center w-12 h-12 rounded-full bg-[#0f0f1a]/90 border border-white/[0.2] text-white/75 hover:text-white hover:border-white/[0.3] transition-all duration-300 shadow-xl backdrop-blur-sm"
          :class="{ 'opacity-50 cursor-not-allowed': !canScrollNext }"
          :disabled="!canScrollNext"
          aria-label="Next templates"
        >
          <i class="fas fa-chevron-right"></i>
        </button>

        <!-- Scrollable gallery -->
        <div 
          ref="galleryRef"
          class="flex gap-5 overflow-x-auto snap-x snap-mandatory scrollbar-hide pb-4 -mx-6 px-6 md:mx-0 md:px-0"
          @scroll="updateScrollState"
          @keydown="handleGalleryKeyNav"
          role="region"
          aria-label="App template gallery"
          tabindex="0"
        >
          <div 
            v-for="(template, idx) in templates" 
            :key="idx"
            class="flex-shrink-0 w-[300px] md:w-[340px] snap-start"
          >
            <!-- Template card -->
            <div class="group relative h-full rounded-2xl border border-white/[0.12] bg-white/[0.05] backdrop-blur-sm hover:bg-white/[0.08] hover:border-white/[0.20] transition-all duration-500 overflow-hidden">
              <!-- Hover glow -->
              <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <div class="absolute inset-0 bg-gradient-to-br opacity-[0.08]" :class="template.gradient"></div>
              </div>
              
              <!-- Preview image area -->
              <div class="relative h-40 bg-gradient-to-br from-white/[0.07] to-white/[0.04] border-b border-white/15 overflow-hidden">
                <!-- Stylized preview -->
                <div class="absolute inset-3 rounded-lg bg-[#12121d] border border-white/20 overflow-hidden">
                  <!-- Mini browser chrome -->
                  <div class="flex items-center gap-1 px-2 py-1 bg-white/[0.08] border-b border-white/15">
                    <div class="w-1.5 h-1.5 rounded-full bg-white/30"></div>
                    <div class="w-1.5 h-1.5 rounded-full bg-white/30"></div>
                    <div class="w-1.5 h-1.5 rounded-full bg-white/30"></div>
                  </div>
                  <!-- Preview content -->
                  <div class="p-2">
                    <component :is="template.previewComponent" />
                  </div>
                </div>
                
                <!-- Gradient overlay -->
                <div class="absolute inset-0 bg-gradient-to-t from-[#0d0d12] via-transparent to-transparent opacity-60"></div>
                
                <!-- Category badge -->
                <div class="absolute top-3 right-3 px-2 py-1 rounded-md text-[10px] font-medium"
                     :class="template.categoryClass">
                  {{ template.category }}
                </div>
              </div>
              
              <!-- Content -->
              <div class="p-5">
                <!-- Title and description -->
                <h3 class="text-lg font-semibold text-white mb-2">{{ template.title }}</h3>
                <p class="text-sm text-white/70 leading-relaxed mb-4">{{ template.description }}</p>
                
                <!-- Stack badges -->
                <div class="flex flex-wrap gap-1.5 mb-4">
                  <span v-for="(tech, tIdx) in template.stack" :key="tIdx"
                        class="px-2 py-0.5 bg-white/[0.06] border border-white/10 rounded text-[10px] text-white/70">
                    {{ tech }}
                  </span>
                </div>
                
                <!-- Features -->
                <ul class="space-y-1.5 mb-5">
                  <li v-for="(feature, fIdx) in template.features" :key="fIdx"
                      class="flex items-center gap-2 text-xs text-white/60">
                    <i class="fas fa-check text-[8px]" :class="template.checkColor"></i>
                    {{ feature }}
                  </li>
                </ul>
                
                <!-- CTA -->
                <router-link 
                  to="/auth/signin"
                  class="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-sm font-medium transition-all duration-300"
                  :class="template.buttonClass"
                >
                  <i class="fas fa-wand-magic-sparkles text-xs"></i>
                  Use This Template
                </router-link>
              </div>
              
              <!-- Bottom accent -->
              <div class="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                   :class="template.accentClass"></div>
            </div>
          </div>
        </div>
        
        <!-- Scroll indicators -->
        <div class="flex items-center justify-center gap-2 mt-6">
          <button 
            v-for="(_, idx) in Math.ceil(templates.length / visibleCount)" 
            :key="idx"
            @click="scrollToIndex(idx)"
            class="w-2 h-2 rounded-full transition-all duration-300"
            :class="currentPage === idx ? 'bg-violet-400 w-6' : 'bg-white/20 hover:bg-white/30'"
            :aria-label="`Go to page ${idx + 1}`"
          ></button>
        </div>
      </div>
      
      <!-- Bottom CTA -->
      <div class="text-center mt-12">
        <p class="text-white/60 text-sm mb-4">Don't see what you need? Describe any app and we'll build it.</p>
        <router-link 
          to="/auth/signin"
          class="inline-flex items-center gap-2 px-6 py-3 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-xl text-white font-medium transition-all duration-300"
        >
          <i class="fas fa-plus text-violet-400"></i>
          Start from Scratch
        </router-link>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref, onMounted, onUnmounted, h } from 'vue'
import { SectionPill } from '@/apps/home/components/atoms'

// Mini preview components
const EcommercePreview = {
  render() {
    return h('div', { class: 'space-y-1.5' }, [
      h('div', { class: 'h-2 bg-violet-500/30 rounded w-1/2' }),
      h('div', { class: 'grid grid-cols-3 gap-1 mt-2' }, [
        h('div', { class: 'h-6 bg-white/[0.04] rounded border border-white/[0.06]' }),
        h('div', { class: 'h-6 bg-white/[0.04] rounded border border-white/[0.06]' }),
        h('div', { class: 'h-6 bg-white/[0.04] rounded border border-white/[0.06]' })
      ]),
      h('div', { class: 'h-1.5 bg-white/[0.06] rounded w-3/4 mt-2' })
    ])
  }
}

const DashboardPreview = {
  render() {
    return h('div', { class: 'space-y-1.5' }, [
      h('div', { class: 'flex gap-1' }, [
        h('div', { class: 'w-8 space-y-1' }, [
          h('div', { class: 'h-1.5 bg-fuchsia-500/30 rounded' }),
          h('div', { class: 'h-1 bg-white/[0.06] rounded' }),
          h('div', { class: 'h-1 bg-white/[0.06] rounded' })
        ]),
        h('div', { class: 'flex-1 space-y-1' }, [
          h('div', { class: 'h-4 bg-white/[0.04] rounded border border-white/[0.06]' }),
          h('div', { class: 'grid grid-cols-2 gap-1' }, [
            h('div', { class: 'h-3 bg-white/[0.04] rounded' }),
            h('div', { class: 'h-3 bg-white/[0.04] rounded' })
          ])
        ])
      ])
    ])
  }
}

const BookingPreview = {
  render() {
    return h('div', { class: 'space-y-1.5' }, [
      h('div', { class: 'h-2 bg-emerald-500/30 rounded w-2/3' }),
      h('div', { class: 'grid grid-cols-7 gap-0.5 mt-2' }, 
        Array(14).fill(null).map(() => h('div', { class: 'h-2 bg-white/[0.04] rounded-sm' }))
      ),
      h('div', { class: 'h-2 bg-emerald-500/20 rounded w-1/2 mt-2' })
    ])
  }
}

const CRMPreview = {
  render() {
    return h('div', { class: 'space-y-1' }, [
      h('div', { class: 'h-2 bg-blue-500/30 rounded w-1/2' }),
      h('div', { class: 'space-y-1 mt-2' }, [
        h('div', { class: 'flex items-center gap-1' }, [
          h('div', { class: 'w-3 h-3 rounded-full bg-white/[0.08]' }),
          h('div', { class: 'flex-1 h-1.5 bg-white/[0.06] rounded' })
        ]),
        h('div', { class: 'flex items-center gap-1' }, [
          h('div', { class: 'w-3 h-3 rounded-full bg-white/[0.08]' }),
          h('div', { class: 'flex-1 h-1.5 bg-white/[0.06] rounded' })
        ]),
        h('div', { class: 'flex items-center gap-1' }, [
          h('div', { class: 'w-3 h-3 rounded-full bg-white/[0.08]' }),
          h('div', { class: 'flex-1 h-1.5 bg-white/[0.06] rounded' })
        ])
      ])
    ])
  }
}

const CoursePreview = {
  render() {
    return h('div', { class: 'space-y-1.5' }, [
      h('div', { class: 'h-5 bg-gradient-to-r from-amber-500/20 to-orange-500/20 rounded' }),
      h('div', { class: 'space-y-0.5 mt-1' }, [
        h('div', { class: 'h-1.5 bg-white/[0.06] rounded w-full' }),
        h('div', { class: 'h-1.5 bg-white/[0.06] rounded w-4/5' })
      ]),
      h('div', { class: 'h-1 bg-amber-500/30 rounded w-1/3 mt-1' })
    ])
  }
}

const InternalToolPreview = {
  render() {
    return h('div', { class: 'space-y-1.5' }, [
      h('div', { class: 'flex gap-1' }, [
        h('div', { class: 'h-2 bg-rose-500/30 rounded flex-1' }),
        h('div', { class: 'h-2 bg-white/[0.06] rounded w-4' })
      ]),
      h('div', { class: 'h-6 bg-white/[0.04] rounded border border-white/[0.06] mt-1' }),
      h('div', { class: 'grid grid-cols-2 gap-1 mt-1' }, [
        h('div', { class: 'h-2 bg-white/[0.06] rounded' }),
        h('div', { class: 'h-2 bg-rose-500/20 rounded' })
      ])
    ])
  }
}

export default defineComponent({
  name: 'TemplateGallerySection',
  components: {
    SectionPill
  },
  setup() {
    const galleryRef = ref(null)
    const canScrollPrev = ref(false)
    const canScrollNext = ref(true)
    const currentPage = ref(0)
    const visibleCount = ref(3)
    
    const templates = [
      {
        title: 'E-Commerce Store',
        description: 'Full-featured online store with product catalog, cart, and checkout flow.',
        category: 'Commerce',
        categoryClass: 'bg-violet-500/20 text-violet-300 border border-violet-500/30',
        gradient: 'from-violet-500 to-purple-500',
        checkColor: 'text-violet-400',
        accentClass: 'bg-gradient-to-r from-transparent via-violet-500/50 to-transparent',
        buttonClass: 'bg-violet-500/20 text-violet-300 border border-violet-500/30 hover:bg-violet-500/30',
        stack: ['Vue.js', 'Django', 'REST API'],
        features: ['Product management', 'Shopping cart', 'Order tracking'],
        previewComponent: EcommercePreview
      },
      {
        title: 'Admin Dashboard',
        description: 'Data-rich dashboard with charts, tables, and user management.',
        category: 'Business',
        categoryClass: 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/30',
        gradient: 'from-fuchsia-500 to-pink-500',
        checkColor: 'text-fuchsia-400',
        accentClass: 'bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent',
        buttonClass: 'bg-fuchsia-500/20 text-fuchsia-300 border border-fuchsia-500/30 hover:bg-fuchsia-500/30',
        stack: ['Vue.js', 'Django', 'Charts'],
        features: ['Analytics widgets', 'User roles', 'Data export'],
        previewComponent: DashboardPreview
      },
      {
        title: 'Booking System',
        description: 'Appointment scheduling with calendar, availability, and notifications.',
        category: 'Services',
        categoryClass: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
        gradient: 'from-emerald-500 to-teal-500',
        checkColor: 'text-emerald-400',
        accentClass: 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent',
        buttonClass: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/30',
        stack: ['Vue.js', 'Django', 'Calendar'],
        features: ['Time slot picker', 'Email reminders', 'Staff management'],
        previewComponent: BookingPreview
      },
      {
        title: 'Customer CRM',
        description: 'Manage contacts, deals, and communications in one place.',
        category: 'Sales',
        categoryClass: 'bg-blue-500/20 text-blue-300 border border-blue-500/30',
        gradient: 'from-blue-500 to-cyan-500',
        checkColor: 'text-blue-400',
        accentClass: 'bg-gradient-to-r from-transparent via-blue-500/50 to-transparent',
        buttonClass: 'bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30',
        stack: ['Vue.js', 'Django', 'REST API'],
        features: ['Contact database', 'Deal pipeline', 'Activity log'],
        previewComponent: CRMPreview
      },
      {
        title: 'Course Platform',
        description: 'Online learning with video lessons, quizzes, and progress tracking.',
        category: 'Education',
        categoryClass: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
        gradient: 'from-amber-500 to-orange-500',
        checkColor: 'text-amber-400',
        accentClass: 'bg-gradient-to-r from-transparent via-amber-500/50 to-transparent',
        buttonClass: 'bg-amber-500/20 text-amber-300 border border-amber-500/30 hover:bg-amber-500/30',
        stack: ['Vue.js', 'Django', 'Media'],
        features: ['Course builder', 'Student progress', 'Certificates'],
        previewComponent: CoursePreview
      },
      {
        title: 'Internal Tool',
        description: 'Custom business tool with forms, workflows, and data management.',
        category: 'Operations',
        categoryClass: 'bg-rose-500/20 text-rose-300 border border-rose-500/30',
        gradient: 'from-rose-500 to-pink-500',
        checkColor: 'text-rose-400',
        accentClass: 'bg-gradient-to-r from-transparent via-rose-500/50 to-transparent',
        buttonClass: 'bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30',
        stack: ['Vue.js', 'Django', 'Forms'],
        features: ['Custom forms', 'Approval flows', 'Reports'],
        previewComponent: InternalToolPreview
      }
    ]
    
    const updateScrollState = () => {
      if (!galleryRef.value) return
      const { scrollLeft, scrollWidth, clientWidth } = galleryRef.value
      canScrollPrev.value = scrollLeft > 10
      canScrollNext.value = scrollLeft < scrollWidth - clientWidth - 10
      
      // Update current page
      const cardWidth = 340 + 20 // card width + gap
      currentPage.value = Math.round(scrollLeft / (cardWidth * visibleCount.value))
    }
    
    const scrollPrev = () => {
      if (!galleryRef.value) return
      galleryRef.value.scrollBy({ left: -360, behavior: 'smooth' })
    }
    
    const scrollNext = () => {
      if (!galleryRef.value) return
      galleryRef.value.scrollBy({ left: 360, behavior: 'smooth' })
    }
    
    const scrollToIndex = (idx) => {
      if (!galleryRef.value) return
      const cardWidth = 340 + 20
      galleryRef.value.scrollTo({ left: idx * cardWidth * visibleCount.value, behavior: 'smooth' })
    }
    
    const handleGalleryKeyNav = (e) => {
      if (e.key === 'ArrowRight') {
        e.preventDefault()
        scrollNext()
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        scrollPrev()
      } else if (e.key === 'Home') {
        e.preventDefault()
        scrollToIndex(0)
      } else if (e.key === 'End') {
        e.preventDefault()
        scrollToIndex(Math.ceil(templates.length / visibleCount.value) - 1)
      }
    }
    
    const updateVisibleCount = () => {
      visibleCount.value = window.innerWidth >= 768 ? 3 : 1
    }
    
    onMounted(() => {
      updateVisibleCount()
      window.addEventListener('resize', updateVisibleCount)
      setTimeout(updateScrollState, 100)
    })
    
    onUnmounted(() => {
      window.removeEventListener('resize', updateVisibleCount)
    })
    
    return {
      galleryRef,
      templates,
      canScrollPrev,
      canScrollNext,
      currentPage,
      visibleCount,
      updateScrollState,
      scrollPrev,
      scrollNext,
      scrollToIndex,
      handleGalleryKeyNav
    }
  }
})
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
