import React, { useState, useEffect } from 'react';
import { Box, Plus, RefreshCw, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function ToolCenterPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [toolsData, setToolsData] = useState<any>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [risk, setRisk] = useState(0.3);
  const [loading, setLoading] = useState(false);

  const loadTools = async () => {
    try {
      const res = await fetch(`${API}/api/tools`);
      if (res.ok) setToolsData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadTools();
  }, []);

  const registerTool = async () => {
    if (!name.trim() || loading) return;
    setLoading(true);
    try {
      await fetch(`${API}/api/tools`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, risk: Number(risk) })
      });
      setName('');
      setDescription('');
      await loadTools();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const authorizeTool = async (toolName: string) => {
    try {
      await fetch(`${API}/api/tools/${toolName}/authorize`);
      await loadTools();
      onRefresh();
    } catch {}
  };

  const tools = toolsData?.items || [];

  return (
    <div className="tool-center-page">
      <div className="section card form">
        <div className="title"><h2>Register Declarative Tool</h2></div>
        <div className="grid2">
          <div className="field">
            <label>Tool Name</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. MemoryExporter" />
          </div>
          <div className="field">
            <label>Risk Level (0.0 - 1.0)</label>
            <input type="number" step="0.1" min="0" max="1" value={risk} onChange={e => setRisk(Number(e.target.value))} />
          </div>
        </div>
        <div className="field">
          <label>Description & Scope</label>
          <input value={description} onChange={e => setDescription(e.target.value)} placeholder="Export memory records to JSON format..." />
        </div>
        <button className="btn primary" onClick={registerTool} disabled={loading}>
          <Plus size={15} /> Register Tool
        </button>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Registered Tool Ecosystem</h2>
          <button className="btn" onClick={loadTools}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="list">
          {tools.map((t: any) => (
            <div className="row" key={t.id || t.name}>
              <div className="rowTop">
                <b>{t.name}</b>
                <span className="tag" style={{ background: t.risk > 0.5 ? '#7f1d1d' : '#1e293b', color: t.risk > 0.5 ? '#fca5a5' : '#38bdf8' }}>
                  Risk: {Math.round((t.risk || 0.2) * 100)}%
                </span>
              </div>
              <p className="muted" style={{ margin: '4px 0' }}>{t.description}</p>
              <div className="actions" style={{ marginTop: 8 }}>
                <button className="btn primary" onClick={() => authorizeTool(t.name)}>
                  Authorize / Test Execution
                </button>
              </div>
            </div>
          ))}
          {tools.length === 0 && <div className="empty">No external tools registered. Execution is simulated safely.</div>}
        </div>
      </div>
    </div>
  );
}
