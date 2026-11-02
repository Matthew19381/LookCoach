import { useEffect, useRef, useState } from 'react'
import { ScanLine } from 'lucide-react'

// Plan 5.7: kod kreskowy wpisany ręcznie albo odczytany kamerą (BarcodeDetector — Chrome/Android;
// gdzie go nie ma, zostaje wpisanie kodu).
export default function BarcodeBox({ onCode, busy }) {
  const [code, setCode] = useState('')
  const [scanning, setScanning] = useState(false)
  const [camError, setCamError] = useState(null)
  const videoRef = useRef(null)
  // latest callback without restarting the camera on every parent render
  const onCodeRef = useRef(onCode)
  useEffect(() => { onCodeRef.current = onCode })
  const supported = typeof window !== 'undefined' && 'BarcodeDetector' in window

  useEffect(() => {
    if (!scanning) return undefined
    let stream
    let timer
    let stopped = false
    const start = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
        if (stopped) return
        videoRef.current.srcObject = stream
        await videoRef.current.play()
        const detector = new window.BarcodeDetector({ formats: ['ean_13', 'ean_8', 'upc_a', 'upc_e'] })
        timer = setInterval(async () => {
          const found = await detector.detect(videoRef.current).catch(() => [])
          if (found.length) {
            setScanning(false)
            setCode(found[0].rawValue)
            onCodeRef.current(found[0].rawValue)
          }
        }, 400)
      } catch {
        setCamError('Brak dostępu do kamery — wpisz kod ręcznie.')
        setScanning(false)
      }
    }
    start()
    return () => {
      stopped = true
      clearInterval(timer)
      stream?.getTracks().forEach((t) => t.stop())
    }
  }, [scanning])

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          aria-label="Kod kreskowy"
          inputMode="numeric"
          className="border rounded px-2 py-2 text-sm flex-1"
          placeholder="Kod kreskowy (EAN)"
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 14))}
        />
        <button onClick={() => onCode(code)} disabled={busy || code.length < 8}
          className="bg-blue-600 disabled:opacity-50 text-white rounded px-3 text-sm">Szukaj</button>
        {supported && (
          <button onClick={() => { setCamError(null); setScanning(!scanning) }} aria-label="Skanuj kamerą"
            className="border rounded px-2 hover:bg-gray-50"><ScanLine size={18} /></button>
        )}
      </div>
      {scanning && <video ref={videoRef} muted playsInline className="w-full max-h-56 rounded bg-black" />}
      {camError && <p className="text-xs text-red-600">{camError}</p>}
      <p className="text-xs text-gray-500">Skład z otwartej bazy Open Beauty Facts — nie każdy produkt tam jest.</p>
    </div>
  )
}
