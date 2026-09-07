import React, { useState, useEffect } from 'react';
import { Target, Plus, Play, Pause, CheckCircle2, RefreshCw, Trash2 } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function GoalsPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [goals, setGoals] = useState<any[]>([]);
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState(0.5);
  const [loading, setLoading] = useState(false);

  const loadGoals = async () => {
    try {
      const res = await fetch(`${API}/api/goals`);
      if (res.ok) {
        const data = await res.json();
        setGoals(data.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadGoals();
  }, []);

  const addGoal = async () => {
    if (!title.trim() || loading) return;
    setLoading(true);
    try {
      await fetch(`${API}/api/goals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority: Number(priority) })
      });
      setTitle('');
      await loadGoals();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const updateGoalStatus = async (goalId: number, status: string, progress?: number) => {
    try {
      const body: any = { status };
      if (progress !== undefined) body.progress = progress;
      await fetch(`${API}/api/goals/${goalId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      await loadGoals();
      onRefresh();
    } catch {}
  };

  const deleteGoal = async (goalId: number) => {
    try {
      await fetch(`${API}/api/goals/${goalId}`, { method: 'DELETE' });
      await loadGoals();
      onRefresh();
    } catch {}
  };

  return (
    <div className="goals-page">
      <div className="section card form">
        <div className="title"><h2>Create New Goal</h2></div>
        <div className="grid2">
          <div className="field">
            <label>Goal Title / Objective</label>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Implement Memory Federation Engine" />
          </div>
          <div className="field">
            <label>Priority (0.0 - 1.0)</label>
            <input type="number" step="0.1" min="0" max="1" value={priority} onChange={e => setPriority(Number(e.target.value))} />
          </div>
        </div>
        <button className="btn primary" onClick={addGoal} disabled={loading}>
          <Plus size={15} /> Create Goal
        </button>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Active & Paused Goals</h2>
          <button className="btn" onClick={loadGoals}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="list">
          {goals.map(g => (
            <div className="row" key={g.id}>
              <div className="rowTop">
                <b>#{g.id} · {g.title}</b>
                <span className="tag" style={{ background: g.status === 'completed' ? '#064e3b' : '#1e293b', color: g.status === 'completed' ? '#34d399' : '#38bdf8' }}>
                  {g.status.toUpperCase()}
                </span>
              </div>
              <div className="bar" style={{ margin: '8px 0' }}>
                <i style={{ width: `${(g.progress || 0) * 100}%` }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <small className="muted">Progress: {Math.round((g.progress || 0) * 100)}% · Priority: {Math.round((g.priority || 0.5) * 100)}%</small>
                <div className="actions">
                  {g.status !== 'completed' && (
                    <>
                      <button className="btn" onClick={() => updateGoalStatus(g.id, g.status === 'paused' ? 'active' : 'paused')}>
                        {g.status === 'paused' ? <Play size={13} /> : <Pause size={13} />}
                        {g.status === 'paused' ? 'Resume' : 'Pause'}
                      </button>
                      <button className="btn primary" onClick={() => updateGoalStatus(g.id, 'completed', 1.0)}>
                        <CheckCircle2 size={13} /> Complete
                      </button>
                    </>
                  )}
                  <button className="btn danger" onClick={() => deleteGoal(g.id)}>
                    <Trash2 size={13} /> Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
          {goals.length === 0 && <div className="empty">No active goals found in goal engine.</div>}
        </div>
      </div>
    </div>
  );
}
