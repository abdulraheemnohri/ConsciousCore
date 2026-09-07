import React, { useState, useEffect } from 'react';
import { BookOpen, Zap, RefreshCw, CheckCircle2 } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function ReflectionPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [reflectionData, setReflectionData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadReflection = async () => {
    try {
      const res = await fetch(`${API}/api/reflection`);
      if (res.ok) setReflectionData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadReflection();
  }, []);

  const triggerReflection = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/reflection`, { method: 'POST' });
      await loadReflection();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const ref = reflectionData?.reflection || {};
  const history = reflectionData?.history || [];

  return (
    <div className="reflection-page">
      <div className="section card">
        <div className="title">
          <h2><BookOpen size={16} /> Latest Cycle Reflection</h2>
          <button className="btn primary" onClick={triggerReflection} disabled={loading}>
            <Zap size={14} /> Run Post-Cycle Reflection
          </button>
        </div>

        {ref.summary ? (
          <div>
            <div className="kv"><span>Reflection Summary:</span> <b>{ref.summary}</b></div>
            <div className="kv"><span>Lessons Extracted:</span> <b>{(ref.lessons || []).length} lessons</b></div>
            <div className="kv"><span>Uncertainties Identified:</span> <b>{(ref.uncertainties || []).length} items</b></div>
            <div style={{ marginTop: 12 }}>
              <b style={{ color: '#f8fafc', fontSize: 13 }}>Next Action Recommendations:</b>
              <ul style={{ margin: '6px 0', paddingLeft: 20, color: '#94a3b8' }}>
                {(ref.next_actions || ['Maintain active goal alignment', 'Consolidate working memory']).map((act: string, i: number) => (
                  <li key={i}>{act}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <div className="empty">No active reflection available for the current cycle.</div>
        )}
      </div>

      <div className="section card">
        <div className="title">
          <h2>Reflection History Timeline</h2>
          <button className="btn" onClick={loadReflection}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="list">
          {history.map((h: any, i: number) => (
            <div className="row" key={h.id || i}>
              <div className="rowTop">
                <b>Reflection #{h.id || i + 1}</b>
                <span className="tag">{h.created_at || 'Recent'}</span>
              </div>
              <p style={{ color: '#f8fafc', margin: '4px 0' }}>{h.summary}</p>
            </div>
          ))}
          {history.length === 0 && <div className="empty">No historical reflections logged yet.</div>}
        </div>
      </div>
    </div>
  );
}
