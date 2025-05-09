<!--
  VersionControlDropdown.vue
  This component displays a dropdown of version history (git commits)
  and allows the user to reset to a previous version.
-->
<template>
  <div class="version-control-dropdown">
    <!-- Dropdown button -->
    <button 
      @click="toggleDropdown"
      class="flex items-center justify-between w-full px-3 py-2 text-left text-sm font-medium rounded-md bg-dark-700 hover:bg-dark-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 text-gray-200"
    >
      <span class="flex items-center">
        <svg class="w-5 h-5 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Version History
      </span>
      <svg class="w-5 h-5 ml-2 -mr-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>

    <!-- Dropdown menu -->
    <div v-if="dropdownOpen" class="absolute z-10 mt-1 w-full bg-dark-800 shadow-lg rounded-md py-1 text-sm text-gray-200 max-h-64 overflow-y-auto">
      <div v-if="isLoading" class="px-4 py-2 text-center text-gray-400">
        Loading versions...
      </div>
      <template v-else-if="versions.length > 0">
        <button
          v-for="version in versions"
          :key="version.hash"
          @click="selectVersion(version)"
          class="w-full text-left px-4 py-2 hover:bg-dark-700"
        >
          <div class="flex flex-col">
            <span class="font-medium truncate" :title="version.message">{{ truncateMessage(version.message) }}</span>
            <div class="flex justify-between text-xs text-gray-400">
              <span>{{ version.relative_date }}</span>
              <span class="font-mono">{{ version.hash.substring(0, 7) }}</span>
            </div>
          </div>
        </button>
      </template>
      <div v-else class="px-4 py-2 text-center text-gray-400">
        No versions available
      </div>
    </div>

    <!-- Confirmation modal -->
    <div v-if="showConfirmation" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Background overlay -->
        <div class="fixed inset-0 bg-black bg-opacity-75 transition-opacity" aria-hidden="true"></div>

        <!-- Modal panel -->
        <div class="inline-block align-bottom bg-dark-800 rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div>
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
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
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:col-start-2 sm:text-sm"
            >
              Reset Project
            </button>
            <button 
              @click="cancelReset"
              type="button" 
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-dark-700 text-base font-medium text-gray-300 hover:bg-dark-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm"
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
import axios from 'axios';

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
    const response = await axios.get(`/api/v1/builder/${props.projectId}/versions/`);
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
    const response = await axios.post(`/api/v1/builder/${props.projectId}/versions/reset/`, {
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
</style> 