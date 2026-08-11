import { TrendingUp, Clock, Gauge } from 'lucide-react'
import { Card, CardBody, Badge } from './index'
import type { Prediction } from '../types'

interface PredictiveAlertCardProps {
  prediction: Prediction
}

function formatTimeToBreach(minutes: number) {
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours < 24) return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
  const days = Math.floor(hours / 24)
  return `${days}d ${hours % 24}h`
}

export function PredictiveAlertCard({ prediction }: PredictiveAlertCardProps) {
  const getUrgencyColor = (timeToBreach: number) => {
    if (timeToBreach < 30) return 'text-red-600 bg-red-50'
    if (timeToBreach < 60) return 'text-amber-600 bg-amber-50'
    return 'text-blue-600 bg-blue-50'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600'
    if (confidence >= 60) return 'text-amber-600'
    return 'text-red-600'
  }

  return (
    <Card>
      <CardBody>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{prediction.componentName}</h3>
              <p className="text-sm text-gray-500 capitalize">{prediction.metric} Prediction</p>
            </div>
          </div>
          <Badge variant={prediction.timeToBreach < 30 ? 'danger' : prediction.timeToBreach < 60 ? 'warning' : 'info'}>
            {prediction.timeToBreach < 60 ? 'Critical' : 'Warning'}
          </Badge>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className={`p-3 rounded-lg ${getUrgencyColor(prediction.timeToBreach)}`}>
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-4 h-4" />
              <span className="text-xs font-medium">Time to Breach</span>
            </div>
            <p className="text-lg font-bold">{formatTimeToBreach(prediction.timeToBreach)}</p>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Gauge className="w-4 h-4 text-gray-500" />
              <span className="text-xs font-medium text-gray-500">Current</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{prediction.currentValue}%</p>
          </div>

          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="w-4 h-4 text-gray-500" />
              <span className="text-xs font-medium text-gray-500">Predicted</span>
            </div>
            <p className="text-lg font-bold text-gray-900">{prediction.predictedValue}%</p>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">
            Threshold: <span className="font-medium text-gray-900">{prediction.threshold}%</span>
          </span>
          <span className={`font-medium ${getConfidenceColor(prediction.confidence)}`}>
            Confidence: {prediction.confidence}%
          </span>
        </div>

        {prediction.confidenceInterval && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Confidence Interval</span>
              <span>{prediction.confidenceInterval.lower}% - {prediction.confidenceInterval.upper}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{
                  width: `${prediction.confidenceInterval.upper - prediction.confidenceInterval.lower}%`,
                  marginLeft: `${prediction.confidenceInterval.lower}%`,
                }}
              />
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  )
}