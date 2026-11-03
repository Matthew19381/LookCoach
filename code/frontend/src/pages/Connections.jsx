import { useState, useEffect } from 'react'
import { Link2 } from 'lucide-react'
import { getEcosystemOverview, getConnectionStatus } from '../api/client'

// Plan 3.8 / 3.12: co LookCoach wie z innych modułów i jak działa łącze z hubem.

const SOURCE_PL = {
  hub: 'aktualne dane z huba',
  cache: 'hub niedostępny — ostatnie zapisane dane',
  unavailable: 'hub niedostępny, brak zapisanych danych',
}
const EVENT_PL = {
  protocol_done: 'rutyna wykonana',
  protocol_skipped: 'rutyna pominięta',
  state_observation: 'obserwacja stanu',
  module_directive: 'dyrektywa dla modułu',
}
const STATUS_PL = { pending: 'czeka', sent: 'wysłane', failed: 'błąd' }
const TREND_PL = { rośnie: '↑', spada: '↓', stabilnie: '→' }

const formatDate = (iso) => (iso ? new Date(iso).toLocaleString('pl-PL') : '—')

export default function Connections() {
  const [overview, setOverview] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getEcosystemOverview().catch(() => null), getConnectionStatus().catch(() => null)])
      .then(([o, s]) => { setOverview(o); setStatus(s) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-20">Ładowanie...</div>

  const measurements = overview?.forge_body?.measurements?.values || {}
  const weight = overview?.dieta?.weight
  const affect = overview?.affect_last_7_days
  const outbox = status?.outbox
  const directives = status?.directives

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <Link2 size={28} className="text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-900">Połączenia</h1>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-1">Dane z innych modułów</h3>
        <p className="text-xs text-gray-500 mb-4">
          {SOURCE_PL[overview?.source] || 'brak danych'}
          {overview?.fetched_at ? ` · ${formatDate(overview.fetched_at)}` : ''}
        </p>
        <div className="grid sm:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium mb-1">ForgeBody — pomiary</h4>
            {Object.keys(measurements).length === 0 ? (
              <p className="text-gray-500">Brak pomiarów.</p>
            ) : (
              <ul>
                {Object.entries(measurements).map(([k, m]) => (
                  <li key={k}>{m.label}: {m.latest} {m.trend ? TREND_PL[m.trend] : ''}</li>
                ))}
              </ul>
            )}
            <p className="mt-1">Treningi w ostatnich 7 dniach: {overview?.forge_body?.workouts_last_7_days ?? '—'}</p>
          </div>
          <div>
            <h4 className="font-medium mb-1">Dieta — waga</h4>
            <p>{weight ? `${weight.latest_kg} kg ${weight.trend ? TREND_PL[weight.trend] : ''}` : 'Brak wpisów.'}</p>
            <h4 className="font-medium mt-3 mb-1">Samopoczucie (7 dni)</h4>
            <p>
              {affect
                ? [affect.stress && `stres: ${affect.stress}`, affect.energy && `energia: ${affect.energy}`,
                   affect.mood && `nastrój: ${affect.mood}`].filter(Boolean).join(', ')
                : 'Brak danych.'}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-2">Wysyłka do huba</h3>
        {outbox ? (
          <>
            <p className="text-sm mb-3">
              Czeka: <strong>{outbox.pending}</strong> · Błędy: <strong>{outbox.failed}</strong>
            </p>
            {outbox.recent.length === 0 ? (
              <p className="text-sm text-gray-500">Jeszcze nic nie wysłano.</p>
            ) : (
              <ul className="text-sm space-y-1">
                {outbox.recent.map((e, i) => (
                  <li key={i} className="flex justify-between gap-2 border-b py-1">
                    <span>
                      {EVENT_PL[e.event_type] || e.event_type}
                      {e.data?.target_module ? ` → ${e.data.target_module}` : ''}
                    </span>
                    <span className={e.status === 'failed' ? 'text-red-600' : 'text-gray-600'}>
                      {STATUS_PL[e.status] || e.status}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </>
        ) : (
          <p className="text-sm text-gray-500">Brak danych.</p>
        )}
      </div>

      <div className="bg-white border rounded-lg p-6 text-sm">
        <h3 className="text-lg font-semibold mb-2">Dyrektywy z huba</h3>
        <p>Tryb przetrwania: {directives?.survival_mode ? 'włączony' : 'wyłączony'}</p>
        <p>Priorytet: {directives?.priority || '—'}</p>
        <p>Cisza: {directives?.quiet_hours ? `${directives.quiet_hours.from}–${directives.quiet_hours.to}` : '—'}</p>
      </div>
    </div>
  )
}
