<template>
  <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-dark-900">
      <!-- Hero Section -->
      <section class="relative min-h-[60vh] flex items-center justify-center overflow-hidden pt-32 pb-16 sm:pt-36 sm:pb-20">
        <!-- Background Effects -->
        <div class="absolute inset-0 bg-dark-900">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-dark-900 to-violet-500/10"></div>
          <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-full blur-[120px] opacity-70"></div>
          <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
        </div>

        <!-- Content -->
        <div class="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <HeroBadge text="Privacy & Security" />
          
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
            <span class="text-white block mb-2 sm:mb-3">Privacy Policy</span>
            <GradientText variant="primary" class="font-bold block text-5xl sm:text-6xl lg:text-7xl">
              Your Privacy Matters
            </GradientText>
          </h1>
          
          <p class="text-lg sm:text-xl text-gray-300 max-w-2xl mx-auto">
            We are committed to protecting your privacy and ensuring the security of your personal information.
          </p>
        </div>
      </section>

      <!-- Main Content -->
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24 relative">
        <!-- Decorative background elements -->
        <div class="absolute inset-0 overflow-hidden pointer-events-none">
          <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-500 rounded-full blur-[100px] opacity-20 transform rotate-45"></div>
          <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-500 rounded-full blur-[100px] opacity-20 transform -rotate-45"></div>
        </div>

        <!-- Introduction -->
        <div class="relative mb-16">
          <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/30 transition-all duration-300">
            <p class="text-lg text-gray-300 mb-4">
              At Imagi Oasis, we value your privacy and are dedicated to maintaining the trust and confidence of all visitors to our website. This Privacy Policy explains how we collect, use, and protect your personal information.
            </p>
            <p class="text-lg text-gray-300">
              This policy was last updated on July 15, 2023. We may update this policy from time to time, so please check this page occasionally to ensure you're happy with any changes.
            </p>
          </div>
        </div>

        <!-- Privacy Content -->
        <div class="space-y-16 relative">
          <SectionHeader 
            title="Our Privacy Commitments" 
            subtitle="At Imagi Oasis, we take your privacy seriously. Here's what you need to know about how we handle your information."
          />
          
          <!-- Privacy Sections -->
          <div class="space-y-12">
            <!-- Information Collection Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-database text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Information Collection and Use</h2>
                </div>
                <p class="text-gray-300 mb-5">We collect and process personal information necessary to provide our services. This information is handled with utmost care and in compliance with applicable data protection laws:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Account Information:</strong> Name, email, password (encrypted), profile picture, and registration details
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Technical Data:</strong> IP address, browser type, device information, operating system, and cookies
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Usage Information:</strong> Interaction with our services, generated applications, API calls, and feature usage patterns
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Payment Details:</strong> Billing information, transaction history (stored securely via payment processors)
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Generated Content:</strong> Applications, code, and configurations created using our services
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Communication Data:</strong> Support tickets, feedback, and correspondence with our team
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Data Processing Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-violet-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-microchip text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Data Processing and Storage</h2>
                </div>
                <p class="text-gray-300 mb-5">We implement robust security measures to protect your data:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>End-to-end encryption for sensitive data transmission</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Regular security audits and penetration testing</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Data backup and disaster recovery protocols</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Access controls and authentication mechanisms</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Regular updates to security infrastructure</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Compliance with industry security standards</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Use of Information Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-indigo-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-cog text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Use of Information</h2>
                </div>
                <p class="text-gray-300 mb-5">Your information is used for the following purposes:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Service Provision:</strong> Delivering and maintaining our AI-powered development platform
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Personalization:</strong> Customizing and optimizing your experience
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Analytics:</strong> Improving our services and understanding user needs
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Security:</strong> Protecting against fraud and unauthorized access
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Communication:</strong> Sending service updates, notifications, and support responses
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Legal Compliance:</strong> Meeting regulatory requirements and enforcing our terms
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Data Sharing Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-purple-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-fuchsia-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-share-nodes text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Data Sharing and Third Parties</h2>
                </div>
                <p class="text-gray-300 mb-5">We may share your information with:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Service Providers:</strong> Cloud hosting, analytics, payment processing, and security services
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Legal Requirements:</strong> Court orders, law enforcement requests, or regulatory obligations
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Business Transfers:</strong> Mergers, acquisitions, or asset sales (with user notification)
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Aggregated Data:</strong> Anonymous, statistical data for research and analysis
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Divider -->
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-dark-700"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="bg-dark-900 px-4 text-sm text-gray-400">Additional Information</span>
            </div>
          </div>

          <!-- Additional Information -->
          <SectionHeader 
            title="Your Rights and Our Policies" 
            subtitle="Learn more about your privacy rights and how we handle your data."
          />

          <!-- Additional sections -->
          <div class="space-y-12">
            <!-- Privacy Rights Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-green-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-teal-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-user-shield text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Your Privacy Rights</h2>
                </div>
                <p class="text-gray-300 mb-5">You have the following rights regarding your personal data:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Access:</strong> Request copies of your personal data
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Rectification:</strong> Correct inaccurate or incomplete information
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Deletion:</strong> Request erasure of your personal data
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Portability:</strong> Receive and transfer your data to another controller
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Restriction:</strong> Limit how we process your data
                      </span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-green-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>
                        <strong class="text-white">Objection:</strong> Object to certain types of processing
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Data Retention Section -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-primary-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-indigo-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-clock text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">Data Retention</h2>
                </div>
                <p class="text-gray-300 mb-5">We retain your information according to these principles:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Active accounts: Data retained while account is active</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Deleted accounts: Data removed within 30 days of deletion request</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Backup retention: Up to 90 days for disaster recovery</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Legal requirements: As required by applicable laws</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-primary-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Anonymous data: May be retained indefinitely</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- International Data Transfers -->
            <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-violet-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
              <div class="p-7">
                <div class="flex items-center gap-4 mb-5">
                  <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center shadow-md">
                    <i class="fas fa-globe text-white text-xl"></i>
                  </div>
                  <h2 class="text-2xl font-bold text-white">International Data Transfers</h2>
                </div>
                <p class="text-gray-300 mb-5">For users outside our primary operating region:</p>
              </div>
              
              <div class="px-7 pb-7">
                <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                  <ul class="space-y-4">
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Data may be processed in different jurisdictions</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>We ensure appropriate safeguards for international transfers</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>EU-US Privacy Shield compliance where applicable</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Standard contractual clauses with service providers</span>
                    </li>
                    <li class="flex items-start">
                      <div class="w-2 h-2 rounded-full bg-violet-400 mt-2.5 mr-3 flex-shrink-0"></div>
                      <span>Regular audits of international data protection measures</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- Children's Privacy & Policy Changes (2 column) -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <!-- Children's Privacy -->
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-purple-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
                <div class="p-7">
                  <div class="flex items-center gap-4 mb-5">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-fuchsia-500 flex items-center justify-center shadow-md">
                      <i class="fas fa-child text-white text-xl"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-white">Children's Privacy</h2>
                  </div>
                  <p class="text-gray-300 mb-5">Regarding users under 16 years of age:</p>
                </div>
                
                <div class="px-7 pb-7">
                  <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                    <ul class="space-y-4">
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Services not intended for children under 16</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>We do not knowingly collect children's data</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Immediate deletion upon discovery of minor's data</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Parental consent required for legitimate minor users</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-purple-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Special protections for authorized minor accounts</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <!-- Changes to Privacy Policy -->
              <div class="group bg-gradient-to-b from-dark-800/80 to-dark-900/80 backdrop-blur-xl rounded-2xl border border-dark-700/40 transition-all duration-300 hover:border-indigo-500/30 hover:shadow-xl shadow-[0_4px_20px_-2px_rgba(0,0,0,0.2)]">
                <div class="p-7">
                  <div class="flex items-center gap-4 mb-5">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center shadow-md">
                      <i class="fas fa-file-contract text-white text-xl"></i>
                    </div>
                    <h2 class="text-2xl font-bold text-white">Changes to Privacy Policy</h2>
                  </div>
                  <p class="text-gray-300 mb-5">Our policy update procedures:</p>
                </div>
                
                <div class="px-7 pb-7">
                  <div class="bg-dark-900/50 backdrop-blur-sm rounded-xl p-5 border border-dark-800">
                    <ul class="space-y-4">
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Regular reviews and updates as needed</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Notice of material changes via email</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>30-day advance notice for significant changes</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Continued use constitutes acceptance</span>
                      </li>
                      <li class="flex items-start">
                        <div class="w-2 h-2 rounded-full bg-indigo-400 mt-2.5 mr-3 flex-shrink-0"></div>
                        <span>Previous versions available upon request</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Contact Section -->
          <section class="bg-gradient-to-br from-primary-600/90 via-violet-600/90 to-purple-600/90 rounded-2xl p-8 relative overflow-hidden mt-12">
            <div class="absolute inset-0">
              <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
            </div>
            
            <div class="relative z-10">
              <div class="flex items-center mb-6">
                <div class="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center mr-4">
                  <i class="fas fa-envelope text-xl text-white"></i>
                </div>
                <h2 class="text-2xl sm:text-3xl font-bold text-white">Contact Us</h2>
              </div>
              
              <p class="text-lg text-white/90">
                If you have any questions or concerns about this Privacy Policy, please 
                <HomeNavbarButton
                  to="/contact" 
                  class="inline-block font-semibold text-white hover:text-primary-200 underline decoration-primary-400/30 hover:decoration-primary-200 transition-colors"
                >
                  contact us
                </HomeNavbarButton>.
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { 
  GradientText, 
  HeroBadge,
  HomeNavbarButton,
  FeatureCard, 
  CardContainer,
  SectionHeader 
} from '@/apps/home/components'

export default defineComponent({
  name: 'PrivacyPolicy',
  components: {
    DefaultLayout,
    GradientText,
    HeroBadge,
    HomeNavbarButton,
    FeatureCard,
    CardContainer,
    SectionHeader
  }
})
</script>

<style scoped>
/* Style for list items */
ul {
  padding-left: 0;
  margin: 0;
  list-style: none;
}

li {
  margin-bottom: 0.5rem;
  color: #d1d5db; /* text-gray-300 */
}

strong {
  font-weight: 600;
}
</style>