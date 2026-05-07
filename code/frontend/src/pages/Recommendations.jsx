import { useState, useEffect } from 'react'
import { getRecommendations } from '../api/client'
import { Zap, Clock, BarChart3 } from 'lucide-react'

const evidenceColors = {
  'RCT': 'bg-green-100 text-green-800',
  'meta': 'bg-blue-100 text-blue-800',
  'observational': 'bg-yellow-100 text-yellow-800',
  'expert': 'bg-gray-100 text-gray-800',
}

export default function Recommendations() {
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getRecommendations(10).then((data) => {
      setRecs(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-20">Loading recommendations...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
      <div className="grid gap-4">
        {recs.map((rec, idx) => (
          <div key={idx} className="bg-white border rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{rec.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                <div className="flex gap-2 mt-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${evidenceColors[rec.evidence_level] || 'bg-gray-100'}`}>
                    {rec.evidence_level}
                  </span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium flex items-center gap-1">
                    <Zap size={12} />
                    {(rec.effect_size * 100).toFixed(0)}% effect
                  </span>
                  <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium flex items-center gap-1">
                    <Clock size={12} />
                    {rec.time_to_effect} weeks
                  </span>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium flex items-center gap-1">
                    <BarChart3 size={12} />
                    ROI: {rec.roi_score.toFixed(3)}
                  </span>
                </div>
              </div>
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                #{rec.priority || idx + 1}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
