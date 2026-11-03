import { useState, useEffect, useCallback } from 'react'
import { 
  logAdherence, 
  getAdherenceHistory, 
  getAdherenceRate, 
  getRecommendedDifficulty, 
  getAllProtocolsStatus,
  getConsistencySummary,
  recalculateMetrics,
  getPatternAlert
} from '../api/client'

// Must match ProtocolType in backend services/consistency_tracker.py. Until 2026-11-02 the page
// offered skincare/exercise/supplements, which the API rejects (400) - logging skincare never worked.
const PROTOCOL_PL = {
  skincare_morning: 'Pielęgnacja rano',
  skincare_evening: 'Pielęgnacja wieczorem',
  training: 'Trening',
  sleep: 'Sen',
  nutrition: 'Żywienie',
  stress: 'Stres',
}

export default function ConsistencyTracker() {
  const [protocols, setProtocols] = useState([])
  const [selectedProtocol, setSelectedProtocol] = useState('')
  const [adherenceHistory, setAdherenceHistory] = useState([])
  const [adherenceRate, setAdherenceRate] = useState(null)
  const [recommendedDifficulty, setRecommendedDifficulty] = useState(null)
  const [consistencySummary, setConsistencySummary] = useState(null)
  const [patternAlerts, setPatternAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [date, setDate] = useState('')
  const [completed, setCompleted] = useState(false)
  const [difficultyLevel, setDifficultyLevel] = useState('full')
  const [notes, setNotes] = useState('')

  const loadAllData = useCallback(async () => {
    try {

      // Load all protocols status
      const statusResponse = await getAllProtocolsStatus()
      // API returns {protocols: {protocol_type: {...}}} - turn it into the list the page renders
      const p = statusResponse?.protocols ?? {}
      setProtocols(Array.isArray(p) ? p : Object.entries(p).map(([protocol_type, v]) => ({ protocol_type, ...v })))
      
      // Load consistency summary
      const summaryResponse = await getConsistencySummary()
      setConsistencySummary(summaryResponse)
      
      // Load pattern alerts
      const alertsResponse = await getPatternAlert()
      setPatternAlerts(alertsResponse?.alerts ?? [])
      
      setLoading(false)
    } catch (error) {
      console.error('Failed to load data:', error)
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // loader sets state only after await; .then keeps it out of the effect body (react-hooks lint)
    Promise.resolve().then(loadAllData)
  }, [loadAllData])

  const handleLogAdherence = async () => {
    if (!selectedProtocol) return
    
    try {
      await logAdherence({
        protocol_type: selectedProtocol,
        completed,
        date,
        difficulty_level: difficultyLevel,
        notes
      })
      
      // Reset form
      setDate('')
      setCompleted(false)
      setDifficultyLevel('full')
      setNotes('')
      
      // Reload data
      await loadAllData()
    } catch (error) {
      console.error('Failed to log adherence:', error)
    }
  }

  const handleLoadHistory = async () => {
    if (!selectedProtocol) return
    
    try {
      const history = await getAdherenceHistory(selectedProtocol)
      setAdherenceHistory(history?.logs ?? [])
      
      // Load rate and recommended difficulty
      const rate = await getAdherenceRate(selectedProtocol)
      setAdherenceRate(rate)
      
      const diff = await getRecommendedDifficulty(selectedProtocol)
      setRecommendedDifficulty(diff)
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const handleRecalculate = async () => {
    try {
      await recalculateMetrics()
      await loadAllData()
    } catch (error) {
      console.error('Failed to recalculate:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-20">Ładowanie...</div>
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Regularność</h1>
      
      {/* Summary Section */}
      {consistencySummary && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Podsumowanie</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {Math.round((consistencySummary.average_adherence ?? 0) * 100)}%
              </p>
              <p className="text-sm text-gray-500">Średnia regularność</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {consistencySummary.system_status}
              </p>
              <p className="text-sm text-gray-500">Stan systemu</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {consistencySummary.total_protocols}
              </p>
              <p className="text-sm text-gray-500">Protokoły</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {consistencySummary.protocols_needing_reduction}
              </p>
              <p className="text-sm text-gray-500">Do uproszczenia</p>
            </div>
          </div>
        </div>
      )}

      {/* Pattern Alerts */}
      {patternAlerts.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 text-yellow-800">Zauważone wzorce</h3>
          <div className="space-y-2">
            {patternAlerts.map((alert, index) => (
              <div key={index} className="bg-yellow-100 border border-yellow-300 rounded p-3">
                <p className="font-medium text-yellow-800">{alert.protocol_type}</p>
                <p className="text-sm text-yellow-700">{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Log Adherence Form */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Zapisz wykonanie</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="ct-protocol" className="block text-sm font-medium text-gray-700 mb-2">Protokół</label>
            <select
              id="ct-protocol"
              value={selectedProtocol}
              onChange={(e) => setSelectedProtocol(e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="">Wybierz protokół...</option>
              {Object.entries(PROTOCOL_PL).map(([protocol, label]) => (
                <option key={protocol} value={protocol}>{label}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="ct-date" className="block text-sm font-medium text-gray-700 mb-2">Data</label>
            <input
              id="ct-date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          
          <div>
            <label htmlFor="ct-completed" className="block text-sm font-medium text-gray-700 mb-2">Wykonane</label>
            <select
              id="ct-completed"
              value={completed.toString()}
              onChange={(e) => setCompleted(e.target.value === 'true')}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="true">Tak</option>
              <option value="false">Nie</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="ct-difficulty" className="block text-sm font-medium text-gray-700 mb-2">Poziom</label>
            <select
              id="ct-difficulty"
              value={difficultyLevel}
              onChange={(e) => setDifficultyLevel(e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="full">Pełny</option>
              <option value="reduced">Skrócony</option>
              <option value="minimum">Minimum</option>
            </select>
          </div>
          
          <div className="md:col-span-2">
            <label htmlFor="ct-notes" className="block text-sm font-medium text-gray-700 mb-2">Notatki</label>
            <textarea
              id="ct-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full border rounded-md px-3 py-2"
              placeholder="Dodatkowe uwagi..."
            />
          </div>
        </div>
        
        <button
          onClick={handleLogAdherence}
          disabled={!selectedProtocol}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          Zapisz wykonanie
        </button>
      </div>

      {/* Protocol Status Overview */}
      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Stan protokołów</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {protocols.map((protocol, index) => (
            <div key={index} className="border rounded-lg p-4">
              <h4 className="font-medium capitalize">{protocol.protocol_type}</h4>
              <div className="mt-2 space-y-1">
                <p className="text-sm">
                  <span className="font-medium">Regularność:</span> {Math.round(protocol.adherence_rate * 100)}%
                </p>
                <p className="text-sm">
                  <span className="font-medium">Poziom:</span> {protocol.adherence_level}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Trudność:</span> {protocol.current_difficulty}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Zalecany:</span> {protocol.recommended_difficulty}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* History and Details */}
      {selectedProtocol && (
        <div className="bg-white border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">{selectedProtocol.charAt(0).toUpperCase() + selectedProtocol.slice(1)} Details</h3>
          
          <div className="mb-4">
            <button
              onClick={handleLoadHistory}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Pokaż historię i analizę
            </button>
          </div>

          {adherenceRate && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <h4 className="font-medium text-blue-800">Analiza regularności</h4>
              <div className="mt-2 space-y-1">
                <p className="text-sm">
                  <span className="font-medium">Regularność:</span> {Math.round(adherenceRate.adherence_rate * 100)}%
                </p>
                <p className="text-sm">
                  <span className="font-medium">Poziom:</span> {adherenceRate.adherence_level}
                </p>
              </div>
            </div>
          )}

          {recommendedDifficulty && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
              <h4 className="font-medium text-green-800">Zalecenia</h4>
              <div className="mt-2 space-y-1">
                <p className="text-sm">
                  <span className="font-medium">Zalecany poziom:</span> {recommendedDifficulty.recommended_difficulty}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Minimalny skuteczny protokół:</span> {recommendedDifficulty.minimum_effective_protocol}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Wymaga uproszczenia:</span> {recommendedDifficulty.needs_reduction ? 'Tak' : 'Nie'}
                </p>
              </div>
            </div>
          )}

          <div className="mb-4">
            <button
              onClick={handleRecalculate}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
            >
              Przelicz
            </button>
          </div>

          {adherenceHistory.length > 0 && (
            <div>
              <h4 className="font-medium mb-2">Ostatnia historia</h4>
              <div className="space-y-2">
                {adherenceHistory.map((log, index) => (
                  <div key={index} className="border rounded p-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium capitalize">{log.protocol_type}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(log.date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          log.completed 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {log.completed ? 'Wykonane' : 'Pominięte'}
                        </span>
                        <p className="text-xs text-gray-500 mt-1">
                          {log.difficulty_level} difficulty
                        </p>
                      </div>
                    </div>
                    {log.notes && (
                      <p className="text-sm text-gray-600 mt-2">{log.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}