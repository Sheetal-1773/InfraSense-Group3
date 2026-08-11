import { Lightbulb, TrendingUp, Clock, Activity } from 'lucide-react'
import { Card, CardHeader, CardBody } from './index'

interface PredictionExplanationPanelProps {
  prediction: {
    componentName: string
    metric: string
    currentValue: number
    predictedValue: number
    timeToThreshold: number
    confidence: number
    threshold?: number
  }
}

export function PredictionExplanationPanel({ prediction }: PredictionExplanationPanelProps) {
  const getExplanation = () => {
    const metric = prediction.metric.toLowerCase()
    
    if (metric === 'cpu') {
      return `The CPU usage for ${prediction.componentName} has been steadily increasing over the past 24 hours. Based on the current trend, it is predicted to reach ${prediction.predictedValue}% within ${prediction.timeToThreshold} minutes, exceeding the ${prediction.threshold || 90}% threshold.`
    }
    
    if (metric === 'memory') {
      return `Memory consumption in ${prediction.componentName} shows a consistent upward pattern. The system is projected to hit ${prediction.predictedValue}% memory usage, which may lead to performance degradation or OOM conditions.`
    }
    
    return `The ${metric} metric for ${prediction.componentName} is trending upward and is expected to breach the threshold within ${prediction.timeToThreshold} minutes.`
  }

  const factors = [
    { icon: TrendingUp, label: 'Trend', value: 'Consistently increasing over 24h' },
    { icon: Clock, label: 'Rate', value: `+${Math.round((prediction.predictedValue - prediction.currentValue) / (prediction.timeToThreshold / 60))}%/hour` },
    { icon: Activity, label: 'Volatility', value: prediction.confidence > 80 ? 'Low' : 'Moderate' },
  ]

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-amber-500" />
          <h3 className="text-lg font-semibold">Prediction Explanation</h3>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        <p className="text-gray-700">{getExplanation()}</p>
        
        <div className="border-t border-gray-200 pt-4">
          <h4 className="text-sm font-medium text-gray-500 mb-3">Contributing Factors</h4>
          <div className="space-y-3">
            {factors.map((factor, index) => (
              <div key={index} className="flex items-center gap-3">
                <factor.icon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">{factor.label}:</span>
                <span className="text-sm font-medium text-gray-900">{factor.value}</span>
              </div>
            ))}
          </div>
        </div>
      </CardBody>
    </Card>
  )
}