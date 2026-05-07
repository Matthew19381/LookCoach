import { Outlet, NavLink } from 'react-router-dom'
import { Camera, Heart, Droplets, LineChart, Moon } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Upload', icon: Camera },
  { to: '/analysis', label: 'Analysis', icon: Heart },
  { to: '/recommendations', label: 'Recommendations', icon: Droplets },
  { to: '/progress', label: 'Progress', icon: LineChart },
  { to: '/skincare', label: 'Skincare', icon: Moon },
]

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-xl text-gray-900">LookCoach</span>
            </div>
            <div className="flex space-x-4">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`
                  }
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  )
}