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

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <h2 className="text-2xl font-bold text-blue-900">Look Score</h2>
        <p className="text-5xl font-bold text-blue-600 mt-2">{analysis.overall_score}</p>
      </div>

      {analysis.lever && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-900">Primary Focus: {analysis.lever.primary_lever}</h3>
          <p className="text-green-700 mt-1">{analysis.lever.reason}</p>
          <div className="mt-3">
            <p className="text-sm font-medium text-green-800">Secondary levers:</p>
            <div className="flex gap-2 mt-1">
              {analysis.lever.secondary_levers.map((l) => (
                <span key={l} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">{l}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {analysis.face && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Face Analysis</h3>
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">{JSON.stringify(analysis.face, null, 2)}</pre>
        </div>
      )}

      {analysis.body && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Body Analysis</h3>
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">{JSON.stringify(analysis.body, null, 2)}</pre>
        </div>
      )}

      {analysis.skin && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Skin Analysis</h3>
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">{JSON.stringify(analysis.skin, null, 2)}</pre>
        </div>
      )}

      {analysis.hair && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Hair Analysis</h3>
          <pre className="bg-gray-50 p-4 rounded text-sm overflow-auto">{JSON.stringify(analysis.hair, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
