import { useEffect, useState } from 'react'
import {
  deleteProduct, getMyRotation, getProducts, getSkincareRoutine, logProductUsage,
  logSkinReaction, parseProductText, saveProduct, scanProductLabel,
} from '../api/client'
import { AlertTriangle, Camera, Check, Droplets, Info, Moon, RotateCcw, Sun, Trash2 } from 'lucide-react'

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
      <input className="w-full border rounded px-3 py-2" placeholder="Nazwa produktu" value={name} onChange={(e) => setName(e.target.value)} />
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
            <textarea className="border rounded p-2 text-sm flex-1" rows={3} placeholder="…albo wklej skład: Aqua, Glycerin, Niacinamide, …" value={text} onChange={(e) => setText(e.target.value)} />
            <button onClick={parse} disabled={!text.trim()} className="bg-blue-600 disabled:opacity-50 text-white rounded py-2 text-sm">Sprawdź skład</button>
          </div>
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
        <select className="border rounded px-2 py-2" value={ingredient} onChange={(e) => setIngredient(e.target.value)}>
          <option value="">Składnik…</option>
          {actives.map((a) => <option key={a}>{a}</option>)}
        </select>
        <select className="border rounded px-2 py-2" value={reaction} onChange={(e) => setReaction(e.target.value)}>
          {REACTIONS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
        </select>
        <select className="border rounded px-2 py-2" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="low">lekka</option><option value="medium">średnia</option><option value="high">silna</option>
        </select>
      </div>
      <button onClick={submit} disabled={!ingredient} className="bg-gray-800 disabled:opacity-50 text-white rounded px-4 py-2 text-sm">Zapisz reakcję</button>
      {done && <p className="text-sm text-green-700">{done}</p>}
    </div>
  )
}

export default function SkincareRoutine() {
  const [routine, setRoutine] = useState(null)
  const [loading, setLoading] = useState(true)
  const [rotation, setRotation] = useState({ actives: [], recommendations: [] })

  const loadRotation = () => getMyRotation().then(setRotation).catch(() => {})
  useEffect(() => {
    getSkincareRoutine().then(setRoutine).catch(() => setRoutine(null)).finally(() => setLoading(false))
    loadRotation()
  }, [])

  if (loading) return <div className="text-center py-20">Wczytuję rutynę…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Droplets size={28} className="text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Pielęgnacja</h1>
      </div>

      {routine && (
        <>
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
