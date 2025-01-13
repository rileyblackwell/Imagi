<template>
  <div class="container mx-auto px-4 py-12">
    <h1 class="text-4xl font-bold text-white mb-8">Careers at Imagi</h1>
    
    <div class="prose prose-invert max-w-none">
      <p class="text-gray-300 mb-8">
        Join us in building the future of web development. At Imagi, we're revolutionizing how people create web applications through the power of natural language and AI.
      </p>

      <h2 class="text-2xl font-semibold text-white mt-12 mb-6">Open Positions</h2>
      
      <div class="grid gap-6 md:grid-cols-2">
        <div class="bg-dark-800 p-6 rounded-lg border border-dark-700">
          <h3 class="text-xl font-semibold text-white mb-3">Full Stack Developer</h3>
          <p class="text-gray-300 mb-4">
            We're looking for experienced full-stack developers to help build and scale our platform.
          </p>
          <a href="mailto:careers@imagi.ai" class="text-primary-400 hover:text-primary-300">
            Apply Now →
          </a>
        </div>

        <div class="bg-dark-800 p-6 rounded-lg border border-dark-700">
          <h3 class="text-xl font-semibold text-white mb-3">AI/ML Engineer</h3>
          <p class="text-gray-300 mb-4">
            Join our AI team to improve and expand our natural language processing capabilities.
          </p>
          <a href="mailto:careers@imagi.ai" class="text-primary-400 hover:text-primary-300">
            Apply Now →
          </a>
        </div>
      </div>

      <h2 class="text-2xl font-semibold text-white mt-12 mb-6">Why Join Imagi?</h2>
      
      <ul class="list-none space-y-4">
        <li class="flex items-start">
          <span class="text-primary-400 mr-3">✓</span>
          <span class="text-gray-300">Work with cutting-edge AI and web technologies</span>
        </li>
        <li class="flex items-start">
          <span class="text-primary-400 mr-3">✓</span>
          <span class="text-gray-300">Flexible remote work options</span>
        </li>
        <li class="flex items-start">
          <span class="text-primary-400 mr-3">✓</span>
          <span class="text-gray-300">Competitive salary and equity packages</span>
        </li>
        <li class="flex items-start">
          <span class="text-primary-400 mr-3">✓</span>
          <span class="text-gray-300">Health, dental, and vision insurance</span>
        </li>
        <li class="flex items-start">
          <span class="text-primary-400 mr-3">✓</span>
          <span class="text-gray-300">Professional development opportunities</span>
        </li>
      </ul>

      <div class="mt-12 p-6 bg-dark-800 rounded-lg border border-dark-700">
        <h3 class="text-xl font-semibold text-white mb-4">Don't see a position that fits?</h3>
        <p class="text-gray-300 mb-4">
          We're always looking for talented individuals to join our team. Send us your resume and let us know how you can contribute to Imagi.
        </p>
        <a href="mailto:careers@imagi.ai" class="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors">
          Get in Touch
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CareersView'
}
</script> 