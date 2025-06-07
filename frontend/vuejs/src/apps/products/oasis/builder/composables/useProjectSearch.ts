import { ref, computed } from 'vue';
import type { ComputedRef } from 'vue';
import type { Project } from '../types/components';

interface UseProjectSearchOptions {
  includeDescription?: boolean;
}

export function useProjectSearch(projects: ComputedRef<Project[]>, options: UseProjectSearchOptions = {}) {
  const searchQuery = ref('');
  
  const filteredProjects = computed(() => {
    // Early return for empty queries
    const trimmedQuery = searchQuery.value?.trim() || '';
    
    if (!trimmedQuery) {
      return projects.value || [];
    }

    // Ensure we have projects to filter
    if (!projects.value || !Array.isArray(projects.value)) {
      return [];
    }

    const query = trimmedQuery.toLowerCase();
    
    const filtered = projects.value.filter(project => {
      // Ensure project has required properties
      if (!project || !project.name || typeof project.name !== 'string') {
        return false;
      }
      
      // Primary filter: project name must start with the search query
      const nameStartsWithQuery = project.name.toLowerCase().startsWith(query);
      
      // For short queries (1-2 characters), only search by name to avoid false positives
      // For longer queries, also include description searching
      const shouldSearchDescription = options.includeDescription && query.length >= 3;
      const descriptionMatches = shouldSearchDescription && 
        project.description && 
        typeof project.description === 'string' &&
        project.description.toLowerCase().includes(query);
      
      return nameStartsWithQuery || (shouldSearchDescription && descriptionMatches);
    });
    
    return filtered;
  });

  return {
    searchQuery,
    filteredProjects
  };
}
