import { useState } from 'react'
import { Network, AlertTriangle, Server, Database, Cpu, Activity, Zap } from 'lucide-react'
import { Badge } from '../components'
import { useCorrelationGroups } from '../hooks'

interface IncidentDetail {
  id: string
  title: string
  severity: 'critical' | 'warning' | 'info'
  status: 'active' | 'investigating' | 'resolved'
  rootCause: string
  businessImpact: string
  affectedComponents: string[]
  dependencyChain: { name: string; type: string; status: string }[]
  relatedAlerts: { id: string; title: string; severity: string }[]
  timeline: { time: string; event: string }[]
  recommendedAction: string
}

const mockIncidents: IncidentDetail[] = [
  {
    id: 'inc-001',
    title: 'Payment Service Degradation',
    severity: 'critical',
    status: 'active',
    rootCause: 'Database connection pool exhaustion due to high transaction volume',
    businessImpact: 'Customer checkout failures, revenue impact potential',
    affectedComponents: ['Payment Service', 'PostgreSQL Primary', 'Message Queue'],
    dependencyChain: [
      { name: 'Load Balancer', type: 'network', status: 'healthy' },
      { name: 'APP-01 Server', type: 'server', status: 'degraded' },
      { name: 'PostgreSQL Primary', type: 'database', status: 'critical' },
      { name: 'Payment API', type: 'api', status: 'degraded' },
      { name: 'Customer Checkout', type: 'service', status: 'degraded' },
    ],
    relatedAlerts: [
      { id: 'alert-001', title: 'High CPU Usage - Payment Service', severity: 'warning' },
      { id: 'alert-002', title: 'Memory Pressure - PostgreSQL', severity: 'warning' },
      { id: 'alert-004', title: 'Service Degraded - Payment Service', severity: 'critical' },
    ],
    timeline: [
      { time: '10:30', event: 'Alert triggered: High CPU on Payment Service' },
      { time: '10:35', event: 'Database connection pool at 85%' },
      { time: '10:42', event: 'Payment API response time increased' },
      { time: '10:45', event: 'Customer checkout failures detected' },
    ],
    recommendedAction: 'Scale up database connection pool and investigate long-running queries',
  },
  {
    id: 'inc-002',
    title: 'API Gateway Latency',
    severity: 'warning',
    status: 'investigating',
    rootCause: 'Auth service latency due to certificate validation delays',
    businessImpact: 'Slower user authentication, increased login failures',
    affectedComponents: ['API Gateway', 'Auth Service'],
    dependencyChain: [
      { name: 'External Network', type: 'network', status: 'healthy' },
      { name: 'API Gateway', type: 'network', status: 'degraded' },
      { name: 'Auth Service', type: 'service', status: 'degraded' },
      { name: 'User Sessions', type: 'cache', status: 'healthy' },
    ],
    relatedAlerts: [
      { id: 'alert-005', title: 'API Response Time Increased', severity: 'warning' },
    ],
    timeline: [
      { time: '09:15', event: 'Auth service certificate expiring soon' },
      { time: '09:20', event: 'Increased latency detected' },
      { time: '09:30', event: 'Investigation started' },
    ],
    recommendedAction: 'Renew SSL certificate and review auth service configuration',
  },
]

