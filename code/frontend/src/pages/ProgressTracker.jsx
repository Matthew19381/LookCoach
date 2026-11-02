import { useState, useEffect } from 'react'
import { getTimeline, comparePhotos, getStateTimeline, getCorrelations } from '../api/client'

// LC-9: postęp pokazujemy słowami (stan przed → po) z prawdziwych analiz.
// Do 2026-11-02 była tu linia „Look Score” rosnąca o 5 pkt na każde zdjęcie,
// niezależnie od analizy — usunięta jako zmyślona ocena wyglądu.

const PHOTO_TYPE_PL = { front: 'przód', side: 'bok', back: 'tył' }

const formatDate = (iso) => (iso ? new Date(iso).toLocaleDateString('pl-PL') : '')

export default function ProgressTracker() {
  const [photos, setPhotos] = useState([])
  const [beforeId, setBeforeId] = useState('')
  const [afterId, setAfterId] = useState('')
  const [compareResult, setCompareResult] = useState(null)
  const [compareError, setCompareError] = useState(null)
  const [split, setSplit] = useState(50) // plan 5.2: before/after slider position (%)
  const [loading, setLoading] = useState(true)
  const [states, setStates] = useState(null)
  const [correlations, setCorrelations] = useState(null)

  useEffect(() => {
    getTimeline().then((data) => {
      setPhotos(data)
      setLoading(false)
    }).catch(() => setLoading(false))
    getStateTimeline().then(setStates).catch(() => setStates(null))
    getCorrelations().then(setCorrelations).catch(() => setCorrelations(null))
  }, [])

  const handleCompare = async () => {
    if (!beforeId || !afterId) return
    setCompareError(null)
    try {
      const result = await comparePhotos(parseInt(beforeId), parseInt(afterId))
      setCompareResult(result)
    } catch {
      setCompareError('Nie udało się porównać zdjęć.')
    }
  }

  if (loading) {
    return <div className="text-center py-20">Ładowanie postępu...</div>
  }

  const photoOption = (p) => (
    <option key={p.id} value={p.id}>
      {PHOTO_TYPE_PL[p.photo_type] || p.photo_type} — {formatDate(p.uploaded_at)}
    </option>
  )

  const changes = compareResult?.changes || []

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Postęp</h1>

      {states?.sessions?.length > 0 && (
        <div className="bg-white border rounded-lg p-6 overflow-x-auto">
          <h3 className="text-lg font-semibold mb-4">Jak zmieniał się stan</h3>
          <table className="text-sm min-w-full">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2 pr-4">Obszar</th>
                {states.sessions.map((s) => <th key={s.photo_id} className="py-2 pr-4 whitespace-nowrap">{formatDate(s.date)}</th>)}
              </tr>
            </thead>
            <tbody>
              {states.areas.map((area) => (
                <tr key={area} className="border-b">
                  <td className="py-2 pr-4 text-gray-700">{area}</td>
                  {states.sessions.map((s) => <td key={s.photo_id} className="py-2 pr-4">{s.labels[area] ?? '—'}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {correlations && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Co idzie w parze</h3>
          {correlations.insights.length === 0 ? (
            <p className="text-sm text-gray-600">
              Za mało sesji zdjęć, żeby coś powiedzieć ({correlations.front_sessions} zdjęć z przodu). Wnioski pojawią się,
              gdy będzie po co najmniej {correlations.needed_per_group} sesje w porównywanych grupach.
            </p>
          ) : (
            <>
              <ul className="space-y-2 text-sm">
                {correlations.insights.map((i) => (
                  <li key={i.area}><strong>{i.area}:</strong> {i.text}</li>
                ))}
              </ul>
              <p className="text-xs text-gray-500 mt-3">{correlations.caveat}</p>
            </>
          )}
        </div>
      )}

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Porównaj zdjęcia</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <select
            aria-label="Zdjęcie przed"
            value={beforeId}
            onChange={(e) => setBeforeId(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Wybierz zdjęcie „przed”...</option>
            {photos.map(photoOption)}
          </select>
          <select
            aria-label="Zdjęcie po"
            value={afterId}
            onChange={(e) => setAfterId(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Wybierz zdjęcie „po”...</option>
            {photos.map(photoOption)}
          </select>
        </div>
        <button
          onClick={handleCompare}
          disabled={!beforeId || !afterId}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Porównaj
        </button>

        {compareError && <p className="mt-4 text-red-600">{compareError}</p>}

        {compareResult && (
          <div className="mt-6 space-y-4">
            {!compareResult.same_type && (
              <p className="text-amber-700 bg-amber-50 border border-amber-200 rounded-md p-3 text-sm">
                Zdjęcia są z różnych ujęć — porównanie stanu ma sens tylko dla tego samego ujęcia.
              </p>
            )}
            <p className="text-sm text-gray-600">
              Przed ({formatDate(compareResult.before.uploaded_at)}) ↔ po ({formatDate(compareResult.after.uploaded_at)})
            </p>
            <div className="relative max-w-md select-none">
              <img src={compareResult.before.url} alt="Przed" className="w-full rounded-lg border" />
              <img src={compareResult.after.url} alt="Po" className="absolute inset-0 w-full h-full object-cover rounded-lg"
                style={{ clipPath: `inset(0 0 0 ${split}%)` }} />
              <div className="absolute inset-y-0 w-0.5 bg-white shadow" style={{ left: `${split}%` }} aria-hidden="true" />
            </div>
            <input type="range" min="0" max="100" value={split} onChange={(e) => setSplit(Number(e.target.value))}
              aria-label="Suwak przed/po" className="w-full max-w-md" />

            {changes.length > 0 ? (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="py-2">Obszar</th>
                    <th className="py-2">Przed</th>
                    <th className="py-2">Po</th>
                  </tr>
                </thead>
                <tbody>
                  {changes.map((c) => (
                    <tr key={c.area} className={`border-b ${c.changed ? 'font-medium' : 'text-gray-600'}`}>
                      <td className="py-2">{c.area}</td>
                      <td className="py-2">{c.before ?? '—'}</td>
                      <td className="py-2">{c.after ?? '—'}{c.changed ? ' •' : ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-gray-600 text-sm">
                Brak analizy dla jednego ze zdjęć — przeanalizuj oba, żeby zobaczyć zmiany stanu.
              </p>
            )}
          </div>
        )}
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Oś czasu zdjęć</h3>
        {photos.length === 0 ? (
          <p className="text-gray-600">Nie masz jeszcze zdjęć. Zacznij od zakładki ze zdjęciami.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {photos.map((p) => (
              <div key={p.id} className="border rounded-lg overflow-hidden">
                <img src={p.url} alt={PHOTO_TYPE_PL[p.photo_type] || p.photo_type} className="w-full h-32 object-cover" />
                <div className="p-2 text-center">
                  <p className="text-sm font-medium">{PHOTO_TYPE_PL[p.photo_type] || p.photo_type}</p>
                  <p className="text-xs text-gray-500">{formatDate(p.uploaded_at)}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
