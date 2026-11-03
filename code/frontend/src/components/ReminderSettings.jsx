import { useEffect, useState } from 'react'
import { Bell } from 'lucide-react'
import { getVapidKey, pushSubscribe, getReminderSettings, putReminderSettings, testPush } from '../api/client'

// Plan 5.5: przypomnienia push — rutyna rano/wieczorem i zdjęcia kontrolne. Respektują ciszę
// nocną i tryb przetrwania z huba; każde najwyżej raz dziennie.

const toUint8 = (base64url) => {
  const raw = atob(base64url.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - (base64url.length % 4)) % 4))
  return Uint8Array.from(raw, (c) => c.charCodeAt(0))
}

export default function ReminderSettings() {
  const [settings, setSettings] = useState(null)
  const [message, setMessage] = useState(null)
  const supported = typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window

  useEffect(() => {
    getReminderSettings().then(setSettings).catch(() => setSettings(null))
  }, [])

  if (!settings) return null

  const enablePush = async () => {
    setMessage(null)
    try {
      const { key } = await getVapidKey()
      if (!key) { setMessage('Serwer nie ma kluczy VAPID — zobacz scripts/generate_vapid_keys.py.'); return }
      if ((await Notification.requestPermission()) !== 'granted') { setMessage('Brak zgody na powiadomienia w przeglądarce.'); return }
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: toUint8(key) })
      await pushSubscribe(sub.toJSON())
      setSettings({ ...settings, subscriptions: settings.subscriptions + 1 })
      setMessage('Powiadomienia włączone na tym urządzeniu.')
    } catch {
      setMessage('Nie udało się włączyć powiadomień.')
    }
  }

  const save = async () => {
    const { enabled, morning_time, evening_time, photo_reminders } = settings
    try {
      await putReminderSettings({ enabled, morning_time, evening_time, photo_reminders })
      setMessage('Zapisano.')
    } catch {
      setMessage('Sprawdź godziny (HH:MM).')
    }
  }

  return (
    <section className="bg-white border rounded-lg p-6 space-y-3">
      <h3 className="text-lg font-semibold flex items-center gap-2"><Bell size={18} /> Przypomnienia</h3>
      {!settings.configured && (
        <p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-2">
          Serwer nie ma jeszcze kluczy VAPID — przypomnienia nie będą wysyłane.
        </p>
      )}
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={settings.enabled} onChange={(e) => setSettings({ ...settings, enabled: e.target.checked })} />
        Wysyłaj przypomnienia
      </label>
      <div className="grid grid-cols-2 gap-4 text-sm max-w-sm">
        <label className="flex flex-col gap-1">Rano
          <input type="time" className="border rounded px-2 py-1" value={settings.morning_time}
            onChange={(e) => setSettings({ ...settings, morning_time: e.target.value })} />
        </label>
        <label className="flex flex-col gap-1">Wieczorem
          <input type="time" className="border rounded px-2 py-1" value={settings.evening_time}
            onChange={(e) => setSettings({ ...settings, evening_time: e.target.value })} />
        </label>
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={settings.photo_reminders}
          onChange={(e) => setSettings({ ...settings, photo_reminders: e.target.checked })} />
        Przypominaj o zdjęciach kontrolnych (co 2 tygodnie)
      </label>
      <div className="flex flex-wrap gap-2">
        <button onClick={save} className="px-3 py-1.5 border rounded text-sm">Zapisz przypomnienia</button>
        {supported && <button onClick={enablePush} className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm">Włącz na tym urządzeniu</button>}
        {settings.subscriptions > 0 && (
          <button onClick={() => testPush().then((r) => setMessage(`Wysłano: ${r.sent}`)).catch(() => setMessage('Test się nie udał.'))}
            className="px-3 py-1.5 border rounded text-sm">Wyślij test</button>
        )}
      </div>
      <p className="text-xs text-gray-500">Urządzenia z włączonymi powiadomieniami: {settings.subscriptions}</p>
      {message && <p className="text-sm text-gray-700">{message}</p>}
    </section>
  )
}
