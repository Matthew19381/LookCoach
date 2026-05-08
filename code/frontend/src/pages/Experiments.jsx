import { useState, useEffect } from 'react'
import { FlaskConical, Play, Check, BarChart3, Plus, Calendar } from 'lucide-react'
import { getExperimentTemplates, startExperiment, getExperiment, logDaily, getResults, getActiveExperiments, finishExperiment } from '../api/client'

export default function Experiments() {
  const [templates, setTemplates] = useState([])
  const [activeExps, setActiveExps] = useState([])
  const [loading, setLoading] = useState(true)
  const [showStart, setShowStart] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [customName, setCustomName] = useState('')
  const [currentExp, setCurrentExp] = useState(null)
  const [dayRating, setDayRating] = useState(5)
  const [dayNotes, setDayNotes] = useState('')
  const [dayNumber, setDayNumber] = useState(1)
  const [results, setResults] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [tplRes, activeRes] = await Promise.all([
        getExperimentTemplates(),
        getActiveExperiments()
      ])
      setTemplates(tplRes.data || tplRes)
      setActiveExps(activeRes.data || activeRes)
    } catch (e) {
      console.error('Error loading experiments:', e)
    }
    setLoading(false)
  }

  const handleStart = async () => {
    if (!selectedTemplate) return
    try {
      const res = await startExperiment(selectedTemplate, customName || undefined)
      const exp = res.data || res
      setActiveExps([...activeExps, exp])
      setCurrentExp(exp)
      setShowStart(false)
      setSelectedTemplate(null)
      setCustomName('')
    } catch (e) {
      console.error('Error starting experiment:', e)
    }
  }

  const handleLogDay = async () => {
    if (!currentExp) return
    try {
      await logDaily(currentExp.id, dayNumber, dayRating, dayNotes)
      alert(`Day ${dayNumber} logged!`)
      setDayNotes('')
      setDayNumber(d => d + 1)
    } catch (e) {
      console.error('Error logging day:', e)
    }
  }

  const handleFinish = async () => {
    if (!currentExp) return
    try {
      const res = await finishExperiment(currentExp.id)
      setResults(res.data || res)
      setActiveExps(activeExps.filter(e => e.id !== currentExp.id))
    } catch (e) {
      console.error('Error finishing experiment:', e)
    }
  }

  const loadExperiment = async (exp) => {
    setCurrentExp(exp)
    setResults(null)
    try {
      const res = await getResults(exp.id)
      if (res.data || res) {
        setResults(res.data || res)
      }
    } catch (e) {
      console.error('Error loading results:', e)
    }
  }

  if (loading) return <div className="p-8 text-center">Loading experiments...</div>

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <FlaskConical className="text-purple-500" /> Personal Experiment Engine
        </h1>
        <button
          onClick={() => setShowStart(true)}
          className="bg-purple-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-purple-600"
        >
          <Plus size={18} /> Start Experiment
        </button>
      </div>

      {/* Active Experiments */}
      {activeExps.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Play className="text-green-500" /> Active Experiments
          </h2>
          <div className="grid gap-4">
            {activeExps.map(exp => (
              <div
                key={exp.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  currentExp?.id === exp.id ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-purple-300'
                }`}
                onClick={() => loadExperiment(exp)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg">{exp.name}</h3>
                    <p className="text-sm text-gray-600">
                      {exp.category} • Day {exp.daily_logs?.length || 0}/{exp.duration_days}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {exp.start_date} → {exp.end_date}
                    </p>
                  </div>
                  <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-sm">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current Experiment Detail */}
      {currentExp && (
        <div className="bg-white border rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-2">{currentExp.name}</h2>
          <p className="text-gray-600 mb-4">
            Testing: {currentExp.variants?.map(v => v.name).join(' vs ')}
          </p>

          {/* Log Daily */}
          <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Calendar size={18} /> Log Day {dayNumber}
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-1">Rating (1-10)</label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={dayRating}
                  onChange={e => setDayRating(Number(e.target.value))}
                  className="w-full"
                />
                <div className="text-center font-bold text-purple-600">{dayRating}/10</div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Notes</label>
                <textarea
                  value={dayNotes}
                  onChange={e => setDayNotes(e.target.value)}
                  className="w-full p-2 border rounded"
                  rows="2"
                  placeholder="How did it go today?"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleLogDay}
                  className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600"
                >
                  <Check size={16} className="inline mr-1" /> Log Day {dayNumber}
                </button>
                <button
                  onClick={handleFinish}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                >
                  Finish Experiment
                </button>
              </div>
            </div>
          </div>

          {/* Logs */}
          {currentExp.daily_logs?.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Daily Logs</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {currentExp.daily_logs.map((log, i) => (
                  <div key={i} className="flex items-center gap-4 text-sm bg-gray-50 p-2 rounded">
                    <span className="font-medium">Day {log.day}</span>
                    <span className="text-purple-600 font-bold">{log.rating}/10</span>
                    <span className="text-gray-600">{log.notes}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <BarChart3 className="text-green-600" /> Experiment Results
          </h2>
          <div className="bg-white rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-lg text-green-700">
              Winner: {results.winner?.name}
            </h3>
            <p className="text-3xl font-bold text-green-600 mt-2">
              {results.winner?.average_rating?.toFixed(1)}/10
            </p>
          </div>

          {results.variant_results && (
            <div className="space-y-2">
              <h4 className="font-semibold">All Variants:</h4>
              {Object.entries(results.variant_results).map(([idx, data]) => (
                <div key={idx} className="bg-white p-3 rounded flex justify-between items-center">
                  <span>{data.variant_name}</span>
                  <span className="font-bold">{data.average_rating?.toFixed(1)}/10 ({data.sample_size} days)</span>
                </div>
              ))}
            </div>
          )}

          <p className="mt-4 font-medium text-green-800">{results.conclusion}</p>
        </div>
      )}

      {/* Templates */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Available Templates</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {templates.map((tpl, i) => (
            <div key={i} className="border rounded-lg p-4 hover:border-purple-300 transition-colors">
              <h3 className="font-semibold">{tpl.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{tpl.description}</p>
              <div className="flex gap-2 mt-2 flex-wrap">
                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded text-xs">
                  {tpl.category}
                </span>
                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                  {tpl.duration_days} days
                </span>
                <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">
                  {tpl.variants?.length} variants
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Start Modal */}
      {showStart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Start New Experiment</h2>
            <div className="space-y-3 mb-4">
              {templates.map((tpl, i) => (
                <div
                  key={i}
                  onClick={() => setSelectedTemplate(tpl.category === 'skincare' ? `skincare_${tpl.name.toLowerCase().replace(' ', '_')}` :
                    tpl.category === 'diet' ? `diet_${tpl.name.toLowerCase().replace(' ', '_')}` :
                    `technique_${tpl.name.toLowerCase().replace(' ', '_')}`)}
                  className={`border rounded p-3 cursor-pointer transition-colors ${
                    selectedTemplate === (`skincare_${tpl.name.toLowerCase().replace(' ', '_')}`) ? 'border-purple-500 bg-purple-50' : 'hover:border-purple-300'
                  }`}
                >
                  <div className="font-semibold">{tpl.name}</div>
                  <div className="text-sm text-gray-600">{tpl.description}</div>
                </div>
              ))}
            </div>
            <input
              type="text"
              placeholder="Custom name (optional)"
              value={customName}
              onChange={e => setCustomName(e.target.value)}
              className="w-full p-2 border rounded mb-4"
            />
            <div className="flex gap-2">
              <button
                onClick={handleStart}
                disabled={!selectedTemplate}
                className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 disabled:bg-gray-300"
              >
                Start Experiment
              </button>
              <button
                onClick={() => { setShowStart(false); setSelectedTemplate(null) }}
                className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
