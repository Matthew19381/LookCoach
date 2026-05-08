import { useState, useEffect } from 'react';
import { Apple, Droplets, Zap } from 'lucide-react';
import { getNutritionFactors, getNutritionRecommendations, getMealPlan, analyzeDiet } from '../api/client';

export default function NutritionLooks() {
  const [factors, setFactors] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [dietLog, setDietLog] = useState({ water: 0, sugar: 0, veg: 0, protein: 0 });
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [f, r, m] = await Promise.all([
        getNutritionFactors(),
        getNutritionRecommendations(),
        getMealPlan("pre_event"),
      ]);
      setFactors(f);
      setRecommendations(r);
      setMealPlan(m);
    } catch (err) {
      console.error("Failed to load nutrition data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const result = await analyzeDiet(dietLog);
      setAnalysis(result);
    } catch (err) {
      console.error("Failed to analyze diet:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Loading nutrition data...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Apple className="w-8 h-8 text-green-500" /> Nutrition for Looks
      </h1>

      {/* Factors */}
      {factors && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Nutrition Factors</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(factors).map(([key, factor]) => (
              <div key={key} className="border rounded p-4">
                <h3 className="font-semibold">{factor.name}</h3>
                <p className="text-sm text-gray-600">{factor.looks_impact}</p>
                <div className="mt-2 text-sm">
                  <span className="text-green-600">Optimal: {factor.optimal}</span>
                  {factor.poor && <span className="text-red-600 ml-2">Avoid: {factor.poor}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Recommendations</h2>
          <ul className="space-y-2">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2">
                <Zap className="w-4 h-4 text-yellow-500 mt-1" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Meal Plan */}
      {mealPlan && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-500" /> Pre-Event Meal Plan
          </h2>
          <div className="space-y-3">
            {mealPlan.map((item, i) => (
              <div key={i} className="border-l-4 border-blue-500 pl-4">
                <div className="font-medium">{item.timing}</div>
                <div className="text-sm text-gray-600">{item.foods}</div>
                <div className="text-xs text-green-600">{item.looks_benefit}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Diet Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Diet Analysis</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <input type="number" placeholder="Water (glasses)" value={dietLog.water}
            onChange={(e) => setDietLog({...dietLog, water: +e.target.value})}
            className="border rounded p-2" />
          <input type="number" placeholder="Sugar (tsp)" value={dietLog.sugar}
            onChange={(e) => setDietLog({...dietLog, sugar: +e.target.value})}
            className="border rounded p-2" />
          <input type="number" placeholder="Vegetables (serv)" value={dietLog.veg}
            onChange={(e) => setDietLog({...dietLog, veg: +e.target.value})}
            className="border rounded p-2" />
          <input type="number" placeholder="Protein (g)" value={dietLog.protein}
            onChange={(e) => setDietLog({...dietLog, protein: +e.target.value})}
            className="border rounded p-2" />
        </div>
        <button onClick={handleAnalyze} disabled={analyzing}
          className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50">
          {analyzing ? 'Analyzing...' : 'Analyze Diet'}
        </button>

        {analysis && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <div className="text-2xl font-bold text-green-600">Score: {analysis.score}/100</div>
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
    </div>
  );
}
