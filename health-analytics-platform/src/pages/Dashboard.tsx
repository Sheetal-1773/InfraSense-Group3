import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, Network, Cpu, Zap, Gauge, Layers, AlertTriangle, Server, Database, Clock, ArrowRight, X, Monitor, Play } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { useHealthScore, useComponents, usePredictions, useAlerts, useCorrelationGroups } from '../hooks'
import { getSourcesBreakdown, getSourceCategoryBreakdown } from '../services/api'

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

const ORANGE = '#FF7900'

export function Dashboard() {
  const navigate = useNavigate()
  const { data: healthScore, isLoading: healthLoading } = useHealthScore()
  const { data: components, isLoading: componentsLoading } = useComponents()
  const { data: predictions, isLoading: predictionsLoading } = usePredictions()
  const { data: alerts } = useAlerts()
  const { data: correlations } = useCorrelationGroups()

  const [currentTime, setCurrentTime] = useState(new Date())
  const [selectedPrediction, setSelectedPrediction] = useState<any>(null)
  const [sourcesData, setSourcesData] = useState<any>(null)
  const [sourceCategoryData, setSourceCategoryData] = useState<any>(null)
  const [healthTrendRange, setHealthTrendRange] = useState<'24h' | '7d' | '30d'>('24h')

  useEffect(() => {
    getSourcesBreakdown().then(setSourcesData)
    getSourceCategoryBreakdown().then(setSourceCategoryData)
  }, [])

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])

  const liveComponents = useMemo(() => {
    if (!components) return components
    return components
  }, [components])

  const mergedAlerts = useMemo(() => {
    return alerts || []
  }, [alerts])

  const mergedPredictions = useMemo(() => {
    return predictions || []
  }, [predictions])

  const networkComponents = liveComponents?.filter((c: any) => c.type === 'network' || c.category === 'network') || []
  const networkHealth = networkComponents.length > 0 ? Math.round(networkComponents.reduce((acc, c) => acc + (c.health_score || c.healthScore || 0), 0) / networkComponents.length) : 98
  
  const appComponents = liveComponents?.filter((c: any) => ['api', 'service', 'cache', 'queue', 'application'].includes(c.type || c.category)) || []
  const appHealth = appComponents.length > 0 ? Math.round(appComponents.reduce((acc, c) => acc + (c.health_score || c.healthScore || 0), 0) / appComponents.length) : 94
  
  const dbComponents = liveComponents?.filter((c: any) => c.type === 'database' || c.category === 'database') || []
  const dbHealth = dbComponents.length > 0 ? Math.round(dbComponents.reduce((acc, c) => acc + (c.health_score || c.healthScore || 0), 0) / dbComponents.length) : 96
  
  const serverComponents = liveComponents?.filter((c: any) => c.type === 'server' || c.category === 'server') || []
  const serverHealth = serverComponents.length > 0 ? Math.round(serverComponents.reduce((acc, c) => acc + (c.health_score || c.healthScore || 0), 0) / serverComponents.length) : 97

  const overallHealth = healthScore?.overall ?? 96

  const sourceBreakdown = useMemo(() => {
    if (!sourcesData?.by_provider) return []
    const colors: Record<string, string> = {
      local: '#3B82F6',
      simulated: '#8B5CF6',
      prometheus: '#E11D48'
    }
    return Object.entries(sourcesData.by_provider).map(([source, count]: [string, any]) => ({
      name: source === 'local' ? 'Local' : source === 'simulated' ? 'Simulated' : source.charAt(0).toUpperCase() + source.slice(1),
      source: source,
      count: count,
      icon: source === 'local' ? Monitor : Play,
      color: colors[source] || '#6B7280'
    }))
  }, [sourcesData])

  if (healthLoading || componentsLoading || predictionsLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-2 border-[#FF7900] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-[#8A8A8A]">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const getHealthTrendData = () => {
    const trend = healthScore?.trend
    const overall = healthScore?.overall ?? 85
    
    if (!trend || trend.length === 0) {
      if (healthTrendRange === '24h') {
        return Array.from({ length: 24 }, (_, i) => ({ 
          time: `${i}:00`, 
          score: overall + (Math.random() - 0.5) * 10 
        }))
      } else if (healthTrendRange === '7d') {
        return Array.from({ length: 7 }, (_, i) => ({ 
          time: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i], 
          score: overall + (Math.random() - 0.5) * 15 
        }))
      } else {
        return Array.from({ length: 30 }, (_, i) => ({ 
          time: `${i + 1}`, 
          score: overall + (Math.random() - 0.5) * 12 
        }))
      }
    }
    
    const filteredTrend = trend.filter((point: any) => {
      const pointDate = new Date(point.timestamp)
      const now = new Date()
      if (healthTrendRange === '24h') {
        const hoursDiff = (now.getTime() - pointDate.getTime()) / (1000 * 60 * 60)
        return hoursDiff <= 24
      } else if (healthTrendRange === '7d') {
        const daysDiff = (now.getTime() - pointDate.getTime()) / (1000 * 60 * 60 * 24)
        return daysDiff <= 7
      } else {
        return true
      }
    })
    
    return filteredTrend.map((point: any, idx: number) => {
      const pointDate = new Date(point.timestamp)
      let timeLabel: string
      if (healthTrendRange === '24h') {
        timeLabel = pointDate.getHours() + ':00'
      } else if (healthTrendRange === '7d') {
        timeLabel = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][pointDate.getDay()]
      } else {
        timeLabel = pointDate.getDate().toString()
      }
      return {
        time: timeLabel,
        score: Math.round(point.score),
        predicted: idx > filteredTrend.length - 5 ? Math.round(point.score + (Math.random() - 0.5) * 8) : null,
      }
    })
  }
  
  const chartData = getHealthTrendData()

  const healthDistribution = [
    { name: 'Healthy', value: healthScore?.components?.healthy ?? components?.filter((c: any) => c.status === 'healthy').length ?? 12, color: '#22C55E' },
    { name: 'Warning', value: healthScore?.components?.warning ?? components?.filter((c: any) => c.status === 'degraded').length ?? 3, color: ORANGE },
    { name: 'Critical', value: healthScore?.components?.critical ?? components?.filter((c: any) => c.status === 'critical' || c.status === 'down').length ?? 1, color: '#EF4444' },
  ]

  const categoryHealth = [
    { name: 'Network', health: networkHealth, components: networkComponents.length, color: ORANGE },
    { name: 'Apps', health: appHealth, components: appComponents.length, color: ORANGE },
    { name: 'Databases', health: dbHealth, components: dbComponents.length, color: ORANGE },
    { name: 'Servers', health: serverHealth, components: serverComponents.length, color: ORANGE },
  ]

  const cpuData = Array.from({ length: 12 }, (_, i) => ({
    time: `${i * 10}m`,
    cpu: 30 + Math.random() * 40,
    memory: 40 + Math.random() * 30,
  }))

  const alertData = [
    { name: 'Critical', value: 2, color: '#EF4444' },
    { name: 'Warning', value: 5, color: ORANGE },
    { name: 'Info', value: 8, color: '#8A8A8A' },
  ]

  return (
    <div className="bg-white min-h-screen">
      <div className="p-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-[#111111]">InfraSense Dashboard</h1>
            <p className="text-sm text-[#8A8A8A] mt-1">Real-time monitoring with predictive insights</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-[#FFF4E6] rounded-full">
              <span className="w-2 h-2 rounded-full bg-[#FF7900] animate-pulse"></span>
              <span className="text-sm font-medium text-[#FF7900]">Live</span>
            </div>
            <p className="text-xs text-[#8A8A8A]">Updated: {currentTime.toLocaleTimeString()}</p>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              {overallHealth >= 90 ? (
                <TrendingUp className="w-5 h-5 text-green-600" />
              ) : overallHealth >= 70 ? (
                <Gauge className="w-5 h-5 text-yellow-500" />
              ) : (
                <Gauge className="w-5 h-5 text-red-600" />
              )}
              <span className="text-sm font-medium text-[#111111]">Overall Health</span>
            </div>
            <p className="text-3xl font-bold text-[#111111] mb-2">{overallHealth}%</p>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${overallHealth >= 90 ? 'bg-green-500' : overallHealth >= 70 ? 'bg-[#FF7900]' : 'bg-red-500'}`}
                style={{ width: `${overallHealth}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-[#8A8A8A]">
              <span>{components?.length || 0} components</span>
              <span className={`font-medium ${
                overallHealth >= 90 ? 'text-green-600' : 
                overallHealth >= 70 ? 'text-[#FF7900]' : 'text-red-600'
              }`}>
                {overallHealth >= 90 ? 'Healthy' : overallHealth >= 70 ? 'Warning' : 'Critical'}
              </span>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Network className="w-5 h-5 text-[#8A8A8A]" />
              <span className="text-sm font-medium text-[#111111]">Network</span>
            </div>
            <p className="text-3xl font-bold text-[#111111] mb-2">{networkHealth}%</p>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${networkHealth >= 90 ? 'bg-green-500' : networkHealth >= 70 ? 'bg-[#FF7900]' : 'bg-red-500'}`}
                style={{ width: `${networkHealth}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-[#8A8A8A]">
              <span>{networkComponents.length} components</span>
              <span className={`font-medium ${
                networkHealth >= 90 ? 'text-green-600' : 
                networkHealth >= 70 ? 'text-[#FF7900]' : 'text-red-600'
              }`}>
                {networkHealth >= 90 ? 'Good' : networkHealth >= 70 ? 'Degraded' : 'Critical'}
              </span>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Cpu className="w-5 h-5 text-[#8A8A8A]" />
              <span className="text-sm font-medium text-[#111111]">Applications</span>
            </div>
            <p className="text-3xl font-bold text-[#111111] mb-2">{appHealth}%</p>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${appHealth >= 90 ? 'bg-green-500' : appHealth >= 70 ? 'bg-[#FF7900]' : 'bg-red-500'}`}
                style={{ width: `${appHealth}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-[#8A8A8A]">
              <span>{appComponents.length} components</span>
              <span className={`font-medium ${
                appHealth >= 90 ? 'text-green-600' : 
                appHealth >= 70 ? 'text-[#FF7900]' : 'text-red-600'
              }`}>
                {appHealth >= 90 ? 'Good' : appHealth >= 70 ? 'Degraded' : 'Critical'}
              </span>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-5 h-5 text-[#8A8A8A]" />
              <span className="text-sm font-medium text-[#111111]">Databases</span>
            </div>
            <p className="text-3xl font-bold text-[#111111] mb-2">{dbHealth}%</p>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${dbHealth >= 90 ? 'bg-green-500' : dbHealth >= 70 ? 'bg-[#FF7900]' : 'bg-red-500'}`}
                style={{ width: `${dbHealth}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-[#8A8A8A]">
              <span>{dbComponents.length} components</span>
              <span className={`font-medium ${
                dbHealth >= 90 ? 'text-green-600' : 
                dbHealth >= 70 ? 'text-[#FF7900]' : 'text-red-600'
              }`}>
                {dbHealth >= 90 ? 'Good' : dbHealth >= 70 ? 'Degraded' : 'Critical'}
              </span>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Server className="w-5 h-5 text-[#8A8A8A]" />
              <span className="text-sm font-medium text-[#111111]">Servers</span>
            </div>
            <p className="text-3xl font-bold text-[#111111] mb-2">{serverHealth}%</p>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${serverHealth >= 90 ? 'bg-green-500' : serverHealth >= 70 ? 'bg-[#FF7900]' : 'bg-red-500'}`}
                style={{ width: `${serverHealth}%` }}
              />
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-[#8A8A8A]">
              <span>{serverComponents.length} components</span>
              <span className={`font-medium ${
                serverHealth >= 90 ? 'text-green-600' : 
                serverHealth >= 70 ? 'text-[#FF7900]' : 'text-red-600'
              }`}>
                {serverHealth >= 90 ? 'Good' : serverHealth >= 70 ? 'Degraded' : 'Critical'}
              </span>
            </div>
          </div>
        </div>

        {sourceBreakdown.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
              <h3 className="font-semibold text-[#111111] mb-4">Data Sources</h3>
              <div className="h-56 flex items-center">
                <div className="w-1/2 h-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sourceBreakdown}
                        cx="50%"
                        cy="50%"
                        innerRadius={45}
                        outerRadius={75}
                        paddingAngle={3}
                        dataKey="count"
                        nameKey="name"
                        label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                        labelLine={false}
                      >
                        {sourceBreakdown.map((s: any) => (
                          <Cell key={s.source} fill={s.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #E5E5E5',
                          borderRadius: '8px',
                        }}
                        formatter={(value: number, name: string) => [`${value} components`, name]}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="w-1/2 pl-4 space-y-2">
                  {sourceBreakdown.map((source: any) => (
                    <div key={source.source} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: source.color }}></span>
                        <span className="text-sm text-[#111111]">{source.name}</span>
                      </div>
                      <span className="text-sm font-semibold text-[#111111]">{source.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
              <h3 className="font-semibold text-[#111111] mb-4">Components by Source & Category</h3>
              {sourceCategoryData ? (
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={Object.entries(sourceCategoryData).map(([source, categories]: [string, any]) => ({
                        source: source.charAt(0).toUpperCase() + source.slice(1),
                        network: categories.network || 0,
                        application: categories.application || 0,
                        server: categories.server || 0,
                        database: categories.database || 0,
                      }))}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                      <XAxis type="number" stroke="#8A8A8A" fontSize={12} />
                      <YAxis dataKey="source" type="category" stroke="#8A8A8A" fontSize={12} width={80} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #E5E5E5',
                          borderRadius: '8px',
                        }}
                      />
                      <Bar dataKey="network" stackId="a" fill="#3B82F6" name="Network" />
                      <Bar dataKey="application" stackId="a" fill="#8B5CF6" name="Application" />
                      <Bar dataKey="server" stackId="a" fill="#10B981" name="Server" />
                      <Bar dataKey="database" stackId="a" fill="#F59E0B" name="Database" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-56 flex items-center justify-center text-[#8A8A8A]">
                  Loading...
                </div>
              )}
              <div className="flex flex-wrap gap-3 mt-3 justify-center">
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-[#3B82F6]"></span>
                  <span className="text-xs text-[#8A8A8A]">Network</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-[#8B5CF6]"></span>
                  <span className="text-xs text-[#8A8A8A]">Application</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-[#10B981]"></span>
                  <span className="text-xs text-[#8A8A8A]">Server</span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="w-3 h-3 rounded-full bg-[#F59E0B]"></span>
                  <span className="text-xs text-[#8A8A8A]">Database</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-[#FFF4E6] border border-[#FF7900]/20 rounded-xl p-5 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#FF7900] rounded-lg">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-[#111111]">Predictive Early Warnings</h2>
                <p className="text-sm text-[#8A8A8A]">AI-powered alerts before issues become incidents</p>
              </div>
            </div>
            <button 
              onClick={() => navigate('/predictions')}
              className="flex items-center gap-2 px-3 py-1.5 bg-white rounded-lg border border-[#FF7900]/30 hover:bg-[#FF7900]/5 transition-colors"
            >
              <AlertTriangle className="w-4 h-4 text-[#FF7900]" />
              <span className="text-sm font-semibold text-[#FF7900]">{mergedPredictions?.length || 0} Total</span>
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mergedPredictions?.slice(0, 3).map((pred: any) => {
              const timeToBreach = pred.timeToBreach ?? pred.time_to_breach_minutes ?? pred.time_to_breach
              return (
                <div 
                  key={pred.id} 
                  onClick={() => setSelectedPrediction(pred)}
                  className="bg-white rounded-lg p-4 border border-[#E5E5E5] cursor-pointer hover:border-[#FF7900] hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium text-[#111111]">{pred.component_name || pred.componentName}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      timeToBreach < 30 ? 'bg-red-100 text-red-700' : 
                      timeToBreach < 60 ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {formatTimeRemaining(timeToBreach)} to breach
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mb-2">
                    <div className="flex-1">
                      <div className="flex justify-between text-xs text-[#8A8A8A] mb-1">
                        <span>Current: {pred.current_value ?? pred.currentValue ?? 0}%</span>
                        <span>Predicted: {pred.predicted_value ?? pred.predictedValue ?? 0}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-[#FF7900] to-red-500 rounded-full"
                          style={{ width: `${Math.min(100, ((pred.predicted_value ?? pred.predictedValue ?? 0) / (pred.threshold ?? 100)) * 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-xs text-[#8A8A8A]">
                    <span>Confidence: {pred.confidence ?? 0}%</span>
                    <span className="capitalize">{pred.prediction_type || pred.metric || 'metric'} usage</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="col-span-2 bg-white border border-[#E5E5E5] rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#111111]">Health Trend</h3>
              <div className="flex items-center gap-1">
                <button 
                  onClick={() => setHealthTrendRange('24h')}
                  className={`px-3 py-1 text-xs font-medium rounded transition-colors ${healthTrendRange === '24h' ? 'bg-[#FF7900] text-white' : 'text-[#8A8A8A] hover:text-[#111111]'}`}
                >
                  24H
                </button>
                <button 
                  onClick={() => setHealthTrendRange('7d')}
                  className={`px-3 py-1 text-xs font-medium rounded transition-colors ${healthTrendRange === '7d' ? 'bg-[#FF7900] text-white' : 'text-[#8A8A8A] hover:text-[#111111]'}`}
                >
                  7D
                </button>
                <button 
                  onClick={() => setHealthTrendRange('30d')}
                  className={`px-3 py-1 text-xs font-medium rounded transition-colors ${healthTrendRange === '30d' ? 'bg-[#FF7900] text-white' : 'text-[#8A8A8A] hover:text-[#111111]'}`}
                >
                  30D
                </button>
              </div>
            </div>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={ORANGE} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={ORANGE} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                  <XAxis dataKey="time" stroke="#8A8A8A" fontSize={11} tickLine={false} />
                  <YAxis domain={[0, 100]} stroke="#8A8A8A" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: `1px solid ${ORANGE}`,
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="score"
                    stroke={ORANGE}
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorScore)"
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="#8A8A8A"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
            <h3 className="font-semibold text-[#111111] mb-4">Component Health</h3>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryHealth} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                  <XAxis type="number" domain={[0, 100]} stroke="#8A8A8A" fontSize={11} />
                  <YAxis dataKey="name" type="category" stroke="#8A8A8A" fontSize={11} width={60} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #E5E5E5',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="health" fill="#8A8A8A" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-6 mb-6">
          <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
            <h3 className="font-semibold text-[#111111] mb-4">Status Distribution</h3>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={healthDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={60}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {healthDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-2">
              {healthDistribution.map((item) => (
                <div key={item.name} className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-xs text-[#8A8A8A]">{item.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="col-span-2 bg-white border border-[#E5E5E5] rounded-xl p-5">
            <h3 className="font-semibold text-[#111111] mb-4">Resource Usage</h3>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={cpuData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                  <XAxis dataKey="time" stroke="#8A8A8A" fontSize={10} />
                  <YAxis stroke="#8A8A8A" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #E5E5E5',
                      borderRadius: '8px',
                    }}
                  />
                  <Line type="monotone" dataKey="cpu" stroke={ORANGE} strokeWidth={2} dot={false} name="CPU %" />
                  <Line type="monotone" dataKey="memory" stroke="#8A8A8A" strokeWidth={2} dot={false} name="Memory %" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
            <h3 className="font-semibold text-[#111111] mb-4">Alert Severity</h3>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={alertData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
                  <XAxis dataKey="name" stroke="#8A8A8A" fontSize={10} />
                  <YAxis stroke="#8A8A8A" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #E5E5E5',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {alertData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
            <h3 className="font-semibold text-[#111111] mb-4">Active Correlations</h3>
            <div className="space-y-3">
              {correlations && correlations.length > 0 ? (
                correlations.slice(0, 3).map((corr: any) => (
                  <div 
                    key={corr.id} 
                    className={`p-3 rounded-lg border ${
                      corr.correlation_score > 0.7 ? 'bg-[#FFF4E6] border-[#FF7900]/20' : 'bg-gray-50 border-[#E5E5E5]'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Layers className={`w-4 h-4 ${corr.correlation_score > 0.7 ? 'text-[#FF7900]' : 'text-[#8A8A8A]'}`} />
                      <span className="text-sm font-medium text-[#111111]">{corr.correlation_type.replace(/_/g, ' ')}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-[#8A8A8A] mb-2">
                      <span className="text-[#111111]">{corr.source_component_name}</span>
                      <ArrowRight className="w-3 h-3" />
                      <span className="text-[#111111]">{corr.target_component_name}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <span className="text-[#8A8A8A]">Correlation: <span className="text-[#111111] font-medium">{corr.correlation_score}</span></span>
                      <span className="text-[#8A8A8A]">Impact: <span className={`font-medium ${corr.correlation_score > 0.7 ? 'text-[#FF7900]' : 'text-[#8A8A8A]'}`}>{corr.correlation_score > 0.7 ? 'High' : corr.correlation_score > 0.5 ? 'Medium' : 'Low'}</span></span>
                      <span className="text-[#8A8A8A]">Detected: <span className="text-[#111111]">{new Date(corr.detected_at).toLocaleTimeString()}</span></span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-[#8A8A8A]">
                  <p className="text-sm">No active correlations</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
            <h3 className="font-semibold text-[#111111] mb-4">Category Overview</h3>
            <div className="space-y-4">
              {categoryHealth.map((cat) => {
                const catComponents = cat.name === 'Network' ? networkComponents : 
                                      cat.name === 'Apps' ? appComponents :
                                      cat.name === 'Databases' ? dbComponents : serverComponents
                const degradedCount = catComponents.filter((c: any) => c.status === 'degraded').length
                const downCount = catComponents.filter((c: any) => c.status === 'down').length
                return (
                  <div key={cat.name} className="p-3 bg-[#F7F7F7] rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {cat.name === 'Network' && <Network className="w-4 h-4 text-[#8A8A8A]" />}
                        {cat.name === 'Apps' && <Cpu className="w-4 h-4 text-[#8A8A8A]" />}
                        {cat.name === 'Databases' && <Database className="w-4 h-4 text-[#8A8A8A]" />}
                        {cat.name === 'Servers' && <Server className="w-4 h-4 text-[#8A8A8A]" />}
                        <span className="text-sm font-medium text-[#111111]">{cat.name}</span>
                      </div>
                      <span className="text-sm font-bold text-[#111111]">{cat.health}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden mb-2">
                      <div 
                        className={`h-full rounded-full ${cat.health >= 90 ? 'bg-green-500' : cat.health >= 70 ? 'bg-[#FF7900]' : 'bg-red-500'}`}
                        style={{ width: `${cat.health}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-[#8A8A8A]">{cat.components} components</span>
                      <div className="flex items-center gap-2">
                        {degradedCount > 0 && <span className="text-[#FF7900]">{degradedCount} degraded</span>}
                        {downCount > 0 && <span className="text-red-600">{downCount} down</span>}
                        {degradedCount === 0 && downCount === 0 && <span className="text-green-600">All healthy</span>}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
        <div className="bg-white border border-[#E5E5E5] rounded-xl p-5">
          <h3 className="font-semibold text-[#111111] mb-4">Active Alerts</h3>
            <div className="space-y-3">
              {mergedAlerts?.filter((a: any) => a.status === 'active').slice(0, 3).map((alert: any) => (
                <div key={alert.id} className="p-3 bg-red-50 rounded-lg border border-red-100">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${
                        alert.severity === 'critical' ? 'bg-red-600' : 'bg-[#FF7900]'
                      }`}></span>
                      <span className="text-sm font-medium text-[#111111]">{alert.title}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      alert.severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
                    }`}>
                      {alert.severity}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-[#8A8A8A]">
                    <span>{alert.componentName}</span>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {new Date(alert.createdAt).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              {(!mergedAlerts || mergedAlerts.filter((a: any) => a.status === 'active').length === 0) && (
                <div className="text-center py-4 text-[#8A8A8A]">
                  <p className="text-sm">No active alerts</p>
                </div>
              )}
            </div>
          </div>
        </div>

      {selectedPrediction && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedPrediction(null)}>
          <div className="bg-white rounded-xl w-[70%] max-w-4xl h-[85%] mx-4 flex flex-col" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between p-6 border-b border-[#E5E5E5]">
              <div>
                <h3 className="text-xl font-semibold text-[#111111]">Predictive Warning Details</h3>
                <p className="text-sm text-[#8A8A8A] mt-1">AI-powered prediction analysis</p>
              </div>
              <button onClick={() => setSelectedPrediction(null)} className="p-2 hover:bg-[#F7F7F7] rounded-lg">
                <X className="w-6 h-6 text-[#8A8A8A]" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-6">
                <div className="p-5 bg-[#F7F7F7] rounded-lg">
                  <p className="text-sm text-[#8A8A8A] mb-2">Affected Component</p>
                  <p className="text-2xl font-bold text-[#111111]">{selectedPrediction.componentName}</p>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-sm text-[#8A8A8A] mb-2">Current Value</p>
                    <p className="text-3xl font-bold text-[#111111]">{selectedPrediction.currentValue}%</p>
                    <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-green-500 rounded-full" style={{ width: `${selectedPrediction.currentValue}%` }} />
                    </div>
                  </div>
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-sm text-[#8A8A8A] mb-2">Predicted Value</p>
                    <p className="text-3xl font-bold text-[#FF7900]">{selectedPrediction.predictedValue}%</p>
                    <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-[#FF7900] rounded-full" style={{ width: `${Math.min(selectedPrediction.predictedValue, 100)}%` }} />
                    </div>
                  </div>
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-sm text-[#8A8A8A] mb-2">Threshold</p>
                    <p className="text-3xl font-bold text-[#111111]">{selectedPrediction.threshold}%</p>
                    <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="h-full bg-red-500 rounded-full" style={{ width: `${selectedPrediction.threshold}%` }} />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-sm text-[#8A8A8A] mb-2">Time to Breach</p>
                    <p className="text-2xl font-bold text-red-600">{formatTimeRemaining(selectedPrediction.timeToBreach ?? selectedPrediction.time_to_breach_minutes ?? selectedPrediction.time_to_breach)}</p>
                    <p className="text-xs text-[#8A8A8A] mt-1">Until threshold is exceeded</p>
                  </div>
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-sm text-[#8A8A8A] mb-2">Confidence Level</p>
                    <p className="text-2xl font-bold text-[#111111]">{selectedPrediction.confidence ?? 0}%</p>
                    <p className="text-xs text-[#8A8A8A] mt-1">Prediction accuracy</p>
                  </div>
                </div>

                <div className="p-5 bg-[#F7F7F7] rounded-lg">
                  <p className="text-sm text-[#8A8A8A] mb-2">Metric Type</p>
                  <p className="text-xl font-medium text-[#111111] capitalize">{selectedPrediction.prediction_type || selectedPrediction.metric || 'metric'} usage</p>
                </div>

                <div className="p-5 bg-[#FFF4E6] border border-[#FF7900]/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5 text-[#FF7900]" />
                    <p className="text-lg font-semibold text-[#111111]">Recommended Action</p>
                  </div>
                  <p className="text-[#111111]">
                    {(selectedPrediction.timeToBreach ?? selectedPrediction.time_to_breach_minutes ?? 999) < 30 
                      ? 'Immediate action required. Scale up resources or optimize usage to prevent service degradation.'
                      : (selectedPrediction.timeToBreach ?? selectedPrediction.time_to_breach_minutes ?? 999) < 60
                      ? 'Monitor closely and prepare for scaling. Consider proactive resource allocation.'
                      : 'Continue monitoring. Schedule resource review in the next maintenance window.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}