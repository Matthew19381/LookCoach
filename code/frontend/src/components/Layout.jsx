import { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import PageErrorBoundary from './PageErrorBoundary'
import {
  Camera, Heart, Droplets, LineChart, Moon, Play, Calendar, Brain, FlaskConical, Dumbbell, Move, Apple,
  Bed, Activity, Shield, Link2, User, Scissors, Sun, Menu, X, ListChecks, MessageCircle,
} from 'lucide-react'

// Plan 6.2: nawigacja w grupach, po polsku, z menu na telefonie (wcześniej 15+ pozycji w jednym rzędzie).
export const NAV_GROUPS = [
  {
    title: null,
    items: [
      { to: '/', label: 'Dziś', icon: Sun },
      { to: '/assistant', label: 'Asystent', icon: MessageCircle },
    ],
  },
  {
    title: 'Analiza',
    items: [
      { to: '/photos', label: 'Zdjęcia', icon: Camera },
      { to: '/analysis', label: 'Wyniki analizy', icon: Heart },
      { to: '/progress', label: 'Postęp', icon: LineChart },
      { to: '/style', label: 'Styl', icon: Scissors },
    ],
  },
  {
    title: 'Plan',
    items: [
      { to: '/recommendations', label: 'Rekomendacje', icon: Droplets },
      { to: '/skincare', label: 'Pielęgnacja', icon: Moon },
      { to: '/consistency', label: 'Regularność', icon: ListChecks },
      { to: '/experiments', label: 'Eksperymenty', icon: FlaskConical },
    ],
  },
  {
    title: 'Styl życia',
    items: [
      { to: '/training', label: 'Trening', icon: Dumbbell },
      { to: '/nutrition', label: 'Żywienie', icon: Apple },
      { to: '/sleep', label: 'Sen', icon: Bed },
      { to: '/stress', label: 'Stres', icon: Activity },
      { to: '/posture', label: 'Postawa', icon: Move },
    ],
  },
  {
    title: 'Więcej',
    items: [
      { to: '/videos', label: 'Wideo', icon: Play },
      { to: '/event', label: 'Przed wydarzeniem', icon: Calendar },
      { to: '/confidence', label: 'Pewność siebie', icon: Brain },
      { to: '/connections', label: 'Połączenia', icon: Link2 },
      { to: '/profile', label: 'Profil', icon: User },
      { to: '/privacy', label: 'Prywatność', icon: Shield },
    ],
  },
]

function NavList({ onNavigate }) {
  return (
    <nav aria-label="Nawigacja" className="space-y-4">
      {NAV_GROUPS.map((group) => (
        <div key={group.title || 'start'}>
          {group.title && <p className="px-3 mb-1 text-xs font-semibold uppercase tracking-wide text-gray-400">{group.title}</p>}
          <ul className="space-y-0.5">
            {group.items.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === '/'}
                  onClick={onNavigate}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }`
                  }
                >
                  <item.icon size={18} aria-hidden="true" />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  )
}

export default function Layout() {
  const [open, setOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b md:hidden">
        <div className="flex items-center justify-between h-14 px-4">
          <span className="font-bold text-lg text-gray-900">LookCoach</span>
          <button
            onClick={() => setOpen(!open)}
            aria-label={open ? 'Zamknij menu' : 'Otwórz menu'}
            aria-expanded={open}
            className="p-2 rounded-md text-gray-600 hover:bg-gray-100"
          >
            {open ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
        {open && (
          <div className="px-2 pb-4 border-t">
            <NavList onNavigate={() => setOpen(false)} />
          </div>
        )}
      </header>

      <div className="flex">
        <aside className="hidden md:block w-56 shrink-0 bg-white border-r min-h-screen p-3">
          <p className="font-bold text-xl text-gray-900 px-3 py-3">LookCoach</p>
          <NavList />
        </aside>
        <main className="flex-1 min-w-0 max-w-5xl py-6 px-4 sm:px-6 lg:px-8">
          <PageErrorBoundary key={location.pathname}><Outlet /></PageErrorBoundary>
        </main>
      </div>
    </div>
  )
}