function DependencyChain({ chain }: { chain: { name: string; type: string; status: string }[] }) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'network': return Network
      case 'server': return Server
      case 'database': return Database
      case 'api': return Cpu
      case 'cache': return Activity
      default: return Server
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500'
      case 'degraded': return 'bg-[#FF7900]'
      case 'critical': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-1">
      {chain.map((item, idx) => {
        const Icon = getIcon(item.type)
        return (
          <div key={idx} className="flex items-center gap-3">
            {idx > 0 && (
              <div className="absolute left-4 w-0.5 h-4 bg-[#E5E5E5] -mt-4"></div>
            )}
            <div className="relative flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${getStatusColor(item.status)}`}></div>
              <Icon className="w-3 h-3 text-[#8A8A8A]" />
              <span className="text-xs text-[#111111]">{item.name}</span>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function IncidentCard({ incident, isSelected, onClick }: { incident: IncidentDetail; isSelected: boolean; onClick: () => void }) {
  const getSeverityVariant = (severity: string) => {
    switch (severity) {
      case 'critical': return 'danger'
      case 'warning': return 'warning'
      default: return 'info'
    }
  }

  return (
    <div 
      onClick={onClick}
      className={`p-3 rounded-lg border cursor-pointer transition-all ${
        isSelected 
          ? 'border-[#FF7900] bg-white shadow-sm' 
          : 'border-[#E5E5E5] bg-white hover:border-[#8A8A8A]'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <AlertTriangle className={`w-4 h-4 ${
            incident.severity === 'critical' ? 'text-red-600' : 
            incident.severity === 'warning' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'
          }`} />
          <span className="text-sm font-medium text-[#111111]">{incident.title}</span>
        </div>
        <Badge variant={getSeverityVariant(incident.severity)}>
          {incident.severity}
        </Badge>
      </div>

      <div className="flex items-center gap-2 mb-2">
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
          incident.status === 'active' ? 'bg-red-50 text-red-600' : 
          incident.status === 'investigating' ? 'bg-[#FF7900]/10 text-[#FF7900]' : 'bg-green-50 text-green-600'
        }`}>
          {incident.status}
        </span>
        <span className="text-xs text-[#8A8A8A]">
          {incident.affectedComponents.length} components
        </span>
      </div>

      <p className="text-xs text-[#8A8A8A] line-clamp-1">{incident.rootCause}</p>
    </div>
  )
}

function IncidentDetailView({ incident }: { incident: IncidentDetail }) {
  return (
    <div className="space-y-4">
      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-[#111111]">{incident.title}</h3>
            <p className="text-xs text-[#8A8A8A]">Incident ID: {incident.id}</p>
          </div>
          <Badge variant={incident.severity === 'critical' ? 'danger' : incident.severity === 'warning' ? 'warning' : 'info'}>
            {incident.severity}
          </Badge>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div className="p-2 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-0.5">Root Cause</p>
            <p className="text-xs font-medium text-[#111111]">{incident.rootCause}</p>
          </div>
          <div className="p-2 bg-[#F7F7F7] rounded">
            <p className="text-xs text-[#8A8A8A] mb-0.5">Business Impact</p>
            <p className="text-xs font-medium text-[#111111]">{incident.businessImpact}</p>
          </div>
        </div>

        <div className="p-2 bg-[#FF7900]/5 rounded border border-[#FF7900]/20">
          <div className="flex items-center gap-1.5 mb-1">
            <Zap className="w-3 h-3 text-[#FF7900]" />
            <span className="text-xs font-medium text-[#111111]">Recommended Action</span>
          </div>
          <p className="text-xs text-[#8A8A8A]">{incident.recommendedAction}</p>
        </div>
      </div>

      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h4 className="text-xs font-semibold text-[#111111] mb-3">Dependency Chain</h4>
        <div className="relative pl-2">
          <DependencyChain chain={incident.dependencyChain} />
        </div>
      </div>

      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h4 className="text-xs font-semibold text-[#111111] mb-3">Blast Radius</h4>
        <div className="flex flex-wrap gap-1.5">
          {incident.affectedComponents.map((comp, idx) => (
            <span key={idx} className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs font-medium">
              {comp}
            </span>
          ))}
        </div>
        <p className="text-xs text-[#8A8A8A] mt-2">
          {incident.affectedComponents.length} services potentially impacted
        </p>
      </div>

      <div className="bg-white border border-[#E5E5E5] rounded-lg p-4">
        <h4 className="text-xs font-semibold text-[#111111] mb-3">Timeline</h4>
        <div className="space-y-2">
          {incident.timeline.map((event, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-xs font-medium text-[#8A8A8A] w-10">{event.time}</span>
              <div className="w-1.5 h-1.5 rounded-full bg-[#FF7900] mt-1"></div>
              <span className="text-xs text-[#111111]">{event.event}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function Correlations() {
  const { isLoading } = useCorrelationGroups()
  const [selectedIncident, setSelectedIncident] = useState<string | null>(mockIncidents[0]?.id || null)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#FF7900]"></div>
      </div>
    )
  }

  const selected = mockIncidents.find(i => i.id === selectedIncident)

  return (
    <div className="bg-white min-h-screen">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-[#111111]">Correlations</h1>
            <p className="text-sm text-[#8A8A8A]">Incident analysis and dependency mapping</p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="danger">{mockIncidents.filter(i => i.status === 'active').length} active</Badge>
            <Badge variant="warning">{mockIncidents.filter(i => i.status === 'investigating').length} investigating</Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <h2 className="text-sm font-semibold text-[#111111] mb-4">Incidents</h2>
            <div className="space-y-2">
              {mockIncidents.map(incident => (
                <IncidentCard 
                  key={incident.id} 
                  incident={incident}
                  isSelected={selectedIncident === incident.id}
                  onClick={() => setSelectedIncident(incident.id)}
                />
              ))}
            </div>
          </div>

          <div className="lg:col-span-2">
            <h2 className="text-sm font-semibold text-[#111111] mb-4">Incident Details</h2>
            {selected ? (
              <IncidentDetailView incident={selected} />
            ) : (
              <div className="py-12 text-center bg-white border border-[#E5E5E5] rounded-lg border-dashed">
                <Network className="w-8 h-8 mx-auto mb-2 text-[#E5E5E5]" />
                <p className="text-sm text-[#8A8A8A]">Select an incident to view details</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}