export interface Component {
  id: string
  name: string
  hostname?: string
  type?: string
  category?: string
  status: 'healthy' | 'degraded' | 'down' | 'unknown' | 'warning' | 'critical' | 'offline'
  health_score: number
  healthScore?: number
  criticality?: string
  owner?: string
  description?: string
  environment?: string
  source?: string
  provider?: string
  category_id?: number
  last_seen?: string
  lastUpdated?: string
  metrics?: Record<string, number>
  cpu?: number
  memory?: number
  disk?: number
}

export interface Alert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  status: 'active' | 'open' | 'acknowledged' | 'resolved'
  componentId: string
  componentName: string
  timeToBreach?: number
  confidenceInterval?: {
    lower: number
    upper: number
  }
  createdAt: string
  acknowledgedAt?: string
  resolvedAt?: string
}

export interface HealthScore {
  overall: number
  components: {
    healthy: number
    warning: number
    critical: number
    offline: number
  }
  total?: number
  trend?: HealthTrendPoint[]
  timestamp?: string
  categories?: {
    server: number
    network: number
    database: number
    application: number
  }
}

export interface ComponentHealthScore {
  componentId: string
  componentName: string
  score: number
}

export interface HealthTrendPoint {
  timestamp: string
  score: number
}

export interface Prediction {
  id: string
  componentId: string
  componentName: string
  metric: string
  currentValue: number
  predictedValue: number
  timeToThreshold: number
  timeToBreach?: number
  confidence: number
  threshold: number
  confidenceInterval?: {
    lower: number
    upper: number
  }
  createdAt: string
}

export interface CorrelationGroup {
  id: string
  name: string
  components: string[]
  rootCause?: string
  blastRadius: number
}

export interface RecommendedAction {
  id: string
  title: string
  description: string
  runbookUrl?: string
  priority: 'high' | 'medium' | 'low'
}