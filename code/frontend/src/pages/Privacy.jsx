import { useState } from 'react'
import { Shield, Download, Trash2 } from 'lucide-react'
import { dataExportUrl, deleteAllData } from '../api/client'

const PHRASE = 'USUN-WSZYSTKO'

export default function Privacy() {
  const [confirm, setConfirm] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)

  const handleDelete = async () => {
    setBusy(true)
    setError(null)
    try {
      await deleteAllData(confirm)
      setResult('Wszystkie Twoje dane i zdjęcia zostały trwale usunięte.')
      setConfirm('')
    } catch (e) {
      setError(e.response?.data?.detail || 'Nie udało się usunąć danych.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <Shield size={28} className="text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-900">Prywatność</h1>
      </div>

      <div className="bg-white border rounded-lg p-6 space-y-2 text-sm text-gray-700">
        <p>Zdjęcia są przechowywane tylko na tym komputerze. Przy wysyłce usuwamy z nich metadane
          (w tym lokalizację GPS). Do analizy AI zdjęcie jest wysyłane do dostawcy modelu
          (OpenRouter lub Google Gemini).</p>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-2">Pobierz swoje dane</h3>
        <p className="text-sm text-gray-600 mb-4">Archiwum ZIP: wszystkie zapisane dane (JSON) i zdjęcia.</p>
        <a
          href={dataExportUrl()}
          download
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <Download size={18} /> Pobierz archiwum
        </a>
      </div>

      <div className="bg-white border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-red-700 mb-2">Usuń wszystkie dane</h3>
        <p className="text-sm text-gray-600 mb-4">
          Trwale usuwa zdjęcia, analizy, rutyny, eksperymenty i historię. Tego nie da się cofnąć —
          najpierw pobierz archiwum. Wpisz <code className="font-mono">{PHRASE}</code>, aby potwierdzić.
        </p>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            aria-label="Fraza potwierdzenia"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="border rounded-md px-3 py-2 font-mono flex-1"
            placeholder={PHRASE}
          />
          <button
            onClick={handleDelete}
            disabled={confirm !== PHRASE || busy}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            <Trash2 size={18} /> Usuń trwale
          </button>
        </div>
        {result && <p className="mt-4 text-green-700">{result}</p>}
        {error && <p className="mt-4 text-red-700">{error}</p>}
      </div>
    </div>
  )
}
