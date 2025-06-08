<template>
  <DashboardLayout :navigationItems="navigationItems">
    <!-- Enhanced Main Content with Dynamic Background -->
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Improved Decorative Background Elements -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10">
        <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12 py-12 sm:py-20">
          <!-- Modern Welcome Header Section -->
          <div class="pt-16 pb-16">
            <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
              <div class="space-y-6 md:max-w-3xl">
                <!-- Enhanced Badge -->
                <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full">
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">DASHBOARD</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h2 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  Welcome back, {{ authStore.user?.name || 'Developer' }}! 👋<br class="hidden sm:block" />
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Imagi Oasis</span>
                </h2>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Your AI-powered app builder dashboard. Create, manage, and deploy applications with ease.
                </p>
              </div>
            </div>
            
            <!-- Animated Divider Line -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent my-12 animate-pulse-slow"></div>
          </div>

          <!-- Enhanced Stats Overview with Modern Glassmorphism -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-16">
            <div 
              v-for="stat in statsData" 
              :key="stat.title"
              class="group relative transform transition-all duration-300 hover:-translate-y-1"
            >
              <!-- Modern glassmorphism container -->
              <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                <!-- Sleek gradient header -->
                <div class="h-1 w-full"
                  :class="{
                    'bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400': stat.color === 'primary',
                    'bg-gradient-to-r from-green-400 via-emerald-400 to-green-400': stat.color === 'success',
                    'bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-400': stat.color === 'warning',
                    'bg-gradient-to-r from-blue-400 via-sky-400 to-blue-400': stat.color === 'info'
                  }"
                ></div>
                
                <!-- Subtle background effects -->
                <div class="absolute -top-16 -right-16 w-32 h-32 rounded-full blur-2xl opacity-30 transition-opacity duration-500 group-hover:opacity-40"
                  :class="{
                    'bg-gradient-to-br from-indigo-400/20 to-violet-400/20': stat.color === 'primary',
                    'bg-gradient-to-br from-green-400/20 to-emerald-400/20': stat.color === 'success',
                    'bg-gradient-to-br from-yellow-400/20 to-amber-400/20': stat.color === 'warning',
                    'bg-gradient-to-br from-blue-400/20 to-sky-400/20': stat.color === 'info'
                  }"
                ></div>
                
                <div class="relative z-10 p-6">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-sm font-medium text-gray-400 uppercase tracking-wider">{{ stat.title }}</h3>
                    <div class="w-9 h-9 rounded-xl flex items-center justify-center border transition-all duration-300 group-hover:scale-110"
                      :class="{
                        'bg-gradient-to-br from-indigo-400/20 to-violet-400/20 border-indigo-400/20': stat.color === 'primary',
                        'bg-gradient-to-br from-green-400/20 to-emerald-400/20 border-green-400/20': stat.color === 'success',
                        'bg-gradient-to-br from-yellow-400/20 to-amber-400/20 border-yellow-400/20': stat.color === 'warning',
                        'bg-gradient-to-br from-blue-400/20 to-sky-400/20 border-blue-400/20': stat.color === 'info'
                      }"
                    >
                                             <i :class="[
                           stat.icon, 
                           'text-sm',
                           {
                             'text-indigo-300': stat.color === 'primary',
                             'text-green-300': stat.color === 'success',
                             'text-yellow-300': stat.color === 'warning',
                             'text-blue-300': stat.color === 'info'
                           }
                         ]"
                       ></i>
                    </div>
                  </div>
                  <div class="text-2xl font-bold text-white mb-1">{{ stat.value }}</div>
                  <div v-if="stat.trend" class="text-xs font-medium"
                    :class="{
                      'text-green-400': stat.trend.startsWith('+'),
                      'text-red-400': stat.trend.startsWith('-'),
                      'text-gray-400': !stat.trend.startsWith('+') && !stat.trend.startsWith('-')
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
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Modern header section -->
                    <div class="flex items-center justify-between mb-6">
                      <div class="flex items-center gap-3">
                        <!-- Modern icon with subtle gradient -->
                        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-400/20 to-violet-400/20 flex items-center justify-center border border-indigo-400/20 flex-shrink-0">
                          <svg class="w-4 h-4 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                          </svg>
                        </div>
                        <h2 class="text-xl font-semibold text-white">Recent Projects</h2>
                      </div>
                      <router-link 
                        to="/products/oasis/builder/projects"
                        class="inline-flex items-center px-3 py-1.5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-indigo-400/30 text-gray-400 hover:text-gray-300 rounded-xl transition-all duration-200 text-sm font-medium"
                      >
                        View All
                        <svg class="w-3 h-3 ml-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                      </router-link>
                    </div>
                    
                    <!-- Modern separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                    
                    <div class="space-y-5">
                      <div 
                        v-for="project in recentProjects"
                        :key="project.id"
                        class="group relative transform transition-all duration-300"
                      >
                        <!-- Modern glassmorphism container matching ProjectCardWithDescription -->
                        <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-white/20 hover:shadow-black/40 transform hover:-translate-y-1 cursor-pointer"
                             @click="goToProject(project.id)">
                          <!-- Sleek gradient header -->
                          <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-indigo-400 to-violet-400 opacity-80"></div>
                          
                          <!-- Subtle background effects -->
                          <div class="absolute -top-16 -left-16 w-32 h-32 bg-gradient-to-br from-violet-400/4 to-indigo-400/4 rounded-full blur-2xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                          
                          <!-- Content with padding matching ProjectCardWithDescription -->
                          <div class="relative z-10 p-5 flex flex-col h-full">
                            <!-- Modern project header -->
                            <div class="flex items-center gap-3 mb-4">
                              <!-- Modern icon with subtle gradient -->
                              <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-400/20 to-indigo-400/20 flex items-center justify-center border border-violet-400/20 flex-shrink-0">
                                <svg class="w-4 h-4 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                </svg>
                              </div>
                              
                              <!-- Project name with improved typography -->
                              <div class="flex-1 min-w-0">
                                <h3 class="text-base font-semibold text-white truncate leading-tight">{{ project.name }}</h3>
                                <div class="flex items-center text-xs text-gray-400 mt-1">
                                  <svg class="w-3 h-3 mr-1.5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                  </svg>
                                  {{ formatDate(project.updated_at) }}
                                </div>
                              </div>
                            </div>
                            
                            <!-- Modern separator -->
                            <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
                            
                            <!-- Project description -->
                            <div class="mb-4 flex-grow">
                              <p class="text-gray-300 text-sm line-clamp-2 leading-relaxed">
                                {{ project.description || 'No description provided' }}
                              </p>
                            </div>
                            
                            <!-- Footer section with modern styling -->
                            <div class="mt-auto">
                              <!-- Sleek Open button -->
                              <div class="w-full inline-flex items-center justify-center px-4 py-2.5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-violet-400/30 text-white rounded-xl transition-all duration-300 text-sm font-medium group/button">
                                <svg class="w-4 h-4 mr-2 group-hover/button:text-violet-400 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                </svg>
                                Open Project
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div v-if="!recentProjects.length" class="flex flex-col items-center justify-center py-12">
                        <div class="w-12 h-12 bg-gradient-to-br from-indigo-400/20 to-violet-400/20 rounded-2xl flex items-center justify-center mb-4 border border-indigo-400/20">
                          <svg class="w-5 h-5 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                          </svg>
                        </div>
                        <h3 class="text-lg font-medium text-white mb-1">No projects yet</h3>
                        <p class="text-gray-400 text-center max-w-md mb-4 text-sm">Create your first project to start building with Imagi</p>
                        
                        <!-- Elegant directional hint -->
                        <div class="flex items-center text-indigo-400 text-sm">
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
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-green-400 via-emerald-400 to-green-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-green-400/4 to-emerald-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Modern header section -->
                    <div class="flex items-center justify-between mb-6">
                      <div class="flex items-center gap-3">
                        <!-- Modern icon with subtle gradient -->
                        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-green-400/20 to-emerald-400/20 flex items-center justify-center border border-green-400/20 flex-shrink-0">
                          <svg class="w-5 h-5 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                          </svg>
                        </div>
                        <h2 class="text-xl font-semibold text-white">Payment Transactions</h2>
                      </div>
                      <router-link 
                        :to="{ name: 'PaymentHistory' }"
                        class="inline-flex items-center px-3 py-1.5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-green-400/30 text-gray-400 hover:text-gray-300 rounded-xl transition-all duration-200 text-sm font-medium"
                      >
                        View All
                        <svg class="w-3 h-3 ml-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                      </router-link>
                    </div>
                    
                    <!-- Modern separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                    
                    <div class="space-y-3">
                      <div v-if="recentTransactions.length" class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-dark-700">
                          <thead>
                            <tr>
                              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Date</th>
                              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Model</th>
                              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Request Type</th>
                              <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Amount</th>
                            </tr>
                          </thead>
                          <tbody class="divide-y divide-dark-700">
                            <tr v-for="tx in recentTransactions" :key="tx.id" class="hover:bg-dark-800/40 transition-colors">
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{{ formatDate(tx.created_at) }}</td>
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{{ tx.model || '—' }}</td>
                              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-300">{{ mapRequestType(tx.request_type) }}</td>
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
                        <div class="w-14 h-14 bg-gradient-to-br from-green-400/20 to-emerald-400/20 rounded-2xl flex items-center justify-center mb-4 border border-green-400/20">
                          <svg class="w-6 h-6 text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                          </svg>
                        </div>
                        <h3 class="text-lg font-medium text-white mb-1">No transactions yet</h3>
                        <p class="text-gray-400 text-center max-w-md mb-4 text-sm">Add funds to your account to see transactions here</p>
                        
                        <!-- Elegant directional hint -->
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
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-orange-400 via-amber-400 to-orange-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-orange-400/4 to-amber-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Modern header section -->
                    <div class="flex items-center gap-3 mb-6">
                      <!-- Modern icon with subtle gradient -->
                      <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-400/20 to-amber-400/20 flex items-center justify-center border border-orange-400/20 flex-shrink-0">
                        <svg class="w-4 h-4 text-orange-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                      </div>
                      <h2 class="text-xl font-semibold text-white">Quick Actions</h2>
                    </div>
                    
                    <!-- Modern separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                    
                    <div class="space-y-4">
                      <button
                        v-for="action in quickActions"
                        :key="action.title"
                        @click="$router.push(action.route)"
                        class="w-full flex items-center justify-between p-5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-orange-400/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 text-white hover:text-orange-400 group"
                      >
                                                  <div class="flex items-center gap-4">
                            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-400/20 to-amber-400/20 border border-orange-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                              <i :class="[action.icon, 'text-orange-300 text-sm']"></i>
                            </div>
                            <span class="font-medium">{{ action.title }}</span>
                          </div>
                          <svg class="w-4 h-4 text-gray-500 group-hover:text-orange-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                          </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Resources -->
              <div class="group relative">
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-blue-400 via-sky-400 to-blue-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-blue-400/4 to-sky-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative z-10 p-8">
                    <!-- Modern header section -->
                    <div class="flex items-center gap-3 mb-6">
                      <!-- Modern icon with subtle gradient -->
                      <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-400/20 to-sky-400/20 flex items-center justify-center border border-blue-400/20 flex-shrink-0">
                        <svg class="w-4 h-4 text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                        </svg>
                      </div>
                      <h2 class="text-xl font-semibold text-white">Resources</h2>
                    </div>
                    
                    <!-- Modern separator -->
                    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
                    
                    <div class="space-y-4">
                      <template v-for="resource in resourceLinks" :key="resource.title">
                        <router-link 
                          v-if="resource.url.startsWith('/')"
                          :to="resource.url" 
                          class="block p-5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-blue-400/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
                        >
                                                      <div class="flex items-center justify-between">
                                                              <div class="flex items-center gap-4">
                                  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-400/20 to-sky-400/20 border border-blue-400/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                                    <i :class="[resource.icon, 'text-blue-300 text-sm']"></i>
                                  </div>
                                  <div>
                                    <h3 class="text-white group-hover:text-blue-400 transition-colors font-medium">{{ resource.title }}</h3>
                                    <p class="text-sm text-gray-400">{{ resource.description }}</p>
                                  </div>
                                </div>
                                <svg class="w-4 h-4 text-gray-500 group-hover:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
import { useRouter } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import { useAuthStore } from '@/apps/auth/stores'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useNotification } from '@/shared/composables/useNotification'

// Store initialization
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
const router = useRouter()
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
/* Enhanced scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: theme('colors.gray.700');
  border-radius: 9999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: theme('colors.gray.600');
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

.delay-700 {
  animation-delay: 700ms;
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