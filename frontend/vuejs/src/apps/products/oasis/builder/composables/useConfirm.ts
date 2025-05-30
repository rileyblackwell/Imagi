import type { ConfirmOptions } from '../types/composables'

export function useConfirm() {
  /**
   * Shows a confirmation dialog and returns a promise that resolves 
   * to true if confirmed, false if cancelled
   */
  const confirm = (options: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      // For now, use the native browser confirm dialog
      // In the future, this could be replaced with a custom modal component
      const isConfirmed = window.confirm(options.message);
      resolve(isConfirmed);
    });
  };

  return {
    confirm
  };
}

 