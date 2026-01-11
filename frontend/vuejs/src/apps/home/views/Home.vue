<!-- Home landing page -->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-[#050509] relative overflow-hidden">
      <!-- Ultra Premium Background System -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Deep space base with richer gradients -->
        <div class="absolute inset-0 bg-gradient-to-b from-[#08081a] via-[#050509] to-[#020204]"></div>
        
        <!-- Animated mesh gradient layer - enhanced -->
        <div class="absolute inset-0 opacity-95">
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(124,58,237,0.22),transparent_50%)] animate-pulse-slow"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_90%_70%_at_90%_20%,rgba(139,92,246,0.15),transparent_45%)] animate-drift"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_5%_60%,rgba(217,70,239,0.10),transparent_40%)] animate-drift-reverse"></div>
          <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_100%,rgba(79,70,229,0.12),transparent_50%)]"></div>
        </div>
        
        <!-- Refined grid pattern - more subtle -->
        <div class="absolute inset-0 opacity-[0.025]" style="background-image: linear-gradient(rgba(139,92,246,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.4) 1px, transparent 1px); background-size: 80px 80px;"></div>
        
        <!-- Premium noise texture - refined -->
        <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 512 512%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.7%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
        
        <!-- Northern lights aurora - enhanced -->
        <div class="absolute top-0 left-0 right-0 h-[800px] overflow-hidden">
          <div class="absolute inset-x-[5%] top-0 h-full opacity-45 animate-aurora">
            <div class="absolute inset-0 bg-gradient-to-b from-violet-500/30 via-fuchsia-500/15 to-transparent blur-[140px] transform rotate-[-2deg]"></div>
          </div>
          <div class="absolute inset-x-[15%] top-0 h-[600px] opacity-30 animate-aurora-delayed">
            <div class="absolute inset-0 bg-gradient-to-b from-cyan-400/15 via-violet-400/10 to-transparent blur-[120px] transform rotate-[1deg]"></div>
          </div>
        </div>
        
        <!-- Floating luminous orbs - refined positions and colors -->
        <div class="absolute top-[10%] right-[5%] w-[700px] h-[700px] rounded-full bg-gradient-to-br from-violet-600/10 via-indigo-600/6 to-transparent blur-[180px] animate-float-slow"></div>
        <div class="absolute bottom-[10%] left-[0%] w-[600px] h-[600px] rounded-full bg-gradient-to-tr from-fuchsia-600/8 via-purple-600/5 to-transparent blur-[160px] animate-float-delayed"></div>
        <div class="absolute top-[50%] right-[20%] w-[400px] h-[400px] rounded-full bg-gradient-to-bl from-amber-500/6 via-rose-500/4 to-transparent blur-[120px] animate-float-reverse"></div>
        <div class="absolute top-[30%] left-[10%] w-[350px] h-[350px] rounded-full bg-gradient-to-br from-cyan-500/5 to-transparent blur-[100px] animate-float-gentle"></div>
        
        <!-- Additional subtle accent orbs -->
        <div class="absolute top-[70%] left-[40%] w-[300px] h-[300px] rounded-full bg-gradient-to-br from-emerald-500/4 to-transparent blur-[100px] animate-float-slow" style="animation-delay: -10s;"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <HeroSection />
        
        <!-- Elegant Divider with Glow - Enhanced -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative flex items-center justify-center">
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.12] to-transparent"></div>
            <div class="mx-10 flex items-center gap-4">
              <div class="w-1.5 h-1.5 rounded-full bg-violet-400/40 animate-pulse"></div>
              <div class="relative w-2.5 h-2.5">
                <div class="absolute inset-0 rounded-full bg-gradient-to-br from-violet-400 to-fuchsia-400 opacity-70 animate-pulse"></div>
                <div class="absolute -inset-1.5 rounded-full bg-violet-400/25 blur-md"></div>
              </div>
              <div class="w-1.5 h-1.5 rounded-full bg-violet-400/40 animate-pulse"></div>
            </div>
            <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.12] to-transparent"></div>
          </div>
        </div>
        
        <!-- Product Tour Section -->
        <ProductTourSection />
        
        <!-- Refined Divider - Fuchsia accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-fuchsia-500/15 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- Features Section -->
        <FeaturesSection />
        
        <!-- Refined Divider - Violet accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-violet-500/15 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- Template Gallery Section -->
        <TemplateGallerySection />
        
        <!-- Refined Divider - Emerald accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-500/12 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- How It Works Section -->
        <HowItWorksSection />
        
        <!-- Refined Divider - Blue accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/12 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- Deploy Preview Section -->
        <DeployPreviewSection />
        
        <!-- Refined Divider - Amber accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-amber-500/12 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- Stats Section -->
        <StatsSection />
        
        <!-- Refined Divider - Rose accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-rose-500/12 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- Testimonials Section -->
        <TestimonialsSection />
        
        <!-- Refined Divider - Cyan accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/12 to-transparent blur-sm"></div>
          </div>
        </div>
        
        <!-- FAQ Section -->
        <FAQSection />
        
        <!-- Final Divider - Gradient accent -->
        <div class="relative py-12 md:py-16 max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
          <div class="relative h-px">
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/[0.10] to-transparent"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-violet-500/10 via-fuchsia-500/15 to-violet-500/10 blur-sm"></div>
          </div>
        </div>
        
        <!-- CTA Section -->
        <CTASection 
          icon="fas fa-rocket" 
          title="Build Your App" 
          highlightedText="Today" 
          description="Transform your ideas into production-ready full-stack web applications. No coding required — just describe what you want and"
          highlightedStat="start building for free"
          descriptionSuffix="."
          primaryButtonText="Start Building Free"
          primaryButtonTo="/products/oasis/builder/dashboard"
          :showSecondaryButton="true"
          secondaryButtonText="Join Deploy Waitlist"
          secondaryButtonTo="/contact"
        />
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { 
  HeroSection,
  FeaturesSection,
  HowItWorksSection,
  StatsSection,
  TestimonialsSection,
  CTASection,
  ProductTourSection,
  DeployPreviewSection,
  TemplateGallerySection,
  FAQSection
} from '@/apps/home/components/organisms/sections'

