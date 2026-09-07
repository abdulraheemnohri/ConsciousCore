import React, { useState } from 'react';
import { Box, Play, ShieldAlert, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function SimulationPage({ state }: { state: AppState }) {
  const [scenario, setScenario] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runSimulation = async () => {
    if (!scenario.trim() || loading) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/simulation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario, steps: ['Simulate hypothetical actions', 'Evaluate potential outcomes'] })
      });
      if (res.ok) {
        setResult(await res.json());
      }
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulation-page">
      <div className="notice" style={{ marginBottom: 16, borderColor: '#f59e0b' }}>
        <ShieldAlert size={18} style={{ color: '#f59e0b' }} />
        <span><b>Safe Sandbox Guarantee:</b> Simulation runs strictly inside an isolated hypothetical sandbox. It MUST NOT and CANNOT automatically execute real-world actions or tool calls.</span>
      </div>

      <div className="section card form">
        <div className="title"><h2>Imagination & Hypothetical Scenario Simulation</h2></div>
        <div className="field">
          <label>Hypothetical Scenario / What-If Analysis</label>
          <textarea value={scenario} onChange={e => setScenario(e.target.value)} placeholder="e.g. What would happen if remote AI server becomes unavailable during parallel debate?" />
        </div>
        <button className="btn primary" onClick={runSimulation} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={15} /> : <Play size={15} />} Run Safe Simulation
        </button>
      </div>

      {result && (
        <div className="section card">
          <div className="title"><h2>Simulation Results</h2></div>
          <div className="kv"><span>Scenario:</span> <b>{result.scenario}</b></div>
          <div className="kv"><span>Simulated Outcome:</span> <b>{result.simulated_outcome}</b></div>
          <div className="kv"><span>Uncertainty:</span> <b>{Math.round((result.uncertainty || 0.2) * 100)}%</b></div>
          <div className="kv"><span>Confidence:</span> <b>{Math.round((result.confidence || 0.8) * 100)}%</b></div>
        </div>
      )}
    </div>
  );
}
