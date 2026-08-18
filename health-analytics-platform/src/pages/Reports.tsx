import { useState } from 'react'
import { useHealthScore, useComponents, useAlerts } from '../hooks'
import { Skeleton, SkeletonChart } from '../components/Skeleton'
import { Download, TrendingUp, AlertTriangle, Activity, Server, Database, Network } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts'

type ReportPeriod = '7d' | '30d' | '90d'

export function Reports() {
  const { data: healthScore, isLoading: healthLoading } = useHealthScore()
  const { data: components, isLoading: componentsLoading } = useComponents()
  const { data: alerts, isLoading: alertsLoading } = useAlerts()
  const [period, setPeriod] = useState<ReportPeriod>('30d')

  const isLoading = healthLoading || componentsLoading || alertsLoading

  const handleExport = (format: 'pdf' | 'csv') => {
    const data = {
      period,
      healthScore,
      components,
      alerts,
      generatedAt: new Date().toISOString(),
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: format === 'pdf' ? 'application/json' : 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `infrasense-report-${period}.${format === 'pdf' ? 'json' : 'csv'}`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <div className="bg-white min-h-screen p-6">
        <Skeleton width={200} height={28} className="mb-6" />
        <div className="grid grid-cols-2 gap-6">
          <SkeletonChart />
          <SkeletonChart />
          <SkeletonChart />
        </div>
      </div>
    )
  }

  const periodDays = period === '7d' ? 7 : period === '30d' ? 30 : 90
  const trendPoints = Math.min(periodDays, 30)
  const dayStep = periodDays > 30 ? 3 : 1

  const healthTrend = Array.from({ length: trendPoints }, (_, i) => ({
    date: new Date(Date.now() - (trendPoints - 1 - i) * dayStep * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    score: 75 + Math.random() * 20,
  }))

  const alertTrend = Array.from({ length: trendPoints }, (_, i) => ({
    name: new Date(Date.now() - (trendPoints - 1 - i) * dayStep * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    critical: Math.floor(Math.random() * 4),
    warning: 2 + Math.floor(Math.random() * 6),
  }))

  const componentTypes = [
    { type: 'Server', count: healthScore?.categories?.server || 0, icon: Server },
    { type: 'Database', count: healthScore?.categories?.database || 0, icon: Database },
    { type: 'Network', count: healthScore?.categories?.network || 0, icon: Network },
    { type: 'Application', count: healthScore?.categories?.application || 0, icon: Activity },
  ]

  const avgHealth = typeof healthScore?.overall === 'number' ? healthScore.overall : 0
  const totalComponents = componentTypes.reduce((sum, ct) => sum + ct.count, 0)
  const activeAlerts = (alerts as any[])?.filter((a: any) => a.status === 'open' || a.status === 'acknowledged').length || 0

  return (
    <div className="bg-white min-h-screen p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-[#111111]">Reports & Analytics</h1>
          <p className="text-sm text-[#8A8A8A]">Historical trends and insights</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as ReportPeriod)}
            className="px-3 py-2 border border-[#E5E5E5] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FF7900]/20"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <button
            onClick={() => handleExport('pdf')}
            className="flex items-center gap-2 px-4 py-2 border border-[#E5E5E5] rounded-lg hover:bg-[#F7F7F7] transition-colors"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="border border-[#E5E5E5] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <span className="text-sm text-[#8A8A8A]">Avg Health</span>
          </div>
          <p className="text-2xl font-bold text-[#111111]">{avgHealth > 0 ? `${avgHealth}%` : 'N/A'}</p>
          <p className="text-xs text-green-500 flex items-center gap-1 mt-1">
            <TrendingUp className="w-3 h-3" /> +2% from last period
          </p>
        </div>
        <div className="border border-[#E5E5E5] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Server className="w-4 h-4 text-[#8A8A8A]" />
            <span className="text-sm text-[#8A8A8A]">Total Components</span>
          </div>
          <p className="text-2xl font-bold text-[#111111]">{totalComponents}</p>
          <p className="text-xs text-[#8A8A8A] mt-1">Across all categories</p>
        </div>
        <div className="border border-[#E5E5E5] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="text-sm text-[#8A8A8A]">Active Alerts</span>
          </div>
          <p className="text-2xl font-bold text-[#111111]">{activeAlerts}</p>
          <p className="text-xs text-red-500 mt-1">Requires attention</p>
        </div>
        <div className="border border-[#E5E5E5] rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-[#FF7900]" />
            <span className="text-sm text-[#8A8A8A]">Uptime</span>
          </div>
          <p className="text-2xl font-bold text-[#111111]">99.8%</p>
          <p className="text-xs text-green-500 mt-1">Last 30 days</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="border border-[#E5E5E5] rounded-xl p-4">
          <h3 className="text-lg font-semibold text-[#111111] mb-4">Health Score Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={healthTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
              <XAxis dataKey="date" stroke="#8A8A8A" fontSize={12} />
              <YAxis domain={[0, 100]} stroke="#8A8A8A" fontSize={12} />
              <Tooltip />
              <Area type="monotone" dataKey="score" stroke="#FF7900" fill="#FF7900" fillOpacity={0.2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="border border-[#E5E5E5] rounded-xl p-4">
          <h3 className="text-lg font-semibold text-[#111111] mb-4">Alert Trends</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={alertTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E5E5" />
              <XAxis dataKey="name" stroke="#8A8A8A" fontSize={12} />
              <YAxis stroke="#8A8A8A" fontSize={12} />
              <Tooltip />
              <Bar dataKey="critical" name="Critical" fill="#EF4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="warning" name="Warning" fill="#FF7900" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="border border-[#E5E5E5] rounded-xl p-4">
        <h3 className="text-lg font-semibold text-[#111111] mb-4">Component Distribution</h3>
        <div className="grid grid-cols-4 gap-4">
          {componentTypes.map(({ type, count, icon: Icon }) => (
            <div key={type} className="flex items-center gap-3 p-3 bg-[#F7F7F7] rounded-lg">
              <div className="p-2 bg-white rounded-lg">
                <Icon className="w-5 h-5 text-[#FF7900]" />
              </div>
              <div>
                <p className="text-lg font-bold text-[#111111]">{count}</p>
                <p className="text-xs text-[#8A8A8A]">{type}s</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}