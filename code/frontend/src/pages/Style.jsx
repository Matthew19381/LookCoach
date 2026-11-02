import { useState, useEffect } from 'react'
import { Scissors } from 'lucide-react'
import { getStyleAdvice } from '../api/client'

// Plan 4.1-4.8: porady z jakościowej analizy zdjęć. Każda ma jawny poziom:
// porada stylistyczna / hipoteza / wpis z bazy dowodów. Bez ocen wyglądu (LC-9).

const LEVEL = {
  'porada stylistyczna': ['porada stylistyczna', 'bg-gray-100 text-gray-700'],
  hipoteza: ['HIPOTEZA', 'bg-amber-100 text-amber-800'],
  rct: ['badania (RCT)', 'bg-green-100 text-green-800'],
  expert: ['opinia ekspertów', 'bg-blue-100 text-blue-800'],
  blokada: ['przeciwwskazanie', 'bg-red-100 text-red-800'],
}

function Level({ level, evidenceId }) {
  const [label, cls] = LEVEL[level] || [level, 'bg-gray-100 text-gray-700']
  return (
    <span className={`inline-block text-xs px-2 py-0.5 rounded ${cls}`}>
      {label}{evidenceId ? ` · ${evidenceId}` : ''}
    </span>
  )
}

function Items({ title, items }) {
  if (!items || items.length === 0) return null
  return (
    <section className="bg-white border rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-3">{title}</h3>
      <ul className="space-y-2">
        {items.map((i) => (
          <li key={i.text} className="text-sm">
            <p>{i.text}</p>
            <Level level={i.level} evidenceId={i.evidence_id} />
          </li>
        ))}
      </ul>
    </section>
  )
}

export default function Style() {
  const [advice, setAdvice] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getStyleAdvice().then(setAdvice).catch(() => setError('Nie udało się wczytać porad.'))
  }, [])

  if (!advice) return <div className="text-center py-20">{error || 'Ładowanie...'}</div>

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <Scissors size={28} className="text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-900">Styl</h1>
      </div>

      {!advice.has_front_photo && (
        <p className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-blue-900">
          Zrób i przeanalizuj zdjęcie z przodu, żeby zobaczyć porady dotyczące fryzury, brwi i zarostu.
        </p>
      )}

      {advice.hair && (
        <section className="bg-white border rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold">Fryzura — propozycje</h3>
          <div className="grid gap-3 sm:grid-cols-3">
            {advice.hair.proposals.map((p) => (
              <div key={p.name} className="border rounded-lg p-3 text-sm space-y-1">
                <p className="font-medium">{p.name}</p>
                <p className="text-gray-700"><span className="text-gray-500">Powiedz fryzjerowi:</span> {p.tell_barber}</p>
                <p className="text-xs text-gray-500">układanie ok. {p.styling_minutes} min</p>
              </div>
            ))}
          </div>
          <ul className="space-y-2">
            {advice.hair.notes.map((n) => (
              <li key={n.text} className="text-sm"><p>{n.text}</p><Level level={n.level} evidenceId={n.evidence_id} /></li>
            ))}
          </ul>
        </section>
      )}

      <Items title="Brwi" items={advice.brows} />
      <Items title="Zarost" items={advice.beard} />
      <Items title="Okolica oczu" items={advice.eyes} />
      <Items title="Oprawki okularów" items={advice.glasses} />
      <Items title="Ubiór i sylwetka" items={advice.clothing} />
      <Items title="Kolorystyka (HIPOTEZA)" items={advice.colors} />
    </div>
  )
}
