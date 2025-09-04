<template>
  <!-- Enhanced sophisticated dark background with enhanced effects matching About page -->
  <div class="absolute inset-0 pointer-events-none overflow-hidden">
    <!-- Enhanced Pattern Overlay -->
    <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
    <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
    <div class="absolute inset-0 bg-gradient-to-br from-dark-950/10 via-dark-900 to-violet-950/10"></div>

    <!-- Enhanced Glowing Orbs Animation -->
    <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
    <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-float-delay"></div>

    <!-- Animated Lines and Particles -->
    <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
    <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
  </div>
</template>

<script setup lang="ts">
// Pure presentational background component
</script>

<style scoped>
/* Float animation for background orbs, matching global style if not already present */
@keyframes float { 0%, 100% { transform: translateY(0) } 50% { transform: translateY(-20px) } }
.animate-float { animation: float 15s ease-in-out infinite }
.animate-float-delay { animation: float 18s ease-in-out infinite reverse }

@keyframes pulse { 0%, 100% { opacity: 1 } 50% { opacity: 0.7 } }
.animate-pulse-slow { animation: pulse 3s ease-in-out infinite }

.delay-700 { animation-delay: 700ms }
</style>
