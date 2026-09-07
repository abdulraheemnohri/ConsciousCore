import React, { useState, useEffect } from 'react';
import { Sliders, RefreshCw, CheckCircle2, Play, Search } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function ModelsPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [modelsData, setModelsData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadModels = async () => {
    try {
      const res = await fetch(`${API}/api/models`);
      if (res.ok) setModelsData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadModels();
  }, []);

  const discoverModels = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/models/discover`, { method: 'POST' });
      await loadModels();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const activateModel = async (modelId: string) => {
    try {
      await fetch(`${API}/api/models/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId })
      });
      await loadModels();
      onRefresh();
    } catch {}
  };

  const registered = modelsData?.registered || [];

  return (
    <div className="models-page">
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="title"><h2>Active Model Info</h2></div>
        <div className="kv"><span>Model Name:</span> <b>{state.model?.name || state.model?.model_id || 'Deterministic Fallback Model'}</b></div>
        <div className="kv"><span>Backend:</span> <b>{state.model?.backend || 'Python Deterministic Fallback'}</b></div>
        <div className="kv"><span>Context Window:</span> <b>{state.model?.n_ctx || 4096} tokens</b></div>
        <div className="kv"><span>Status:</span> <b style={{ color: '#34d399' }}>ACTIVE</b></div>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Local GGUF Model Registry</h2>
          <div className="actions">
            <button className="btn primary" onClick={discoverModels} disabled={loading}>
              {loading ? <RefreshCw className="spin" size={14} /> : <Search size={14} />} Discover Local GGUF Files
            </button>
            <button className="btn" onClick={loadModels}><RefreshCw size={14} /> Refresh</button>
          </div>
        </div>

        <div className="list">
          {registered.map((m: any) => (
            <div className="row" key={m.model_id}>
              <div className="rowTop">
                <b>{m.name || m.model_id}</b>
                <span className="tag">{m.status || 'registered'}</span>
              </div>
              <p className="muted" style={{ margin: '4px 0' }}>Path: {m.path || 'models/'}</p>
              <div className="actions" style={{ marginTop: 8 }}>
                <button className="btn primary" onClick={() => activateModel(m.model_id)}>
                  <Play size={13} /> Activate Model
                </button>
              </div>
            </div>
          ))}
          {registered.length === 0 && (
            <div className="empty">
              No local GGUF models registered in <code>models/</code> directory. Click "Discover Local GGUF Files" or place `.gguf` models in the `models/` directory. ConsciousCore will run using the robust deterministic fallback model when no local model file is loaded.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
