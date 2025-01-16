/**
 * Format a date string to a relative time (e.g., "2 hours ago")
 * @param {string|Date} date - The date to format
 * @returns {string} The formatted relative time string
 */
export function formatRelativeTime(date) {
  const now = new Date();
  const target = new Date(date);
  const diff = Math.floor((now - target) / 1000); // difference in seconds

  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)} days ago`;
  if (diff < 31536000) return `${Math.floor(diff / 2592000)} months ago`;
  return `${Math.floor(diff / 31536000)} years ago`;
} 