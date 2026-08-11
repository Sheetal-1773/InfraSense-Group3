export interface Component {
  id: string
  name: string
  type: 'network' | 'server' | 'database' | 'api' | 'service' | 'cache' | 'queue'
  status: 'healthy' | 'degraded' | 'down' | 'unknown'
  healthScore: number
  cpu: number
  memory: number
  disk: number
  lastUpdated: string
}

export interface Alert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  status: 'active' | 'acknowledged' | 'resolved'
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
  components: ComponentHealthScore[]
  trend: HealthTrendPoint[]
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