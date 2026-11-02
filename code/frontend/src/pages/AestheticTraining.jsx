import { useState, useEffect, useCallback } from 'react'
import { Dumbbell } from 'lucide-react'
import { getEcosystemNeeds, sendEcosystemNeeds } from '../api/client'
import NeedsCard from '../components/NeedsCard'
import { MUSCLE_PL } from '../components/muscles'

// LC-4: LookCoach nie układa planów treningowych. Z analizy zdjęć wynika, które partie
// mięśni warto podciągnąć — ten priorytet trafia do ForgeBody (przez hub), który
// dobiera ćwiczenia w Twoim planie.
export default function AestheticTraining() {
  const [needs, setNeeds] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState(null)

  const load = useCallback(() => {
    return getEcosystemNeeds().then(setNeeds).catch(() => setNeeds(null)).finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  const handleSend = async (force) => {
    setSending(true)
    try {
      const res = await sendEcosystemNeeds(force)
      setMessage(res.queued?.includes('aesthetic_priority') ? 'Priorytet przekazany do ForgeBody.' : 'Nic nowego do wysłania.')
      await load()
    } catch {
      setMessage('Nie udało się wysłać — spróbuj później.')
    } finally {
      setSending(false)
    }
  }

  if (loading) return <div className="text-center py-20">Ładowanie...</div>

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <Dumbbell size={28} className="text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Trening</h1>
      </div>
      <p className="text-gray-700">
        Plan treningowy prowadzi <strong>ForgeBody</strong>. LookCoach przekazuje mu tylko, które partie
        warto podciągnąć według analizy Twoich zdjęć (zdjęcie z boku).
      </p>
      <NeedsCard
        title="Priorytet mięśni dla ForgeBody"
        moduleName="ForgeBody"
        need={needs?.aesthetic_priority}
        sending={sending}
        onSend={handleSend}
        renderPayload={(p) => (
          <ul className="list-disc ml-5">
            {p.muscle_groups.map((g) => <li key={g}>{MUSCLE_PL[g] || g}</li>)}
            <li className="list-none text-sm text-gray-500 -ml-5 mt-1">na {p.duration_weeks} tyg.</li>
          </ul>
        )}
      />
      {message && <p className="text-sm text-gray-700">{message}</p>}
    </div>
  )
}
