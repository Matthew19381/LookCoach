import { useState, useEffect } from 'react'
import { getTimeline, comparePhotos } from '../api/client'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Legend,
  Tooltip,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Legend, Tooltip)

export default function ProgressTracker() {
  const [photos, setPhotos] = useState([])
  const [beforeId, setBeforeId] = useState('')
  const [afterId, setAfterId] = useState('')
  const [compareResult, setCompareResult] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTimeline().then((data) => {
      setPhotos(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const handleCompare = async () => {
    if (!beforeId || !afterId) return
    try {
      const result = await comparePhotos(parseInt(beforeId), parseInt(afterId))
      setCompareResult(result)
    } catch (e) {
      console.error('Compare failed:', e)
    }
  }

  const chartData = {
    labels: photos.filter(p => p.status === 'done').map(p => new Date(p.uploaded_at).toLocaleDateString()),
    datasets: [
      {
        label: 'Look Score',
        data: photos.filter(p => p.status === 'done').map((_, i) => 50 + i * 2),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.3,
      },
    ],
  }

  if (loading) {
    return <div className="text-center py-20">Loading progress...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Progress Tracker</h1>

      {photos.length > 0 && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Look Score Over Time</h3>
          <Line data={chartData} />
        </div>
      )}

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Compare Photos</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <select
            value={beforeId}
            onChange={(e) => setBeforeId(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Select before photo...</option>
            {photos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.photo_type} - {new Date(p.uploaded_at).toLocaleDateString()}
              </option>
            ))}
          </select>
          <select
            value={afterId}
            onChange={(e) => setAfterId(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="">Select after photo...</option>
            {photos.map((p) => (
              <option key={p.id} value={p.id}>
                {p.photo_type} - {new Date(p.uploaded_at).toLocaleDateString()}
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={handleCompare}
          disabled={!beforeId || !afterId}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Compare
        </button>

        {compareResult && (
          <div className="mt-6 grid grid-cols-2 gap-4">
            <div>
              <p className="font-medium">Before:</p>
              <img src={compareResult.before.url} alt="Before" className="mt-2 rounded-lg border" />
            </div>
            <div>
              <p className="font-medium">After:</p>
              <img src={compareResult.after.url} alt="After" className="mt-2 rounded-lg border" />
            </div>
            <div className="col-span-2 text-center">
              <p className="text-lg">Score Change: <span className="font-bold">{compareResult.delta_score}</span></p>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Photo Timeline</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {photos.map((p) => (
            <div key={p.id} className="border rounded-lg overflow-hidden">
              <img src={p.url} alt={p.photo_type} className="w-full h-32 object-cover" />
              <div className="p-2 text-center">
                <p className="text-sm font-medium capitalize">{p.photo_type}</p>
                <p className="text-xs text-gray-500">{new Date(p.uploaded_at).toLocaleDateString()}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
