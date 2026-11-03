import { useEffect, useRef, useState } from 'react'

// Plan 4.10: aparat z nakładką-szablonem — to samo ujęcie co ostatnio = porównywalne zdjęcia.
const GUIDES = {
  front: { facing: 'user', hint: 'Twarz w owalu, na wprost, światło od okna przed Tobą.',
    shape: <ellipse cx="50" cy="45" rx="22" ry="30" /> },
  side: { facing: 'environment', hint: 'Cała sylwetka z profilu w ramce, telefon na wysokości bioder.',
    shape: <path d="M50 8 a6 6 0 1 1 0.1 0 M44 20 h12 l4 30 h-6 l-2 38 h-4 l-2 -38 h-6 z" /> },
  smile: { facing: 'user', hint: 'Usta w prostokącie, szeroki uśmiech, światło od przodu.',
    shape: <rect x="28" y="50" width="44" height="20" rx="8" /> },
  back: { facing: 'environment', hint: 'Czubek głowy w kole, zdjęcie z tyłu i lekko z góry.',
    shape: <circle cx="50" cy="45" r="24" /> },
}

export default function CameraCapture({ type, onCapture, onClose }) {
  const videoRef = useRef(null)
  const [error, setError] = useState(null)
  const guide = GUIDES[type]

  useEffect(() => {
    let stream
    let stopped = false
    const start = async () => {
      if (!navigator.mediaDevices?.getUserMedia) {
        setError('Ta przeglądarka nie daje dostępu do aparatu — wybierz plik.')
        return
      }
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: guide.facing } })
        if (stopped) return
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      } catch {
        setError('Brak dostępu do aparatu — sprawdź uprawnienia albo wybierz plik.')
      }
    }
    start()
    return () => {
      stopped = true
      stream?.getTracks().forEach((t) => t.stop())
    }
  }, [guide.facing])

  const capture = () => {
    const video = videoRef.current
    if (!video?.videoWidth) return
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    canvas.toBlob((blob) => {
      if (blob) onCapture(new File([blob], `${type}.jpg`, { type: 'image/jpeg' }))
    }, 'image/jpeg', 0.92)
  }

  return (
    <div role="dialog" aria-label="Aparat" className="fixed inset-0 z-50 bg-black/80 flex flex-col items-center justify-center p-4 gap-3">
      {error ? (
        <p className="text-white bg-red-700 rounded p-3">{error}</p>
      ) : (
        <div className="relative w-full max-w-md">
          <video ref={videoRef} muted playsInline className="w-full rounded" />
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 w-full h-full pointer-events-none"
            fill="none" stroke="white" strokeWidth="0.8" strokeDasharray="2 2" aria-hidden="true">
            {guide.shape}
          </svg>
        </div>
      )}
      <p className="text-white text-sm text-center max-w-md">{guide.hint}</p>
      <div className="flex gap-3">
        {!error && <button onClick={capture} className="px-5 py-2 bg-white rounded-full font-medium">Zrób zdjęcie</button>}
        <button onClick={onClose} className="px-4 py-2 border border-white text-white rounded-full">Zamknij</button>
      </div>
    </div>
  )
}
