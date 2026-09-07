import React, { useState } from 'react';
import { Radio, RefreshCw, Play, CheckCircle2 } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function ParallelAIPage({ state }: { state: AppState }) {
  const [strategy, setStrategy] = useState('judge');
  const [prompt, setPrompt] = useState('Compare consensus on local cognitive continuity');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runParallel = async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/runtime/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          mode: 'parallel',
          privacy: 'private',
          candidates: ['local'],
          parallel_strategy: strategy
        })
      });
      if (res.ok) {
        setResult(await res.json());
      }
    } catch (e: any) {
      alert(`Parallel execution error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="parallel-ai-page">
      <div className="grid">
        <div className="card metric">
          <span>RACE Strategy</span>
          <small>Fastest valid response wins</small>
        </div>
        <div className="card metric">
          <span>JUDGE Strategy</span>
          <small>Evaluator model selects winner</small>
        </div>
        <div className="card metric">
          <span>CONSENSUS Strategy</span>
          <small>Highest agreement ratio</small>
        </div>
        <div className="card metric">
          <span>SPECIALIST / DEBATE</span>
          <small>Domain role routing</small>
        </div>
      </div>

      <div className="section card form">
        <div className="title"><h2>Parallel AI Model Execution Surface</h2></div>
        <div className="field">
          <label>Parallel Selection Strategy</label>
          <select value={strategy} onChange={e => setStrategy(e.target.value)}>
            <option value="race">Race (Fastest valid response)</option>
            <option value="judge">Judge (Evaluator model chooses best answer)</option>
            <option value="consensus">Consensus (Compare outputs & select agreement)</option>
            <option value="specialist">Specialist (Route by capability match)</option>
            <option value="debate">Debate (Bounded independent candidate roles)</option>
          </select>
        </div>
        <div className="field">
          <label>Prompt / Task</label>
          <input value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Type prompt..." />
        </div>
        <button className="btn primary" onClick={runParallel} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={15} /> : <Play size={15} />} Execute Parallel AI
        </button>

        {result && (
          <div style={{ marginTop: 12, padding: 12, background: '#020617', border: '1px solid #38bdf8', borderRadius: 8 }}>
            <div style={{ color: '#38bdf8', fontWeight: 600, marginBottom: 4 }}>
              <CheckCircle2 size={14} style={{ display: 'inline', marginRight: 6 }} /> Winner Output ({result.provider} / {result.model})
            </div>
            <p style={{ color: '#f8fafc', margin: '4px 0', fontSize: 14 }}>{result.text}</p>
            <small className="muted">Latency: {result.latency_ms} ms · Strategy: {strategy}</small>
          </div>
        )}
      </div>
    </div>
  );
}
