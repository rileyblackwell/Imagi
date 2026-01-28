<template>
  <DocsLayout>
    <DocsContentWrapper
      title="Troubleshooting"
      description="Solutions to common issues and challenges with Imagi Oasis."
      badge-text="HELP & SUPPORT"
    >
      <!-- Introduction -->
      <DocsCard color-variant="primary">
        <DocsCardHeader title="Resolving Common Issues" icon="fas fa-wrench" color="primary" />
        <p class="text-white/50 leading-relaxed">
          Even the most intuitive platforms can sometimes present challenges. This guide will help you quickly resolve common issues you might encounter while using Imagi Oasis.
        </p>
      </DocsCard>

      <!-- Account & Access Issues -->
      <DocsCard color-variant="violet">
        <DocsCardHeader title="Account & Access Issues" icon="fas fa-user-shield" color="violet" />
        
        <div class="space-y-6 mt-4">
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">I forgot my password</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If you can't remember your password:</p>
              <ol class="list-decimal pl-5 space-y-2">
                <li>Go to the login page</li>
                <li>Click the "Forgot Password" link below the login form</li>
                <li>Enter the email address associated with your account</li>
                <li>Check your email for a password reset link (including spam/junk folders)</li>
                <li>Follow the link to create a new password</li>
              </ol>
              <p class="mt-3 text-violet-400 flex items-center gap-2">
                <i class="fas fa-info-circle"></i> 
                Password reset links expire after 24 hours for security reasons.
              </p>
            </div>
          </div>
          
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">I'm not receiving the verification email</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If you haven't received your account verification or password reset email:</p>
              <ol class="list-decimal pl-5 space-y-2">
                <li>Check your spam, promotions, or junk folders</li>
                <li>Make sure you entered the correct email address</li>
                <li>Add <code class="text-violet-300 bg-white/[0.05] px-1.5 py-0.5 rounded">support@imagioasis.com</code> to your contacts or safe senders list</li>
                <li>Wait 5-10 minutes as emails can sometimes be delayed</li>
                <li>Try requesting a new verification email from the login page</li>
              </ol>
            </div>
          </div>
          
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">I'm getting "Access Denied" or "Unauthorized" errors</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If you're seeing access errors when trying to use Imagi Oasis:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="violet" size="sm">Make sure you're logged in with the correct account</DocsListItem>
                <DocsListItem icon="fas fa-check" color="violet" size="sm">Check if your session may have expired (try logging out and back in)</DocsListItem>
                <DocsListItem icon="fas fa-check" color="violet" size="sm">Verify that your account has the necessary permissions</DocsListItem>
                <DocsListItem icon="fas fa-check" color="violet" size="sm">Clear your browser cache and cookies, then try again</DocsListItem>
                <DocsListItem icon="fas fa-check" color="violet" size="sm">Try using a different browser or disable browser extensions</DocsListItem>
              </ul>
            </div>
          </div>
        </div>
      </DocsCard>
      
      <!-- Project Creation Issues -->
      <DocsCard color-variant="blue">
        <DocsCardHeader title="Project Creation Issues" icon="fas fa-project-diagram" color="blue" />
        
        <div class="space-y-6 mt-4">
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">My project is taking too long to generate</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If your project is taking longer than expected to generate:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Complex projects with many features can take 5-10 minutes to generate</DocsListItem>
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Check your internet connection - a stable connection is needed during generation</DocsListItem>
                <DocsListItem icon="fas fa-check" color="blue" size="sm">If generation takes more than 15 minutes, try refreshing the page</DocsListItem>
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Consider breaking down very complex applications into smaller projects</DocsListItem>
              </ul>
              <div class="mt-4 p-3 bg-blue-500/10 border border-blue-400/20 rounded-xl">
                <p class="text-blue-300 font-medium text-sm">Quick Fix:</p>
                <p class="text-white/60 text-sm mt-1">If your project seems stuck, cancel the generation, wait a minute, and try again with a slightly modified description.</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">My project description isn't being understood correctly</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If Imagi misunderstands what you're trying to build:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="cyan" size="sm">Use clear, specific language in your project description</DocsListItem>
                <DocsListItem icon="fas fa-check" color="cyan" size="sm">Break down complex features into simpler components</DocsListItem>
                <DocsListItem icon="fas fa-check" color="cyan" size="sm">Specify exactly what data you want to store and relationships between them</DocsListItem>
                <DocsListItem icon="fas fa-check" color="cyan" size="sm">Include examples of user workflows</DocsListItem>
                <DocsListItem icon="fas fa-check" color="cyan" size="sm">Reference existing apps that have similar functionality to what you want</DocsListItem>
              </ul>
              <div class="mt-4 p-3 bg-cyan-500/10 border border-cyan-400/20 rounded-xl">
                <p class="text-cyan-300 font-medium text-sm">Example of a good description:</p>
                <p class="text-white/60 text-sm mt-1 italic">"I need a task management app where users can create projects, add tasks to projects, and assign tasks to team members. Each task should have a title, description, due date, priority level, and status."</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">I'm out of AI credits</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If you've run out of AI credits for creating or modifying projects:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Visit the "Billing" section from your account dashboard</DocsListItem>
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Purchase additional AI credits using our secure payment system</DocsListItem>
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Credits are usually added to your account immediately after payment</DocsListItem>
                <DocsListItem icon="fas fa-check" color="blue" size="sm">Consider our subscription plans for regular users, which offer better value</DocsListItem>
              </ul>
              <router-link 
                to="/payments/checkout" 
                class="group/btn mt-4 inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
              >
                <i class="fas fa-coins text-sm"></i>
                <span>Purchase AI Credits</span>
              </router-link>
            </div>
          </div>
        </div>
      </DocsCard>
      
      <!-- Deployment & Performance Issues -->
      <DocsCard color-variant="emerald">
        <DocsCardHeader title="Deployment & Performance Issues" icon="fas fa-server" color="emerald" />
        
        <div class="space-y-6 mt-4">
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">My deployed application is slow</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If your deployed application is running slower than expected:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Check your internet connection speed and stability</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Try accessing the application from a different device or network</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Consider upgrading to a higher performance hosting tier if you have many users</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Large media files can slow down your application - optimize them if possible</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Consider pagination for large data sets</DocsListItem>
              </ul>
              <div class="mt-4 p-3 bg-emerald-500/10 border border-emerald-400/20 rounded-xl">
                <p class="text-emerald-300 font-medium text-sm">Performance Tip:</p>
                <p class="text-white/60 text-sm mt-1">For applications with many users, consider enabling database caching in your deployment settings to improve performance.</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">Deployment is failing</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If your application fails to deploy:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Check if your chosen subdomain name is already taken - try a different one</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Ensure your application passes all validation checks before deployment</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Verify that you have sufficient AI credits for deployment</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Check if there are any specific error messages in the deployment log</DocsListItem>
                <DocsListItem icon="fas fa-check" color="emerald" size="sm">Make sure your application doesn't exceed the size limits for your plan</DocsListItem>
              </ul>
            </div>
          </div>
        </div>
      </DocsCard>
      
      <!-- Data & Content Issues -->
      <DocsCard color-variant="amber">
        <DocsCardHeader title="Data & Content Issues" icon="fas fa-database" color="amber" />
        
        <div class="space-y-6 mt-4">
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">My data isn't saving correctly</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If data isn't being saved or appears to be lost:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Make sure you're clicking the "Save" or "Submit" button after making changes</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Check if you're encountering any validation errors (red text near form fields)</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Ensure your internet connection is stable when submitting forms</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Verify that you have the necessary permissions to create or edit the content</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Try clearing your browser cache and cookies, then try again</DocsListItem>
              </ul>
              <div class="mt-4 p-3 bg-amber-500/10 border border-amber-400/20 rounded-xl">
                <p class="text-amber-300 font-medium text-sm">Data Entry Tip:</p>
                <p class="text-white/60 text-sm mt-1">For important data, consider copying it to your clipboard before submitting forms as a backup.</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white/[0.03] border border-white/[0.08] rounded-xl p-5 backdrop-blur-sm">
            <h4 class="text-white font-semibold mb-3">File uploads aren't working</h4>
            <div class="text-white/50 text-sm space-y-3">
              <p>If you're having trouble uploading files:</p>
              <ul class="space-y-2">
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Check that your file is under the maximum size limit (typically 10MB for images, 50MB for documents)</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Verify the file is in a supported format (.jpg, .png, .pdf, .docx are usually supported)</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Ensure you have a stable internet connection during the upload</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">Try using a different browser or device</DocsListItem>
                <DocsListItem icon="fas fa-check" color="amber" size="sm">If uploading images, try compressing them first using an online tool</DocsListItem>
              </ul>
            </div>
          </div>
        </div>
      </DocsCard>
      
      <!-- Still Need Help? -->
      <DocsCard color-variant="fuchsia">
        <div class="text-center">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-fuchsia-400/20 to-violet-400/20 border border-fuchsia-400/20 flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-headset text-2xl text-fuchsia-300"></i>
          </div>
          <h3 class="text-xl font-semibold text-white/90 mb-2">Still Need Help?</h3>
          <p class="text-white/50 text-center max-w-md mx-auto mb-6">
            If you're experiencing an issue not covered here, our support team is ready to help you.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="mailto:support@imagioasis.com" 
              class="group inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
            >
              <i class="fas fa-envelope"></i>
              <span>Contact Support</span>
            </a>
            <router-link 
              to="/docs" 
              class="group/btn inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-xl text-white font-medium transition-all duration-300"
            >
              <i class="fas fa-arrow-left"></i>
              <span>Back to Documentation</span>
            </router-link>
          </div>
        </div>
      </DocsCard>
    </DocsContentWrapper>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
import { DocsContentWrapper, DocsCard, DocsCardHeader, DocsListItem } from '../components'
</script>

<style scoped>
/* Override Tailwind prose styling for lists with custom icons */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style>
