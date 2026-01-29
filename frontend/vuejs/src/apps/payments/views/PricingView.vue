<template>
  <PaymentLayout>
    <div class="pricing-view min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Minimal Background Effects (matching home page) -->
      <div class="fixed inset-0 pointer-events-none -z-10">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern for texture -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
        
        <!-- Subtle ambient background -->
        <div class="absolute top-1/2 left-1/2 w-[800px] h-[400px] bg-gradient-radial from-gray-200/30 dark:from-white/[0.02] via-transparent to-transparent rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10 max-w-5xl mx-auto px-6 sm:px-8 lg:px-12 pt-24 pb-24 md:pt-32 md:pb-32">
        <!-- Header Section (matching home page style) -->
        <div class="mb-16 md:mb-20 text-center">
          <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">
            Pricing
          </p>
          <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
            Simple, transparent pricing
          </h1>
          <p class="text-xl text-gray-500 dark:text-white/60 max-w-3xl mx-auto transition-colors duration-300">
            Pay only for what you use. No subscriptions, no hidden fees. Add credits to your account and they're automatically deducted as you build.
          </p>
        </div>
        
        <!-- Pricing Section -->
        <div class="mb-12">
          <ModelPricingSection :animate="false" />
        </div>

        <!-- CTA Button to Checkout -->
        <div class="text-center">
          <router-link 
            to="/payments/checkout"
            class="inline-flex items-center gap-3 px-8 py-4 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-2xl font-medium text-lg transition-all duration-200 active:scale-[0.98]"
          >
            <span>Purchase Credits</span>
            <i class="fas fa-arrow-right text-sm"></i>
          </router-link>
        </div>
      </div>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import PaymentLayout from '../layouts/PaymentLayout.vue'
import ModelPricingSection from '../components/organisms/sections/ModelPricingSection/ModelPricingSection.vue'
</script>

<style scoped>
/* Minimal, clean styling matching home page */
</style>
