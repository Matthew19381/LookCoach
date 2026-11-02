import { useState } from 'react'
import { Camera, Upload, CheckCircle, Loader2 } from 'lucide-react'
import { uploadPhoto, analyzePhoto } from '../api/client'

// D1 (2026-11-02): co jest analizowane z którego ujęcia
const PHOTO_GUIDE = {
  front: { title: 'Przód', what: 'twarz, skóra, brwi, zarost, linia włosów', how: 'twarz na wprost, równe światło dzienne, bez filtrów' },
  side: { title: 'Bok', what: 'sylwetka i postawa', how: 'cała sylwetka z profilu, swobodna postawa' },
  back: { title: 'Tył', what: 'czubek głowy (gęstość włosów)', how: 'z tyłu i lekko z góry, widoczny czubek głowy' },
}

export default function PhotoUpload() {
  const [uploading, setUploading] = useState({ front: false, side: false, back: false })
  const [uploaded, setUploaded] = useState({ front: null, side: null, back: null })
  const [error, setError] = useState('')
  // per view: {state: 'analyzing'|'done'|'quality'|'failed', problems?, message?}
  const [analysis, setAnalysis] = useState({ front: null, side: null, back: null })
  const [wellbeing, setWellbeing] = useState(null)

  // Until 2026-11-02 nothing in the UI ever called the analysis endpoint:
  // photos stayed "pending" and the results page was always empty.
  const runAnalysis = async (photoId, type, force = false) => {
    setAnalysis((prev) => ({ ...prev, [type]: { state: 'analyzing' } }))
    try {
      await analyzePhoto(photoId, force)
      setAnalysis((prev) => ({ ...prev, [type]: { state: 'done' } }))
    } catch (e) {
      const detail = e.response?.data?.detail
      if (e.response?.status === 422 && detail?.problems) {
        setAnalysis((prev) => ({ ...prev, [type]: { state: 'quality', problems: detail.problems } }))
      } else if (e.response?.status === 429 && detail?.message) {
        // Plan 5.6: very frequent checking - pause, the user decides
        setAnalysis((prev) => ({ ...prev, [type]: { state: 'paused', problems: [detail.message] } }))
      } else {
        const message = typeof detail === 'string' ? detail : 'Analiza nie powiodła się.'
        setAnalysis((prev) => ({ ...prev, [type]: { state: 'failed', message } }))
      }
    }
  }

  const handleUpload = async (file, type) => {
    if (!file) return
    setUploading((prev) => ({ ...prev, [type]: true }))
    setError('')
    try {
      const result = await uploadPhoto(file, type)
      setUploaded((prev) => ({ ...prev, [type]: result }))
      if (result.wellbeing?.message) setWellbeing(result.wellbeing)
      if (result.quality && !result.quality.ok) {
        setAnalysis((prev) => ({ ...prev, [type]: { state: 'quality', problems: result.quality.problems } }))
      } else {
        runAnalysis(result.id, type)
      }
    } catch (e) {
      // Backend explains why (format, size) in Polish - show that, not axios' generic text.
      setError(`Nie udało się wysłać zdjęcia: ${e.response?.data?.detail || e.message}`)
    } finally {
      setUploading((prev) => ({ ...prev, [type]: false }))
    }
  }

  const handleDrop = (e, type) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && file.type.startsWith('image/')) {
      handleUpload(file, type)
    }
  }

  const handleFileSelect = (e, type) => {
    const file = e.target.files[0]
    if (file) handleUpload(file, type)
  }

  const anyAnalyzed = Object.values(analysis).some((a) => a?.state === 'done')

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Upload Your Photos</h1>
        <p className="mt-2 text-gray-600">
          Upload front, side, and back photos for AI analysis
        </p>
      </div>

      {wellbeing && (
        <div role="note" className={`rounded-md p-4 border ${wellbeing.level === 'concern'
          ? 'bg-purple-50 border-purple-200 text-purple-900' : 'bg-blue-50 border-blue-200 text-blue-900'}`}>
          {wellbeing.message}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {['front', 'side', 'back'].map((type) => (
          <div
            key={type}
            onDrop={(e) => handleDrop(e, type)}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
          >
            <div className="flex flex-col items-center space-y-4">
              <div className={`p-4 rounded-full ${uploaded[type] ? 'bg-green-100' : 'bg-gray-100'}`}>
                {uploaded[type] ? (
                  <CheckCircle size={32} className="text-green-600" />
                ) : (
                  <Camera size={32} className="text-gray-500" />
                )}
              </div>
              <div>
                <p className="font-medium">{PHOTO_GUIDE[type].title}</p>
                <p className="text-xs text-gray-600">Analiza: {PHOTO_GUIDE[type].what}</p>
                <p className="text-xs text-gray-500">{PHOTO_GUIDE[type].how}</p>
                <p className="text-sm text-gray-500">
                  {uploaded[type] ? 'Uploaded!' : 'Drop image or click to upload'}
                </p>
              </div>
              {uploading[type] && <Loader2 size={20} className="animate-spin text-blue-600" />}
              <AnalysisStatus
                status={analysis[type]}
                onForce={() => runAnalysis(uploaded[type].id, type, true)}
              />
              <label className="cursor-pointer inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                <Upload size={16} className="mr-2" />
                Choose File
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={(e) => handleFileSelect(e, type)}
                />
              </label>
            </div>
          </div>
        ))}
      </div>

      {anyAnalyzed && (
        <div className="flex justify-center">
          <a
            href="/analysis"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            Zobacz wyniki analizy
          </a>
        </div>
      )}
    </div>
  )
}


function AnalysisStatus({ status, onForce }) {
  if (!status) return null
  if (status.state === 'analyzing') {
    return <p className="text-sm text-blue-700 flex items-center gap-1"><Loader2 size={14} className="animate-spin" /> Analizuję…</p>
  }
  if (status.state === 'done') return <p className="text-sm text-green-700">Analiza gotowa</p>
  if (status.state === 'failed') return <p className="text-sm text-red-700">{status.message}</p>
  return (
    <div className="text-left text-sm bg-amber-50 border border-amber-200 rounded p-2 space-y-1">
      {status.problems.map((p) => <p key={p} className="text-amber-900">{p}</p>)}
      <button onClick={onForce} className="text-amber-800 underline">
        {status.state === 'paused' ? 'Rozumiem, analizuj' : 'Analizuj mimo to'}
      </button>
    </div>
  )
}
