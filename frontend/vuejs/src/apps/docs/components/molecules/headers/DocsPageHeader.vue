<template>
  <div class="mb-12 md:mb-16">
    <!-- Animated badge matching homepage hero -->
    <div class="mb-8 inline-block animate-fade-in">
      <div class="group inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-400"></span>
        </span>
        <span class="text-sm font-medium text-white/70 tracking-wide uppercase">{{ badgeText }}</span>
      </div>
    </div>
    
    <!-- Hero title with gradient text -->
    <h1 class="text-3xl sm:text-4xl md:text-5xl font-semibold tracking-tight mb-6 leading-[1.15] animate-fade-in-up" style="animation-delay: 100ms">
      <span class="relative inline-block">
        <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
          {{ title }}
        </span>
      </span>
    </h1>
    
    <!-- Description -->
    <p class="text-lg sm:text-xl text-white/50 leading-relaxed max-w-3xl animate-fade-in-up" style="animation-delay: 200ms">
      {{ description }}
    </p>
    
    <!-- Elegant divider matching homepage -->
    <div class="relative py-6 md:py-8 animate-fade-in-up" style="animation-delay: 300ms">
      <div class="relative flex items-center justify-start">
        <div class="flex items-center gap-2">
          <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
          <div class="w-1.5 h-1.5 rounded-full bg-violet-400/70"></div>
          <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
        </div>
        <div class="flex-1 h-px bg-gradient-to-r from-white/[0.1] via-white/[0.08] to-transparent ml-4"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string;
  description: string;
  badgeText?: string;
}>(), {
  badgeText: 'DOCUMENTATION'
});
</script>

<style scoped>
/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out forwards;
}

/* Fade in up animation */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in-up {
  opacity: 0;
  animation: fade-in-up 0.8s ease-out forwards;
}

/* Gradient animation */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 4s ease infinite;
}
</style>
