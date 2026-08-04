/**
 * Turning an API failure into something a person can read.
 *
 * This was copied byte-for-byte into sellService, operateService and
 * marketingService. It knows the shapes DRF actually returns, so it belongs
 * next to the shared api client rather than in three tools that each talk to
 * the same backend.
 */
export function extractError(error: unknown, fallback = 'Something went wrong'): string {
  const data = (error as { response?: { data?: unknown } })?.response?.data
  if (typeof data === 'string') return fallback
  if (data && typeof data === 'object') {
    const payload = data as Record<string, unknown>
    if (typeof payload.error === 'string') return payload.error
    if (typeof payload.detail === 'string') return payload.detail
    // DRF field errors: {"field": ["message", ...]}
    for (const [field, value] of Object.entries(payload)) {
      const first = Array.isArray(value) ? value[0] : value
      if (typeof first === 'string') {
        return field === 'non_field_errors' ? first : `${field.replace(/_/g, ' ')}: ${first}`
      }
    }
  }
  const message = (error as { message?: string })?.message
  return message || fallback
}
