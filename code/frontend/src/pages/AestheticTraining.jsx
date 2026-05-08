import { useState, useEffect } from 'react'
import { Barbell, Target, Activity } from 'lucide-react'
import { getAvailablePlans, generateTrainingPlan, analyzePhysique } from '../api/client'

export default function AestheticTraining() {
  const [plans, setPlans] = useState([])
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    getAvailablePlans().then(data => {
      setPlans(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const handleSelectPlan = async (planId) => {
    setGenerating(true)
    try {
      const result = await generateTrainingPlan(planId, 'beginner')
      setSelectedPlan(result)
    } catch (e) {
      console.error('Plan generation failed:', e)
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return <div className="text-center py-20">Loading training plans...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Barbell size={28} className="text-blue-600" />
        <h1 className="text-3xl font-bold text-gray-900">Aesthetic Training</h1>
      </div>

      {selectedPlan ? (
        <div className="space-y-4">
          <div className="bg-white border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-2">{selectedPlan.name}</h2>
            <p className="text-gray-600 mb-4">{selectedPlan.description}</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-blue-50 p-3 rounded-lg text-center">
                <p className="text-sm text-gray-600">Frequency</p>
                <p className="font-bold text-blue-600">{selectedPlan.frequency}</p>
              </div>
              <div className="bg-green-50 p-3 rounded-lg text-center">
                <p className="text-sm text-gray-600">Duration</p>
                <p className="font-bold text-green-600">{selectedPlan.duration_weeks} weeks</p>
              </div>
              <div className="bg-purple-50 p-3 rounded-lg text-center">
                <p className="text-sm text-gray-600">Reps</p>
                <p className="font-bold text-purple-600">{selectedPlan.reps}</p>
              </div>
            </div>
            {selectedPlan.notes && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">{selectedPlan.notes}</p>
              </div>
            )}
          </div>

          {selectedPlan.weekly_schedule && (
            <div className="bg-white border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Weekly Schedule</h3>
              {Object.entries(selectedPlan.weekly_schedule).map(([day, exercises]) => (
                <div key={day} className="mb-4">
                  <h4 className="font-medium text-gray-700 capitalize mb-2">{day}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    {exercises.map((ex, i) => (
                      <div key={i} className="bg-gray-50 p-3 rounded border">
                        <p className="font-medium text-sm">{ex.replace('_', ' ')}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => setSelectedPlan(null)}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Back to plans
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className="bg-white border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => handleSelectPlan(plan.id)}
            >
              <div className="flex items-center gap-2 mb-3">
                <Target size={20} className="text-blue-500" />
                <h3 className="font-semibold">{plan.name}</h3>
              </div>
              <p className="text-sm text-gray-600">{plan.description}</p>
              {generating && plan.id === plan.id && (
                <p className="text-sm text-blue-600 mt-2">Generating...</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
