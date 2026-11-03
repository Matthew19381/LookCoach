import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Sun } from 'lucide-react'
import { getToday } from '../api/client'

// Plan 5.4: strona startowa — co dziś zrobić, bez konfigurowania.

export default function Today() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getToday().then(setData).catch(() => setError('Nie udało się wczytać planu na dziś.'))
  }, [])

  if (!data) return <div className="text-center py-20">{error || 'Ładowanie...'}</div>

  const state = Object.entries(data.state || {})
  const eco = data.ecosystem

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <Sun size={28} className="text-amber-500" />
        <h1 className="text-3xl font-bold text-gray-900">Dziś</h1>
      </div>

      {data.directives.survival_mode && (
        <p className="bg-gray-100 border rounded-lg p-4 text-gray-800">
          Tryb przetrwania z huba: dziś tylko wersja minimum — to w porządku.
        </p>
      )}
      {data.wellbeing?.message && (
        <p role="note" className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-purple-900">
          {data.wellbeing.message}
        </p>
      )}

      <section className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-3">Na dziś</h3>
        {data.actions.length === 0 ? (
          <p className="text-gray-600 text-sm">
            {data.has_photos ? 'Nic zaległego — wszystko zrobione albo nic nie jest śledzone.'
              : 'Zacznij od zdjęć — bez nich LookCoach nie wie, na czym się skupić.'}
          </p>
        ) : (
          <ul className="space-y-2">
            {data.actions.map((a) => (
              <li key={a.title} className="flex justify-between gap-2 border-b pb-2 text-sm">
                <span><strong>{a.title}</strong> <span className="text-gray-500">— {a.intention_cue}</span></span>
                <span className="text-gray-500 whitespace-nowrap">{a.estimated_minutes} min</span>
              </li>
            ))}
          </ul>
        )}
        <div className="mt-4 flex flex-wrap gap-3 text-sm">
          <Link to="/consistency" className="underline text-blue-700">Odhacz rutynę</Link>
          <Link to="/photos" className="underline text-blue-700">Zdjęcia</Link>
          <Link to="/recommendations" className="underline text-blue-700">Rekomendacje</Link>
        </div>
      </section>

      <section className="bg-white border rounded-lg p-6 text-sm">
        <h3 className="text-lg font-semibold mb-3">Ostatnio zaobserwowany stan</h3>
        {state.length === 0 ? (
          <p className="text-gray-600">Brak analizy.</p>
        ) : (
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1">
            {state.map(([k, v]) => (
              <div key={k} className="flex justify-between border-b py-1"><dt className="text-gray-600">{k}</dt><dd>{v}</dd></div>
            ))}
          </dl>
        )}
        {data.next_photos_in_days !== null && (
          <p className="mt-3 text-gray-600">
            {data.next_photos_in_days === 0 ? 'Pora na zdjęcia kontrolne.' : `Następne zdjęcia kontrolne za ${data.next_photos_in_days} dni.`}
          </p>
        )}
      </section>

      {eco && (
        <section className="bg-white border rounded-lg p-6 text-sm">
          <h3 className="text-lg font-semibold mb-2">Z innych modułów</h3>
          <p>Treningi w tym tygodniu: {eco.forge_body?.workouts_last_7_days ?? '—'}</p>
          {eco.dieta?.weight && <p>Waga: {eco.dieta.weight.latest_kg} kg</p>}
          {eco.affect_last_7_days?.stress && <p>Stres (7 dni): {eco.affect_last_7_days.stress}</p>}
          <Link to="/connections" className="underline text-blue-700">Więcej</Link>
        </section>
      )}
    </div>
  )
}
