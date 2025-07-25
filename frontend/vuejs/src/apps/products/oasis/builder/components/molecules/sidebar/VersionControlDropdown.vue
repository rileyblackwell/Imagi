<!--
  VersionControlDropdown.vue
  This component displays a dropdown of version history (git commits)
  and allows the user to reset to a previous version.
-->
<template>
  <div class="version-control-dropdown">
    <!-- Dropdown button with enhanced styling to match other sidebar elements -->
    <button 
      @click="toggleDropdown"
      class="group relative flex items-center justify-between w-full py-3 px-4 text-left text-sm font-medium rounded-lg bg-dark-800/70 hover:bg-dark-800 border border-dark-700/50 hover:border-primary-500/30 transition-all duration-300"
    >
      <!-- Subtle glow effect on hover -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/30 to-violet-500/30 rounded-lg blur opacity-0 group-hover:opacity-75 transition duration-300"></div>
      
      <div class="relative flex items-center">
        <i class="fas fa-history mr-2 text-primary-400"></i>
        <span class="text-white">Version History</span>
      </div>
      
      <i class="fas fa-chevron-down text-gray-400 group-hover:text-white transition-colors"></i>
    </button>

    <!-- Dropdown menu with enhanced styling -->
    <div 
      v-if="dropdownOpen" 
      class="absolute z-10 mt-2 w-full bg-dark-800/90 backdrop-blur-sm shadow-xl rounded-xl py-1 text-sm text-gray-200 max-h-64 overflow-y-auto border border-dark-700/60"
    >
      <div v-if="isLoading" class="px-4 py-3 text-center text-gray-400">
        <div class="flex items-center justify-center space-x-2">
          <i class="fas fa-spinner fa-spin"></i>
          <span>Loading versions...</span>
        </div>
      </div>
      <template v-else-if="versions.length > 0">
        <button
          v-for="version in versions"
          :key="version.hash"
          @click="selectVersion(version)"
          class="w-full text-left px-4 py-3 hover:bg-dark-700/70 hover:bg-gradient-to-r hover:from-primary-500/10 hover:to-violet-500/5 transition-all duration-200"
        >
          <div class="flex flex-col">
            <span class="font-medium truncate text-gray-200" :title="version.message">{{ truncateMessage(version.message) }}</span>
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>{{ version.relative_date }}</span>
              <span class="font-mono text-primary-400/80">{{ version.hash.substring(0, 7) }}</span>
            </div>
          </div>
        </button>
      </template>
      <div v-else class="px-4 py-3 text-center text-gray-400">
        <div class="flex flex-col items-center justify-center">
          <i class="fas fa-history text-gray-500 mb-1"></i>
          <span>No versions available</span>
        </div>
      </div>
    </div>

    <!-- Confirmation modal with styling consistent with the modern UI -->
    <div v-if="showConfirmation" class="fixed inset-0 z-50 overflow-y-auto backdrop-blur-sm" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-black bg-opacity-75 transition-opacity" aria-hidden="true"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-dark-900/90 backdrop-blur-md rounded-xl px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6 border border-dark-700/60">
          <div>
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-900/30 border border-red-700/40">
              <i class="fas fa-exclamation-triangle text-red-500"></i>
            </div>
            <div class="mt-3 text-center sm:mt-5">
              <h3 class="text-lg leading-6 font-medium text-white" id="modal-title">
                Reset to Previous Version?
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-300">
                  This will permanently reset your project to version: {{ selectedVersion ? truncateMessage(selectedVersion.message) : '' }}. All changes made after this version will be lost. This action cannot be undone.
                </p>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
            <button 
              @click="confirmReset"
              type="button" 
              class="group relative w-full inline-flex justify-center rounded-lg border border-transparent px-4 py-2 bg-gradient-to-r from-red-600/90 to-red-700/90 text-base font-medium text-white hover:from-red-600 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:col-start-2 sm:text-sm transition-all duration-200"
            >
              Reset Project
            </button>
            <button 
              @click="cancelReset"
              type="button" 
              class="mt-3 w-full inline-flex justify-center rounded-lg border border-dark-700/60 px-4 py-2 bg-dark-800/70 text-base font-medium text-gray-300 hover:bg-dark-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500/50 sm:mt-0 sm:col-start-1 sm:text-sm transition-colors duration-200"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute } from 'vue-router';
import api, { buildApiUrl } from '@/shared/services/api';

const props = defineProps({
  projectId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['version-reset']);

const route = useRoute();
const dropdownOpen = ref(false);
const isLoading = ref(false);
const versions = ref([]);
const showConfirmation = ref(false);
const selectedVersion = ref(null);

// Toggle dropdown
const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value;
  if (dropdownOpen.value) {
    loadVersions();
  }
};

// Load versions from API
const loadVersions = async () => {
  if (!props.projectId) return;
  
  isLoading.value = true;
  try {
    const response = await api.get(buildApiUrl(`/api/v1/builder/${props.projectId}/versions/`));
    if (response.data.success && response.data.versions) {
      versions.value = response.data.versions;
    } else {
      versions.value = [];
    }
  } catch (error) {
    console.error('Error loading versions:', error);
    versions.value = [];
  } finally {
    isLoading.value = false;
  }
};

// Select a version
const selectVersion = (version) => {
  selectedVersion.value = version;
  showConfirmation.value = true;
  dropdownOpen.value = false;
};

// Confirm version reset
const confirmReset = async () => {
  if (!selectedVersion.value || !props.projectId) {
    cancelReset();
    return;
  }
  
  try {
    const response = await api.post(buildApiUrl(`/api/v1/builder/${props.projectId}/versions/reset/`), {
      commit_hash: selectedVersion.value.hash
    });
    
    if (response.data.success) {
      emit('version-reset', selectedVersion.value);
      // Reload the page to reflect changes
      window.location.reload();
    } else {
      console.error('Error resetting version:', response.data.error);
    }
  } catch (error) {
    console.error('Error resetting version:', error);
  } finally {
    cancelReset();
  }
};

// Cancel version reset
const cancelReset = () => {
  showConfirmation.value = false;
  selectedVersion.value = null;
};

// Truncate long commit messages
const truncateMessage = (message) => {
  if (!message) return '';
  return message.length > 50 ? message.substring(0, 47) + '...' : message;
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  const dropdown = document.querySelector('.version-control-dropdown');
  if (dropdown && !dropdown.contains(event.target)) {
    dropdownOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Watch for project ID changes
watch(() => props.projectId, (newProjectId) => {
  if (newProjectId && dropdownOpen.value) {
    loadVersions();
  }
});
</script>

<style scoped>
.version-control-dropdown {
  position: relative;
  width: 100%;
}

/* Add consistent scrollbar styling to match other sidebar components */
.max-h-64 {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.600') transparent;
}

.max-h-64::-webkit-scrollbar {
  width: 6px;
}

.max-h-64::-webkit-scrollbar-track {
  background: transparent;
}

.max-h-64::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.600');
  border-radius: 3px;
}
</style> 