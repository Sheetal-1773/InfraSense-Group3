import { Play, ExternalLink } from 'lucide-react'
import { Card, CardHeader, CardBody, Button, Badge } from './index'
import type { RecommendedAction } from '../types'

interface RecommendedActionsProps {
  actions: RecommendedAction[]
}

function getPriorityVariant(priority: string) {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'default'
    default: return 'default'
  }
}

export function RecommendedActions({ actions }: RecommendedActionsProps) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold">Recommended Actions</h3>
      </CardHeader>
      <CardBody className="space-y-3">
        {actions.map(action => (
          <div
            key={action.id}
            className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-medium text-gray-900">{action.title}</h4>
                <Badge variant={getPriorityVariant(action.priority)}>
                  {action.priority}
                </Badge>
              </div>
              <p className="text-sm text-gray-600">{action.description}</p>
            </div>
            <div className="flex items-center gap-2 ml-4">
              {action.runbookUrl && (
                <a
                  href={action.runbookUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
              <Button size="sm" variant="outline">
                <Play className="w-3 h-3 mr-1" />
                Run
              </Button>
            </div>
          </div>
        ))}
      </CardBody>
    </Card>
  )
}