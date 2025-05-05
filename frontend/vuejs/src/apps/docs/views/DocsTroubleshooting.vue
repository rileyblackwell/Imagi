<template>
  <DocsLayout>
    <div class="max-w-4xl mx-auto">
      <!-- Page header with attractive styling -->
      <div class="mb-10">
        <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
          <span class="text-primary-400 font-semibold text-sm tracking-wider">DOCUMENTATION</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
          Troubleshooting
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          Solutions to common issues and challenges with Imagi Oasis.
        </p>
      </div>

      <!-- Attractive divider -->
      <div class="relative h-16 mb-10">
        <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
      </div>

      <!-- Main content -->
      <div class="prose prose-invert prose-lg max-w-none">
        <!-- Introduction -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 mb-8">
          <h2 class="text-2xl font-bold text-white mb-4">Resolving Common Issues</h2>
          <p class="text-gray-300">
            Even the most intuitive platforms can sometimes present challenges. This guide will help you quickly resolve common issues you might encounter while using Imagi Oasis.
          </p>
        </div>

        <!-- Account & Access Issues -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-primary-500 to-violet-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">Account & Access Issues</h2>
            
            <div class="space-y-8 mt-6">
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">I forgot my password</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you can't remember your password:</p>
                  <ol class="list-decimal pl-5 space-y-2">
                    <li>Go to the login page</li>
                    <li>Click the "Forgot Password" link below the login form</li>
                    <li>Enter the email address associated with your account</li>
                    <li>Check your email for a password reset link (including spam/junk folders)</li>
                    <li>Follow the link to create a new password</li>
                  </ol>
                  <p class="mt-3 text-primary-400">
                    <i class="fas fa-info-circle mr-1"></i> 
                    Password reset links expire after 24 hours for security reasons.
                  </p>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">I'm not receiving the verification email</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you haven't received your account verification or password reset email:</p>
                  <ol class="list-decimal pl-5 space-y-2">
                    <li>Check your spam, promotions, or junk folders</li>
                    <li>Make sure you entered the correct email address</li>
                    <li>Add <code>support@imagioasis.com</code> to your contacts or safe senders list</li>
                    <li>Wait 5-10 minutes as emails can sometimes be delayed</li>
                    <li>Try requesting a new verification email from the login page</li>
                  </ol>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">I'm getting "Access Denied" or "Unauthorized" errors</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you're seeing access errors when trying to use Imagi Oasis:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Make sure you're logged in with the correct account</li>
                    <li>Check if your session may have expired (try logging out and back in)</li>
                    <li>Verify that your account has the necessary permissions for the action you're trying to perform</li>
                    <li>Clear your browser cache and cookies, then try again</li>
                    <li>Try using a different browser or disable browser extensions that might be interfering</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Project Creation Issues -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-500 to-sky-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">Project Creation Issues</h2>
            
            <div class="space-y-8 mt-6">
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">My project is taking too long to generate</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If your project is taking longer than expected to generate:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Complex projects with many features can take 5-10 minutes to generate</li>
                    <li>Check your internet connection - a stable connection is needed during generation</li>
                    <li>If generation takes more than 15 minutes, try refreshing the page</li>
                    <li>Consider breaking down very complex applications into smaller projects</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-primary-300 font-medium">Quick Fix:</p>
                    <p>If your project seems stuck, cancel the generation, wait a minute, and try again with a slightly modified description.</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">My project description isn't being understood correctly</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If Imagi misunderstands what you're trying to build:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Use clear, specific language in your project description</li>
                    <li>Break down complex features into simpler components</li>
                    <li>Specify exactly what data you want to store and relationships between them</li>
                    <li>Include examples of user workflows (e.g., "User logs in, creates a task, assigns it to another user")</li>
                    <li>Reference existing apps that have similar functionality to what you want</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-blue-300 font-medium">Example of a good description:</p>
                    <p class="italic">"I need a task management app where users can create projects, add tasks to projects, and assign tasks to team members. Each task should have a title, description, due date, priority level, and status. Users should be able to filter tasks by status and due date, and get notifications when tasks are assigned to them or approaching deadline."</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">I'm out of AI credits</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you've run out of AI credits for creating or modifying projects:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Visit the "Billing" section from your account dashboard</li>
                    <li>Purchase additional AI credits using our secure payment system</li>
                    <li>Credits are usually added to your account immediately after payment</li>
                    <li>Consider our subscription plans for regular users, which offer better value than one-time purchases</li>
                  </ul>
                  <router-link 
                    to="/payments/checkout" 
                    class="mt-4 inline-flex items-center px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 rounded-lg transition-all duration-300"
                  >
                    <i class="fas fa-coins mr-2"></i>
                    Buy AI Credits
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Deployment & Performance Issues -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-green-500 to-emerald-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">Deployment & Performance Issues</h2>
            
            <div class="space-y-8 mt-6">
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">My deployed application is slow</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If your deployed application is running slower than expected:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Check your internet connection speed and stability</li>
                    <li>Try accessing the application from a different device or network</li>
                    <li>Consider upgrading to a higher performance hosting tier if you have many users</li>
                    <li>Large media files (images, videos) can slow down your application - optimize them if possible</li>
                    <li>Complex database queries or reports can affect performance - consider pagination for large data sets</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-green-300 font-medium">Performance Tip:</p>
                    <p>For applications with many users, consider enabling database caching in your deployment settings to improve performance.</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">Deployment is failing</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If your application fails to deploy:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Check if your chosen subdomain name is already taken - try a different one</li>
                    <li>Ensure your application passes all validation checks before deployment</li>
                    <li>Verify that you have sufficient AI credits for deployment</li>
                    <li>Check if there are any specific error messages in the deployment log</li>
                    <li>Make sure your application doesn't exceed the size limits for your plan</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-green-300 font-medium">Quick Fix:</p>
                    <p>If deployment fails, try again after waiting a few minutes. Temporary issues with deployment services sometimes resolve themselves.</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">My custom domain isn't working</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you're having issues with your custom domain:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Verify that you've set up the DNS records exactly as specified in the custom domain instructions</li>
                    <li>DNS changes can take 24-48 hours to propagate globally - be patient</li>
                    <li>Check if your domain registration is active and not expired</li>
                    <li>Make sure SSL certificates are properly set up for secure connections</li>
                    <li>Confirm that your account plan supports custom domains</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-green-300 font-medium">DNS Verification:</p>
                    <p>Use online DNS lookup tools to verify your domain's DNS records are correctly configured.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Data & Content Issues -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-yellow-500 to-amber-500"></div>
          <div class="pl-4">
            <h2 class="text-2xl font-bold text-white mb-4">Data & Content Issues</h2>
            
            <div class="space-y-8 mt-6">
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">My data isn't saving correctly</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If data isn't being saved or appears to be lost:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Make sure you're clicking the "Save" or "Submit" button after making changes</li>
                    <li>Check if you're encountering any validation errors (red text near form fields)</li>
                    <li>Ensure your internet connection is stable when submitting forms</li>
                    <li>Verify that you have the necessary permissions to create or edit the content</li>
                    <li>Try clearing your browser cache and cookies, then try again</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-yellow-300 font-medium">Data Entry Tip:</p>
                    <p>For important data, consider copying it to your clipboard before submitting forms as a backup.</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">File uploads aren't working</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you're having trouble uploading files:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Check that your file is under the maximum size limit (typically 10MB for images, 50MB for documents)</li>
                    <li>Verify the file is in a supported format (common formats like .jpg, .png, .pdf, .docx are usually supported)</li>
                    <li>Ensure you have a stable internet connection during the upload</li>
                    <li>Try using a different browser or device</li>
                    <li>If uploading images, try compressing them first using an online tool</li>
                  </ul>
                </div>
              </div>
              
              <div class="bg-dark-800/50 p-5 rounded-lg border border-dark-700">
                <h4 class="text-white font-medium mb-2">I've accidentally deleted important data</h4>
                <div class="text-gray-300 text-sm space-y-3">
                  <p>If you've accidentally deleted data:</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>Check if your application has a "Trash" or "Recently Deleted" section where items might be recoverable</li>
                    <li>Look for any "Undo" option that might appear immediately after deletion</li>
                    <li>If available, check the "Activity Log" or "History" section to see if previous versions can be restored</li>
                    <li>For important data loss, contact support immediately with details of what was deleted and when</li>
                  </ul>
                  <div class="mt-4 p-3 bg-dark-700/50 rounded-lg">
                    <p class="text-yellow-300 font-medium">Prevention Tip:</p>
                    <p>Regularly export important data from your application as a backup measure.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Still Need Help? -->
        <div class="bg-dark-900/50 border border-dark-800 rounded-xl p-8 my-8">
          <div class="flex flex-col items-center text-center">
            <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mb-5">
              <i class="fas fa-headset text-2xl text-primary-400"></i>
            </div>
            <h3 class="text-xl font-semibold text-white mb-2">Still Need Help?</h3>
            <p class="text-gray-300 text-center max-w-md mb-6">
              If you're experiencing an issue not covered here, our support team is ready to help you.
            </p>
            <div class="flex flex-col sm:flex-row gap-4">
              <a 
                href="mailto:support@imagioasis.com" 
                class="px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 hover:from-primary-600 hover:to-violet-600 text-white rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300"
              >
                <i class="fas fa-envelope mr-2"></i>
                Contact Support
              </a>
              <router-link 
                to="/docs" 
                class="px-6 py-3 bg-dark-800 hover:bg-dark-700 text-white rounded-xl transform hover:-translate-y-1 transition-all duration-300 border border-dark-700"
              >
                <i class="fas fa-arrow-left mr-2"></i>
                Back to Documentation Home
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DocsLayout>
</template>

<script setup>
import DocsLayout from '../layouts/DocsLayout.vue'
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Override Tailwind prose styling for lists with custom icons */
:deep(.prose ul) {
  list-style-type: none;
  padding-left: 0;
}

:deep(.prose ol) {
  padding-left: 1.75rem;
}
</style> 