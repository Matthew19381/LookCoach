import { useEffect, useMemo, useState } from 'react'
import { getRecommendations } from '../api/client'
import { ArrowUpRight, BarChart3, Clock, ShieldCheck, Sparkles } from 'lucide-react'

const confidenceLabels = {
  high: 'High potential',
  moderate: 'Moderate potential',
  low: 'Exploratory',
}

const confidenceKeys = ['high', 'moderate', 'low']

const categoryLabel = (category) => {
  if (!category) return 'LookCoach'
  return category
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const formatWeeks = (weeks) => {
  if (!weeks) return 'Not estimated'
  return `~${weeks} ${Number(weeks) === 1 ? 'week' : 'weeks'}`
}

export default function PriorityBoard() {
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    getRecommendations(20)
      .then((data) => {
        const recommendations = Array.isArray(data) ? [...data] : []
        setRecs(recommendations.sort((a, b) => (b.roi_score ?? 0) - (a.roi_score ?? 0)))
        setError('')
      })
      .catch(() => setError('Priority data could not be loaded. Please try again.'))
      .finally(() => setLoading(false))
  }, [])

  const grouped = useMemo(() => {
    const result = { all: recs }
    confidenceKeys.forEach((key) => {
      result[key] = recs.filter((rec) => rec.confidence === key)
    })
    return result
  }, [recs])

  const visibleRecs = filter === 'all' ? recs : grouped[filter]
  const highConfidenceCount = grouped.high.length
  const moderateConfidenceCount = grouped.moderate.length

  if (loading) {
    return <div className="text-center py-20">Loading ROI priorities...</div>
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <ShieldCheck size={28} className="text-red-600" />
          <h1 className="text-3xl font-bold text-gray-900">ROI priorities</h1>
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
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ROI priorities</h1>
            <p className="text-gray-600 mt-2">
              A focused view of the interventions with the strongest evidence-adjusted return.
            </p>
          </div>
          <BarChart3 size={32} className="text-blue-600 mt-2" aria-hidden="true" />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6">
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-500">Interventions</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{recs.length}</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-500">High potential</p>
            <p className="text-2xl font-bold text-green-700 mt-1">{highConfidenceCount}</p>
          </div>
          <div className="bg-white border rounded-lg p-4">
            <p className="text-sm text-gray-500">Moderate potential</p>
            <p className="text-2xl font-bold text-blue-700 mt-1">{moderateConfidenceCount}</p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="ROI priority filters">
        {[
          ['all', 'All'],
          ['high', 'High potential'],
          ['moderate', 'Moderate potential'],
          ['low', 'Exploratory'],
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={filter === key}
            onClick={() => setFilter(key)}
            className={`px-3 py-2 rounded-md text-sm font-medium border transition-colors ${
              filter === key
                ? 'bg-gray-900 text-white border-gray-900'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {visibleRecs.length > 0 ? (
        <div className="grid gap-4" role="tabpanel" aria-label={`${filter} ROI priorities`}>
          {visibleRecs.map((rec, idx) => {
            const rank = recs.indexOf(rec) + 1
            const confidence = confidenceLabels[rec.confidence] || 'Exploratory'
            return (
              <article key={rec.id || rec.name || idx} className="bg-white border rounded-lg p-5 sm:p-6">
                <div className="flex items-start gap-4">
                  <div className="shrink-0 w-10 h-10 rounded-full bg-blue-50 text-blue-700 flex items-center justify-center font-bold">
                    {rank}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">{rec.name}</h2>
                        <p className="text-sm text-gray-500 mt-1">{categoryLabel(rec.category)}</p>
                      </div>
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                        {confidence}
                      </span>
                    </div>
                    {rec.description && <p className="text-sm text-gray-600 mt-3">{rec.description}</p>}
                    <div className="flex flex-wrap gap-2 mt-4">
                      <span className="px-2 py-1 bg-green-50 text-green-800 border border-green-200 rounded text-xs font-medium">
                        {rec.evidence_level || 'Evidence not classified'}
                      </span>
                      <span className="px-2 py-1 bg-orange-50 text-orange-800 border border-orange-200 rounded text-xs font-medium flex items-center gap-1">
                        <Clock size={12} />
                        {formatWeeks(rec.time_to_effect)}
                      </span>
                      {rec.study_url && (
                        <a
                          href={rec.study_url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-1 bg-blue-50 text-blue-800 border border-blue-200 rounded text-xs font-medium flex items-center gap-1 hover:bg-blue-100"
                        >
                          Evidence <ArrowUpRight size={12} />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      ) : (
        <div className="bg-white border rounded-lg p-8 text-center text-gray-600">
          <Sparkles className="mx-auto text-gray-400" size={28} />
          <p className="mt-3">No interventions in this priority band.</p>
        </div>
      )}
    </div>
  )
}