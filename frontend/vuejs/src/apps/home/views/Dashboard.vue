<template>
  <DashboardLayout>
    <!-- Custom Sidebar Content with modern design -->
    <template #sidebar-content="{ isSidebarCollapsed }">
      <div class="p-4">
        <div class="mb-6">
          <div class="text-xs font-medium text-white/40 uppercase tracking-wider mb-3" v-if="!isSidebarCollapsed">
            Navigation
          </div>
          <ul class="space-y-1">
            <li v-for="item in navigationItems" :key="item.name">
              <router-link
                :to="item.to"
                class="group block px-3 py-2 rounded-xl transition-all duration-200 cursor-pointer"
                :class="[
                  isActiveRoute(item.to, item.exact) 
                    ? 'bg-gradient-to-r from-violet-500/15 to-fuchsia-500/15 text-violet-300 border border-violet-400/20' 
                    : 'hover:bg-white/[0.05] text-white/60 hover:text-white/90 border border-transparent hover:border-white/[0.08]'
                ]"
              >
                <div class="flex items-center">
                  <i :class="[item.icon, isSidebarCollapsed ? '' : 'mr-3', 'w-4 text-center text-sm']"></i>
                  <span v-if="!isSidebarCollapsed" class="text-sm font-medium">{{ item.name }}</span>
                </div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </template>

    <!-- Premium Main Content - Matching Home Page -->
    <div class="min-h-screen bg-[#050508] relative overflow-hidden">
      <!-- Premium Background System -->
      <div class="fixed inset-0 pointer-events-none">
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

      <!-- Content Container -->
      <div class="relative z-10">
        <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12 sm:py-20">
          <!-- Premium Header Section - Matching Home Page -->
          <div class="pt-16 pb-16">
            <div class="text-center">
              <!-- Animated badge matching home page -->
              <div class="mb-8 inline-block animate-fade-in">
                <div class="group inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-400"></span>
                  </span>
                  <span class="text-sm font-medium text-white/70 tracking-wide">Dashboard</span>
                </div>
              </div>
              
              <!-- Title with gradient text -->
              <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight mb-6 leading-[1.1]">
                <span class="block text-white/90">Welcome back,</span>
                <span class="block mt-2">
                  <span class="relative inline-block">
                    <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                      {{ authStore.user?.name || 'Developer' }}! 👋
                    </span>
                    <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
                  </span>
                </span>
              </h1>
              
              <!-- Description -->
              <p class="text-lg sm:text-xl text-white/50 mb-10 max-w-2xl mx-auto leading-relaxed">
                Your AI-powered app builder dashboard. Create, manage, and deploy applications with ease.
              </p>
            </div>
            
            <!-- Elegant Divider -->
            <div class="relative py-8 md:py-12">
              <div class="relative flex items-center justify-center">
                <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
                <div class="mx-6 flex items-center gap-2">
                  <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
                  <div class="w-1.5 h-1.5 rounded-full bg-violet-400/70"></div>
                  <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
                </div>
                <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
              </div>
            </div>
          </div>

          <!-- Stats Overview with Premium Glass Cards -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-16">
            <div 
              v-for="stat in statsData" 
              :key="stat.title"
              class="group relative transform transition-all duration-300 hover:-translate-y-1"
            >
              <!-- Background glow -->
              <div class="absolute -inset-0.5 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                :class="{
                  'bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20': stat.color === 'primary',
                  'bg-gradient-to-r from-green-600/20 via-emerald-600/20 to-green-600/20': stat.color === 'success',
                  'bg-gradient-to-r from-yellow-600/20 via-amber-600/20 to-yellow-600/20': stat.color === 'warning',
                  'bg-gradient-to-r from-blue-600/20 via-sky-600/20 to-blue-600/20': stat.color === 'info'
                }"
              ></div>
              
              <!-- Premium glass card -->
              <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/90 backdrop-blur-xl overflow-hidden h-full transition-all duration-300 hover:border-white/[0.12]">
                <!-- Accent line -->
                <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent to-transparent"
                  :class="{
                    'via-violet-500/50': stat.color === 'primary',
                    'via-green-500/50': stat.color === 'success',
                    'via-yellow-500/50': stat.color === 'warning',
                    'via-blue-500/50': stat.color === 'info'
                  }"
                ></div>
                
                <!-- Decorative blur element -->
                <div class="absolute -bottom-16 -right-16 w-32 h-32 rounded-full blur-2xl pointer-events-none group-hover:opacity-80 transition-opacity duration-500"
                  :class="{
                    'bg-violet-500/5': stat.color === 'primary',
                    'bg-green-500/5': stat.color === 'success',
                    'bg-yellow-500/5': stat.color === 'warning',
                    'bg-blue-500/5': stat.color === 'info'
                  }"
                ></div>
                
                <div class="relative z-10 p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-sm font-medium text-white/40 uppercase tracking-wider">{{ stat.title }}</h3>
                    <div class="w-10 h-10 rounded-xl flex items-center justify-center border transition-all duration-300 group-hover:scale-110"
                      :class="{
                        'bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border-violet-500/20': stat.color === 'primary',
                        'bg-gradient-to-br from-green-500/20 to-emerald-500/20 border-green-500/20': stat.color === 'success',
                        'bg-gradient-to-br from-yellow-500/20 to-amber-500/20 border-yellow-500/20': stat.color === 'warning',
                        'bg-gradient-to-br from-blue-500/20 to-sky-500/20 border-blue-500/20': stat.color === 'info'
                      }"
                    >
                      <i :class="[
                        stat.icon, 
                        'text-sm',
                        {
                          'text-violet-300': stat.color === 'primary',
                          'text-green-300': stat.color === 'success',
                          'text-yellow-300': stat.color === 'warning',
                          'text-blue-300': stat.color === 'info'
                        }
                      ]"
                      ></i>
                    </div>
                  </div>
                  <div class="text-2xl font-bold text-white/90 mb-1">{{ stat.value }}</div>
                  <div v-if="stat.trend" class="text-xs font-medium"
                    :class="{
                      'text-green-400': stat.trend.startsWith('+'),
                      'text-red-400': stat.trend.startsWith('-'),
                      'text-white/40': !stat.trend.startsWith('+') && !stat.trend.startsWith('-')
                    }"
                  >
                    {{ stat.trend }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Enhanced Main Grid with Modern Glassmorphism -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 lg:gap-10">
            <!-- Projects & Activity Column -->
            <div class="lg:col-span-2 space-y-10">
              <!-- Recent Projects -->
              <div class="group relative">
                <!-- Background glow -->
                <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
                
                <!-- Premium glass card -->
                <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden transition-all duration-300 hover:border-white/[0.12]">
                  <!-- Accent line -->
                  <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                  
                  <!-- Decorative elements -->
                  <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Header section -->
                    <div class="flex items-center justify-between mb-6">
                      <div class="flex items-center gap-3">
                        <!-- Icon -->
                        <div class="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                          <svg class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                          </svg>
                        </div>
                        <h2 class="text-xl font-semibold text-white/90">Recent Projects</h2>
                      </div>
                      <router-link 
                        to="/products/oasis/builder/projects"
                        class="inline-flex items-center px-4 py-2 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] hover:border-violet-400/30 text-white/60 hover:text-white/90 rounded-xl transition-all duration-200 text-sm font-medium"
                      >
                        View All
                        <svg class="w-3 h-3 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                      </router-link>
                    </div>
                    
                    <!-- Separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-6"></div>
                    
                    <div class="space-y-5">
                      <div 
                        v-for="project in recentProjects"
                        :key="project.id"
                        class="group/card relative transform transition-all duration-300"
                      >
                        <!-- Background glow -->
                        <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-2xl blur-lg opacity-0 group-hover/card:opacity-100 transition-opacity duration-500"></div>
                        
                        <!-- Premium glass card -->
                        <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/90 backdrop-blur-xl overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-white/[0.12] hover:-translate-y-1 cursor-pointer"
                             @click="goToProject(project.id)">
                          <!-- Accent line -->
                          <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                          
                          <!-- Decorative blur element -->
                          <div class="absolute -bottom-16 -right-16 w-32 h-32 bg-violet-500/5 rounded-full blur-2xl pointer-events-none"></div>
                          
                          <!-- Content -->
                          <div class="relative z-10 p-5 flex flex-col h-full">
                            <!-- Project header -->
                            <div class="flex items-center gap-3 mb-4">
                              <!-- Icon -->
                              <div class="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                                <svg class="w-5 h-5 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                </svg>
                              </div>
                              
                              <!-- Project name -->
                              <div class="flex-1 min-w-0">
                                <h3 class="text-base font-semibold text-white/90 truncate leading-tight">{{ project.name }}</h3>
                                <div class="flex items-center text-xs text-white/40 mt-1">
                                  <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                  </svg>
                                  {{ formatDate(project.updated_at) }}
                                </div>
                              </div>
                            </div>
                            
                            <!-- Separator -->
                            <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-4"></div>
                            
                            <!-- Project description -->
                            <div class="mb-4 flex-grow">
                              <p class="text-white/50 text-sm line-clamp-2 leading-relaxed">
                                {{ project.description || 'No description provided' }}
                              </p>
                            </div>
                            
                            <!-- Footer section -->
                            <div class="mt-auto">
                              <!-- Open button -->
                              <div class="w-full inline-flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 hover:from-violet-500/20 hover:to-fuchsia-500/20 border border-violet-500/20 hover:border-violet-400/40 text-white/90 rounded-xl transition-all duration-300 text-sm font-medium">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                                Open Project
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div v-if="!recentProjects.length" class="flex flex-col items-center justify-center py-12">
                        <div class="w-16 h-16 bg-white/[0.05] border border-white/[0.08] rounded-2xl flex items-center justify-center mb-4">
                          <svg class="w-8 h-8 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                          </svg>
                        </div>
                        <h3 class="text-lg font-medium text-white/90 mb-2">No projects yet</h3>
                        <p class="text-white/40 text-center max-w-md mb-4 text-sm">Create your first project to start building with Imagi</p>
                        
                        <!-- Directional hint -->
                        <div class="flex items-center text-violet-400 text-sm">
                          <svg class="w-4 h-4 mr-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                          </svg>
                          <span>Get started with a new project</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Payment Transactions -->
              <div class="group relative">
                <!-- Background glow -->
                <div class="absolute -inset-1 bg-gradient-to-r from-green-600/20 via-emerald-600/20 to-green-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
                
                <!-- Premium glass card -->
                <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden transition-all duration-300 hover:border-white/[0.12]">
                  <!-- Accent line -->
                  <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-green-500/50 to-transparent"></div>
                  
                  <!-- Decorative elements -->
                  <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-green-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  <div class="absolute -top-20 -left-20 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Header section -->
                    <div class="flex items-center justify-between mb-6">
                      <div class="flex items-center gap-3">
                        <!-- Icon -->
                        <div class="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                          <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                          </svg>
                        </div>
                        <h2 class="text-xl font-semibold text-white/90">Payment Transactions</h2>
                      </div>
                      <router-link 
                        :to="{ name: 'PaymentHistory' }"
                        class="inline-flex items-center px-4 py-2 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] hover:border-green-400/30 text-white/60 hover:text-white/90 rounded-xl transition-all duration-200 text-sm font-medium"
                      >
                        View All
                        <svg class="w-3 h-3 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                      </router-link>
                    </div>
                    
                    <!-- Separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-6"></div>
                    
                    <div class="space-y-3">
                      <div v-if="recentTransactions.length" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-white/[0.05]">
                          <thead>
                            <tr>
                              <th class="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">Date</th>
                              <th class="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">Model</th>
                              <th class="px-4 py-3 text-left text-xs font-medium text-white/40 uppercase tracking-wider">Request Type</th>
                              <th class="px-4 py-3 text-right text-xs font-medium text-white/40 uppercase tracking-wider">Amount</th>
                            </tr>
                          </thead>
                          <tbody class="divide-y divide-white/[0.05]">
                            <tr v-for="tx in recentTransactions" :key="tx.id" class="hover:bg-white/[0.02] transition-colors">
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-white/60">{{ formatDate(tx.created_at) }}</td>
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-white/60">{{ tx.model || '—' }}</td>
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-white/60">{{ mapRequestType(tx.request_type) }}</td>
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-right">
                                <span :class="tx.amount < 0 ? 'text-red-400' : 'text-green-400'">
                                  {{ formatTransactionAmount(Math.abs(tx.amount)) }}
                                </span>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                      <div v-else class="flex flex-col items-center justify-center py-12">
                        <div class="w-16 h-16 bg-white/[0.05] border border-white/[0.08] rounded-2xl flex items-center justify-center mb-4">
                          <svg class="w-8 h-8 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                          </svg>
                        </div>
                        <h3 class="text-lg font-medium text-white/90 mb-2">No transactions yet</h3>
                        <p class="text-white/40 text-center max-w-md mb-4 text-sm">Add funds to your account to see transactions here</p>
                        
                        <!-- Directional hint -->
                        <div class="flex items-center text-green-400 text-sm">
                          <svg class="w-4 h-4 mr-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                          </svg>
                          <span>Get started by adding funds</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions & Resources Column -->
            <div class="space-y-10">
              <!-- Quick Actions -->
              <div class="group relative">
                <!-- Background glow -->
                <div class="absolute -inset-1 bg-gradient-to-r from-orange-600/20 via-amber-600/20 to-orange-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
                
                <!-- Premium glass card -->
                <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden transition-all duration-300 hover:border-white/[0.12]">
                  <!-- Accent line -->
                  <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-orange-500/50 to-transparent"></div>
                  
                  <!-- Decorative elements -->
                  <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-orange-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  <div class="absolute -top-20 -left-20 w-32 h-32 bg-amber-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Header section -->
                    <div class="flex items-center gap-3 mb-6">
                      <!-- Icon -->
                      <div class="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                      </div>
                      <h2 class="text-xl font-semibold text-white/90">Quick Actions</h2>
                    </div>
                    
                    <!-- Separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-6"></div>
                    
                    <div class="space-y-3">
                      <button
                        v-for="action in quickActions"
                        :key="action.title"
                        @click="$router.push(action.route)"
                        class="w-full flex items-center justify-between p-4 bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] hover:border-orange-400/30 rounded-xl transition-all duration-300 transform hover:-translate-y-0.5 group/action"
                      >
                        <div class="flex items-center gap-3">
                          <div class="w-9 h-9 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center group-hover/action:scale-110 transition-all duration-300">
                            <i :class="[action.icon, 'text-orange-400 text-sm']"></i>
                          </div>
                          <span class="font-medium text-white/90 group-hover/action:text-orange-400 transition-colors">{{ action.title }}</span>
                        </div>
                        <svg class="w-4 h-4 text-white/30 group-hover/action:text-orange-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Resources -->
              <div class="group relative">
                <!-- Background glow -->
                <div class="absolute -inset-1 bg-gradient-to-r from-blue-600/20 via-sky-600/20 to-blue-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
                
                <!-- Premium glass card -->
                <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden transition-all duration-300 hover:border-white/[0.12]">
                  <!-- Accent line -->
                  <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"></div>
                  
                  <!-- Decorative elements -->
                  <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  <div class="absolute -top-20 -left-20 w-32 h-32 bg-sky-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Header section -->
                    <div class="flex items-center gap-3 mb-6">
                      <!-- Icon -->
                      <div class="w-10 h-10 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                        </svg>
                      </div>
                      <h2 class="text-xl font-semibold text-white/90">Resources</h2>
                    </div>
                    
                    <!-- Separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-6"></div>
                    
                    <div class="space-y-3">
                      <template v-for="resource in resourceLinks" :key="resource.title">
                        <router-link 
                          v-if="resource.url.startsWith('/')"
                          :to="resource.url" 
                          class="block p-4 bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.08] hover:border-blue-400/30 rounded-xl transition-all duration-300 transform hover:-translate-y-0.5 group/resource"
                        >
                          <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                              <div class="w-9 h-9 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center group-hover/resource:scale-110 transition-all duration-300">
                                <i :class="[resource.icon, 'text-blue-400 text-sm']"></i>
                              </div>
                              <div>
                                <h3 class="text-white/90 group-hover/resource:text-blue-400 transition-colors font-medium text-sm">{{ resource.title }}</h3>
                                <p class="text-xs text-white/40 mt-0.5">{{ resource.description }}</p>
                              </div>
                            </div>
                            <svg class="w-4 h-4 text-white/30 group-hover/resource:text-blue-400 transition-colors flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                          </div>
                        </router-link>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
// --- Request Type Mapping Helper ---
function mapRequestType(type) {
  if (!type || typeof type !== 'string') return '—';
  const normalized = type.replace(/_/g, ' ').toLowerCase().trim();
  if (['build template'].includes(normalized)) return 'Build Template';
  if (['build stylesheet'].includes(normalized)) return 'Build Stylesheet';
  if (['chat'].includes(normalized)) return 'Chat';
  // fallback: capitalize each word
  return normalized.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import { useAuthStore } from '@/apps/auth/stores'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useNotification } from '@/shared/composables/useNotification'

// Store initialization
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const projectStore = useProjectStore()
const paymentsStore = usePaymentStore()
const { showNotification } = useNotification()

// Reactive state
const recentProjects = ref([])
const recentTransactions = ref([])
const stats = ref(null)

// Stats data with computed values
const statsData = computed(() => [
  { 
    title: 'Total Projects', 
    value: projectStore.projects?.length || 0, 
    icon: 'fas fa-folder', 
    trend: '', 
    color: 'primary' 
  },
  { 
    title: 'Account Balance', 
    value: `$${typeof paymentsStore.balance === 'number' ? paymentsStore.balance.toFixed(2) : '0.00'}`, 
    icon: 'fas fa-money-bill-wave', 
    trend: '', 
    color: 'warning' 
  }
])

// Navigation configuration
const navigationItems = [
  { name: 'Dashboard', to: '/dashboard', icon: 'fas fa-home', exact: true },
  { name: 'Oasis Projects', to: '/products/oasis/builder/projects', icon: 'fas fa-folder', exact: true },
  { name: 'Create Project', to: '/products/oasis/builder/dashboard', icon: 'fas fa-plus-circle', exact: true },
  { name: 'Buy AI Credits', to: '/payments/checkout', icon: 'fas fa-money-bill-wave', exact: true }
]

// Quick actions configuration
const quickActions = [
  { 
    title: 'New Project', 
    icon: 'fas fa-plus', 
    route: { name: 'builder-dashboard' } 
  },
  { 
    title: 'Buy Credits', 
    icon: 'fas fa-money-bill-wave', 
    route: { path: '/payments/checkout' } 
  },
  { 
    title: 'Account Settings', 
    icon: 'fas fa-cog', 
    route: { name: 'settings' } 
  }
]

// Resources links
const resourceLinks = [
  { title: 'Documentation', icon: 'fas fa-book', url: '/docs', description: 'Learn how to use Imagi Oasis' },
  { title: 'Contact', icon: 'fas fa-envelope', url: '/contact', description: 'Get in touch with our team' },
  { title: 'Community', icon: 'fas fa-users', url: 'https://discord.gg/imagioasis', description: 'Join our Discord community' }
]

// Check if a route is active (exact match or starts with path for nested routes)
const isActiveRoute = (path, exact) => {
  if (exact) {
    return route.path === path
  }
  return route.path.startsWith(path)
}

// Format date helper
function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}

