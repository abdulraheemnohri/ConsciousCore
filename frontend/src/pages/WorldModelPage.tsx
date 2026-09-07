import React, { useState, useEffect } from 'react';
import { Network, Plus, RefreshCw, AlertTriangle } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function WorldModelPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [worldData, setWorldData] = useState<any>(null);
  const [entityId, setEntityId] = useState('');
  const [entityLabel, setEntityLabel] = useState('');
  const [entityKind, setEntityKind] = useState('concept');
  const [loading, setLoading] = useState(false);

  const loadWorld = async () => {
    try {
      const res = await fetch(`${API}/api/world`);
      if (res.ok) setWorldData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadWorld();
  }, []);

  const addEntity = async () => {
    if (!entityId.trim() || !entityLabel.trim() || loading) return;
    setLoading(true);
    try {
      await fetch(`${API}/api/world/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: entityId, label: entityLabel, kind: entityKind, confidence: 0.9 })
      });
      setEntityId('');
      setEntityLabel('');
      await loadWorld();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const wm = worldData || state.world_model || {};
  const entities = wm.entities || [];
  const relations = wm.relations || [];
  const contradictions = wm.contradictions || [];

  return (
    <div className="world-model-page">
      <div className="grid">
        <div className="card metric">
          <span>Total Entities</span>
          <strong>{entities.length}</strong>
        </div>
        <div className="card metric">
          <span>Relationships</span>
          <strong>{relations.length}</strong>
        </div>
        <div className="card metric">
          <span>Beliefs</span>
          <strong>{(wm.beliefs || []).length}</strong>
        </div>
        <div className="card metric">
          <span>Contradictions</span>
          <strong style={{ color: contradictions.length > 0 ? '#ef4444' : '#10b981' }}>{contradictions.length}</strong>
        </div>
      </div>

      <div className="section grid2">
        <div className="card form">
          <div className="title"><h2>Add World Entity</h2></div>
          <div className="field">
            <label>Entity ID (slug)</label>
            <input value={entityId} onChange={e => setEntityId(e.target.value)} placeholder="e.g. project_consciouscore" />
          </div>
          <div className="field">
            <label>Entity Label</label>
            <input value={entityLabel} onChange={e => setEntityLabel(e.target.value)} placeholder="e.g. ConsciousCore System" />
          </div>
          <div className="field">
            <label>Kind</label>
            <select value={entityKind} onChange={e => setEntityKind(e.target.value)}>
              <option value="concept">Concept</option>
              <option value="person">Person</option>
              <option value="device">Device</option>
              <option value="project">Project</option>
              <option value="organization">Organization</option>
            </select>
          </div>
          <button className="btn primary" onClick={addEntity} disabled={loading}>
            <Plus size={15} /> Add Entity
          </button>
        </div>

        <div className="card">
          <div className="title">
            <h2>Contradiction Detection</h2>
            <button className="btn" onClick={loadWorld}><RefreshCw size={14} /> Refresh</button>
          </div>
          <div className="list">
            {contradictions.map((c: any, i: number) => (
              <div className="row" key={i} style={{ borderLeft: '3px solid #ef4444' }}>
                <b><AlertTriangle size={14} color="#ef4444" /> Contradiction Detected</b>
                <p className="muted" style={{ margin: '4px 0' }}>Left: {JSON.stringify(c.left)} vs Right: {JSON.stringify(c.right)}</p>
              </div>
            ))}
            {contradictions.length === 0 && <div className="empty">No contradictions detected in world state.</div>}
          </div>
        </div>
      </div>

      <div className="section card">
        <div className="title"><h2>Entity Graph Registry</h2></div>
        <div className="list">
          {entities.map((e: any) => (
            <div className="row" key={e.id}>
              <div className="rowTop">
                <b>{e.label} ({e.id})</b>
                <span className="tag">Kind: {e.kind}</span>
              </div>
              <small className="muted">Confidence: {Math.round((e.confidence || 0.8) * 100)}% · Active: {e.active ? 'YES' : 'NO'}</small>
            </div>
          ))}
          {entities.length === 0 && <div className="empty">No world entities registered yet.</div>}
        </div>
      </div>
    </div>
  );
}
