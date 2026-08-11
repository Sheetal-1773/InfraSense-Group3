import { useState } from 'react'
import { TrendingUp, Clock, Activity, Zap } from 'lucide-react'
import { Badge } from '../components'
import { usePredictions } from '../hooks'

function formatTimeRemaining(minutes: number) {
  if (minutes < 60) return `${Math.round(minutes)}m`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return `${hours}h ${mins}m`
}

function PredictionCard({ prediction, isSelected, onClick }: { prediction: any; isSelected: boolean; onClick: () => void }) {
  const getUrgency = (timeToBreach: number) => {
    if (timeToBreach < 30) return { color: 'red', label: 'Critical' }
    if (timeToBreach < 60) return { color: 'orange', label: 'Warning' }
    return { color: 'gray', label: 'Monitor' }
  }
  const urgency = getUrgency(prediction.timeToBreach)

  return (
    <div 
      onClick={onClick}
      className={`p-4 rounded-lg border cursor-pointer transition-all ${
        isSelected 
          ? 'border-[#FF7900] bg-white shadow-sm' 
          : 'border-[#E5E5E5] bg-white hover:border-[#8A8A8A]'
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Clock className={`w-4 h-4 ${urgency.color === 'red' ? 'text-red-600' : urgency.color === 'orange' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'}`} />
          <span className="text-sm font-medium text-[#111111]">{prediction.componentName}</span>
        </div>
        <div className="text-right">
          <span className="text-lg font-semibold text-[#111111]">{formatTimeRemaining(prediction.timeToBreach)}</span>
          <p className="text-xs text-[#8A8A8A]">to breach</p>
        </div>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-[#8A8A8A] capitalize">{prediction.metric} Usage</span>
          <span className="font-medium text-[#111111]">{prediction.currentValue}% → {prediction.predictedValue}%</span>
        </div>
        <div className="h-1.5 bg-[#E5E5E5] rounded-full overflow-hidden">
          <div 
            className="h-full bg-[#FF7900] rounded-full"
            style={{ width: `${Math.min(100, (prediction.currentValue / prediction.threshold) * 100)}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-[#8A8A8A]">
        <span>Confidence: {prediction.confidence}%</span>
        <span>Threshold: {prediction.threshold}%</span>
      </div>
    </div>
  )
}

function PredictionDetail({ prediction }: { prediction: any }) {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h3 className="text-sm font-semibold text-[#111111] mb-4">Prediction Details</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Component</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.componentName}</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Metric</p>
            <p className="text-sm font-medium text-[#111111] capitalize">{prediction.metric}</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Time to Breach</p>
            <p className="text-sm font-semibold text-[#FF7900]">{formatTimeRemaining(prediction.timeToBreach)}</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Confidence Interval</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.confidenceInterval?.lower}% - {prediction.confidenceInterval?.upper}%</p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h3 className="text-sm font-semibold text-[#111111] mb-4">Recommended Actions</h3>
        <div className="space-y-2">
          <div className="flex items-start gap-2 p-2 bg-[#F7F7F7] rounded">
            <Zap className="w-4 h-4 text-[#FF7900] mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[#111111]">Investigate {prediction.metric} usage</p>
              <p className="text-xs text-[#8A8A8A]">Review current processes and identify optimization opportunities</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export function Predictions() {
  const { data: predictions, isLoading } = usePredictions()
  const [selectedPrediction, setSelectedPrediction] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#FF7900]"></div>
      </div>
    )
  }

  const selected = predictions?.find(p => p.id === selectedPrediction)

  return (
    <div className="bg-white min-h-screen">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-[#111111]">Predictions</h1>
            <p className="text-sm text-[#8A8A8A] mt-1">AI-powered early warning system</p>
          </div>
          <Badge variant="warning">{predictions?.length ?? 0} active predictions</Badge>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <h2 className="text-sm font-semibold text-[#111111] mb-4">All Predictions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {predictions?.map(prediction => (
                <PredictionCard 
                  key={prediction.id} 
                  prediction={prediction}
                  isSelected={selectedPrediction === prediction.id}
                  onClick={() => setSelectedPrediction(prediction.id)}
                />
              ))}
              {predictions?.length === 0 && (
                <div className="col-span-2 py-12 text-center bg-white border border-[#E5E5E5] rounded-lg">
                  <TrendingUp className="w-8 h-8 mx-auto mb-2 text-[#E5E5E5]" />
                  <p className="text-[#8A8A8A]">No predictions available</p>
                </div>
              )}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold text-[#111111] mb-4">Details</h2>
            {selected ? (
              <PredictionDetail prediction={selected} />
            ) : (
              <div className="py-12 text-center bg-white border border-[#E5E5E5] rounded-lg border-dashed">
                <Activity className="w-8 h-8 mx-auto mb-2 text-[#E5E5E5]" />
                <p className="text-sm text-[#8A8A8A]">Select a prediction to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}