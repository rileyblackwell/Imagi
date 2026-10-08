<!-- The sign-in and register pages: one centered card. How it looks is
     decided entirely by styles/auth.css. -->
<template>
  <div class="auth-theme auth-page">
    <div class="auth-backdrop" aria-hidden="true"></div>

    <header class="auth-header">
      <router-link to="/" class="auth-brand">{{ brand.name }}</router-link>
    </header>

    <main class="auth-shell">
      <section class="auth-card" :aria-labelledby="headingId">
        <div class="auth-heading">
          <h1 :id="headingId" class="auth-title">{{ title }}</h1>
          <p v-if="subtitle" class="auth-subtitle">{{ subtitle }}</p>
        </div>

        <router-view v-slot="{ Component }">
          <transition name="auth-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { brand } from '../brand'
import '../styles/auth.css'

const route = useRoute()
const headingId = 'auth-heading'
const title = computed(() => String(route.meta.title || ''))
const subtitle = computed(() => String(route.meta.subtitle || ''))
</script>
