<!-- Deploy Preview Section - Stylized deployment card -->
<template>
  <section class="py-20 md:py-32 px-6 sm:px-8 lg:px-12 relative overflow-hidden">
    <div class="max-w-5xl mx-auto relative">
      <!-- Section header -->
      <div class="text-center mb-12 md:mb-16">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-amber-500/10 rounded-full border border-amber-500/20 mb-6">
          <i class="fas fa-rocket text-xs text-amber-400/80"></i>
          <span class="text-sm font-medium text-amber-300/80">Coming Soon</span>
        </div>
        
        <h2 class="text-3xl sm:text-4xl md:text-5xl font-semibold text-white/90 mb-5 tracking-tight">
          One-Click <span class="bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">Deploy</span>
        </h2>
        <p class="text-lg text-white/50 max-w-2xl mx-auto leading-relaxed">
          Publish your app to the web instantly. Imagi handles hosting, SSL, and scaling — you just share your link.
        </p>
      </div>

      <!-- Deploy Card -->
      <div class="relative">
        <!-- Background glow -->
        <div class="absolute -inset-4 bg-gradient-to-r from-amber-600/10 via-orange-600/10 to-amber-600/10 rounded-3xl blur-2xl opacity-60"></div>
        
        <!-- Card container -->
        <div class="relative rounded-2xl border border-amber-500/20 bg-[#0a0a0f]/90 backdrop-blur-xl overflow-hidden">
          <!-- Accent line -->
          <div class="h-px w-full bg-gradient-to-r from-transparent via-amber-500/50 to-transparent"></div>
          
          <!-- Card header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-white/[0.06]">
            <div class="flex items-center gap-3">
              <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30">
                <i class="fas fa-cloud-upload-alt text-amber-400"></i>
              </div>
              <div>
                <h3 class="text-white/90 font-semibold">Deployment Dashboard</h3>
                <p class="text-xs text-white/40">Manage your live applications</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-1 bg-amber-500/20 border border-amber-500/30 rounded-lg text-xs text-amber-300 font-medium">
                Preview
              </span>
            </div>
          </div>
          
          <!-- Card content -->
          <div class="p-6 md:p-8">
            <div class="grid md:grid-cols-2 gap-6 md:gap-8">
              <!-- Left: Deployment info -->
              <div class="space-y-5">
                <!-- Domain section -->
                <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-xs text-white/40 uppercase tracking-wider font-medium">Domain</span>
                    <span class="flex items-center gap-1.5 text-[10px] text-emerald-400">
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      SSL Active
                    </span>
                  </div>
                  <div class="flex items-center gap-3">
                    <div class="flex-1 flex items-center gap-2 px-3 py-2.5 bg-[#0d0d12] rounded-lg border border-white/[0.08]">
                      <i class="fas fa-globe text-amber-400/60 text-sm"></i>
                      <span class="text-white/70 text-sm font-mono">my-awesome-app.imagi.app</span>
                    </div>
                    <button class="p-2.5 bg-white/[0.05] hover:bg-white/[0.08] rounded-lg border border-white/[0.08] transition-colors">
                      <i class="fas fa-copy text-white/40 text-sm"></i>
                    </button>
                  </div>
                  <p class="text-[11px] text-white/30 mt-2">
                    <i class="fas fa-info-circle mr-1"></i>
                    Custom domains available with Pro plan
                  </p>
                </div>
                
                <!-- Environment section -->
                <div class="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-xs text-white/40 uppercase tracking-wider font-medium">Environment</span>
                  </div>
                  <div class="grid grid-cols-2 gap-3">
                    <div class="p-3 bg-[#0d0d12] rounded-lg border border-white/[0.08]">
                      <div class="flex items-center gap-2 mb-1">
                        <i class="fas fa-code-branch text-violet-400/60 text-xs"></i>
                        <span class="text-[11px] text-white/50">Branch</span>
                      </div>
                      <span class="text-sm text-white/80 font-medium">main</span>
                    </div>
                    <div class="p-3 bg-[#0d0d12] rounded-lg border border-white/[0.08]">
                      <div class="flex items-center gap-2 mb-1">
                        <i class="fas fa-layer-group text-fuchsia-400/60 text-xs"></i>
                        <span class="text-[11px] text-white/50">Stack</span>
                      </div>
                      <span class="text-sm text-white/80 font-medium">Vue + Django</span>
                    </div>
                  </div>
                </div>
                
                <!-- Quick stats -->
                <div class="grid grid-cols-3 gap-3">
                  <div class="text-center p-3 bg-white/[0.02] rounded-lg border border-white/[0.06]">
                    <div class="text-lg font-semibold text-white/80">99.9%</div>
                    <div class="text-[10px] text-white/40">Uptime</div>
                  </div>
                  <div class="text-center p-3 bg-white/[0.02] rounded-lg border border-white/[0.06]">
                    <div class="text-lg font-semibold text-white/80">~50ms</div>
                    <div class="text-[10px] text-white/40">Response</div>
                  </div>
                  <div class="text-center p-3 bg-white/[0.02] rounded-lg border border-white/[0.06]">
                    <div class="text-lg font-semibold text-white/80">Auto</div>
                    <div class="text-[10px] text-white/40">Scaling</div>
                  </div>
                </div>
              </div>
              
              <!-- Right: Build logs -->
              <div class="p-4 rounded-xl bg-[#0d0d12] border border-white/[0.08]">
                <div class="flex items-center justify-between mb-4">
                  <span class="text-xs text-white/40 uppercase tracking-wider font-medium">Build Log</span>
                  <span class="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500/15 rounded text-[10px] text-emerald-400 font-medium">
                    <i class="fas fa-check text-[8px]"></i>
                    Success
                  </span>
                </div>
                
                <!-- Log entries -->
                <div class="space-y-2 font-mono text-[11px]">
                  <div class="flex items-start gap-2">
                    <span class="text-white/20 w-12 flex-shrink-0">12:34</span>
                    <span class="text-white/50"><span class="text-violet-400">→</span> Installing dependencies...</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="text-white/20 w-12 flex-shrink-0">12:35</span>
                    <span class="text-white/50"><span class="text-violet-400">→</span> Building Vue.js frontend...</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="text-white/20 w-12 flex-shrink-0">12:36</span>
                    <span class="text-white/50"><span class="text-violet-400">→</span> Configuring Django backend...</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="text-white/20 w-12 flex-shrink-0">12:37</span>
                    <span class="text-white/50"><span class="text-violet-400">→</span> Running migrations...</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="text-white/20 w-12 flex-shrink-0">12:38</span>
                    <span class="text-white/50"><span class="text-violet-400">→</span> Optimizing assets...</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="text-white/20 w-12 flex-shrink-0">12:39</span>
                    <span class="text-emerald-400"><span class="text-emerald-400">✓</span> Deployed successfully!</span>
                  </div>
                </div>
                
                <!-- Deploy time -->
                <div class="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between">
                  <span class="text-[10px] text-white/30">Total build time</span>
                  <span class="text-xs text-white/60 font-medium">~2 minutes</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Card footer -->
          <div class="px-6 py-4 border-t border-white/[0.06] bg-white/[0.01]">
            <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
              <p class="text-sm text-white/40 text-center sm:text-left">
                <i class="fas fa-clock text-amber-400/60 mr-2"></i>
                Imagi-hosted deployment launching Q1 2026
              </p>
              <router-link 
                to="/contact"
                class="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 rounded-lg text-white text-sm font-medium shadow-lg shadow-amber-500/25 hover:shadow-xl hover:shadow-amber-500/30 transition-all duration-300 hover:-translate-y-0.5"
              >
                <i class="fas fa-bell text-xs"></i>
                Join the Waitlist
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Feature highlights -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-10">
        <div v-for="(feature, idx) in features" :key="idx"
             class="flex items-center gap-3 p-4 rounded-xl bg-white/[0.02] border border-white/[0.06]">
          <div class="flex items-center justify-center w-9 h-9 rounded-lg"
               :class="feature.iconBg">
            <i :class="[feature.icon, 'text-sm', feature.iconColor]"></i>
          </div>
          <div>
            <div class="text-sm text-white/80 font-medium">{{ feature.title }}</div>
            <div class="text-[11px] text-white/40">{{ feature.subtitle }}</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'DeployPreviewSection',
  setup() {
    const features = [
      {
        icon: 'fas fa-bolt',
        iconBg: 'bg-amber-500/15',
        iconColor: 'text-amber-400',
        title: 'Instant Deploy',
        subtitle: 'One click to go live'
      },
      {
        icon: 'fas fa-shield-alt',
        iconBg: 'bg-emerald-500/15',
        iconColor: 'text-emerald-400',
        title: 'Auto SSL',
        subtitle: 'HTTPS by default'
      },
      {
        icon: 'fas fa-chart-line',
        iconBg: 'bg-violet-500/15',
        iconColor: 'text-violet-400',
        title: 'Analytics',
        subtitle: 'Built-in insights'
      },
      {
        icon: 'fas fa-expand-arrows-alt',
        iconBg: 'bg-fuchsia-500/15',
        iconColor: 'text-fuchsia-400',
        title: 'Auto Scale',
        subtitle: 'Handle any traffic'
      }
    ]
    
    return {
      features
    }
  }
})
</script>

<style scoped>
</style>
