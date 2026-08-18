import type { Component, Alert, HealthScore, Prediction, CorrelationGroup } from '../types'

const API_BASE = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`)
    }

    const text = await response.text()
    if (!text) {
      return {} as T
    }

    try {
      return JSON.parse(text) as T
    } catch (parseError) {
      console.error('JSON parse error:', parseError, 'Response text:', text)
      return {} as T
    }
  } catch (error) {
    console.error('Fetch error:', error)
    throw error
  }
}

function normalizeMetrics(metrics: any): any {
  if (!metrics) return {}
  const normalized: any = {}
  // Normalize CPU usage
  if (metrics.cpu_usage !== undefined) normalized.cpu = metrics.cpu_usage
  else if (metrics.cpu !== undefined) normalized.cpu = metrics.cpu
  // Normalize memory - handle both memory_usage and memory_percent
  if (metrics.memory_usage !== undefined) normalized.memory = metrics.memory_usage
  else if (metrics.memory_percent !== undefined) normalized.memory = metrics.memory_percent
  else if (metrics.memory !== undefined) normalized.memory = metrics.memory
  // Normalize disk - handle both disk_usage and disk_percent
  if (metrics.disk_usage !== undefined) normalized.disk = metrics.disk_usage
  else if (metrics.disk_percent !== undefined) normalized.disk = metrics.disk_percent
  else if (metrics.disk !== undefined) normalized.disk = metrics.disk
  return normalized
}

export async function getComponents(source?: string): Promise<Component[]> {
  try {
    const params = source && source !== 'all' ? `?source=${source}` : ''
    console.log('[API] getComponents called with source:', source, 'params:', params)
    const result = await fetchApi<{ data: any[] }>(`/api/components${params}`)
    console.log('[API] getComponents result:', result)
    if (!result || !result.data) {
      console.warn('No data in components response')
      return []
    }
    return result.data.map((c: any) => {
      if (!c) return null
      return {
        ...c,
        id: c.id || `comp-${Math.random().toString(36).substr(2, 9)}`,
        name: c.name || 'Unknown Component',
        healthScore: c.health_score ?? c.healthScore ?? 0,
        lastUpdated: c.last_seen ?? c.lastUpdated ?? new Date().toISOString(),
        metrics: normalizeMetrics(c.metrics),
        source: c.source || 'unknown',
        status: c.status || 'unknown',
        type: c.type || c.category || 'unknown',
      }
    }).filter(Boolean)
  } catch (error) {
    console.error('Failed to fetch components:', error)
    return []
  }
}

export async function getComponent(id: string): Promise<Component | undefined> {
  try {
    return await fetchApi<Component>(`/api/components/${id}`)
  } catch (error) {
    console.error('Failed to fetch component:', error)
    return undefined
  }
}

export async function getAlerts(): Promise<Alert[]> {
  try {
    const result = await fetchApi<any>('/api/alerts')
    const data = result.data || result || []
    return transformKeys(data).map((a: any) => ({
      ...a,
      timeToBreach: a.timeToBreach ?? a.time_to_breach ?? null,
    }))
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
    return []
  }
}

export async function getAlert(id: string): Promise<Alert | undefined> {
  try {
    return await fetchApi<Alert>(`/api/alerts/${id}`)
  } catch (error) {
    console.error('Failed to fetch alert:', error)
    return undefined
  }
}

export async function getActiveAlerts(): Promise<Alert[]> {
  try {
    const result = await fetchApi<any>('/api/alerts?status=active')
    const data = result.data || result || []
    return transformKeys(data)
  } catch (error) {
    console.error('Failed to fetch active alerts:', error)
    return []
  }
}

export async function getHealthScore(): Promise<HealthScore> {
  try {
    return await fetchApi<HealthScore>('/api/components/health')
  } catch (error) {
    console.error('Failed to fetch health score:', error)
    return { overall: 0, components: { healthy: 0, warning: 0, critical: 0, offline: 0 } }
  }
}

function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

function transformKeys(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(transformKeys)
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = snakeToCamel(key)
      acc[camelKey] = transformKeys(obj[key])
      return acc
    }, {} as any)
  }
  return obj
}

export async function getPredictions(): Promise<Prediction[]> {
  try {
    const result = await fetchApi<any>('/api/predictions')
    const data = result.data || result || []
    const transformed = transformKeys(data)
    return transformed.map((p: any) => {
      const predictionType = p.predictionType ?? p.prediction_type ?? 'unknown'
      const confidence = p.confidence ?? 0
      const currentValue = p.currentValue ?? p.current_value ?? 0
      const predictedValue = p.predictedValue ?? p.predicted_value ?? 0
      const threshold = p.threshold ?? p.predicted_threshold ?? 100

      const confidenceInterval = calculateConfidenceInterval(confidence, currentValue, predictedValue, threshold)

      return {
        ...p,
        componentName: p.componentName ?? p.component_name ?? 'Unknown',
        metric: predictionType.replace(/_failure|_degradation/g, '').replace(/_/g, ' '),
        predictionType: predictionType,
        timeToBreach: p.timeToBreach ?? p.timeToBreachMinutes ?? p.time_to_breach_minutes ?? p.time_to_breach ?? null,
        currentValue: currentValue,
        predictedValue: predictedValue,
        confidence: confidence,
        confidenceInterval: confidenceInterval,
        threshold: threshold,
        severity: p.severity ?? 'unknown',
        explanation: p.explanation ?? 'No explanation available',
        recommendedAction: p.recommendedAction ?? p.recommended_action ?? 'No action recommended',
        status: p.status ?? 'unknown',
      }
    })
  } catch (error) {
    console.error('Failed to fetch predictions:', error)
    return []
  }
}

function calculateConfidenceInterval(confidence: number, currentValue: number, predictedValue: number, threshold: number) {
  if (!confidence || confidence <= 0) {
    return { lower: null, upper: null }
  }

  const margin = (100 - confidence) / 100 * (threshold - currentValue) * 0.5

  return {
    lower: Math.max(0, Math.round((currentValue - margin) * 10) / 10),
    upper: Math.min(100, Math.round((predictedValue + margin) * 10) / 10)
  }
}

export async function getCorrelationGroups(): Promise<CorrelationGroup[]> {
  try {
    const result = await fetchApi<any>('/api/correlations')
    const data = result.data || result || []
    return data
  } catch (error) {
    console.error('Failed to fetch correlations:', error)
    return []
  }
}

export async function acknowledgeAlert(alertId: string): Promise<Alert | undefined> {
  try {
    return await fetchApi<Alert>(`/api/alerts/${alertId}/acknowledge`, {
      method: 'POST',
    })
  } catch (error) {
    console.error('Failed to acknowledge alert:', error)
    return undefined
  }
}

export async function resolveAlert(alertId: string): Promise<Alert | undefined> {
  try {
    return await fetchApi<Alert>(`/api/alerts/${alertId}/resolve`, {
      method: 'POST',
    })
  } catch (error) {
    console.error('Failed to resolve alert:', error)
    return undefined
  }
}

export async function getInfrastructureSummary() {
  try {
    return await fetchApi<any>('/api/v1/components/infrastructure/summary')
  } catch (error) {
    console.error('Failed to fetch infrastructure summary:', error)
    return null
  }
}

export async function getDataSourceStatus() {
  try {
    return await fetchApi<any>('/api/simulator/status')
  } catch (error) {
    console.error('Failed to fetch data source status:', error)
    return null
  }
}

export async function setSimulatorScenario(scenario: string) {
  try {
    return await fetchApi<any>('/api/simulator/scenario', {
      method: 'POST',
      body: JSON.stringify({ scenario }),
    })
  } catch (error) {
    console.error('Failed to set simulator scenario:', error)
    return null
  }
}

export async function getSimulatorScenarios() {
  try {
    return await fetchApi<any>('/api/simulator/scenarios')
  } catch (error) {
    console.error('Failed to fetch simulator scenarios:', error)
    return null
  }
}

export async function getSourcesBreakdown() {
  try {
    return await fetchApi<any>('/api/components/infrastructure/summary')
  } catch (error) {
    console.error('Failed to fetch sources breakdown:', error)
    return null
  }
}

export async function getSourceCategoryBreakdown() {
  try {
    return await fetchApi<any>('/api/components/infrastructure/source-category')
  } catch (error) {
    console.error('Failed to fetch source category breakdown:', error)
    return null
  }
}