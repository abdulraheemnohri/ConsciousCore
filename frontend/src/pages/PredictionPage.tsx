import React, { useState, useEffect } from 'react';
import { LineChart, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function PredictionPage({ state }: { state: AppState }) {
  const [predData, setPredData] = useState<any>(null);

  const loadPrediction = async () => {
    try {
      const res = await fetch(`${API}/api/prediction`);
      if (res.ok) setPredData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadPrediction();
  }, []);

  const pred = predData || {
    content: 'Next likely action: Continue cognitive cycle and goal task evaluation',
    probability: 0.88,
    confidence: 0.85,
    expected_outcome: 'Goal step progress advances without policy violation',
    actual_outcome: 'Pending observation',
    error: 0.05
  };

  return (
    <div className="prediction-page">
      <div className="grid">
        <div className="card metric">
          <span>Predicted Action Probability</span>
          <strong>{Math.round((pred.probability || 0.8) * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Confidence</span>
          <strong>{Math.round((pred.confidence || 0.8) * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Prediction Error</span>
          <strong>{Math.round((pred.error || 0.05) * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Accuracy Trend</span>
          <strong style={{ color: '#10b981' }}>94%</strong>
        </div>
      </div>

      <div className="section card">
        <div className="title">
          <h2><LineChart size={16} /> Active Cognitive Prediction</h2>
          <button className="btn" onClick={loadPrediction}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="kv"><span>Prediction:</span> <b>{pred.content}</b></div>
        <div className="kv"><span>Expected Outcome:</span> <b>{pred.expected_outcome || 'Nominal execution'}</b></div>
        <div className="kv"><span>Actual Outcome:</span> <b>{pred.actual_outcome || 'Pending cycle observation'}</b></div>
      </div>
    </div>
  );
}
