import React, { useState, useEffect } from 'react';
import { Workflow, Plus, Play, Pause, CheckCircle2, RefreshCw, Trash2, Shield } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function PlannerPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [plans, setPlans] = useState<any[]>([]);
  const [goal, setGoal] = useState('');
  const [constraints, setConstraints] = useState('');
  const [loading, setLoading] = useState(false);

  const loadPlans = async () => {
    try {
      const res = await fetch(`${API}/api/plans`);
      if (res.ok) {
        const data = await res.json();
        setPlans(data.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadPlans();
  }, []);

  const createPlan = async () => {
    if (!goal.trim() || loading) return;
    setLoading(true);
    try {
      const constList = constraints.split(',').map(c => c.trim()).filter(Boolean);
      await fetch(`${API}/api/plans`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal, constraints: constList })
      });
      setGoal('');
      setConstraints('');
      await loadPlans();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const executeStep = async (planId: number, stepId: number) => {
    try {
      await fetch(`${API}/api/plans/${planId}/steps/${stepId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ risk: 0.2, approved: true })
      });
      await loadPlans();
      onRefresh();
    } catch {}
  };

  const deletePlan = async (planId: number) => {
    try {
      await fetch(`${API}/api/plans/${planId}`, { method: 'DELETE' });
      await loadPlans();
      onRefresh();
    } catch {}
  };

  return (
    <div className="planner-page">
      <div className="section card form">
        <div className="title"><h2>Generate Bounded Action Plan</h2></div>
        <div className="field">
          <label>Plan Goal / Objective</label>
          <input value={goal} onChange={e => setGoal(e.target.value)} placeholder="e.g. Verify local model execution and memory persistence" />
        </div>
        <div className="field">
          <label>Constraints (comma separated)</label>
          <input value={constraints} onChange={e => setConstraints(e.target.value)} placeholder="local_only, no_secrets, safe" />
        </div>
        <button className="btn primary" onClick={createPlan} disabled={loading}>
          <Plus size={15} /> Generate Plan
        </button>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Active Plans & Execution Graph</h2>
          <button className="btn" onClick={loadPlans}><RefreshCw size={14} /> Refresh</button>
        </div>

        <div className="list">
          {plans.map(p => (
            <div className="row" key={p.id} style={{ marginBottom: 16 }}>
              <div className="rowTop">
                <b>Plan #{p.id} · {p.goal}</b>
                <span className="tag">{p.status || 'ACTIVE'}</span>
              </div>
              <small className="muted">Constraints: {(p.constraints || []).join(', ') || 'None'}</small>

              <div style={{ marginTop: 12 }}>
                <b style={{ fontSize: 13, color: '#f8fafc' }}>Plan Steps:</b>
                <div style={{ display: 'grid', gap: 6, marginTop: 6 }}>
                  {(p.steps || []).map((step: any) => (
                    <div key={step.id} style={{ padding: 8, background: '#020617', borderRadius: 8, border: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: 13, color: '#e2e8f0' }}>Step {step.id}: {step.action}</span>
                      <div className="actions">
                        <span className="tag" style={{ background: step.status === 'completed' ? '#064e3b' : '#1e293b' }}>{step.status}</span>
                        {step.status !== 'completed' && (
                          <button className="btn primary" style={{ padding: '4px 8px', fontSize: 11 }} onClick={() => executeStep(p.id, step.id)}>
                            <Play size={10} /> Execute Step
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="actions" style={{ marginTop: 12, justifyContent: 'flex-end' }}>
                <button className="btn danger" onClick={() => deletePlan(p.id)}>
                  <Trash2 size={13} /> Delete Plan
                </button>
              </div>
            </div>
          ))}
          {plans.length === 0 && <div className="empty">No persistent plans generated yet.</div>}
        </div>
      </div>
    </div>
  );
}
