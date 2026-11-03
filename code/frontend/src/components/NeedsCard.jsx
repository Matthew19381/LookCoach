// Plan 3.11 (LC-4): LookCoach sends needs to ForgeBody/Dieta instead of writing plans.


const STATUS_PL = { pending: 'czeka na wysłanie', sent: 'wysłane', failed: 'nie udało się' }

const formatDate = (iso) => (iso ? new Date(iso).toLocaleString('pl-PL') : '')

export default function NeedsCard({ title, moduleName, need, renderPayload, onSend, sending }) {
  const current = need?.current
  const last = need?.last_sent
  return (
    <div className="bg-white border rounded-lg p-6 space-y-3">
      <h3 className="text-lg font-semibold">{title}</h3>
      {current ? (
        <>
          {renderPayload(current)}
          {current.reason && <p className="text-sm text-gray-600">{current.reason}</p>}
        </>
      ) : (
        <p className="text-gray-600 text-sm">
          Analiza zdjęć nie wskazuje teraz niczego do przekazania do {moduleName}.
        </p>
      )}
      {last && (
        <p className="text-xs text-gray-500">
          Ostatnio do {moduleName}: {STATUS_PL[last.status] || last.status} ({formatDate(last.timestamp)})
        </p>
      )}
      {current && (
        <button
          onClick={() => onSend(Boolean(last))}
          disabled={sending}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {last ? `Wyślij ponownie do ${moduleName}` : `Wyślij do ${moduleName}`}
        </button>
      )}
    </div>
  )
}
