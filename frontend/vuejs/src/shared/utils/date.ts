/**
 * Format a date string or Date object into a human-readable format
 * @param date - Date string or Date object to format
 * @param options - Intl.DateTimeFormat options
 * @returns Formatted date string
 */
export const formatDate = (
  date: string | Date,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }
): string => {
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    return new Intl.DateTimeFormat('en-US', options).format(dateObj)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Invalid date'
  }
}

/**
 * Get relative time string (e.g., "2 days ago", "just now")
 * @param date - Date string or Date object to format
 * @returns Relative time string
 */
export const getRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date
    const now = new Date()
    const diff = now.getTime() - dateObj.getTime()

    const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (days > 0) return rtf.format(-days, 'day')
    if (hours > 0) return rtf.format(-hours, 'hour')
    if (minutes > 0) return rtf.format(-minutes, 'minute')
    return 'just now'
  } catch (error) {
    console.error('Error calculating relative time:', error)
    return 'Invalid date'
  }
}

export type DateFormat = 'short' | 'medium' | 'long' | 'relative'

type DateFormatOptions = Record<Exclude<DateFormat, 'relative'>, Intl.DateTimeFormatOptions>

/**
 * Format a date with a predefined format style
 * @param date - Date string or Date object to format
 * @param format - Predefined format style
 * @returns Formatted date string
 */
export const formatDateWithStyle = (date: string | Date, format: DateFormat = 'medium'): string => {
  const styles: DateFormatOptions = {
    short: { month: 'numeric', day: 'numeric', year: '2-digit' },
    medium: { year: 'numeric', month: 'short', day: 'numeric' },
    long: { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' }
  }

  if (format === 'relative') {
    return getRelativeTime(date)
  }

  return formatDate(date, styles[format])
}
