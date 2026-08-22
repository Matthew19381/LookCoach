import { useState, useEffect } from 'react'
import { RefreshCw, AlertCircle } from 'lucide-react'
import { getAnalysis } from '../api/client'

export default function AnalysisResults() {
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchAnalysis = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getAnalysis()
      setAnalysis(data)
    } catch (e) {
      setError(`Failed to load analysis: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnalysis()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <RefreshCw size={32} className="animate-spin text-blue-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
        <AlertCircle className="inline mr-2" size={18} />
        {error}
      </div>
    )
  }

  if (!analysis || analysis.photos_analyzed === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-6 text-center">
          <p className="text-yellow-800 mb-4">Please upload all 3 photos (front, side, back) to get your analysis.</p>
          <a href="/" className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Go to Upload
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
        <button
          onClick={fetchAnalysis}
          className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
        >
          <RefreshCw size={16} className="mr-2" />
          Refresh
        </button>
      </div>

      {(analysis.face?.observations?.length || analysis.body?.observations?.length) ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-2xl font-bold text-blue-900">Observations</h2>
          <ul className="mt-2 space-y-1 text-blue-800">
            {[...(analysis.face?.observations || []), ...(analysis.body?.observations || [])].map((obs, i) => (
              <li key={i}>• {obs}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {analysis.lever && analysis.lever.primary_lever && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900">Primary Focus: {analysis.lever.primary_lever}</h3>
          <p className="text-green-700 mt-1">{analysis.lever.reason}</p>
          {analysis.lever.secondary_levers && (
            <div className="mt-3">
              <p className="text-sm font-medium text-green-800">Secondary levers:</p>
              <div className="flex gap-2 mt-1 flex-wrap">
                {analysis.lever.secondary_levers.map((l) => (
                  <span key={l} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">{l}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {analysis.face && (
        <SectionCard title="Face Analysis" data={analysis.face} />
      )}
      {analysis.body && (
        <SectionCard title="Body Analysis" data={analysis.body} />
      )}
      {analysis.skin && (
        <SectionCard title="Skin Analysis" data={analysis.skin} />
      )}
      {analysis.hair && (
        <SectionCard title="Hair Analysis" data={analysis.hair} />
      )}
    </div>
  )
}

function SectionCard({ title, data }) {
  return (
    <div className="bg-white border rounded-lg p-6">
      <h3 className="text-xl font-semibold mb-4">{title}</h3>
      <dl className="space-y-2 text-sm">
        {Object.entries(data).map(([key, value]) => (
          <div key={key} className="flex flex-col sm:flex-row sm:gap-2">
            <dt className="font-medium text-gray-700 capitalize sm:w-48 shrink-0">
              {key.replace(/_/g, ' ')}
            </dt>
            <dd className="text-gray-600">
              {Array.isArray(value)
                ? value.map((v, i) => (
                    <span key={i} className="inline-block mr-1">
                      {typeof v === 'object' ? JSON.stringify(v) : v};
                    </span>
                  ))
                : typeof value === 'object' && value !== null
                  ? Object.entries(value).map(([k, v]) => `${k.replace(/_/g, ' ')}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' · ')
                  : String(value)}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