// Add navigation method
const goToProject = (id) => {
  router.push({
    name: 'builder-workspace',
    params: { projectId: String(id) }
  }).catch(err => {
    console.error('Navigation error:', err)
    showNotification({
      type: 'error',
      message: 'Unable to load project details'
    })
  })
}

// Enhanced data fetching
async function fetchDashboardData() {
  try {
    if (projectStore.fetchProjects) {
      // Only fetch projects if not available or stale (older than 5 minutes)
      const needsProjectsRefresh = !projectStore.projects || 
        projectStore.projects.length === 0 || 
        !projectStore.lastFetch || 
        (Date.now() - projectStore.lastFetch.getTime()) > 5 * 60 * 1000
      
      if (needsProjectsRefresh) {
        await projectStore.fetchProjects(false) // Don't force, let store handle caching
      }
      
      recentProjects.value = projectStore.projects?.slice(0, 5) || []
    }
    
    // Fetch payments data - only fetch balance if not available or stale
    try {
      // Only fetch balance if it's not available or stale (older than 5 minutes)
      const needsBalanceRefresh = paymentsStore.balance === null || 
        paymentsStore.balance === 0 || 
        !paymentsStore.lastUpdated || 
        (Date.now() - new Date(paymentsStore.lastUpdated).getTime()) > 5 * 60 * 1000
      
      if (needsBalanceRefresh) {
        await paymentsStore.fetchBalance()
      }
      
      await paymentsStore.fetchTransactions()
      recentTransactions.value = paymentsStore.transactions.slice(0, 5) || []
    } catch (err) {
      console.error('Failed to fetch payment data:', err)
      recentTransactions.value = []
    }
    
    // Stats endpoint doesn't exist yet, so we don't need to try fetching it
    stats.value = {
      apiCallCount: 0
    }
  } catch (err) {
    showNotification({
      type: 'error',
      message: 'Failed to load dashboard data'
    })
  }
}

