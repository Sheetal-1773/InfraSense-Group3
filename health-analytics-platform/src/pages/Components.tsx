import { useState, useMemo } from 'react'
import { LayoutGrid, List, ChevronLeft, ChevronRight, Network, Database, Server, Cpu, Activity, Clock, X, Zap, HardDrive } from 'lucide-react'
import { Badge, Input } from '../components'
import { useComponents } from '../hooks'

const CATEGORIES = [
  { id: 'network', label: 'Network', icon: Network },
  { id: 'applications', label: 'Applications', icon: Cpu },
  { id: 'databases', label: 'Databases', icon: Database },
  { id: 'servers', label: 'Servers', icon: Server },
]

const TYPE_MAPPING: Record<string, string[]> = {
  network: ['network', 'loadbalancer', 'firewall'],
  applications: ['api', 'service', 'queue', 'cache'],
  databases: ['database'],
  servers: ['server', 'container'],
}

function getStatusVariant(status: string) {
  switch (status) {
    case 'healthy': return 'success'
    case 'degraded': return 'warning'
    case 'down': return 'danger'
    default: return 'default'
  }
}

function ComponentCard({ component, onClick }: { component: any; onClick: () => void }) {
  return (
    <div 
      onClick={onClick}
      className="bg-white border border-[#E5E5E5] rounded-lg p-4 hover:border-[#FF7900] hover:shadow-md cursor-pointer transition-all"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded ${
            component.status === 'healthy' ? 'bg-green-50' :
            component.status === 'degraded' ? 'bg-[#FF7900]/10' : 'bg-red-50'
          }`}>
            <Activity className={`w-4 h-4 ${
              component.status === 'healthy' ? 'text-green-600' :
              component.status === 'degraded' ? 'text-[#FF7900]' : 'text-red-600'
            }`} />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-[#111111]">{component.name}</h4>
            <p className="text-xs text-[#8A8A8A] capitalize">{component.type}</p>
          </div>
        </div>
        <Badge variant={getStatusVariant(component.status)}>
          {component.status}
        </Badge>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="text-center p-2 bg-[#F7F7F7] rounded">
          <p className="text-xs text-[#8A8A8A]">CPU</p>
          <p className="text-sm font-medium text-[#111111]">{component.cpu}%</p>
        </div>
        <div className="text-center p-2 bg-[#F7F7F7] rounded">
          <p className="text-xs text-[#8A8A8A]">Memory</p>
          <p className="text-sm font-medium text-[#111111]">{component.memory}%</p>
        </div>
        <div className="text-center p-2 bg-[#F7F7F7] rounded">
          <p className="text-xs text-[#8A8A8A]">Disk</p>
          <p className="text-sm font-medium text-[#111111]">{component.disk}%</p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-[#E5E5E5]">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#8A8A8A]">Health:</span>
          <span className={`text-sm font-semibold ${
            component.healthScore >= 90 ? 'text-green-600' : 
            component.healthScore >= 70 ? 'text-[#FF7900]' : 'text-red-600'
          }`}>
            {component.healthScore}
          </span>
        </div>
        <div className="flex items-center gap-1 text-xs text-[#8A8A8A]">
          <Clock className="w-3 h-3" />
          {new Date(component.lastUpdated).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}

type SortOption = 'name-asc' | 'name-desc' | 'health-asc' | 'health-desc' | 'updated'
type CategoryFilter = 'all' | 'network' | 'applications' | 'databases' | 'servers'
type StatusFilter = 'all' | 'healthy' | 'degraded' | 'down'

const ITEMS_PER_PAGE = 12

export function Components() {
  const { data: components, isLoading } = useComponents()
  const [view, setView] = useState<'grid' | 'list'>('grid')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>('all')
  const [sortBy, setSortBy] = useState<SortOption>('name-asc')
  const [page, setPage] = useState(1)
  const [selectedComponent, setSelectedComponent] = useState<any>(null)

  const filteredComponents = useMemo(() => {
    if (!components) return []
    
    let result = [...components]

    if (search) {
      const searchLower = search.toLowerCase()
      result = result.filter(c => c.name.toLowerCase().includes(searchLower))
    }

    if (statusFilter !== 'all') {
      result = result.filter(c => c.status === statusFilter)
    }

    if (categoryFilter !== 'all') {
      const allowedTypes = TYPE_MAPPING[categoryFilter] || []
      result = result.filter(c => allowedTypes.includes(c.type))
    }

    switch (sortBy) {
      case 'name-asc':
        result.sort((a, b) => a.name.localeCompare(b.name))
        break
      case 'name-desc':
        result.sort((a, b) => b.name.localeCompare(a.name))
        break
      case 'health-asc':
        result.sort((a, b) => a.healthScore - b.healthScore)
        break
      case 'health-desc':
        result.sort((a, b) => b.healthScore - a.healthScore)
        break
      case 'updated':
        result.sort((a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime())
        break
    }

    return result
  }, [components, search, statusFilter, categoryFilter, sortBy])

  const categoryStats = useMemo(() => {
    if (!components) return {}
    const stats: Record<string, { total: number; healthy: number; degraded: number; down: number }> = {}
    
    CATEGORIES.forEach(cat => {
      const allowedTypes = TYPE_MAPPING[cat.id] || []
      const filtered = components.filter(c => allowedTypes.includes(c.type))
      stats[cat.id] = {
        total: filtered.length,
        healthy: filtered.filter(c => c.status === 'healthy').length,
        degraded: filtered.filter(c => c.status === 'degraded').length,
        down: filtered.filter(c => c.status === 'down').length,
      }
    })
    return stats
  }, [components])

  const totalPages = Math.ceil(filteredComponents.length / ITEMS_PER_PAGE)
  const paginatedComponents = filteredComponents.slice(
    (page - 1) * ITEMS_PER_PAGE,
    page * ITEMS_PER_PAGE
  )

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
            <h1 className="text-2xl font-semibold text-[#111111]">Components</h1>
            <p className="text-sm text-[#8A8A8A]">Monitor all infrastructure components</p>
          </div>
          <div className="flex items-center gap-2 bg-white border border-[#E5E5E5] rounded-md p-1">
            <button
              onClick={() => setView('grid')}
              className={`p-1.5 rounded transition-colors ${
                view === 'grid' ? 'bg-[#F7F7F7] text-[#111111]' : 'text-[#8A8A8A] hover:text-[#111111]'
              }`}
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
            <button
              onClick={() => setView('list')}
              className={`p-1.5 rounded transition-colors ${
                view === 'list' ? 'bg-[#F7F7F7] text-[#111111]' : 'text-[#8A8A8A] hover:text-[#111111]'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4">
          {CATEGORIES.map(cat => {
            const stats = categoryStats[cat.id] || { total: 0, healthy: 0, degraded: 0, down: 0 }
            const isActive = categoryFilter === cat.id
            return (
              <button
                key={cat.id}
                onClick={() => { setCategoryFilter(isActive ? 'all' : cat.id as CategoryFilter); setPage(1); }}
                className={`p-4 rounded-lg border text-left transition-all ${
                  isActive 
                    ? 'border-[#FF7900] bg-white shadow-sm' 
                    : 'border-[#E5E5E5] bg-white hover:border-[#8A8A8A]'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <cat.icon className={`w-4 h-4 ${isActive ? 'text-[#FF7900]' : 'text-[#8A8A8A]'}`} />
                  <span className="text-sm font-medium text-[#111111]">{cat.label}</span>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-[#8A8A8A]">{stats.total} total</span>
                  {stats.degraded > 0 && <span className="text-[#FF7900]">{stats.degraded} degraded</span>}
                  {stats.down > 0 && <span className="text-red-600">{stats.down} down</span>}
                </div>
              </button>
            )
          })}
        </div>

        <div className="flex flex-wrap items-center gap-4 bg-white p-4 border border-[#E5E5E5] rounded-lg">
          <Input
            placeholder="Search components..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-64"
          />
          
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value as StatusFilter); setPage(1); }}
            className="px-3 py-1.5 border border-[#E5E5E5] rounded text-sm focus:outline-none focus:ring-1 focus:ring-[#FF7900] bg-white"
          >
            <option value="all">All Status</option>
            <option value="healthy">Healthy</option>
            <option value="degraded">Degraded</option>
            <option value="down">Down</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="px-3 py-1.5 border border-[#E5E5E5] rounded text-sm focus:outline-none focus:ring-1 focus:ring-[#FF7900] bg-white"
          >
            <option value="name-asc">Name (A-Z)</option>
            <option value="name-desc">Name (Z-A)</option>
            <option value="health-desc">Health (High-Low)</option>
            <option value="health-asc">Health (Low-High)</option>
            <option value="updated">Last Updated</option>
          </select>

          <span className="text-sm text-[#8A8A8A] ml-auto">
            {filteredComponents.length} components
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {paginatedComponents.map(component => (
            <ComponentCard key={component.id} component={component} onClick={() => setSelectedComponent(component)} />
          ))}
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 bg-white p-4 border border-[#E5E5E5] rounded-lg">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1.5 rounded hover:bg-[#F7F7F7] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm text-[#8A8A8A]">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1.5 rounded hover:bg-[#F7F7F7] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {selectedComponent && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedComponent(null)}>
            <div className="bg-white rounded-xl w-[70%] max-w-4xl h-[85%] mx-4 flex flex-col" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between p-6 border-b border-[#E5E5E5]">
                <div className="flex items-center gap-4">
                  <div className={`p-4 rounded-lg ${
                    selectedComponent.status === 'healthy' ? 'bg-green-50' :
                    selectedComponent.status === 'degraded' ? 'bg-[#FF7900]/10' : 'bg-red-50'
                  }`}>
                    <Activity className={`w-8 h-8 ${
                      selectedComponent.status === 'healthy' ? 'text-green-600' :
                      selectedComponent.status === 'degraded' ? 'text-[#FF7900]' : 'text-red-600'
                    }`} />
                  </div>
                  <div>
                    <h3 className="text-2xl font-semibold text-[#111111]">{selectedComponent.name}</h3>
                    <p className="text-base text-[#8A8A8A] capitalize">{selectedComponent.type}</p>
                  </div>
                </div>
                <button onClick={() => setSelectedComponent(null)} className="p-2 hover:bg-[#F7F7F7] rounded-lg">
                  <X className="w-6 h-6 text-[#8A8A8A]" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-6">
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-5 bg-[#F7F7F7] rounded-lg">
                    <div>
                      <p className="text-base text-[#8A8A8A] mb-2">Status</p>
                      <Badge variant={getStatusVariant(selectedComponent.status)} className="mt-1">
                        {selectedComponent.status}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <p className="text-base text-[#8A8A8A] mb-2">Health Score</p>
                      <p className={`text-4xl font-bold ${
                        selectedComponent.healthScore >= 90 ? 'text-green-600' : 
                        selectedComponent.healthScore >= 70 ? 'text-[#FF7900]' : 'text-red-600'
                      }`}>
                        {selectedComponent.healthScore}%
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-5">
                    <div className="p-5 bg-[#F7F7F7] rounded-lg">
                      <div className="flex items-center gap-3 mb-3">
                        <Cpu className="w-5 h-5 text-[#8A8A8A]" />
                        <p className="text-base text-[#8A8A8A]">CPU Usage</p>
                      </div>
                      <p className="text-3xl font-bold text-[#111111]">{selectedComponent.cpu}%</p>
                      <div className="mt-3 h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${selectedComponent.cpu > 80 ? 'bg-red-500' : selectedComponent.cpu > 60 ? 'bg-[#FF7900]' : 'bg-green-500'}`}
                          style={{ width: `${selectedComponent.cpu}%` }}
                        />
                      </div>
                    </div>
                    <div className="p-5 bg-[#F7F7F7] rounded-lg">
                      <div className="flex items-center gap-3 mb-3">
                        <Zap className="w-5 h-5 text-[#8A8A8A]" />
                        <p className="text-base text-[#8A8A8A]">Memory Usage</p>
                      </div>
                      <p className="text-3xl font-bold text-[#111111]">{selectedComponent.memory}%</p>
                      <div className="mt-3 h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${selectedComponent.memory > 80 ? 'bg-red-500' : selectedComponent.memory > 60 ? 'bg-[#FF7900]' : 'bg-green-500'}`}
                          style={{ width: `${selectedComponent.memory}%` }}
                        />
                      </div>
                    </div>
                    <div className="p-5 bg-[#F7F7F7] rounded-lg">
                      <div className="flex items-center gap-3 mb-3">
                        <HardDrive className="w-5 h-5 text-[#8A8A8A]" />
                        <p className="text-base text-[#8A8A8A]">Disk Usage</p>
                      </div>
                      <p className="text-3xl font-bold text-[#111111]">{selectedComponent.disk}%</p>
                      <div className="mt-3 h-3 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${selectedComponent.disk > 80 ? 'bg-red-500' : selectedComponent.disk > 60 ? 'bg-[#FF7900]' : 'bg-green-500'}`}
                          style={{ width: `${selectedComponent.disk}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <div className="flex items-center gap-3 mb-3">
                      <Clock className="w-5 h-5 text-[#8A8A8A]" />
                      <p className="text-lg font-medium text-[#111111]">Last Updated</p>
                    </div>
                    <p className="text-lg text-[#111111]">{new Date(selectedComponent.lastUpdated).toLocaleString()}</p>
                  </div>

                  <div className="p-5 bg-[#F7F7F7] rounded-lg">
                    <p className="text-base text-[#8A8A8A] mb-3">Component ID</p>
                    <p className="text-sm text-[#111111] font-mono bg-white p-3 rounded border border-[#E5E5E5]">{selectedComponent.id}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}