import { useEffect, useState } from 'react'
import {
  addRoutineStep, createDefaultRoutine, deleteProduct, deleteRoutineStep, getMyRotation, getMyRoutine,
  getProducts, getRoutineToday, getSkincareRoutine, logAdherence, logProductUsage, logSkinReaction,
  lookupProductBarcode, parseProductText, saveProduct, scanProductLabel, updateRoutineStep,
} from '../api/client'
import BarcodeBox from '../components/BarcodeBox'
import { AlertTriangle, Camera, Check, Droplets, Info, ListChecks, Moon, Plus, RotateCcw, Sun, Trash2 } from 'lucide-react'

const SLOTS = [['morning', 'Rano'], ['evening', 'Wieczór'], ['both', 'Rano i wieczór']]
const REACTIONS = [['poczerwienienie', 'Zaczerwienienie'], ['pieczenie', 'Pieczenie / szczypanie'],
  ['nowe_wysipy', 'Nowe wypryski'], ['suchosc_skrajna', 'Mocne przesuszenie'], ['reakcja_alergiczna', 'Reakcja alergiczna']]
const errText = (e) => e?.response?.data?.detail || e?.message || 'Coś poszło nie tak'

function RoutineColumn({ icon, title, steps }) {
  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center gap-2 mb-4">{icon}<h2 className="text-xl font-semibold">{title}</h2></div>
      <ol className="space-y-3">
        {steps.map((step, idx) => (
          <li key={idx} className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 bg-gray-100 text-gray-800 rounded-full flex items-center justify-center text-sm font-medium">{idx + 1}</span>
            <span className="text-gray-900">{step}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}

/** Result of a label scan / pasted list, before saving. */
function ProductReport({ report, onSaved, onCancel }) {
  const [name, setName] = useState(report.name || '')
  const [slot, setSlot] = useState('evening')
  const [err, setErr] = useState('')
  const save = async () => {
    try {
      await saveProduct({ name: name || 'Produkt', ingredients: report.ingredients, slot })
      onSaved()
    } catch (e) { setErr(errText(e)) }
  }
  return (
    <div className="border rounded-lg p-4 space-y-3 bg-gray-50">
      <input aria-label="Nazwa produktu" className="w-full border rounded px-3 py-2" placeholder="Nazwa produktu" value={name} onChange={(e) => setName(e.target.value)} />
      <div>
        <p className="text-sm font-medium text-gray-700">Składniki aktywne</p>
        {report.actives.length === 0 && <p className="text-sm text-gray-500">Brak rozpoznanych aktywnych — produkt bazowy (np. nawilżający).</p>}
        <ul className="text-sm mt-1 space-y-1">
          {report.actives.map((a) => (
            <li key={a.name}>• <b>{a.name}</b> <span className="text-gray-500">({a.inci}{a.hint ? `, ${a.hint}` : ''})</span></li>
          ))}
        </ul>
      </div>
      {report.flags.length > 0 && (
        <div className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-2">
          {report.flags.map((f) => <div key={f}>ⓘ {f}</div>)}
        </div>
      )}
      {report.conflicts.map((c) => (
        <div key={c.type} className="text-sm text-red-800 bg-red-50 border border-red-200 rounded p-2 flex gap-2">
          <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" /> {c.message}
        </div>
      ))}
      {(report.health_warnings || []).map((w) => (
        <div key={w} role="alert" className="text-sm text-red-900 bg-red-100 border border-red-300 rounded p-2 flex gap-2">
          <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" /> {w}
        </div>
      ))}
      {report.tolerance_warnings.map((t) => (
        <div key={t.ingredient} className="text-sm text-red-800 bg-red-50 border border-red-200 rounded p-2">{t.message}</div>
      ))}
      <details className="text-xs text-gray-500"><summary>Pełny skład ({report.ingredients.length})</summary>{report.ingredients.join(', ')}</details>
      <div className="flex flex-wrap gap-2 items-center">
        {SLOTS.map(([k, l]) => (
          <button key={k} onClick={() => setSlot(k)} className={`px-3 py-1 rounded border text-sm ${slot === k ? 'bg-blue-600 text-white border-blue-600' : 'bg-white'}`}>{l}</button>
        ))}
        <button onClick={save} className="ml-auto bg-green-600 text-white px-4 py-2 rounded">Zapisz produkt</button>
        <button onClick={onCancel} className="px-3 py-2 rounded border">Anuluj</button>
      </div>
      {err && <p className="text-sm text-red-600">{err}</p>}
    </div>
  )
}

function MyProducts({ onChange }) {
  const [products, setProducts] = useState([])
  const [report, setReport] = useState(null)
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const load = () => getProducts().then(setProducts).catch(() => setProducts([]))
  useEffect(() => { load() }, [])

  const scan = async (file) => {
    if (!file) return
    setErr(''); setBusy(true)
    try { setReport(await scanProductLabel(file)) } catch (e) { setErr(errText(e)) } finally { setBusy(false) }
  }
  const barcode = async (code) => {
    setErr(''); setBusy(true)
    try { setReport(await lookupProductBarcode(code)) } catch (e) { setErr(errText(e)) } finally { setBusy(false) }
  }
  const parse = async () => {
    setErr('')
    try { setReport(await parseProductText(text)); setText('') } catch (e) { setErr(errText(e)) }
  }
  const used = async (p) => { await logProductUsage([p.id]); load(); onChange?.() }
  const remove = async (p) => { if (window.confirm(`Usunąć „${p.name}”?`)) { await deleteProduct(p.id); load(); onChange?.() } }

  return (
    <div className="bg-white border rounded-lg p-6 space-y-4">
      <h2 className="text-xl font-semibold">Moje produkty</h2>
      {!report && (
        <div className="grid md:grid-cols-2 gap-3">
          <label className="border-2 border-dashed rounded-lg p-4 flex flex-col items-center justify-center gap-2 cursor-pointer hover:bg-gray-50">
            <Camera size={24} className="text-gray-500" />
            <span className="text-sm text-gray-700">{busy ? 'Czytam skład…' : 'Zrób zdjęcie składu (INCI)'}</span>
            <input type="file" accept="image/*" capture="environment" className="hidden" disabled={busy} onChange={(e) => scan(e.target.files?.[0])} />
          </label>
          <div className="flex flex-col gap-2">
            <textarea aria-label="Skład produktu (INCI)" className="border rounded p-2 text-sm flex-1" rows={3} placeholder="…albo wklej skład: Aqua, Glycerin, Niacinamide, …" value={text} onChange={(e) => setText(e.target.value)} />
            <button onClick={parse} disabled={!text.trim()} className="bg-blue-600 disabled:opacity-50 text-white rounded py-2 text-sm">Sprawdź skład</button>
          </div>
          <div className="md:col-span-2"><BarcodeBox onCode={barcode} busy={busy} /></div>
        </div>
      )}
      {err && <p className="text-sm text-red-600">{err}</p>}
      {report && <ProductReport report={report} onSaved={() => { setReport(null); load(); onChange?.() }} onCancel={() => setReport(null)} />}

      {products.length === 0 && !report && <p className="text-sm text-gray-500">Dodaj produkty, których używasz — aplikacja sprawdzi konflikty i podpowie rotację.</p>}
      <ul className="divide-y">
        {products.map((p) => (
          <li key={p.id} className="py-3 flex items-center gap-3">
            <div className="flex-1">
              <p className="font-medium">{p.name} <span className="text-xs text-gray-500">{SLOTS.find(([k]) => k === p.slot)?.[1] ?? ''}</span></p>
              <p className="text-xs text-gray-500">{p.actives.join(', ') || 'bez aktywnych'}</p>
            </div>
            {p.used_today
              ? <span className="text-sm text-green-700 flex items-center gap-1"><Check size={16} /> dziś</span>
              : <button onClick={() => used(p)} className="text-sm border rounded px-3 py-1 hover:bg-gray-50">Użyłem dziś</button>}
            <button onClick={() => remove(p)} className="text-gray-400 hover:text-red-600" aria-label="Usuń"><Trash2 size={16} /></button>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ReactionForm({ actives }) {
  const [ingredient, setIngredient] = useState('')
  const [reaction, setReaction] = useState('poczerwienienie')
  const [severity, setSeverity] = useState('medium')
  const [done, setDone] = useState('')
  const submit = async () => {
    await logSkinReaction(ingredient, reaction, severity)
    setDone('Zapisane — kolejne produkty z tym składnikiem pokażą ostrzeżenie.')
  }
  return (
    <div className="bg-white border rounded-lg p-6 space-y-3">
      <h2 className="text-xl font-semibold">Reakcja skóry</h2>
      <div className="grid md:grid-cols-3 gap-2">
        <select aria-label="Składnik" className="border rounded px-2 py-2" value={ingredient} onChange={(e) => setIngredient(e.target.value)}>
          <option value="">Składnik…</option>
          {actives.map((a) => <option key={a}>{a}</option>)}
        </select>
        <select aria-label="Reakcja skóry" className="border rounded px-2 py-2" value={reaction} onChange={(e) => setReaction(e.target.value)}>
          {REACTIONS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
        </select>
        <select aria-label="Nasilenie" className="border rounded px-2 py-2" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="low">lekka</option><option value="medium">średnia</option><option value="high">silna</option>
        </select>
      </div>
      <button onClick={submit} disabled={!ingredient} className="bg-gray-800 disabled:opacity-50 text-white rounded px-4 py-2 text-sm">Zapisz reakcję</button>
      {done && <p className="text-sm text-green-700">{done}</p>}
    </div>
  )
}


// ── Today + my routine (owner request 2026-10-15: "tworzenie rutyny i podgląd co dzisiaj ma być") ──
const SLOT_NAMES = { morning: 'Rano', evening: 'Wieczór' }
const SLOT_ICONS = { morning: <Sun size={18} className="text-yellow-500" />, evening: <Moon size={18} className="text-indigo-500" /> }
const DAYS = ['Pn', 'Wt', 'Śr', 'Cz', 'Pt', 'So', 'Nd']
const daysText = (w) => (w === '0123456' ? 'codziennie' : [...(w || '')].map((d) => DAYS[+d]).join(', ') || 'żaden dzień')

function Evidence({ evidence }) {
  if (!evidence) return null
  return (
    <p className="text-xs text-gray-500 mt-1">
      Dowody: {evidence.level}. {evidence.ref}{' '}
      {evidence.url && <a href={evidence.url} target="_blank" rel="noreferrer" className="underline">źródło</a>}
    </p>
  )
}

function TodayCard({ today, onDone }) {
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  if (!today) return null
  const markDone = async (slot) => {
    setBusy(slot.slot); setError('')
    try {
      await logAdherence({ protocol_type: slot.protocol_type, completed: true })
      await onDone()
    } catch (e) { setError(errText(e)) } finally { setBusy('') }
  }
  return (
    <div className="bg-white border rounded-lg p-6 space-y-4">
      <h2 className="text-xl font-semibold flex items-center gap-2"><ListChecks size={20} /> Dziś</h2>
      {!today.has_routine && (
        <p className="text-sm text-gray-600">Nie masz jeszcze zapisanej rutyny. Niżej jest gotowa propozycja oparta na badaniach: zapisz ją albo dodaj swoje kroki.</p>
      )}
      {today.survival_mode && <p className="text-sm text-amber-700">Tryb minimum: tylko kroki oznaczone jako podstawowe.</p>}
      {today.has_routine && (
        <div className="grid md:grid-cols-2 gap-4">
          {today.slots.map((slot) => (
            <div key={slot.slot} className="border rounded p-4 space-y-2">
              <div className="flex items-center gap-2 font-medium">{SLOT_ICONS[slot.slot]} {SLOT_NAMES[slot.slot]}</div>
              {slot.steps.length === 0 ? <p className="text-sm text-gray-500">Dziś nic.</p> : (
                <>
                  <ol className="list-decimal list-inside text-sm space-y-1">
                    {slot.steps.map((st) => <li key={st.id}>{st.name}</li>)}
                  </ol>
                  {slot.done
                    ? <p className="text-sm text-green-700 flex items-center gap-1"><Check size={16} /> Zrobione</p>
                    : <button onClick={() => markDone(slot)} disabled={busy === slot.slot}
                        className="bg-green-600 disabled:opacity-50 text-white rounded px-4 py-2 text-sm">Zrobione</button>}
                </>
              )}
            </div>
          ))}
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  )
}

function StepRow({ step, onChange }) {
  const [error, setError] = useState('')
  const run = async (fn) => {
    setError('')
    try { await fn(); await onChange() } catch (e) { setError(errText(e)) }
  }
  return (
    <li className={`border rounded p-3 ${step.active ? '' : 'opacity-60'}`}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-medium text-sm">{step.name}</p>
          <p className="text-xs text-gray-600">{daysText(step.weekdays)}{step.essential ? ' · podstawowy (zostaje w trybie minimum)' : ''}{step.active ? '' : ' · wyłączony'}</p>
          {step.note && <p className="text-xs text-gray-600 mt-1">{step.note}</p>}
          <Evidence evidence={step.evidence} />
        </div>
        {step.id && (
          <div className="flex flex-col items-end gap-1 text-xs">
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={step.active} onChange={(e) => run(() => updateRoutineStep(step.id, { active: e.target.checked }))} /> włączony
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={step.essential} onChange={(e) => run(() => updateRoutineStep(step.id, { essential: e.target.checked }))} /> podstawowy
            </label>
            <button aria-label={`Usuń ${step.name}`} onClick={() => run(() => deleteRoutineStep(step.id))} className="text-red-600"><Trash2 size={16} /></button>
          </div>
        )}
      </div>
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
    </li>
  )
}

function AddStepForm({ onAdded }) {
  const [slot, setSlot] = useState('morning')
  const [name, setName] = useState('')
  const [days, setDays] = useState('0123456')
  const [error, setError] = useState('')
  const toggleDay = (d) => setDays((cur) => (cur.includes(d) ? cur.replace(d, '') : [...cur + d].sort().join('')))
  const submit = async () => {
    setError('')
    try {
      await addRoutineStep({ slot, name, weekdays: days })
      setName('')
      await onAdded()
    } catch (e) { setError(errText(e)) }
  }
  return (
    <div className="border-t pt-4 space-y-2">
      <p className="text-sm font-medium">Dodaj krok</p>
      <div className="flex flex-wrap gap-2">
        <select aria-label="Pora" className="border rounded px-2 py-2" value={slot} onChange={(e) => setSlot(e.target.value)}>
          <option value="morning">Rano</option><option value="evening">Wieczór</option>
        </select>
        <input className="border rounded px-2 py-2 flex-1 min-w-[12rem]" placeholder="np. Krem z filtrem SPF 50" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="flex flex-wrap gap-2 text-sm">
        {DAYS.map((label, i) => (
          <label key={label} className="flex items-center gap-1">
            <input type="checkbox" checked={days.includes(String(i))} onChange={() => toggleDay(String(i))} /> {label}
          </label>
        ))}
      </div>
      <button onClick={submit} disabled={!name.trim() || !days} className="bg-gray-800 disabled:opacity-50 text-white rounded px-4 py-2 text-sm flex items-center gap-1"><Plus size={16} /> Dodaj</button>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  )
}

function MyRoutine({ routine, onChange }) {
  const [error, setError] = useState('')
  if (!routine) return null
  const saveDefault = async () => {
    setError('')
    try { await createDefaultRoutine(); await onChange() } catch (e) { setError(errText(e)) }
  }
  return (
    <div className="bg-white border rounded-lg p-6 space-y-4">
      <h2 className="text-xl font-semibold">Moja rutyna</h2>
      {!routine.saved && (
        <div className="bg-blue-50 border border-blue-200 rounded p-4 space-y-2">
          <p className="text-sm text-blue-900">
            Propozycja na start. Nie znam Twoich kosmetyków, więc to podstawy z najmocniejszymi dowodami. Po zapisaniu możesz kroki wyłączać, usuwać i dodawać własne.
          </p>
          <button onClick={saveDefault} className="bg-blue-600 text-white rounded px-4 py-2 text-sm">Zapisz jako moją rutynę</button>
        </div>
      )}
      <div className="grid md:grid-cols-2 gap-4">
        {Object.keys(SLOT_NAMES).map((slot) => (
          <div key={slot} className="space-y-2">
            <div className="flex items-center gap-2 font-medium">{SLOT_ICONS[slot]} {SLOT_NAMES[slot]}</div>
            <ul className="space-y-2">
              {routine.steps.filter((st) => st.slot === slot).map((st) => <StepRow key={st.id ?? st.name} step={st} onChange={onChange} />)}
            </ul>
          </div>
        ))}
      </div>
      <AddStepForm onAdded={onChange} />
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  )
}

export default function SkincareRoutine() {
  const [routine, setRoutine] = useState(null)
  const [loading, setLoading] = useState(true)
  const [rotation, setRotation] = useState({ actives: [], recommendations: [] })

  const [today, setToday] = useState(null)
  const [myRoutine, setMyRoutine] = useState(null)

  const loadRotation = () => getMyRotation().then(setRotation).catch(() => {})
  const loadMine = () => Promise.all([
    getRoutineToday().then(setToday).catch(() => setToday(null)),
    getMyRoutine().then(setMyRoutine).catch(() => setMyRoutine(null)),
  ])
  useEffect(() => {
    getSkincareRoutine().then(setRoutine).catch(() => setRoutine(null)).finally(() => setLoading(false))
    loadRotation()
    loadMine()
  }, [])

  if (loading) return <div className="text-center py-20">Wczytuję rutynę…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Droplets size={28} className="text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Pielęgnacja</h1>
      </div>

      <TodayCard today={today} onDone={loadMine} />
      <MyRoutine routine={myRoutine} onChange={loadMine} />

      {routine && (
        <>
          <h2 className="text-xl font-semibold pt-2">Rutyna z generatora (przykład, nie zapisuje się)</h2>
          <div className={`${routine.survival_mode ? 'bg-amber-50 border-amber-200' : 'bg-blue-50 border-blue-200'} border rounded-lg p-4 flex items-start gap-3`}>
            <Info size={20} className="text-blue-600 mt-0.5" />
            <div>
              <p className="font-medium text-blue-900">Typ skóry: {routine.skin_type}</p>
              <p className="text-sm text-blue-700 mt-1">{routine.notes}</p>
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <RoutineColumn icon={<Sun size={20} className="text-yellow-500" />} title="Rano" steps={routine.morning} />
            <RoutineColumn icon={<Moon size={20} className="text-indigo-500" />} title="Wieczór" steps={routine.evening} />
          </div>
        </>
      )}
      {!routine && <p className="text-gray-500">Rutyna niedostępna — sprawdź, czy backend działa.</p>}

      <MyProducts onChange={loadRotation} />

      {rotation.recommendations.length > 0 && (
        <div className="bg-white border rounded-lg p-6 space-y-2">
          <h2 className="text-xl font-semibold flex items-center gap-2"><RotateCcw size={18} /> Rotacja składników</h2>
          {rotation.recommendations.map((r) => (
            <p key={r.ingredient} className="text-sm">
              <b>{r.ingredient}</b> jest w użyciu od pełnego cyklu — rozważ przerwę
              {r.alternatives?.length ? ` albo zamianę na: ${r.alternatives.map((a) => a.name || a).join(', ')}` : ''}.
            </p>
          ))}
        </div>
      )}

      <ReactionForm actives={rotation.actives} />
    </div>
  )
}
