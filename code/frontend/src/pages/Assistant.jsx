import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageCircle, Send } from 'lucide-react'
import {
  assistantChat, getAssistantHistory, clearAssistantHistory, sendEcosystemNeeds, startExperiment,
} from '../api/client'

// Plan 8 (D10): asystent na Twoich danych. Akcje są tylko propozycją — wykonują się po kliknięciu.

const EXAMPLES = [
  'Od czego zacząć przy moich wynikach?',
  'Jaką fryzurę wybrać przy mało czasu rano?',
  'Dlaczego warto przekazać priorytety do ForgeBody?',
]

export default function Assistant() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [done, setDone] = useState({})
  const navigate = useNavigate()
  const endRef = useRef(null)

  useEffect(() => {
    getAssistantHistory().then(setMessages).catch(() => {})
  }, [])
  useEffect(() => { endRef.current?.scrollIntoView?.({ behavior: 'smooth' }) }, [messages])

  const send = async (text) => {
    const message = (text ?? input).trim()
    if (!message || busy) return
    setInput('')
    setError(null)
    setBusy(true)
    setMessages((m) => [...m, { role: 'user', content: message }])
    try {
      const res = await assistantChat(message)
      setMessages((m) => [...m, { role: 'assistant', content: res.reply, actions: res.actions }])
    } catch (e) {
      setError(e.response?.data?.detail || 'Asystent nie odpowiedział.')
    } finally {
      setBusy(false)
    }
  }

  const runAction = async (key, action) => {
    if (action.type === 'open_page') {
      navigate(action.path)
      return
    }
    if (!window.confirm(`${action.label}?`)) return
    try {
      if (action.type === 'send_needs') await sendEcosystemNeeds(false)
      if (action.type === 'start_experiment') await startExperiment(action.template_id)
      setDone((d) => ({ ...d, [key]: 'Zrobione.' }))
    } catch {
      setDone((d) => ({ ...d, [key]: 'Nie udało się.' }))
    }
  }

  const handleClear = async () => {
    await clearAssistantHistory()
    setMessages([])
  }

  return (
    <div className="space-y-4 max-w-3xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <MessageCircle size={28} className="text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Asystent</h1>
        </div>
        {messages.length > 0 && (
          <button onClick={handleClear} className="text-sm text-gray-500 underline">Wyczyść rozmowę</button>
        )}
      </div>
      <p className="text-sm text-gray-600">
        Odpowiada na podstawie Twoich analiz, rutyn i profilu. Nie ocenia wyglądu liczbami; przy każdej
        rekomendacji podaje poziom dowodów.
      </p>

      <div className="bg-white border rounded-lg p-4 space-y-3 min-h-[200px]">
        {messages.length === 0 && (
          <div className="space-y-2">
            <p className="text-sm text-gray-500">Przykładowe pytania:</p>
            {EXAMPLES.map((q) => (
              <button key={q} onClick={() => send(q)} className="block text-left text-sm text-blue-700 underline">{q}</button>
            ))}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
            <div className={`inline-block max-w-[85%] text-left whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
              m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
              {m.content}
            </div>
            {m.actions?.length > 0 && (
              <div className="mt-1 flex flex-wrap gap-2">
                {m.actions.map((a, j) => {
                  const key = `${i}-${j}`
                  return done[key] ? (
                    <span key={key} className="text-xs text-gray-600">{done[key]}</span>
                  ) : (
                    <button key={key} onClick={() => runAction(key, a)}
                      className="text-xs px-2 py-1 border border-blue-300 text-blue-700 rounded hover:bg-blue-50">
                      {a.label}{a.path ? ` ${a.path}` : ''}{a.template_id ? `: ${a.template_id}` : ''}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        ))}
        {busy && <p className="text-sm text-gray-500">Asystent pisze…</p>}
        <div ref={endRef} />
      </div>

      {error && <p className="text-red-700 text-sm">{error}</p>}
      <form onSubmit={(e) => { e.preventDefault(); send() }} className="flex gap-2">
        <input
          aria-label="Wiadomość"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          maxLength={2000}
          className="flex-1 border rounded-md px-3 py-2"
          placeholder="Zapytaj o pielęgnację, styl, plan…"
        />
        <button type="submit" disabled={busy || !input.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md disabled:opacity-50" aria-label="Wyślij">
          <Send size={18} />
        </button>
      </form>
    </div>
  )
}
