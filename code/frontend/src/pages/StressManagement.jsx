import { useState, useEffect } from 'react';
import { Brain, Heart, Activity } from 'lucide-react';
import { getStressEffects, getRelaxationTechniques, analyzeStress } from '../api/client';

export default function StressManagement() {
  const [effects, setEffects] = useState(null);
  const [techniques, setTechniques] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stressData, setStressData] = useState({
    level: 'low', physical_signs: [],
  });
  const [analysis, setAnalysis] = useState(null);
  const [signsList] = useState([
    'acne', 'oily skin', 'hair shedding', 'dull skin', 'dark circles',
    'frown lines', 'jaw tension', 'crow\'s feet',
  ]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [e, t] = await Promise.all([
        getStressEffects(),
        getRelaxationTechniques(),
      ]);
      setEffects(e);
      setTechniques(t);
    } catch (err) {
      console.error("Failed to load stress data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      const result = await analyzeStress(stressData);
      setAnalysis(result);
    } catch (err) {
      console.error("Failed to analyze stress:", err);
    }
  };

  const toggleSign = (sign) => {
    const signs = stressData.physical_signs.includes(sign)
      ? stressData.physical_signs.filter(s => s !== sign)
      : [...stressData.physical_signs, sign];
    setStressData({...stressData, physical_signs: signs});
  };

  if (loading) {
    return <div className="p-8 text-center">Loading stress data...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Brain className="w-8 h-8 text-purple-500" /> Stress Management
      </h1>

      {/* Effects */}
      {effects && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Stress Effects on Looks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(effects).map(([key, effect]) => (
              <div key={key} className="border rounded p-4">
                <h3 className="font-semibold">{effect.name}</h3>
                <p className="text-sm text-gray-600">{effect.looks_impact}</p>
                {effect.signs && (
                  <div className="mt-2 text-xs text-red-600">
                    Signs: {effect.signs.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Relaxation Techniques */}
      {techniques && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Heart className="w-5 h-5 text-pink-500" /> Relaxation Techniques
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {techniques.map((tech, i) => (
              <div key={i} className="border rounded p-4 bg-purple-50">
                <h3 className="font-semibold">{tech.name}</h3>
                <p className="text-sm text-gray-600">Duration: {tech.duration}</p>
                <p className="text-xs text-green-600 mt-1">{tech.looks_benefit}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Stress Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" /> Stress Analysis
        </h2>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Stress Level</label>
          <div className="flex gap-4">
            {['low', 'medium', 'high'].map(level => (
              <button key={level} onClick={() => setStressData({...stressData, level})}
                className={`px-4 py-2 rounded ${stressData.level === level ? 'bg-purple-500 text-white' : 'bg-gray-200'}`}>
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Physical Signs</label>
          <div className="flex flex-wrap gap-2">
            {signsList.map(sign => (
              <button key={sign} onClick={() => toggleSign(sign)}
                className={`px-3 py-1 rounded-full text-sm ${stressData.physical_signs.includes(sign) ? 'bg-purple-500 text-white' : 'bg-gray-200'}`}>
                {sign}
              </button>
            ))}
          </div>
        </div>
        <button onClick={handleAnalyze}
          className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
          Analyze Stress
        </button>

        {analysis && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-purple-600">Score: {analysis.score}/100</div>
            {analysis.effects?.length > 0 && (
              <div className="mt-2">
                <div className="font-semibold text-red-600">Active Effects:</div>
                <ul className="list-disc ml-5">
                  {analysis.effects.map((eff, i) => (
                    <li key={i}>{eff.name} - {eff.looks_impact}</li>
                  ))}
                </ul>
              </div>
            )}
            {analysis.recommendations?.length > 0 && (
              <div className="mt-2">
                <div className="font-semibold text-green-600">Recommendations:</div>
                <ul className="list-disc ml-5">
                  {analysis.recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
