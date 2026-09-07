import React, { useState, useEffect } from 'react';
import { Cpu, RefreshCw, Play, ShieldCheck, Activity } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function RuntimeCenterPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [runtimeData, setRuntimeData] = useState<any>(null);
  const [testPrompt, setTestPrompt] = useState('Hello ConsciousCore');
  const [selectedMode, setSelectedMode] = useState('auto');
  const [genResult, setGenResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadRuntime = async () => {
    try {
      const res = await fetch(`${API}/api/runtime`);
      if (res.ok) setRuntimeData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadRuntime();
  }, []);

  const testGenerate = async () => {
    if (!testPrompt.trim() || loading) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/runtime/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: testPrompt,
          mode: selectedMode,
          privacy: 'private',
          allow_cloud: false,
          allow_remote: false
        })
      });
      if (res.ok) {
        setGenResult(await res.json());
      }
    } catch (e: any) {
      alert(`Runtime generation error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="runtime-center-page">
      <div className="grid">
        <div className="card metric">
          <span>Active Mode</span>
          <strong style={{ color: '#38bdf8' }}>HYBRID / AUTO</strong>
        </div>
        <div className="card metric">
          <span>Local Model</span>
          <strong>{state.model?.name || 'Fallback'}</strong>
        </div>
        <div className="card metric">
          <span>Cloud / Remote</span>
          <strong>OFF (Opt-in)</strong>
        </div>
        <div className="card metric">
          <span>Data Boundary</span>
          <strong style={{ color: '#34d399' }}>PRIVATE / LOCAL</strong>
        </div>
      </div>

      <div className="section grid2">
        <div className="card form">
          <div className="title"><h2>Runtime Router Dispatch Test</h2></div>
          <div className="field">
            <label>Runtime Mode</label>
            <select value={selectedMode} onChange={e => setSelectedMode(e.target.value)}>
              <option value="auto">AUTO (Policy Router)</option>
              <option value="local">LOCAL (Device Execution)</option>
              <option value="hybrid">HYBRID (Local State + Specialist Gen)</option>
              <option value="parallel">PARALLEL (Multi-Model Race/Judge)</option>
              <option value="remote">REMOTE (User Server)</option>
              <option value="cloud">CLOUD (Opt-in Vendor)</option>
            </select>
          </div>
          <div className="field">
            <label>Test Prompt</label>
            <input value={testPrompt} onChange={e => setTestPrompt(e.target.value)} placeholder="Type prompt..." />
          </div>
          <button className="btn primary" onClick={testGenerate} disabled={loading}>
            {loading ? <RefreshCw className="spin" size={15} /> : <Play size={15} />} Test Runtime Dispatch
          </button>

          {genResult && (
            <div style={{ marginTop: 12, padding: 12, background: '#020617', border: '1px solid #1e293b', borderRadius: 8 }}>
              <div className="kv"><span>Text Output:</span> <b>{genResult.text}</b></div>
              <div className="kv"><span>Provider:</span> <b>{genResult.provider}</b></div>
              <div className="kv"><span>Model:</span> <b>{genResult.model}</b></div>
              <div className="kv"><span>Latency:</span> <b>{genResult.latency_ms} ms</b></div>
            </div>
          )}
        </div>

        <div className="card">
          <div className="title">
            <h2>Provider Registry & Health</h2>
            <button className="btn" onClick={loadRuntime}><RefreshCw size={14} /> Refresh</button>
          </div>
          <pre className="json">{JSON.stringify(runtimeData || {}, null, 2)}</pre>
        </div>
      </div>
    </div>
  );
}
