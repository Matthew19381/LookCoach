import { useState } from 'react'
import { Calendar, Clock, Sun, Moon, Droplets } from 'lucide-react'
import { generateEventPlan, getEventTips } from '../api/client'

export default function EventMode() {
  const [eventDate, setEventDate] = useState('')
  const [eventType, setEventType] = useState('general')
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [tips, setTips] = useState([])

  const handleGeneratePlan = async (e) => {
    e.preventDefault()
    if (!eventDate) return
    setLoading(true)
    try {
      const data = await generateEventPlan(eventDate, eventType)
      setPlan(data)
    } catch (e) {
      console.error('Plan generation failed:', e)
    } finally {
      setLoading(false)
    }
  }

  const handleGetTips = async (type) => {
    try {
      const data = await getEventTips(type)
      setTips(data.tips || [])
    } catch (e) {
      console.error('Tips failed:', e)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Calendar size={28} className="text-purple-600" />
        <h1 className="text-3xl font-bold text-gray-900">Event Mode</h1>
      </div>

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Prepare for Your Event</h3>
        <form onSubmit={handleGeneratePlan} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Event Date
              </label>
              <input
                type="date"
                aria-label="Event Date"
                value={eventDate}
                onChange={(e) => setEventDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Event Type
              </label>
              <select
                aria-label="Event Type"
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="general">General</option>
                <option value="party">Party</option>
                <option value="photoshoot">Photoshoot</option>
                <option value="date">Date</option>
                <option value="wedding">Wedding</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={!eventDate || loading}
            className="px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Plan'}
          </button>
        </form>
      </div>

      {plan && plan.timeline && (
        <div className="space-y-4">
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Clock size={20} className="text-purple-600" />
              <h2 className="text-xl font-semibold">
                {plan.days_until_event} days until event
              </h2>
            </div>
            <p className="text-purple-700">
              Event Type: <span className="font-medium">{plan.event_type}</span>
            </p>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Daily Action Plan</h3>
            {plan.timeline.map((day, idx) => (
              <div key={idx} className="bg-white border rounded-lg p-6">
                <h4 className="font-medium text-gray-900 mb-3">
                  {day.days_before === 0 ? 'Day of Event' : `${day.days_before} days before`}
                </h4>
                <ul className="space-y-2">
                  {day.actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="flex-shrink-0 w-5 h-5 bg-purple-100 text-purple-800 rounded-full flex items-center justify-center text-xs">
                        {i + 1}
                      </span>
                      <span className="text-gray-700">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {plan.day_of_event && plan.day_of_event.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h4 className="font-medium text-green-900 mb-3">Day of Event - Quick Actions</h4>
              <ul className="space-y-2">
                {plan.day_of_event.map((action, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <Sun size={16} className="text-green-600 mt-0.5" />
                    <span className="text-green-800">{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="bg-white border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Tips by Event Type</h3>
        <div className="flex gap-2 mb-4 flex-wrap">
          {['party', 'photoshoot', 'date', 'wedding', 'general'].map((type) => (
            <button
              key={type}
              onClick={() => handleGetTips(type)}
              className={`px-3 py-1 rounded-md text-sm ${
                eventType === type
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
        {tips.length > 0 && (
          <ul className="space-y-2">
            {tips.map((tip, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <Droplets size={16} className="text-blue-600 mt-0.5" />
                <span className="text-gray-700">{tip}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
