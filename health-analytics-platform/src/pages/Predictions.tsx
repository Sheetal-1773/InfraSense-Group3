import { useState } from 'react'
import { TrendingUp, Clock, Activity, Zap } from 'lucide-react'
import { Badge } from '../components'
import { usePredictions } from '../hooks'

function formatTimeRemaining(minutes: number | undefined | null) {
  if (minutes === undefined || minutes === null || isNaN(minutes) || !isFinite(minutes)) return 'N/A'
  if (minutes < 0) return 'Breached'
  if (minutes < 60) return `${Math.round(minutes)}m`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  if (hours >= 24) {
    const days = Math.floor(hours / 24)
    const remainingHours = hours % 24
    return `${days}d ${remainingHours}h`
  }
  return `${hours}h ${mins}m`
}

function PredictionCard({ prediction, isSelected, onClick }: { prediction: any; isSelected: boolean; onClick: () => void }) {
  const timeToBreach = prediction.timeToBreach ?? prediction.time_to_breach_minutes ?? prediction.time_to_breach ?? null
  const getUrgency = (ttb: number | null) => {
    if (ttb === null || isNaN(ttb) || !isFinite(ttb)) return { color: 'gray', label: 'Unknown' }
    if (ttb < 30) return { color: 'red', label: 'Critical' }
    if (ttb < 60) return { color: 'orange', label: 'Warning' }
    return { color: 'gray', label: 'Monitor' }
  }
  const urgency = getUrgency(timeToBreach)

  const currentValue = prediction.currentValue ?? 0
  const predictedValue = prediction.predictedValue ?? 0
  const threshold = prediction.threshold ?? 100

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
          <span className="text-sm font-medium text-[#111111]">{prediction.componentName || 'Unknown'}</span>
        </div>
        <div className="text-right">
          <span className="text-lg font-semibold text-[#111111]">{formatTimeRemaining(timeToBreach)}</span>
          <p className="text-xs text-[#8A8A8A]">to breach</p>
        </div>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-[#8A8A8A] capitalize">{(prediction.metric || 'unknown')} Usage</span>
          <span className="font-medium text-[#111111]">{currentValue.toFixed(1)}% → {predictedValue.toFixed(1)}%</span>
        </div>
        <div className="h-1.5 bg-[#E5E5E5] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#FF7900] rounded-full"
            style={{ width: `${Math.min(100, (currentValue / threshold) * 100)}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-[#8A8A8A]">
        <span>Confidence: {(prediction.confidence ?? 0).toFixed(0)}%</span>
        <span>Threshold: {threshold}%</span>
      </div>
    </div>
  )
}

function PredictionDetail({ prediction }: { prediction: any }) {
  const timeToBreach = prediction.timeToBreach ?? prediction.time_to_breach_minutes ?? prediction.time_to_breach ?? null
  const confidenceInterval = prediction.confidenceInterval

  const getSeverityVariant = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'danger'
      case 'warning': return 'warning'
      default: return 'default'
    }
  }

  const getTrend = (current: number, predicted: number) => {
    if (predicted > current) return 'Increasing'
    if (predicted < current) return 'Decreasing'
    return 'Stable'
  }

  return (
    <div className="space-y-4">
      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h3 className="text-sm font-semibold text-[#111111] mb-4">Prediction Details</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Component</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.componentName || 'Unknown'}</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Metric</p>
            <p className="text-sm font-medium text-[#111111] capitalize">{prediction.metric || 'Unknown'}</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Current Value</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.currentValue ?? 0}%</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Predicted Value</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.predictedValue ?? 0}%</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Threshold</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.threshold ?? 100}%</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Time to Breach</p>
            <p className="text-sm font-semibold text-[#FF7900]">{formatTimeRemaining(timeToBreach)}</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Confidence Level</p>
            <p className="text-sm font-medium text-[#111111]">{prediction.confidence ?? 0}%</p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Confidence Interval</p>
            <p className="text-sm font-medium text-[#111111]">
              {confidenceInterval?.lower !== null ? `${confidenceInterval?.lower}% - ${confidenceInterval?.upper}%` : 'N/A'}
            </p>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Risk/Severity</p>
            <Badge variant={getSeverityVariant(prediction.severity)}>{prediction.severity || 'Unknown'}</Badge>
          </div>
          <div className="p-3 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-1">Trend</p>
            <p className="text-sm font-medium text-[#111111]">{getTrend(prediction.currentValue, prediction.predictedValue)}</p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h3 className="text-sm font-semibold text-[#111111] mb-4">Why This Prediction Was Generated</h3>
        <div className="p-3 bg-[#F7F7F7] rounded">
          <p className="text-sm text-[#111111]">{prediction.explanation || 'No explanation available'}</p>
        </div>
      </div>

      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h3 className="text-sm font-semibold text-[#111111] mb-4">Recommended Actions</h3>
        <div className="space-y-2">
          <div className="flex items-start gap-2 p-2 bg-[#F7F7F7] rounded">
            <Zap className="w-4 h-4 text-[#FF7900] mt-0.5" />
            <div>
              <p className="text-sm font-medium text-[#111111]">{prediction.recommendedAction || 'No action recommended'}</p>
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