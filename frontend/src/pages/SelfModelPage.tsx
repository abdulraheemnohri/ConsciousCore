import React, { useState } from 'react';
import { UserRound, Shield, AlertTriangle, CheckCircle2, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function SelfModelPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [role, setRole] = useState(state.self_model_v2?.role || 'Cognitive Operating Layer');
  const [autonomy, setAutonomy] = useState(state.safety?.autonomy_level ?? 1);
  const [loading, setLoading] = useState(false);

  const updateSelfModel = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/self`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role, autonomy_level: Number(autonomy) })
      });
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const sm = state.self_model_v2 || {};

  return (
    <div className="self-model-page">
      <div className="notice" style={{ marginBottom: 16, borderColor: '#0284c7' }}>
        <Shield size={18} style={{ color: '#38bdf8' }} />
        <span><b>Scientific Boundary Disclaimer:</b> ConsciousCore models computational functions associated with self-modeling, capabilities, and autonomy. It does NOT possess phenomenal consciousness, feelings, or subjective awareness.</span>
      </div>

      <div className="grid2">
        <div className="card form">
          <div className="title">
            <h2>Identity & Autonomy Configuration</h2>
          </div>
          <div className="field">
            <label>Configured Identity Role</label>
            <input value={role} onChange={e => setRole(e.target.value)} />
          </div>
          <div className="field">
            <label>Autonomy Level (Level 0 - Level 3)</label>
            <select value={autonomy} onChange={e => setAutonomy(Number(e.target.value))}>
              <option value={0}>Level 0: Manual (No autonomous execution)</option>
              <option value={1}>Level 1: Suggestion (System suggests, human executes)</option>
              <option value={2}>Level 2: Low-Risk Approved Actions (Approved routine actions)</option>
              <option value={3}>Level 3: Policy Autonomous (Strict bounded policy workflows)</option>
            </select>
          </div>
          <button className="btn primary" onClick={updateSelfModel} disabled={loading}>
            Update Self Model
          </button>
        </div>

        <div className="card">
          <div className="title"><h2>Current Functional State</h2></div>
          <div className="kv"><span>System Name:</span> <b>{sm.name || 'ConsciousCore'}</b></div>
          <div className="kv"><span>Architecture:</span> <b>Consciousness-Inspired Layer</b></div>
          <div className="kv"><span>Autonomy Level:</span> <b>Level {sm.autonomy_level ?? autonomy}</b></div>
          <div className="kv"><span>Energy Level:</span> <b>{Math.round((state.state?.energy ?? 0.8) * 100)}%</b></div>
          <div className="kv"><span>Workload Pressure:</span> <b>{Math.round((state.state?.workload ?? 0.1) * 100)}%</b></div>
        </div>
      </div>

      <div className="section grid2">
        <div className="card">
          <div className="title"><h2><CheckCircle2 size={16} /> Capabilities</h2></div>
          <div className="list">
            {(sm.capabilities || ['reasoning', 'memory_retrieval', 'planning', 'prediction', 'reflection', 'tool_execution']).map((cap: string) => (
              <div key={cap} className="row">
                <b>{cap.toUpperCase()}</b>
                <p className="muted" style={{ margin: 0, fontSize: 12 }}>Enabled functional capability module.</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="title"><h2><AlertTriangle size={16} /> System Limitations & Invariants</h2></div>
          <div className="list">
            {[
              'No Phenomenal Consciousness (Strict scientific boundary)',
              'No Password / Cookie / OTP Extraction',
              'No Unrestricted Self-Modification',
              'No Unrestricted Hacking or Surveillance'
            ].map(lim => (
              <div key={lim} className="row" style={{ borderLeft: '3px solid #f59e0b' }}>
                <b>{lim}</b>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
