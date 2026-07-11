import { AgentService } from './agentService'

/**
 * Version Control Service for handling automatic commits after file operations
 */
export class VersionControlService {
  /**
   * Automatically commit changes after a file operation
   * This runs in the background and doesn't block the UI
   */
  static async commitAfterFileOperation(
    projectId: string,
    filePath: string,
    description: string
  ): Promise<void> {
    // Run in background without blocking the UI
    // Use setTimeout to avoid race conditions where git runs before file changes are persisted
    setTimeout(async () => {
      try {
        if (!projectId) return
        
        // Format file path properly
        const normalizedPath = filePath 
          ? (filePath.startsWith('/') ? filePath : `/${filePath}`) 
          : '/'
        
        // Create a summary for the commit message (limit to 50 chars)
        const summary = description.length > 50 
          ? description.substring(0, 47) + '...' 
          : description
        
        // Call the backend to create the commit
        await AgentService.createVersion(projectId, {
          file_path: normalizedPath,
          description: summary
        })
      } catch (error) {
        // Version control errors are non-critical
        // They shouldn't interrupt the user's workflow
      }
         }, 500) // Delay to ensure file operations are complete and avoid race conditions
  }
} 