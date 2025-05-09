<template>
  <div class="mt-12">
    <h2 class="text-2xl font-bold text-white mb-6">{{ title }}</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <router-link 
        v-for="link in links" 
        :key="link.to"
        :to="link.to" 
        class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
      >
        <div class="flex items-start space-x-4">
          <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
            <i :class="[link.icon, 'text-xl text-primary-400']"></i>
          </div>
          <div>
            <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">{{ link.title }}</h3>
            <p class="text-gray-400 text-sm">{{ link.description }}</p>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
interface DocLink {
  title: string;
  description: string;
  to: string;
  icon: string;
}

defineProps<{
  title?: string;
  links: DocLink[];
}>();
</script> 