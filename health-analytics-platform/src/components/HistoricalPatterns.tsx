import { History, AlertTriangle, CheckCircle } from 'lucide-react'
import { Card, CardHeader, CardBody, Badge } from './index'

interface HistoricalPattern {
  id: string
  date: string
  similarity: number
  outcome: 'resolved' | 'escalated' | 'ignored'
  duration: string
}

interface HistoricalPatternsProps {
  componentName?: string
  metric?: string
}

const mockPatterns: HistoricalPattern[] = [
  {
    id: 'pat-001',
    date: '2024-01-15',
    similarity: 92,
    outcome: 'resolved',
    duration: '2h 30m',
  },
  {
    id: 'pat-002',
    date: '2024-01-08',
    similarity: 87,
    outcome: 'resolved',
    duration: '1h 45m',
  },
  {
    id: 'pat-003',
    date: '2023-12-20',
    similarity: 78,
    outcome: 'escalated',
    duration: '4h 15m',
  },
]

export function HistoricalPatterns({ componentName: _componentName, metric: _metric }: HistoricalPatternsProps) {
  const getOutcomeVariant = (outcome: string) => {
    switch (outcome) {
      case 'resolved': return 'success'
      case 'escalated': return 'danger'
      case 'ignored': return 'warning'
      default: return 'default'
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-gray-500" />
          <h3 className="text-lg font-semibold">Historical Patterns</h3>
        </div>
      </CardHeader>
      <CardBody className="p-0">
        <div className="divide-y divide-gray-200">
          {mockPatterns.map(pattern => (
            <div key={pattern.id} className="px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-lg font-bold text-gray-900">{pattern.similarity}%</p>
                  <p className="text-xs text-gray-500">match</p>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{pattern.date}</p>
                  <p className="text-sm text-gray-500">Duration: {pattern.duration}</p>
                </div>
              </div>
              <Badge variant={getOutcomeVariant(pattern.outcome)}>
                {pattern.outcome === 'resolved' && <CheckCircle className="w-3 h-3 mr-1" />}
                {pattern.outcome === 'escalated' && <AlertTriangle className="w-3 h-3 mr-1" />}
                {pattern.outcome}
              </Badge>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  )
}