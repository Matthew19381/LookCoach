import { useState, useEffect, useCallback } from 'react';
import { Apple, Zap } from 'lucide-react';
import { getNutritionFactors, getNutritionRecommendations, getEcosystemNeeds, sendEcosystemNeeds } from '../api/client';
import NeedsCard from '../components/NeedsCard';

export default function NutritionLooks() {
  const [factors, setFactors] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [needs, setNeeds] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [message, setMessage] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [f, r, n] = await Promise.all([
        getNutritionFactors(),
        getNutritionRecommendations(),
        getEcosystemNeeds().catch(() => null),
      ]);
      setFactors(f);
      setRecommendations(r);
      setNeeds(n);
    } catch (err) {
      console.error("Failed to load nutrition data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSend = async (force) => {
    setSending(true);
    try {
      const res = await sendEcosystemNeeds(force);
      setMessage(res.queued?.includes('nutrition_needs') ? 'Potrzeby przekazane do Diety.' : 'Nic nowego do wysłania.');
      setNeeds(await getEcosystemNeeds());
    } catch {
      setMessage('Nie udało się wysłać — spróbuj później.');
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Ładowanie...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
        <Apple className="w-8 h-8 text-green-500" /> Żywienie
      </h1>

      <p className="text-gray-700 mb-4">
        Jadłospis i dziennik posiłków prowadzi <strong>Dieta</strong>. LookCoach przekazuje jej tylko
        potrzeby wynikające z analizy zdjęć — każdą z poziomem dowodów.
      </p>
      <div className="mb-6">
        <NeedsCard
          title="Potrzeby żywieniowe dla Diety"
          moduleName="Diety"
          need={needs?.nutrition_needs}
          sending={sending}
          onSend={handleSend}
          renderPayload={(p) => (
            <ul className="list-disc ml-5">
              {p.sodium_limit_mg && <li>Sód do {p.sodium_limit_mg} mg dziennie</li>}
              {p.low_glycemic_load && <li>Dieta o niskim ładunku glikemicznym</li>}
              {(p.items || []).map((i) => (
                <li key={i.need} className="list-none text-xs text-gray-500 -ml-5">
                  {i.need}: dowody {i.evidence_level} ({i.evidence_id})
                </li>
              ))}
            </ul>
          )}
        />
        {message && <p className="text-sm text-gray-700 mt-2">{message}</p>}
      </div>

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
                  {/* API fields are recommendation/timing (optimal/poor never existed) */}
                  <span className="text-green-600">{factor.recommendation}</span>
                  {factor.timing && <span className="text-gray-500 ml-2">· {factor.timing}</span>}
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
                <span>{typeof rec === 'string' ? rec : `${rec.name}: ${rec.recommendation}`}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

    </div>
  );
}
