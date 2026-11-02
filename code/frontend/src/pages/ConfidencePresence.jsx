import { useState, useEffect } from 'react'
import { Brain } from 'lucide-react'
import { getConfidenceAnalysis, getActionPlan } from '../api/client'

export default function ConfidencePresence() {
  const [analysis, setAnalysis] = useState(null)
  const [plan, setPlan] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getConfidenceAnalysis(),
      getActionPlan(),
    ]).then(([analysisData, planData]) => {
      setAnalysis(analysisData)
      setPlan(planData.plan || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-20">Ładowanie analizy...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain size={28} className="text-purple-600" />
        <h1 className="text-3xl font-bold text-gray-900">Confidence & Presence</h1>
      </div>

      {analysis && analysis.has_analysis === false && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-blue-900">
          {analysis.message}
        </div>
      )}

      {analysis?.has_analysis && (
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Posture Indicators</h3>
            <StatusBadge status={analysis.posture?.status} color="purple" />
            {analysis.posture?.issues?.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Issues:</h4>
                <ul className="space-y-1">
                  {analysis.posture.issues.map((issue, i) => (
                    <li key={i} className="text-sm text-gray-600">• {issue}</li>
                  ))}
                </ul>
              </div>
            )}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations:</h4>
              <ul className="space-y-1">
                {analysis.posture?.recommendations?.map((rec, i) => (
                  <li key={i} className="text-sm text-gray-600">• {rec}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="bg-white border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Facial Expressions</h3>
            <StatusBadge status={analysis.facial?.status} color="blue" />
            {analysis.facial?.issues?.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Issues:</h4>
                <ul className="space-y-1">
                  {analysis.facial.issues.map((issue, i) => (
                    <li key={i} className="text-sm text-gray-600">• {issue}</li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.facial?.micro_habits && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Micro-Habits:</h4>
                <ul className="space-y-1">
                  {analysis.facial.micro_habits.map((habit, i) => (
                    <li key={i} className="text-sm text-gray-600">• {habit}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">7-Day Confidence Building Plan</h3>
        <div className="space-y-4">
          {plan.map((day, idx) => (
            <div key={idx} className="border-l-4 border-purple-500 pl-4">
              <h4 className="font-medium text-gray-900">
                Day {day.day}: <span className="text-purple-600">{day.focus}</span>
              </h4>
              <ul className="mt-2 space-y-1">
                {day.actions.map((action, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-purple-500 mt-0.5">•</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}

function StatusBadge({ status, color }) {
  if (!status || status === 'unknown') return null
  const styles = {
    good: { purple: 'bg-purple-100 text-purple-800', blue: 'bg-blue-100 text-blue-800' },
    needs_work: { purple: 'bg-yellow-100 text-yellow-800', blue: 'bg-yellow-100 text-yellow-800' },
  }
  const labels = { good: 'Good', needs_work: 'Needs work' }
  const palette = styles[status] || {}
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-4 ${palette[color] || 'bg-gray-100 text-gray-700'}`}>
      {labels[status] || status}
    </span>
  )
}
