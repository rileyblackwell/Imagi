// Re-export all services from a central file to avoid circular dependencies
import api, { isString } from './api'
import { ProjectService } from './projectService'
import { BuilderService, ModelService } from './builderService'

// Re-export for backward compatibility
export const BuilderAPI = {
  ...ProjectService,
  ...BuilderService
}

// Export individual services
export { 
  api,
  isString,
  ProjectService, 
  BuilderService, 
  ModelService 
}

// Export default api for convenience
export default api 