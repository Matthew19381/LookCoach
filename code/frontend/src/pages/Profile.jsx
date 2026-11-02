import { useState, useEffect } from 'react'
import { User } from 'lucide-react'
import { getProfile, updateProfile } from '../api/client'
import ReminderSettings from '../components/ReminderSettings'

// Plan 4.12 + LC-8: cele (wpływają na kolejność rekomendacji) i flagi zdrowotne
// (twarde blokady przeciwwskazań — np. ciąża → bez retinolu).

const FOCUS = [
  ['skin', 'Skóra'],
  ['hair', 'Włosy'],
  ['face', 'Twarz'],
  ['body', 'Sylwetka'],
  ['posture', 'Postawa'],
  ['style', 'Styl (fryzura, zarost, ubiór)'],
]
const HEALTH = [
  ['pregnancy', 'Ciąża lub karmienie'],
  ['heart_disease', 'Choroba serca'],
  ['kidney_disease', 'Choroba nerek'],
  ['back_injury', 'Uraz pleców'],
  ['shoulder_injury', 'Uraz barku'],
  ['knee_injury', 'Uraz kolana'],
  ['sensitive_skin', 'Wrażliwa skóra'],
]
const MODES = [
  ['free', 'Swobodny'],
  ['maintenance', 'Utrzymanie'],
  ['improvement', 'Poprawa'],
]

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [saved, setSaved] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getProfile().then(setProfile).catch(() => setError('Nie udało się wczytać profilu.'))
  }, [])

  if (!profile) return <div className="text-center py-20">{error || 'Ładowanie...'}</div>

  const goals = profile.goals || {}
  const setGoal = (key, value) => setProfile({ ...profile, goals: { ...goals, [key]: value } })
  const toggleFocus = (area) => {
    const focus = goals.focus || []
    setGoal('focus', focus.includes(area) ? focus.filter((a) => a !== area) : [...focus, area])
  }
  const numberOrNull = (v) => (v === '' ? null : Number(v))

  const handleSave = async () => {
    setSaved(null)
    setError(null)
    try {
      const { goals: g, health, mode } = profile
      setProfile(await updateProfile({ goals: g, health, mode }))
      setSaved('Zapisano.')
    } catch (e) {
      setError(e.response?.status === 422 ? 'Sprawdź wartości — coś jest poza zakresem.' : 'Nie udało się zapisać.')
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-3">
        <User size={28} className="text-gray-700" />
        <h1 className="text-3xl font-bold text-gray-900">Profil</h1>
      </div>

      <section className="bg-white border rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-semibold">Co chcesz poprawić?</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {FOCUS.map(([key, label]) => (
            <label key={key} className="flex items-center gap-2">
              <input type="checkbox" checked={(goals.focus || []).includes(key)} onChange={() => toggleFocus(key)} />
              {label}
            </label>
          ))}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
          <label className="flex flex-col gap-1">
            Termin (np. wydarzenie)
            <input type="date" className="border rounded px-2 py-1" value={goals.deadline || ''}
              onChange={(e) => setGoal('deadline', e.target.value || null)} />
          </label>
          <label className="flex flex-col gap-1">
            Minut dziennie na pielęgnację
            <input type="number" min="0" max="180" className="border rounded px-2 py-1" value={goals.minutes_per_day ?? ''}
              onChange={(e) => setGoal('minutes_per_day', numberOrNull(e.target.value))} />
          </label>
          <label className="flex flex-col gap-1">
            Minut na układanie włosów
            <input type="number" min="0" max="60" className="border rounded px-2 py-1" value={goals.styling_minutes ?? ''}
              onChange={(e) => setGoal('styling_minutes', numberOrNull(e.target.value))} />
          </label>
        </div>
        <label className="flex flex-col gap-1 text-sm">
          Ograniczenia (praca, sport, dress code)
          <textarea rows={2} maxLength={500} className="border rounded px-2 py-1" value={goals.constraints || ''}
            onChange={(e) => setGoal('constraints', e.target.value || null)} />
        </label>
        <label className="flex flex-col gap-1 text-sm max-w-xs">
          Tryb
          <select className="border rounded px-2 py-1" value={profile.mode}
            onChange={(e) => setProfile({ ...profile, mode: e.target.value })}>
            {MODES.map(([key, label]) => <option key={key} value={key}>{label}</option>)}
          </select>
        </label>
      </section>

      <section className="bg-white border rounded-lg p-6 space-y-3">
        <h3 className="text-lg font-semibold">Zdrowie</h3>
        <p className="text-sm text-gray-600">
          Te informacje usuwają z zaleceń rzeczy przeciwwskazane (np. retinol w ciąży, minoksydyl przy chorobie serca).
          Zostają tylko na tym komputerze.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {HEALTH.map(([key, label]) => (
            <label key={key} className="flex items-center gap-2">
              <input type="checkbox" checked={Boolean(profile.health?.[key])}
                onChange={(e) => setProfile({ ...profile, health: { ...profile.health, [key]: e.target.checked } })} />
              {label}
            </label>
          ))}
        </div>
      </section>

      <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        Zapisz
      </button>
      {saved && <p className="text-green-700">{saved}</p>}
      {error && <p className="text-red-700">{error}</p>}

      <ReminderSettings />
    </div>
  )
}
