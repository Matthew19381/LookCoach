import { useState, useEffect } from 'react'
import { getSkincareRoutine } from '../api/client'
import { Sun, Moon, Droplets, Info } from 'lucide-react'

export default function SkincareRoutine() {
  const [routine, setRoutine] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSkincareRoutine().then((data) => {
      setRoutine(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-20">Loading skincare routine...</div>
  }

  if (!routine) {
    return <div className="text-center py-20 text-gray-500">No routine available</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Droplets size={28} className="text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Skincare Routine</h1>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
        <Info size={20} className="text-blue-600 mt-0.5" />
        <div>
          <p className="font-medium text-blue-900">Skin Type: {routine.skin_type}</p>
          <p className="text-sm text-blue-700 mt-1">{routine.notes}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Sun size={20} className="text-yellow-500" />
            <h2 className="text-xl font-semibold">Morning Routine</h2>
          </div>
          <ol className="space-y-3">
            {routine.morning.map((step, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-yellow-100 text-yellow-800 rounded-full flex items-center justify-center text-sm font-medium">
                  {idx + 1}
                </span>
                <span className="text-gray-900">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        <div className="bg-white border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Moon size={20} className="text-indigo-500" />
            <h2 className="text-xl font-semibold">Evening Routine</h2>
          </div>
          <ol className="space-y-3">
            {routine.evening.map((step, idx) => (
              <li key={idx} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-800 rounded-full flex items-center justify-center text-sm font-medium">
                  {idx + 1}
                </span>
                <span className="text-gray-900">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  )
}
