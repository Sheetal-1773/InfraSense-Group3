import { Database, Server, Zap, HardDrive, Cpu } from 'lucide-react'
import type { Component } from '../types'
import { Card, CardBody, Badge } from './index'

interface HealthScoreCardProps {
  component: Component
  onClick?: () => void
}

const typeIcons = {
  service: Server,
  database: Database,
  api: Zap,
  cache: HardDrive,
  queue: Cpu,
}

function getStatusVariant(status: string) {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'down': return 'danger'
    default: return 'default'
  }
}

function getScoreColor(score: number) {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-amber-500'
  return 'bg-red-500'
}

function MetricBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-500 w-12">{label}</span>
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
      <span className="text-xs text-gray-600 w-8 text-right">{value}%</span>
    </div>
  )
}

export function HealthScoreCard({ component, onClick }: HealthScoreCardProps) {
  const Icon = typeIcons[component.type] || Server

  return (
    <Card
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      <CardBody>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gray-100 rounded-lg">
              <Icon className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{component.name}</h3>
              <p className="text-sm text-gray-500 capitalize">{component.type}</p>
            </div>
          </div>
          <Badge variant={getStatusVariant(component.status)}>
            {component.status}
          </Badge>
        </div>

        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-600">Health Score</span>
              <span className="text-lg font-bold text-gray-900">{component.healthScore}</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${getScoreColor(component.healthScore)} rounded-full transition-all`}
                style={{ width: `${component.healthScore}%` }}
              />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <MetricBar label="CPU" value={component.cpu} color={getScoreColor(component.cpu)} />
          <MetricBar label="Memory" value={component.memory} color={getScoreColor(component.memory)} />
          <MetricBar label="Disk" value={component.disk} color={getScoreColor(component.disk)} />
        </div>

        <p className="text-xs text-gray-400 mt-4">
          Updated: {new Date(component.lastUpdated).toLocaleTimeString()}
        </p>
      </CardBody>
    </Card>
  )
}