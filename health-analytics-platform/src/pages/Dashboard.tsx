import { useState, useEffect } from 'react'
import { TrendingUp, Network, Cpu, Zap, Gauge, Layers, AlertTriangle, Server, Database, Clock, ArrowRight, X } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, LineChart, Line } from 'recharts'
import { useHealthScore, useComponents, usePredictions, useAlerts } from '../hooks'

function formatTimeRemaining(minutes: number) {
  if (minutes < 60) return `${Math.round(minutes)}m`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return `${hours}h ${mins}m`
}

const ORANGE = '#FF7900'

export function Dashboard() {
  const { data: healthScore, isLoading: healthLoading } = useHealthScore()
  const { data: components, isLoading: componentsLoading } = useComponents()
  const { data: predictions, isLoading: predictionsLoading } = usePredictions()
  const { data: alerts } = useAlerts()

  const [currentTime, setCurrentTime] = useState(new Date())
  const [selectedPrediction, setSelectedPrediction] = useState<any>(null)

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000)
    return () => clearInterval(timer)
  }, [])

  const networkComponents = components?.filter((c: any) => c.type === 'network') || []
  const networkHealth = networkComponents.length > 0 ? Math.round(networkComponents.reduce((acc, c) => acc + c.healthScore, 0) / networkComponents.length) : 98
  
  const appComponents = components?.filter((c: any) => ['api', 'service', 'cache', 'queue'].includes(c.type)) || []
  const appHealth = appComponents.length > 0 ? Math.round(appComponents.reduce((acc, c) => acc + c.healthScore, 0) / appComponents.length) : 94
  
  const dbComponents = components?.filter((c: any) => c.type === 'database') || []
  const dbHealth = dbComponents.length > 0 ? Math.round(dbComponents.reduce((acc, c) => acc + c.healthScore, 0) / dbComponents.length) : 96
  
  const serverComponents = components?.filter((c: any) => c.type === 'server') || []
  const serverHealth = serverComponents.length > 0 ? Math.round(serverComponents.reduce((acc, c) => acc + c.healthScore, 0) / serverComponents.length) : 97

  const overallHealth = healthScore?.overall ?? 96

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

  const chartData = healthScore?.trend.map((point, idx) => ({
    time: new Date(point.timestamp).getHours() + ':00',
    score: Math.round(point.score),
    predicted: idx > 18 ? Math.round(point.score + (Math.random() - 0.5) * 8) : null,
  })) ?? []

  const healthDistribution = [
    { name: 'Healthy', value: components?.filter((c: any) => c.status === 'healthy').length || 12, color: '#22C55E' },
    { name: 'Warning', value: components?.filter((c: any) => c.status === 'degraded').length || 3, color: ORANGE },
    { name: 'Critical', value: components?.filter((c: any) => c.status === 'down').length || 1, color: '#EF4444' },
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
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white rounded-lg border border-[#FF7900]/30">
              <AlertTriangle className="w-4 h-4 text-[#FF7900]" />
              <span className="text-sm font-semibold text-[#FF7900]">{predictions?.length || 0} Total Predictive Warnings</span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {predictions?.slice(0, 3).map((pred: any) => (
              <div 
                key={pred.id} 
                onClick={() => setSelectedPrediction(pred)}
                className="bg-white rounded-lg p-4 border border-[#E5E5E5] cursor-pointer hover:border-[#FF7900] hover:shadow-md transition-all"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-medium text-[#111111]">{pred.componentName}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                    pred.timeToBreach < 30 ? 'bg-red-100 text-red-700' : 
                    pred.timeToBreach < 60 ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {formatTimeRemaining(pred.timeToBreach)} to breach
                  </span>
                </div>
                <div className="flex items-center gap-4 mb-2">
                  <div className="flex-1">
                    <div className="flex justify-between text-xs text-[#8A8A8A] mb-1">
                      <span>Current: {pred.currentValue}%</span>
                      <span>Predicted: {pred.predictedValue}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-[#FF7900] to-red-500 rounded-full"
                        style={{ width: `${(pred.predictedValue / pred.threshold) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs text-[#8A8A8A]">
                  <span>Confidence: {pred.confidence}%</span>
                  <span className="capitalize">{pred.metric} usage</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="col-span-2 bg-white border border-[#E5E5E5] rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-[#111111]">Health Trend</h3>
              <div className="flex items-center gap-1">
                <button className="px-3 py-1 text-xs font-medium text-white bg-[#FF7900] rounded">24H</button>
                <button className="px-3 py-1 text-xs font-medium text-[#8A8A8A] hover:text-[#111111]">7D</button>
                <button className="px-3 py-1 text-xs font-medium text-[#8A8A8A] hover:text-[#111111]">30D</button>
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
              <div className="p-3 bg-[#FFF4E6] rounded-lg border border-[#FF7900]/20">
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="w-4 h-4 text-[#FF7900]" />
                  <span className="text-sm font-medium text-[#111111]">Network Latency → App Response</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-[#8A8A8A] mb-2">
                  <span className="text-[#111111]">Network latency</span>
                  <ArrowRight className="w-3 h-3" />
                  <span className="text-[#111111]">App response time</span>
                  <ArrowRight className="w-3 h-3" />
                  <span className="font-medium text-[#FF7900]">Payment Service</span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-[#8A8A8A]">Correlation: <span className="text-[#111111] font-medium">0.87</span></span>
                  <span className="text-[#8A8A8A]">Impact: <span className="text-[#FF7900] font-medium">High</span></span>
                  <span className="text-[#8A8A8A]">Detected: <span className="text-[#111111]">2h ago</span></span>
                </div>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg border border-[#E5E5E5]">
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="w-4 h-4 text-[#8A8A8A]" />
                  <span className="text-sm font-medium text-[#111111]">DB Connections → API Gateway</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-[#8A8A8A] mb-2">
                  <span className="text-[#111111]">DB connections</span>
                  <ArrowRight className="w-3 h-3" />
                  <span className="text-[#111111]">API Gateway</span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-[#8A8A8A]">Correlation: <span className="text-[#111111] font-medium">0.72</span></span>
                  <span className="text-[#8A8A8A]">Impact: <span className="text-[#8A8A8A] font-medium">Medium</span></span>
                  <span className="text-[#8A8A8A]">Detected: <span className="text-[#111111]">5h ago</span></span>
                </div>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg border border-[#E5E5E5]">
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="w-4 h-4 text-[#8A8A8A]" />
                  <span className="text-sm font-medium text-[#111111]">CPU Load → Memory Usage</span>
                </div>
                <div className="flex items-center gap-2 text-xs text-[#8A8A8A] mb-2">
                  <span className="text-[#111111]">Server CPU</span>
                  <ArrowRight className="w-3 h-3" />
                  <span className="text-[#111111]">Memory utilization</span>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <span className="text-[#8A8A8A]">Correlation: <span className="text-[#111111] font-medium">0.65</span></span>
                  <span className="text-[#8A8A8A]">Impact: <span className="text-[#8A8A8A] font-medium">Low</span></span>
                  <span className="text-[#8A8A8A]">Detected: <span className="text-[#111111]">1d ago</span></span>
                </div>
              </div>
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
              {alerts?.filter((a: any) => a.status === 'active').slice(0, 3).map((alert: any) => (
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
              {(!alerts || alerts.filter((a: any) => a.status === 'active').length === 0) && (
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
                    <p className="text-2xl font-bold text-red-600">{formatTimeRemaining(selectedPrediction.timeToBreach)}</p>
                    <p className="text-xs text-[#8A8A8A] mt-1">Until threshold is exceeded</p>
                  </div>
                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-sm text-[#8A8A8A] mb-2">Confidence Level</p>
                    <p className="text-2xl font-bold text-[#111111]">{selectedPrediction.confidence}%</p>
                    <p className="text-xs text-[#8A8A8A] mt-1">Prediction accuracy</p>
                  </div>
                </div>

                <div className="p-5 bg-[#F7F7F7] rounded-lg">
                  <p className="text-sm text-[#8A8A8A] mb-2">Metric Type</p>
                  <p className="text-xl font-medium text-[#111111] capitalize">{selectedPrediction.metric} usage</p>
                </div>

                <div className="p-5 bg-[#FFF4E6] border border-[#FF7900]/20 rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5 text-[#FF7900]" />
                    <p className="text-lg font-semibold text-[#111111]">Recommended Action</p>
                  </div>
                  <p className="text-[#111111]">
                    {selectedPrediction.timeToBreach < 30 
                      ? 'Immediate action required. Scale up resources or optimize usage to prevent service degradation.'
                      : selectedPrediction.timeToBreach < 60
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