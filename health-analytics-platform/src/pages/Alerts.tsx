import { useState, useMemo } from 'react'
import { useAlerts, useAcknowledgeAlert, useResolveAlert } from '../hooks'
import { Badge, Button } from '../components'
import { CheckCircle, Activity, Zap, X, Clock, AlertTriangle, ArrowRight, Info } from 'lucide-react'

function getStatusVariant(status: string) {
  switch (status) {
    case 'active': return 'danger'
    case 'acknowledged': return 'warning'
    case 'resolved': return 'success'
    default: return 'default'
  }
}

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${Math.floor(diffHours / 24)}d ago`
}

function formatTimeRemaining(minutes: number) {
  if (minutes < 60) return `${Math.round(minutes)}m`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return `${hours}h ${mins}m`
}

type TabType = 'predictive' | 'reactive'
type StatusFilter = 'all' | 'active' | 'acknowledged' | 'resolved'
type SeverityFilter = 'all' | 'critical' | 'warning' | 'info'

export function Alerts() {
  const { data: alerts, isLoading } = useAlerts()
  const acknowledgeMutation = useAcknowledgeAlert()
  const resolveMutation = useResolveAlert()
  const [activeTab, setActiveTab] = useState<TabType>('predictive')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all')
  const [selectedAlert, setSelectedAlert] = useState<any>(null)

  const predictiveAlerts = useMemo(() => {
    return alerts?.filter(a => a.timeToBreach !== undefined) ?? []
  }, [alerts])

  const reactiveAlerts = useMemo(() => {
    let result = alerts?.filter(a => a.timeToBreach === undefined) ?? []
    
    if (statusFilter !== 'all') {
      result = result.filter(a => a.status === statusFilter)
    }
    if (severityFilter !== 'all') {
      result = result.filter(a => a.severity === severityFilter)
    }
    
    return result
  }, [alerts, statusFilter, severityFilter])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#FF7900]"></div>
      </div>
    )
  }

  return (
    <div className="bg-white min-h-screen">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-[#111111]">Alerts</h1>
            <p className="text-sm text-[#8A8A8A] mt-1">Predictive and reactive alert management</p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="warning">{predictiveAlerts.length} predictive</Badge>
            <Badge variant="danger">{reactiveAlerts.filter(a => a.status === 'active').length} active</Badge>
          </div>
        </div>

        <div className="flex gap-6 border-b border-[#E5E5E5] bg-white">
          <button
            onClick={() => setActiveTab('predictive')}
            className={`flex items-center gap-2 px-1 py-4 border-b-2 transition-colors ${
              activeTab === 'predictive'
                ? 'border-[#FF7900] text-[#111111]'
                : 'border-transparent text-[#8A8A8A] hover:text-[#333333]'
            }`}
          >
            <Zap className="w-4 h-4" />
            <span className="text-sm font-medium">Predictive Alerts</span>
            <span className="ml-1 px-2 py-0.5 bg-[#FF7900]/10 text-[#FF7900] rounded-full text-xs">
              {predictiveAlerts.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('reactive')}
            className={`flex items-center gap-2 px-1 py-4 border-b-2 transition-colors ${
              activeTab === 'reactive'
                ? 'border-[#FF7900] text-[#111111]'
                : 'border-transparent text-[#8A8A8A] hover:text-[#333333]'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span className="text-sm font-medium">Active/Reactive Alerts</span>
            <span className="ml-1 px-2 py-0.5 bg-red-100 text-red-600 rounded-full text-xs">
              {reactiveAlerts.filter(a => a.status === 'active').length}
            </span>
          </button>
        </div>

        {activeTab === 'predictive' && (
          <div className="bg-white border border-[#E5E5E5] rounded-lg">
            <div className="p-4 border-b border-[#E5E5E5]">
              <h2 className="text-lg font-semibold text-[#111111]">Predictive Alerts</h2>
              <p className="text-sm text-[#8A8A8A]">AI-powered predictions that alert you BEFORE issues become incidents</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[#E5E5E5] bg-[#F7F7F7]">
                    <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Severity</th>
                    <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Alert</th>
                    <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Component</th>
                    <th className="text-right text-xs font-medium text-[#8A8A8A] py-3 px-4">Current Value</th>
                    <th className="text-right text-xs font-medium text-[#8A8A8A] py-3 px-4">Predicted Threshold</th>
                    <th className="text-right text-xs font-medium text-[#8A8A8A] py-3 px-4">Time to Breach</th>
                    <th className="text-right text-xs font-medium text-[#8A8A8A] py-3 px-4">Confidence</th>
                    <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Status</th>
                    <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Impact</th>
                  </tr>
                </thead>
                <tbody>
                  {predictiveAlerts.map(alert => (
                    <tr 
                      key={alert.id} 
                      onClick={() => setSelectedAlert(alert)}
                      className="border-b border-[#E5E5E5] last:border-0 hover:bg-[#FFF4E6] cursor-pointer"
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${
                            alert.severity === 'critical' ? 'bg-red-600' : 
                            alert.severity === 'warning' ? 'bg-[#FF7900]' : 'bg-[#8A8A8A]'
                          }`}></span>
                          <span className="text-sm font-medium text-[#111111] capitalize">{alert.severity}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-sm font-medium text-[#111111]">{alert.title}</span>
                      </td>
                      <td className="py-3 px-4 text-sm text-[#8A8A8A]">{alert.componentName}</td>
                      <td className="py-3 px-4 text-sm text-[#111111] text-right">{alert.confidenceInterval?.lower || 0}%</td>
                      <td className="py-3 px-4 text-sm text-[#111111] text-right font-medium">{alert.confidenceInterval?.upper || 0}%</td>
                      <td className="py-3 px-4 text-sm text-right">
                        <span className={`font-medium ${alert.timeToBreach && alert.timeToBreach < 30 ? 'text-red-600' : alert.timeToBreach && alert.timeToBreach < 60 ? 'text-[#FF7900]' : 'text-[#111111]'}`}>
                          {alert.timeToBreach ? formatTimeRemaining(alert.timeToBreach) : '-'}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-[#8A8A8A] text-right">{alert.confidenceInterval ? `${alert.confidenceInterval.lower}-${alert.confidenceInterval.upper}%` : '-'}</td>
                      <td className="py-3 px-4">
                        <Badge variant={getStatusVariant(alert.status)}>{alert.status}</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`text-xs font-medium ${
                          alert.severity === 'critical' ? 'text-red-600' : 
                          alert.severity === 'warning' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'
                        }`}>
                          {alert.severity === 'critical' ? 'High' : alert.severity === 'warning' ? 'Medium' : 'Low'}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {predictiveAlerts.length === 0 && (
                    <tr>
                      <td colSpan={9} className="py-12 text-center text-[#8A8A8A]">
                        <Zap className="w-8 h-8 mx-auto mb-2 text-[#E5E5E5]" />
                        <p>No predictive alerts</p>
                        <p className="text-xs">All systems operating within normal parameters</p>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'reactive' && (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-4 bg-white p-4 border border-[#E5E5E5] rounded-lg">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
                className="px-3 py-1.5 border border-[#E5E5E5] rounded text-sm focus:outline-none focus:ring-1 focus:ring-[#FF7900] bg-white"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="acknowledged">Acknowledged</option>
                <option value="resolved">Resolved</option>
              </select>

              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value as SeverityFilter)}
                className="px-3 py-1.5 border border-[#E5E5E5] rounded text-sm focus:outline-none focus:ring-1 focus:ring-[#FF7900] bg-white"
              >
                <option value="all">All Severity</option>
                <option value="critical">Critical</option>
                <option value="warning">Warning</option>
                <option value="info">Info</option>
              </select>

              <span className="text-sm text-[#8A8A8A] ml-auto">
                {reactiveAlerts.length} alerts
              </span>
            </div>

            <div className="bg-white border border-[#E5E5E5] rounded-lg">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[#E5E5E5] bg-[#F7F7F7]">
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Severity</th>
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Alert</th>
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Component</th>
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Status</th>
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Age</th>
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Impact</th>
                      <th className="text-left text-xs font-medium text-[#8A8A8A] py-3 px-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reactiveAlerts.map(alert => (
                      <tr 
                        key={alert.id} 
                        onClick={() => setSelectedAlert(alert)}
                        className="border-b border-[#E5E5E5] last:border-0 hover:bg-[#FFF4E6] cursor-pointer"
                      >
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${
                              alert.severity === 'critical' ? 'bg-red-600' : 
                              alert.severity === 'warning' ? 'bg-[#FF7900]' : 'bg-[#8A8A8A]'
                            }`}></span>
                            <span className="text-sm font-medium text-[#111111] capitalize">{alert.severity}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div>
                            <p className="text-sm font-medium text-[#111111]">{alert.title}</p>
                            <p className="text-xs text-[#8A8A8A]">{alert.description}</p>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm text-[#8A8A8A]">{alert.componentName}</td>
                        <td className="py-3 px-4">
                          <Badge variant={getStatusVariant(alert.status)}>{alert.status}</Badge>
                        </td>
                        <td className="py-3 px-4 text-sm text-[#8A8A8A]">
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatTimeAgo(alert.createdAt)}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`text-xs font-medium ${
                            alert.severity === 'critical' ? 'text-red-600' : 
                            alert.severity === 'warning' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'
                          }`}>
                            {alert.severity === 'critical' ? 'High' : alert.severity === 'warning' ? 'Medium' : 'Low'}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                            {alert.status === 'active' && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => acknowledgeMutation.mutate(alert.id)}
                              >
                                Acknowledge
                              </Button>
                            )}
                            {alert.status === 'acknowledged' && (
                              <Button
                                size="sm"
                                variant="primary"
                                onClick={() => resolveMutation.mutate(alert.id)}
                              >
                                Resolve
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                    {reactiveAlerts.length === 0 && (
                      <tr>
                        <td colSpan={7} className="py-12 text-center text-[#8A8A8A]">
                          <CheckCircle className="w-8 h-8 mx-auto mb-2 text-green-500" />
                          <p>No active alerts</p>
                          <p className="text-xs">All systems operating normally</p>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      {selectedAlert && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedAlert(null)}>
          <div className="bg-white rounded-xl w-[70%] max-w-4xl h-[85%] mx-4 flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between p-6 border-b border-[#E5E5E5]">
              <div className="flex items-center gap-4">
                <div className={`p-4 rounded-lg ${
                  selectedAlert.severity === 'critical' ? 'bg-red-50' :
                  selectedAlert.severity === 'warning' ? 'bg-[#FF7900]/10' : 'bg-gray-50'
                }`}>
                  <AlertTriangle className={`w-8 h-8 ${
                    selectedAlert.severity === 'critical' ? 'text-red-600' :
                    selectedAlert.severity === 'warning' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'
                  }`} />
                </div>
                <div>
                  <h3 className="text-2xl font-semibold text-[#111111]">{selectedAlert.title}</h3>
                  <p className="text-base text-[#8A8A8A] capitalize">{selectedAlert.severity} Alert</p>
                </div>
              </div>
              <button onClick={() => setSelectedAlert(null)} className="p-2 hover:bg-[#F7F7F7] rounded-lg">
                <X className="w-6 h-6 text-[#8A8A8A]" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                <div className="flex items-center justify-between p-5 bg-[#F7F7F7] rounded-lg">
                  <div>
                    <p className="text-base text-[#8A8A8A] mb-2">Status</p>
                    <Badge variant={getStatusVariant(selectedAlert.status)} className="mt-1">
                      {selectedAlert.status}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-base text-[#8A8A8A] mb-2">Severity</p>
                    <p className={`text-2xl font-bold ${
                      selectedAlert.severity === 'critical' ? 'text-red-600' :
                      selectedAlert.severity === 'warning' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'
                    }`}>
                      {selectedAlert.severity.charAt(0).toUpperCase() + selectedAlert.severity.slice(1)}
                    </p>
                  </div>
                </div>

                <div className="p-5 bg-[#F7F7F7] rounded-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <Info className="w-5 h-5 text-[#8A8A8A]" />
                    <p className="text-lg font-medium text-[#111111]">Description</p>
                  </div>
                  <p className="text-base text-[#111111]">{selectedAlert.description || 'No description available'}</p>
                </div>

                <div className="p-5 bg-[#F7F7F7] rounded-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <Activity className="w-5 h-5 text-[#8A8A8A]" />
                    <p className="text-lg font-medium text-[#111111]">Affected Component</p>
                  </div>
                  <p className="text-xl font-semibold text-[#111111]">{selectedAlert.componentName}</p>
                </div>

                <div className="grid grid-cols-2 gap-5">
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <div className="flex items-center gap-3 mb-3">
                      <Clock className="w-5 h-5 text-[#8A8A8A]" />
                      <p className="text-base text-[#8A8A8A]">Alert Age</p>
                    </div>
                    <p className="text-2xl font-bold text-[#111111]">{formatTimeAgo(selectedAlert.createdAt)}</p>
                  </div>
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <div className="flex items-center gap-3 mb-3">
                      <AlertTriangle className="w-5 h-5 text-[#8A8A8A]" />
                      <p className="text-base text-[#8A8A8A]">Impact Level</p>
                    </div>
                    <p className={`text-2xl font-bold ${
                      selectedAlert.severity === 'critical' ? 'text-red-600' :
                      selectedAlert.severity === 'warning' ? 'text-[#FF7900]' : 'text-[#8A8A8A]'
                    }`}>
                      {selectedAlert.severity === 'critical' ? 'High' : selectedAlert.severity === 'warning' ? 'Medium' : 'Low'}
                    </p>
                  </div>
                </div>

                {selectedAlert.timeToBreach && (
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <div className="flex items-center gap-3 mb-3">
                      <Zap className="w-5 h-5 text-[#FF7900]" />
                      <p className="text-base text-[#8A8A8A]">Time to Breach</p>
                    </div>
                    <p className="text-2xl font-bold text-[#FF7900]">{formatTimeRemaining(selectedAlert.timeToBreach)}</p>
                  </div>
                )}

                <div className="p-5 bg-[#FFF4E6] border border-[#FF7900]/20 rounded-lg">
                  <div className="flex items-center gap-3 mb-3">
                    <ArrowRight className="w-5 h-5 text-[#FF7900]" />
                    <p className="text-lg font-semibold text-[#111111]">Recommended Action</p>
                  </div>
                  <p className="text-base text-[#111111]">
                    {selectedAlert.severity === 'critical' 
                      ? 'Immediate action required. Investigate the component and underlying infrastructure for root cause.'
                      : selectedAlert.severity === 'warning'
                      ? 'Monitor the component closely. Prepare for potential escalation if conditions worsen.'
                      : 'Continue monitoring. No immediate action required.'}
                  </p>
                </div>

                <div className="p-5 bg-[#F7F7F7] rounded-lg">
                  <p className="text-base text-[#8A8A8A] mb-3">Alert ID</p>
                  <p className="text-sm text-[#111111] font-mono bg-white p-3 rounded border border-[#E5E5E5]">{selectedAlert.id}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}