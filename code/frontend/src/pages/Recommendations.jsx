import { useState, useEffect } from 'react'
import { getRecommendations } from '../api/client'
import { ArrowUpRight, BarChart3, Clock, ShieldCheck } from 'lucide-react'

const evidenceColors = {
  'RCT': 'bg-green-100 text-green-800',
  'meta': 'bg-blue-100 text-blue-800',
  'observational': 'bg-yellow-100 text-yellow-800',
  'expert': 'bg-gray-100 text-gray-800',
}

const confidenceLabels = {
  high: 'High potential',
  moderate: 'Moderate potential',
  low: 'Exploratory',
}

const formatWeeks = (weeks) => {
  if (!weeks) return 'Timing not estimated'
  return `~${weeks} ${Number(weeks) === 1 ? 'week' : 'weeks'}`
}

const RecommendationCard = ({ recommendation, rank }) => (
  <article
    role="article"
    aria-labelledby={`recommendation-${rank}`}
    className="bg-white border rounded-lg p-5 sm:p-6 hover:shadow-md transition-shadow"
  >
    <div className="flex justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 id={`recommendation-${rank}`} className="text-lg font-semibold text-gray-900">
              {recommendation.name}
            </h3>
            <p className="text-xs text-gray-500 mt-1">{recommendation.category || 'LookCoach intervention'}</p>
          </div>
          <span className="shrink-0 px-3 py-1 bg-gray-900 text-white rounded-full text-sm font-medium">
            #{rank}
          </span>
        </div>
        {recommendation.description && (
          <p className="text-sm text-gray-600 mt-3">{recommendation.description}</p>
        )}
        <div className="flex flex-wrap gap-2 mt-4">
          <span className={`px-2 py-1 rounded text-xs font-medium ${evidenceColors[recommendation.evidence_level] || 'bg-gray-100 text-gray-800'}`}>
            {recommendation.evidence_level || 'Evidence not classified'}
          </span>
          <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded text-xs font-medium flex items-center gap-1">
            <Clock size={12} />
            {formatWeeks(recommendation.time_to_effect)}
          </span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium flex items-center gap-1">
            <BarChart3 size={12} />
            {confidenceLabels[recommendation.confidence] || 'Exploratory'}
          </span>
        </div>
        {recommendation.study_url && (
          <a
            href={recommendation.study_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-xs font-medium text-blue-700 hover:text-blue-900 mt-4"
          >
            Evidence source <ArrowUpRight size={12} />
          </a>
        )}
      </div>
    </div>
  </article>
)

export default function Recommendations() {
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getRecommendations(10)
      .then((data) => {
        const recommendations = Array.isArray(data) ? [...data] : []
        setRecs(recommendations.sort((a, b) => (b.roi_score ?? 0) - (a.roi_score ?? 0)))
        setError('')
      })
      .catch(() => {
        setError('Recommendations could not be loaded. Please try again.')
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-20">Loading recommendations...</div>
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <ShieldCheck size={28} className="text-red-600" />
          <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
        <p className="text-gray-600 mt-2">
          Interventions ordered by evidence-adjusted ROI. The ranking is directional; no precise effect score is shown.
        </p>
      </div>
      {recs.length > 0 ? (
        <div className="grid gap-4">
          {recs.map((rec, idx) => (
            <RecommendationCard key={rec.id || rec.name || idx} recommendation={rec} rank={idx + 1} />
          ))}
        </div>
      ) : (
        <div className="bg-white border rounded-lg p-8 text-center text-gray-600">
          No recommendations available right now.
        </div>
      )}
    </div>
  )
}
