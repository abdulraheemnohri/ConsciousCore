import React, { useState } from 'react';
import { ChevronRight, Brain, Target, Layers, Shield, Zap } from 'lucide-react';
import { AppState } from '../types';

interface DashboardPageProps {
  state: AppState;
  onNavigate: (page: string) => void;
}

export function DashboardPage({ state, onNavigate }: DashboardPageProps) {
  const metrics = [
    { label: 'Active Memories', value: state.memory_count ?? 0, sub: 'persistent items' },
    { label: 'Uncertainty', value: `${Math.round((state.state?.uncertainty ?? 0) * 100)}%`, sub: 'metacognitive' },
    { label: 'Energy / Workload', value: `${Math.round((state.state?.energy ?? 0) * 100)}%`, sub: 'functional state' },
    { label: 'Active Goals', value: (state.goals || []).length, sub: 'goal engine' }
  ];

  const focus = state.global_workspace_v2?.current_broadcast?.content || state.global_workspace_v2?.active_candidates?.[0]?.content || 'Idle workspace';

  return (
    <div className="dashboard-page">
      <div className="grid">
        {metrics.map(m => (
          <div className="card metric" key={m.label}>
            <span>{m.label}</span>
            <strong>{m.value}</strong>
            <small>{m.sub}</small>
          </div>
        ))}
      </div>

      <div className="section grid2">
        <div className="card">
          <div className="title">
            <h2><Brain size={16} /> Global Workspace Focus</h2>
            <button className="btn" onClick={() => onNavigate('Global Workspace')}>Inspect</button>
          </div>
          <div style={{ background: '#020617', padding: 14, borderRadius: 10, border: '1px solid #1e293b', marginBottom: 12 }}>
            <div style={{ fontSize: 12, color: '#38bdf8', marginBottom: 4, fontWeight: 600 }}>CURRENT BROADCAST FOCUS</div>
            <div style={{ fontSize: 14, color: '#f8fafc' }}>{focus}</div>
          </div>
          <pre className="json">{JSON.stringify(state.global_workspace_v2 || {}, null, 2)}</pre>
        </div>

        <div className="card">
          <div className="title">
            <h2><Layers size={16} /> Self Model Snapshot</h2>
            <button className="btn" onClick={() => onNavigate('Self Model')}>View Self Model</button>
          </div>
          <pre className="json">{JSON.stringify(state.self_model_v2 || {}, null, 2)}</pre>
        </div>
      </div>

      <div className="section grid3">
        <div className="card">
          <div className="title"><h2><Target size={16} /> Active Goals</h2></div>
          <div className="list">
            {(state.goals || []).slice(0, 3).map((g: any) => (
              <div key={g.id} className="row">
                <div className="rowTop">
                  <b>{g.title}</b>
                  <span className="tag">{g.status}</span>
                </div>
                <div className="bar"><i style={{ width: `${(g.progress || 0) * 100}%` }} /></div>
              </div>
            ))}
            {(!state.goals || state.goals.length === 0) && <div className="empty">No goals defined yet.</div>}
          </div>
        </div>

        <div className="card">
          <div className="title"><h2><Zap size={16} /> Internal Computational State</h2></div>
          <div className="kv"><span>Energy:</span> <b>{Math.round((state.state?.energy ?? 0.5) * 100)}%</b></div>
          <div className="kv"><span>Uncertainty:</span> <b>{Math.round((state.state?.uncertainty ?? 0.5) * 100)}%</b></div>
          <div className="kv"><span>Confidence:</span> <b>{Math.round((state.state?.confidence ?? 0.5) * 100)}%</b></div>
          <div className="kv"><span>Workload:</span> <b>{Math.round((state.state?.workload ?? 0.0) * 100)}%</b></div>
        </div>

        <div className="card">
          <div className="title"><h2><Shield size={16} /> Bounded Safety Engine</h2></div>
          <div className="kv"><span>Autonomy Level:</span> <b>L{state.safety?.autonomy_level ?? 1}</b></div>
          <div className="kv"><span>External Approval:</span> <b>{state.safety?.external_actions_require_approval !== false ? 'REQUIRED' : 'OFF'}</b></div>
          <div className="kv"><span>Secret Blocking:</span> <b>ACTIVE</b></div>
          <div className="kv"><span>Data Classification:</span> <b>PRIVATE (Local)</b></div>
        </div>
      </div>

      <div className="section card">
        <div className="title"><h2>Quick Navigation</h2></div>
        <div className="actions">
          {[
            'Chat Workspace', 'Global Workspace', 'Attention Center', 'Memory',
            'Memory Federation', 'Goals', 'Planner', 'Runtime Center', 'Settings'
          ].map(page => (
            <button key={page} className="btn" onClick={() => onNavigate(page)}>
              {page} <ChevronRight size={13} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
