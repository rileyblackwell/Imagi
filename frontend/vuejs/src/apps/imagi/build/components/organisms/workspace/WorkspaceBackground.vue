<template>
  <!-- Premium Background System - Matching Home Landing Page -->
  <div class="fixed inset-0 pointer-events-none overflow-hidden">
    <!-- Base gradient mesh -->
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(120,119,198,0.15),transparent_50%)]"></div>
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_80%_50%,rgba(78,68,206,0.08),transparent_40%)]"></div>
    <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_10%_80%,rgba(167,139,250,0.06),transparent_35%)]"></div>
    
    <!-- Subtle grain texture -->
    <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
    
    <!-- Animated aurora effect -->
    <div class="absolute top-0 left-1/4 right-1/4 h-[600px] opacity-30">
      <div class="absolute inset-0 bg-gradient-to-b from-violet-500/20 via-fuchsia-500/10 to-transparent blur-[100px] animate-aurora"></div>
    </div>
    
    <!-- Floating orbs -->
    <div class="absolute top-[20%] right-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-600/8 to-violet-600/4 blur-[120px] animate-float-slow"></div>
    <div class="absolute bottom-[10%] left-[5%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-fuchsia-600/6 to-purple-600/3 blur-[100px] animate-float-delayed"></div>
    <div class="absolute top-[60%] right-[30%] w-[300px] h-[300px] rounded-full bg-gradient-to-bl from-amber-500/4 to-orange-500/2 blur-[80px] animate-float-reverse"></div>
  </div>
</template>

<script setup lang="ts">
// Premium background component matching home landing page design
</script>

<style scoped>
/* Aurora animation */
@keyframes aurora {
  0%, 100% {
    transform: translateX(-10%) rotate(-2deg);
    opacity: 0.3;
  }
  50% {
    transform: translateX(10%) rotate(2deg);
    opacity: 0.4;
  }
}

.animate-aurora {
  animation: aurora 20s ease-in-out infinite;
}

/* Float animations */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-25px, -30px) scale(1.03);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, 15px);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 30s ease-in-out infinite;
  animation-delay: -5s;
}

.animate-float-reverse {
  animation: float-reverse 20s ease-in-out infinite;
  animation-delay: -10s;
}
</style>
