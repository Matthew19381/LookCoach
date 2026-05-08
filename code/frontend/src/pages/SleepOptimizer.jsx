import { useState, useEffect } from 'react';
import { Moon, Clock, Bed } from 'lucide-react';
import { getSleepFactors, analyzeSleep, getPreEventSleepTips } from '../api/client';

export default function SleepOptimizer() {
  const [factors, setFactors] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sleepData, setSleepData] = useState({
    hours: 7, quality: 'medium', bedtime: '23:00', back_sleeping: false, silk_pillow: false,
  });
  const [analysis, setAnalysis] = useState(null);
  const [eventType, setEventType] = useState('general');
  const [eventTips, setEventTips] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const f = await getSleepFactors();
      setFactors(f);
    } catch (err) {
      console.error("Failed to load sleep data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      const result = await analyzeSleep(sleepData);
      setAnalysis(result);
    } catch (err) {
      console.error("Failed to analyze sleep:", err);
    }
  };

  const loadEventTips = async () => {
    try {
      const tips = await getPreEventSleepTips(eventType);
      setEventTips(tips);
    } catch (err) {
      console.error("Failed to load event tips:", err);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading sleep data...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Moon className="w-8 h-8 text-indigo-500" /> Sleep Optimizer
      </h1>

      {/* Factors */}
      {factors && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Sleep Factors for Looks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(factors).map(([key, factor]) => (
              <div key={key} className="border rounded p-4">
                <h3 className="font-semibold">{factor.name}</h3>
                <p className="text-sm text-gray-600">{factor.looks_impact}</p>
                <div className="mt-2 text-sm">
                  <span className="text-green-600">Optimal: {factor.optimal}</span>
                  {factor.poor && <span className="text-red-600 ml-2">Poor: {factor.poor}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Sleep Analysis */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" /> Analyze Your Sleep
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Hours of sleep</label>
            <input type="number" value={sleepData.hours}
              onChange={(e) => setSleepData({...sleepData, hours: +e.target.value})}
              className="border rounded p-2 w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Quality</label>
            <select value={sleepData.quality}
              onChange={(e) => setSleepData({...sleepData, quality: e.target.value})}
              className="border rounded p-2 w-full">
              <option value="deep">Deep</option>
              <option value="medium">Medium</option>
              <option value="light">Light</option>
              <option value="poor">Poor</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bedtime</label>
            <input type="time" value={sleepData.bedtime}
              onChange={(e) => setSleepData({...sleepData, bedtime: e.target.value})}
              className="border rounded p-2 w-full" />
          </div>
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={sleepData.back_sleeping}
                onChange={(e) => setSleepData({...sleepData, back_sleeping: e.target.checked})}
                className="rounded" />
              Back sleeping
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={sleepData.silk_pillow}
                onChange={(e) => setSleepData({...sleepData, silk_pillow: e.target.checked})}
                className="rounded" />
              Silk pillowcase
            </label>
          </div>
        </div>
        <button onClick={handleAnalyze}
          className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600">
          Analyze Sleep
        </button>

        {analysis && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-indigo-600">Score: {analysis.score}/100</div>
            {analysis.issues?.length > 0 && (
              <div className="mt-2">
                <div className="font-semibold text-red-600">Issues:</div>
                <ul className="list-disc ml-5">
                  {analysis.issues.map((issue, i) => <li key={i}>{issue}</li>)}
                </ul>
              </div>
            )}
            {analysis.recommendations?.length > 0 && (
              <div className="mt-2">
                <div className="font-semibold text-green-600">Tips:</div>
                <ul className="list-disc ml-5">
                  {analysis.recommendations.map((tip, i) => <li key={i}>{tip}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pre-Event Tips */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Bed className="w-5 h-5" /> Pre-Event Sleep Tips
        </h2>
        <div className="flex gap-4 mb-4">
          {['general', 'party', 'photoshoot', 'date', 'wedding'].map(type => (
            <button key={type} onClick={() => { setEventType(type); setEventTips(null); }}
              className={`px-3 py-1 rounded ${eventType === type ? 'bg-indigo-500 text-white' : 'bg-gray-200'}`}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
        <button onClick={loadEventTips}
          className="bg-indigo-500 text-white px-4 py-2 rounded hover:bg-indigo-600 mb-4">
          Get Tips
        </button>
        {eventTips && (
          <ul className="space-y-2">
            {eventTips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2">
                <Moon className="w-4 h-4 text-indigo-500 mt-1" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
