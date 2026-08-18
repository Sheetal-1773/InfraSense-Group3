import { useState, useMemo } from 'react'
import { Network, AlertTriangle, Server, Database, Cpu, Activity, Zap } from 'lucide-react'
import { Badge } from '../components'
import { useCorrelationGroups, useComponents, useAlerts } from '../hooks'

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
  const { data: correlationGroups, isLoading: correlationsLoading } = useCorrelationGroups()
  const { data: components, isLoading: componentsLoading } = useComponents()
  const { data: alerts, isLoading: alertsLoading } = useAlerts()
  const [selectedIncident, setSelectedIncident] = useState<string | null>(null)

  const isLoading = correlationsLoading || componentsLoading || alertsLoading

  const dynamicIncidents = useMemo(() => {
    const incidents: IncidentDetail[] = []
    const now = new Date()
    
    if (!components || components.length === 0) return incidents

    const criticalComponents = components.filter((c: any) => 
      c.status === 'critical' || c.status === 'down' || (c.health_score ?? c.healthScore ?? 100) < 40
    )
    const degradedComponents = components.filter((c: any) => 
      c.status === 'degraded' || c.status === 'warning' || ((c.health_score ?? c.healthScore ?? 100) >= 40 && (c.health_score ?? c.healthScore ?? 100) < 70)
    )

    if (criticalComponents.length > 0) {
      const primaryCritical = criticalComponents[0]
      const compType = primaryCritical.type || primaryCritical.category || 'unknown'
      
      let rootCause = ''
      let recommendedAction = ''
      let title = ''
      
      if (compType === 'database' || compType === 'db') {
        rootCause = `Database ${primaryCritical.name} is experiencing critical issues affecting query performance and connection handling`
        recommendedAction = 'Investigate database queries, check connection pool settings, and review recent schema changes'
        title = `${primaryCritical.name} Critical`
      } else if (compType === 'application' || compType === 'api') {
        rootCause = `Application ${primaryCritical.name} is degraded due to resource constraints or upstream dependencies`
        recommendedAction = 'Check application logs, review resource allocation, and verify upstream service availability'
        title = `${primaryCritical.name} Degradation`
      } else if (compType === 'server') {
        rootCause = `Server ${primaryCritical.name} is experiencing hardware or resource issues`
        recommendedAction = 'Check server health metrics, review system logs, and consider resource scaling'
        title = `${primaryCritical.name} Health Issue`
      } else {
        rootCause = `Component ${primaryCritical.name} is in critical state affecting dependent services`
        recommendedAction = 'Investigate component health and address root cause immediately'
        title = `${primaryCritical.name} Critical`
      }

      const affectedComps = [primaryCritical.name, ...degradedComponents.slice(0, 3).map((c: any) => c.name)]
      const dependencyChain = [
        { name: 'Load Balancer', type: 'network', status: 'healthy' },
        { name: primaryCritical.name, type: compType, status: primaryCritical.status },
        ...degradedComponents.slice(0, 2).map((c: any) => ({ 
          name: c.name, 
          type: c.type || c.category || 'unknown', 
          status: c.status 
        }))
      ]

      const relatedAlerts = alerts?.filter((a: any) => 
        a.componentId === primaryCritical.id || a.component_name === primaryCritical.name
      ).slice(0, 3).map((a: any) => ({
        id: a.id,
        title: a.title,
        severity: a.severity
      })) || []

      incidents.push({
        id: `inc-crit-${primaryCritical.id}`,
        title,
        severity: 'critical',
        status: 'active',
        rootCause,
        businessImpact: `Service degradation affecting ${affectedComps.length} dependent components`,
        affectedComponents: affectedComps,
        dependencyChain,
        relatedAlerts,
        timeline: [
          { time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), event: 'Issue detected and logged' },
          { time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), event: 'Alert generated for component health' },
          { time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), event: 'Correlation analysis initiated' },
        ],
        recommendedAction
      })
    }

    if (degradedComponents.length > 0 && incidents.length === 0) {
      const primaryDegraded = degradedComponents[0]
      const compType = primaryDegraded.type || primaryDegraded.category || 'unknown'
      
      incidents.push({
        id: `inc-deg-${primaryDegraded.id}`,
        title: `${primaryDegraded.name} Performance Degradation`,
        severity: 'warning',
        status: 'investigating',
        rootCause: `Component ${primaryDegraded.name} showing degraded performance metrics`,
        businessImpact: 'Potential impact on dependent services if condition worsens',
        affectedComponents: [primaryDegraded.name],
        dependencyChain: [
          { name: 'Network', type: 'network', status: 'healthy' },
          { name: primaryDegraded.name, type: compType, status: 'degraded' },
        ],
        relatedAlerts: [],
        timeline: [
          { time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), event: 'Degradation detected' },
          { time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), event: 'Monitoring for changes' },
        ],
        recommendedAction: 'Continue monitoring and prepare contingency actions if needed'
      })
    }

    if (correlationGroups && correlationGroups.length > 0) {
      correlationGroups.slice(0, 2).forEach((group: any) => {
        incidents.push({
          id: `inc-corr-${group.id}`,
          title: group.name || 'Correlation Detected',
          severity: 'info',
          status: 'investigating',
          rootCause: group.rootCause || 'Multiple components showing correlated behavior',
          businessImpact: 'Potential cascading effect across infrastructure',
          affectedComponents: group.components || [],
          dependencyChain: (group.components || []).slice(0, 4).map((name: string, idx: number) => ({
            name,
            type: 'unknown',
            status: idx === 0 ? 'degraded' : 'healthy'
          })),
          relatedAlerts: [],
          timeline: [
            { time: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), event: 'Correlation identified' },
          ],
          recommendedAction: 'Analyze correlation pattern and implement preventive measures'
        })
      })
    }

    return incidents
  }, [components, alerts, correlationGroups])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#FF7900]"></div>
      </div>
    )
  }

  const selected = dynamicIncidents.find(i => i.id === selectedIncident) || dynamicIncidents[0]

  return (
    <div className="bg-white min-h-screen">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-[#111111]">Correlations</h1>
            <p className="text-sm text-[#8A8A8A]">Incident analysis and dependency mapping</p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="danger">{dynamicIncidents.filter(i => i.status === 'active').length} active</Badge>
            <Badge variant="warning">{dynamicIncidents.filter(i => i.status === 'investigating').length} investigating</Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <h2 className="text-sm font-semibold text-[#111111] mb-4">Incidents</h2>
            <div className="space-y-2">
              {dynamicIncidents.map(incident => (
                <IncidentCard 
                  key={incident.id} 
                  incident={incident}
                  isSelected={selectedIncident === incident.id}
                  onClick={() => setSelectedIncident(incident.id)}
                />
              ))}
              {dynamicIncidents.length === 0 && (
                <div className="py-8 text-center text-[#8A8A8A]">
                  <Network className="w-8 h-8 mx-auto mb-2 text-[#E5E5E5]" />
                  <p className="text-sm">No correlations detected</p>
                  <p className="text-xs">All systems operating normally</p>
                </div>
              )}
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