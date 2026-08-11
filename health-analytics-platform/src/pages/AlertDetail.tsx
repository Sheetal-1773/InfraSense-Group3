import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Clock, Gauge, Server, AlertTriangle, CheckCircle } from 'lucide-react'
import { useAlert } from '../hooks'
import { Card, CardHeader, CardBody, Badge, Button } from '../components'

function getSeverityVariant(severity: string) {
  switch (severity) {
    case 'critical': return 'danger'
    case 'warning': return 'warning'
    default: return 'info'
  }
}

function getStatusVariant(status: string) {
  switch (status) {
    case 'active': return 'danger'
    case 'acknowledged': return 'warning'
    case 'resolved': return 'success'
    default: return 'default'
  }
}

function formatDateTime(dateString: string) {
  return new Date(dateString).toLocaleString()
}

function formatTimeToBreach(minutes?: number) {
  if (!minutes) return 'N/A'
  if (minutes < 60) return `${minutes} minutes`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours < 24) return mins > 0 ? `${hours}h ${mins}m` : `${hours} hours`
  const days = Math.floor(hours / 24)
  return `${days} days ${hours % 24}h`
}

export function AlertDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: alert, isLoading } = useAlert(id || '')

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!alert) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Alert not found</p>
        <Link to="/alerts" className="text-blue-600 hover:underline mt-2 inline-block">
          Back to Alerts
        </Link>
      </div>
    )
  }

  return (
    <div>
      <Link to="/alerts" className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6">
        <ArrowLeft className="w-4 h-4" />
        Back to Alerts
      </Link>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{alert.title}</h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge variant={getSeverityVariant(alert.severity)}>
              {alert.severity}
            </Badge>
            <Badge variant={getStatusVariant(alert.status)}>
              {alert.status}
            </Badge>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Description</h2>
            </CardHeader>
            <CardBody>
              <p className="text-gray-700">{alert.description}</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Timeline</h2>
            </CardHeader>
            <CardBody>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-red-100 rounded-full">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Alert Created</p>
                    <p className="text-sm text-gray-500">{formatDateTime(alert.createdAt)}</p>
                  </div>
                </div>

                {alert.acknowledgedAt && (
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-amber-100 rounded-full">
                      <CheckCircle className="w-4 h-4 text-amber-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Alert Acknowledged</p>
                      <p className="text-sm text-gray-500">{formatDateTime(alert.acknowledgedAt)}</p>
                    </div>
                  </div>
                )}

                {alert.resolvedAt && (
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-green-100 rounded-full">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Alert Resolved</p>
                      <p className="text-sm text-gray-500">{formatDateTime(alert.resolvedAt)}</p>
                    </div>
                  </div>
                )}
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold">Details</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <div className="flex items-center gap-3">
                <Server className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm text-gray-500">Component</p>
                  <p className="font-medium text-gray-900">{alert.componentName}</p>
                </div>
              </div>

              {alert.timeToBreach !== undefined && (
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Time to Breach</p>
                    <p className="font-medium text-gray-900">{formatTimeToBreach(alert.timeToBreach)}</p>
                  </div>
                </div>
              )}

              {alert.confidenceInterval && (
                <div className="flex items-center gap-3">
                  <Gauge className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-sm text-gray-500">Confidence Interval</p>
                    <p className="font-medium text-gray-900">
                      {alert.confidenceInterval.lower}% - {alert.confidenceInterval.upper}%
                    </p>
                  </div>
                </div>
              )}
            </CardBody>
          </Card>

          {alert.status !== 'resolved' && (
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold">Actions</h2>
              </CardHeader>
              <CardBody className="space-y-3">
                {alert.status === 'active' && (
                  <Button className="w-full">Acknowledge Alert</Button>
                )}
                <Button variant="outline" className="w-full">
                  View Runbook
                </Button>
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}