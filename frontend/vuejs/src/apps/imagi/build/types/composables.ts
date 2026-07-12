// Types used in composables

/**
 * Options for creating a new file
 */
export interface CreateFileOptions {
  name: string;
  type: string;
  content?: string;
  projectId: string;
  path?: string;
}

/**
 * Confirmation dialog options
 */
export interface ConfirmOptions {
  title?: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'info' | 'warning' | 'danger' | 'success';
}
