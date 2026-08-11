import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Server, Bell, TrendingUp, Network, Settings, User, Search } from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/components', label: 'Components', icon: Server },
  { path: '/alerts', label: 'Alerts', icon: Bell },
  { path: '/predictions', label: 'Predictions', icon: TrendingUp },
  { path: '/correlations', label: 'Correlations', icon: Network },
  { path: '/settings', label: 'Settings', icon: Settings },
]

interface HeaderProps {
  notificationCount?: number
}

function Logo() {
  return (
    <div className="flex items-center gap-3">
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="10" height="10" rx="1" stroke="#111111" strokeWidth="1.5" fill="none"/>
        <rect x="16" y="2" width="10" height="10" rx="1" stroke="#111111" strokeWidth="1.5" fill="none"/>
        <rect x="2" y="16" width="10" height="10" rx="1" stroke="#111111" strokeWidth="1.5" fill="none"/>
        <rect x="16" y="16" width="10" height="10" rx="1" stroke="#111111" strokeWidth="1.5" fill="none"/>
        <path d="M7 12H21M12 7V21" stroke="#111111" strokeWidth="1"/>
      </svg>
      <div className="flex items-baseline">
        <span className="text-base font-medium text-[#111111]">InfraSense</span>
        <span className="text-xs text-[#8A8A8A] ml-1.5">Predict</span>
      </div>
    </div>
  )
}

export function Header({ notificationCount = 3 }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-[#E5E5E5]">
      <div className="flex items-center justify-between h-14 px-6">
        <div className="flex items-center gap-12">
          <Logo />

          <nav className="hidden md:flex items-center gap-1 h-14">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 h-full text-sm font-medium transition-colors relative ${
                    isActive
                      ? 'text-[#111111]'
                      : 'text-[#8A8A8A] hover:text-[#333333]'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <item.icon className="w-4 h-4" />
                    {item.label}
                    {isActive && (
                      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#FF7900]"></div>
                    )}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-[#F7F7F7] rounded-md border border-[#E5E5E5]">
            <Search className="w-4 h-4 text-[#8A8A8A]" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent border-none outline-none text-sm text-[#111111] w-32 placeholder:text-[#8A8A8A]"
            />
            <kbd className="hidden xl:inline-flex items-center px-1.5 py-0.5 text-xs text-[#8A8A8A] bg-white border border-[#E5E5E5] rounded">⌘K</kbd>
          </div>

          <button className="relative p-2 text-[#8A8A8A] hover:text-[#333333] hover:bg-[#F7F7F7] rounded-md transition-colors">
            <Bell className="w-4 h-4" />
            {notificationCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#FF7900] rounded-full"></span>
            )}
          </button>

          <div className="flex items-center gap-3 pl-4 border-l border-[#E5E5E5]">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-[#111111]">Admin User</p>
              <p className="text-xs text-[#8A8A8A]">admin@company.com</p>
            </div>
            <button className="w-8 h-8 bg-[#F7F7F7] rounded-full flex items-center justify-center border border-[#E5E5E5]">
              <User className="w-4 h-4 text-[#8A8A8A]" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}