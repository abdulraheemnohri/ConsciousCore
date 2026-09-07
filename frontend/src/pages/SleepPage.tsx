import React, { useState } from 'react';
import { Clock3, Play, RefreshCw, CheckCircle2 } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function SleepPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runSleepConsolidation = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/sleep`, { method: 'POST' });
      if (res.ok) {
        setResult(await res.json());
        onRefresh();
      }
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <div className="sleep-page">
      <div className="section card">
        <div className="title">
          <h2><Clock3 size={16} /> Sleep & Memory Consolidation Cycle</h2>
          <button className="btn primary" onClick={runSleepConsolidation} disabled={loading}>
            {loading ? <RefreshCw className="spin" size={15} /> : <Play size={15} />} Execute Sleep Cycle
          </button>
        </div>

        <div className="kv"><span>Maintenance Pipeline:</span> <b>Review Working Memory → Merge Memories → Extract Lessons → Resolve Conflicts → Update Timeline</b></div>
        <div className="kv"><span>Auto-Consolidation Schedule:</span> <b>Scheduled / Manual / Idle Trigger</b></div>

        {result && (
          <div style={{ marginTop: 16, padding: 12, background: '#020617', border: '1px solid #10b981', borderRadius: 8 }}>
            <div style={{ color: '#34d399', fontWeight: 600, fontSize: 13, marginBottom: 4 }}>
              <CheckCircle2 size={14} style={{ display: 'inline', marginRight: 6 }} /> Sleep Consolidation Complete
            </div>
            <pre className="json">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
