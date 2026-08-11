import { AlertTriangle, Server } from 'lucide-react'
import { Card, CardBody, Badge, Button } from './index'
import type { Alert } from '../types'

interface ReactiveAlertCardProps {
  alert: Alert
  onAcknowledge?: (id: string) => void
  onResolve?: (id: string) => void
}

function getSeverityVariant(severity: string) {
  switch (severity) {
    case 'critical': return 'danger'
    case 'warning': return 'warning'
    default: return 'info'
  }
}

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${Math.floor(diffHours / 24)}d ago`
}

export function ReactiveAlertCard({ alert, onAcknowledge, onResolve }: ReactiveAlertCardProps) {
  return (
    <Card>
      <CardBody>
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              alert.severity === 'critical' ? 'bg-red-100' : 'bg-amber-100'
            }`}>
              <AlertTriangle className={`w-5 h-5 ${
                alert.severity === 'critical' ? 'text-red-600' : 'text-amber-600'
              }`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{alert.title}</h3>
              <p className="text-sm text-gray-500">{formatTimeAgo(alert.createdAt)}</p>
            </div>
          </div>
          <Badge variant={getSeverityVariant(alert.severity)}>
            {alert.severity}
          </Badge>
        </div>

        <p className="text-sm text-gray-600 mb-4">{alert.description}</p>

        <div className="flex items-center gap-2 mb-4">
          <Server className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-500">{alert.componentName}</span>
        </div>

        {alert.status === 'active' && (
          <div className="flex gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => onAcknowledge?.(alert.id)}
            >
              Acknowledge
            </Button>
            <Button
              size="sm"
              variant="primary"
              onClick={() => onResolve?.(alert.id)}
            >
              Resolve
            </Button>
          </div>
        )}

        {alert.status === 'acknowledged' && (
          <Button
            size="sm"
            variant="primary"
            onClick={() => onResolve?.(alert.id)}
          >
            Resolve
          </Button>
        )}
      </CardBody>
    </Card>
  )
}