export default defineComponent({
  name: 'HomePage',
  components: {
    DefaultLayout,
    HeroSection,
    FeaturesSection,
    HowItWorksSection,
    StatsSection,
    TestimonialsSection,
    CTASection,
    ProductTourSection,
    DeployPreviewSection,
    TemplateGallerySection,
    FAQSection
  }
})
</script>

<style scoped>
/* Slow pulse for mesh gradient */
@keyframes pulse-slow {
  0%, 100% {
    opacity: 0.9;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.02);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 12s ease-in-out infinite;
}

/* Drift animation for gradients */
@keyframes drift {
  0%, 100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(2%, 1%);
  }
  50% {
    transform: translate(0, 2%);
  }
  75% {
    transform: translate(-2%, 0);
  }
}

@keyframes drift-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  25% {
    transform: translate(-1%, 2%);
  }
  50% {
    transform: translate(1%, 0);
  }
  75% {
    transform: translate(0, -1%);
  }
}

.animate-drift {
  animation: drift 30s ease-in-out infinite;
}

.animate-drift-reverse {
  animation: drift-reverse 35s ease-in-out infinite;
}

/* Enhanced Aurora animation */
@keyframes aurora {
  0%, 100% {
    transform: translateX(-8%) scaleY(1) rotate(-2deg);
    opacity: 0.4;
  }
  33% {
    transform: translateX(4%) scaleY(1.05) rotate(1deg);
    opacity: 0.55;
  }
  66% {
    transform: translateX(8%) scaleY(0.95) rotate(-1deg);
    opacity: 0.45;
  }
}

@keyframes aurora-delayed {
  0%, 100% {
    transform: translateX(5%) scaleY(1) rotate(1deg);
    opacity: 0.35;
  }
  50% {
    transform: translateX(-5%) scaleY(1.08) rotate(-2deg);
    opacity: 0.5;
  }
}

.animate-aurora {
  animation: aurora 18s ease-in-out infinite;
}

.animate-aurora-delayed {
  animation: aurora-delayed 22s ease-in-out infinite;
  animation-delay: -8s;
}

/* Float animations - enhanced */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  20% {
    transform: translate(25px, -15px) scale(1.02);
  }
  40% {
    transform: translate(10px, 20px) scale(1.01);
  }
  60% {
    transform: translate(-20px, 10px) scale(0.99);
  }
  80% {
    transform: translate(-10px, -20px) scale(1.01);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(-30px, -25px) scale(1.03);
  }
  66% {
    transform: translate(15px, 15px) scale(0.98);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(15px, 20px) scale(1.02);
  }
  50% {
    transform: translate(25px, -10px) scale(0.98);
  }
  75% {
    transform: translate(-5px, 15px) scale(1.01);
  }
}

@keyframes float-gentle {
  0%, 100% {
    transform: translate(0, 0);
    opacity: 0.6;
  }
  50% {
    transform: translate(-15px, -20px);
    opacity: 0.8;
  }
}

.animate-float-slow {
  animation: float-slow 28s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 32s ease-in-out infinite;
  animation-delay: -6s;
}

.animate-float-reverse {
  animation: float-reverse 24s ease-in-out infinite;
  animation-delay: -12s;
}

.animate-float-gentle {
  animation: float-gentle 20s ease-in-out infinite;
  animation-delay: -4s;
}

/* Custom scrollbar - refined */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.01);
}

:deep(::-webkit-scrollbar-thumb) {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.35), rgba(217, 70, 239, 0.25));
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.5), rgba(217, 70, 239, 0.4));
}
</style>
