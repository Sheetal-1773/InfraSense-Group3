export function safeNumber(value: number | null | undefined, defaultValue: number = 0): number {
  if (value === null || value === undefined) return defaultValue
  if (Number.isNaN(value)) return defaultValue
  if (!Number.isFinite(value)) return defaultValue
  return value
}

export function safeString(value: string | null | undefined, defaultValue: string = 'N/A'): string {
  if (value === null || value === undefined) return defaultValue
  return value
}

export function formatPercentage(value: number | null | undefined, decimals: number = 0): string {
  const safe = safeNumber(value, -1)
  if (safe < 0) return 'N/A'
  return `${safe.toFixed(decimals)}%`
}

export function formatTimeToBreach(minutes: number | null | undefined): string {
  const safe = safeNumber(minutes, -1)
  if (safe < 0) return 'N/A'
  
  if (safe < 60) {
    return `${Math.round(safe)}m`
  }
  
  const hours = Math.floor(safe / 60)
  const mins = Math.round(safe % 60)
  
  if (hours < 24) {
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  }
  
  const days = Math.floor(hours / 24)
  const remainingHours = hours % 24
  return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`
}

export function formatConfidence(value: number | null | undefined): string {
  const safe = safeNumber(value, -1)
  if (safe < 0) return 'N/A'
  return `${Math.round(safe)}%`
}

export function formatHealthScore(score: number | null | undefined): { value: string; status: string } {
  const safe = safeNumber(score, -1)
  
  if (safe < 0) {
    return { value: 'N/A', status: 'Unknown' }
  }
  
  let status: string
  if (safe >= 90) status = 'Healthy'
  else if (safe >= 70) status = 'Good'
  else if (safe >= 50) status = 'Warning'
  else status = 'Critical'
  
  return { value: `${Math.round(safe)}%`, status }
}

export function getStatusColor(status: string | null | undefined): string {
  const s = safeString(status, 'unknown').toLowerCase()
  
  switch (s) {
    case 'healthy':
    case 'good':
      return '#22c55e'
    case 'warning':
      return '#f59e0b'
    case 'critical':
    case 'down':
      return '#ef4444'
    case 'degraded':
      return '#f97316'
    default:
      return '#6b7280'
  }
}

export function getSeverityColor(severity: string | null | undefined): string {
  const s = safeString(severity, 'unknown').toLowerCase()
  
  switch (s) {
    case 'critical':
      return '#ef4444'
    case 'high':
      return '#f97316'
    case 'medium':
      return '#f59e0b'
    case 'low':
    case 'info':
      return '#3b82f6'
    default:
      return '#6b7280'
  }
}

export function getHealthBarColor(score: number | null | undefined): string {
  const safe = safeNumber(score, -1)
  
  if (safe < 0) return '#6b7280'
  if (safe >= 90) return '#22c55e'
  if (safe >= 70) return '#3b82f6'
  if (safe >= 50) return '#f59e0b'
  return '#ef4444'
}