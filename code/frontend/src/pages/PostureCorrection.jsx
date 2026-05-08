import { useState, useEffect } from 'react'
import { Stretch, AlertTriangle, CheckCircle } from 'lucide-react'
import { getPostureIssues, detectPostureIssues, getCorrectionPlan, fullPostureAssessment } from '../api/client'

export default function PostureCorrection() {
  const [issues, setIssues] = useState([])
  const [selectedIssue, setSelectedIssue] = useState(null)
  const [correction, setCorrection] = useState(null)
  const [assessment, setAssessment] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getPostureIssues().then(data => {
      setIssues(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const handleDetect = async () => {
    // In real app, this would use actual body analysis
    const mockAnalysis = { head_position: 'forward', shoulder_position: 'forward' }
    try {
      const result = await detectPostureIssues(mockAnalysis)
      setAssessment(result)
    } catch (e) {
      console.error('Detection failed:', e)
    }
  }

  const handleGetCorrection = async (issueId) => {
    try {
      const result = await getCorrectionPlan(issueId)
      setSelectedIssue(issueId)
      setCorrection(result)
    } catch (e) {
      console.error('Correction plan failed:', e)
    }
  }

  const handleFullAssessment = async () => {
    const mockAnalysis = { head_position: 'forward', shoulder_position: 'forward' }
    try {
      const result = await fullPostureAssessment(mockAnalysis)
      setAssessment(result)
    } catch (e) {
      console.error('Assessment failed:', e)
    }
  }

  if (loading) {
    return <div className="text-center py-20">Loading posture issues...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Stretch size={28} className="text-green-600" />
        <h1 className="text-3xl font-bold text-gray-900">Posture Correction</h1>
      </div>

      <div className="flex gap-2">
        <button
          onClick={handleDetect}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Detect Issues
        </button>
        <button
          onClick={handleFullAssessment}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          Full Assessment
        </button>
      </div>

      {assessment && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Assessment Results</h3>
          <p className="mb-2">Issues detected: <span className="font-bold">{assessment.issues_detected}</span></p>
          {assessment.issues?.map((issue, idx) => (
            <div key={idx} className="bg-white border rounded p-4 mb-2">
              <p className="font-medium">{issue.name}</p>
              <p className="text-sm text-gray-600">{issue.description}</p>
            </div>
          ))}
          {assessment.daily_habits && (
            <div className="mt-4">
              <h4 className="font-medium mb-2">Daily Habits:</h4>
              <ul className="space-y-1">
                {assessment.daily_habits.map((habit, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <CheckCircle size={16} className="text-green-500 mt-0.5" />
                    {habit}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {issues.map((issue) => (
          <div key={issue.id} className="bg-white border rounded-lg p-6">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle size={20} className="text-yellow-500" />
              <h3 className="font-semibold">{issue.name}</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">{issue.description}</p>
            <p className="text-xs text-gray-500 mb-4">Impact: {issue.looks_impact}</p>
            <button
              onClick={() => handleGetCorrection(issue.id)}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
            >
              Get Correction Plan
            </button>
          </div>
        ))}
      </div>

      {correction && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Correction Plan: {correction.issue}</h3>
          <p className="text-sm text-gray-600 mb-4">{correction.info?.description}</p>
          <div className="space-y-3">
            {correction.corrections?.map((ex, idx) => (
              <div key={idx} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                <span className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-800 rounded-full flex items-center justify-center text-xs font-medium">
                  {idx + 1}
                </span>
                <div>
                  <p className="font-medium text-sm">{ex.exercise}</p>
                  <p className="text-xs text-gray-600">{ex.sets} • {ex.focus}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