onMounted(() => {
  fetchDashboardData()
})

// Add this function to the script section
const formatTransactionAmount = (amount) => {
  // Parse the amount if it's a string
  const numAmount = typeof amount === 'number' ? amount : parseFloat(amount);
  
  // Handle small amounts with more precision
  if (Math.abs(numAmount) < 0.01) {
    return numAmount.toFixed(4); // Show 4 decimal places for tiny amounts
  } else if (Math.abs(numAmount) < 0.1) {
    return numAmount.toFixed(3); // Show 3 decimal places for small amounts
  } else {
    return numAmount.toFixed(2); // Show standard 2 decimal places for normal amounts
  }
}
</script>

<style scoped>
/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}

/* Gradient animation for text */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 3s ease infinite;
}

/* Aurora animation */
@keyframes aurora {
  0%, 100% {
    opacity: 0.3;
    transform: translateY(0) scale(1);
  }
  50% {
    opacity: 0.5;
    transform: translateY(-20px) scale(1.05);
  }
}

.animate-aurora {
  animation: aurora 15s ease-in-out infinite;
}

/* Float animations for orbs */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(-30px, 30px) rotate(-120deg);
  }
  66% {
    transform: translate(20px, -20px) rotate(-240deg);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(-30px, -30px);
  }
}

.animate-float-slow {
  animation: float-slow 20s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 25s ease-in-out infinite;
}

.animate-float-reverse {
  animation: float-reverse 18s ease-in-out infinite;
}

/* Line clamp for description */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>