import React, { useState, useEffect } from 'react';
import { RefreshCw, Play } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function MemoryFederationPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [fedData, setFedData] = useState<any>(null);
  const [conflicts, setConflicts] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const loadFederation = async () => {
    try {
      const res = await fetch(`${API}/api/memory/federation`);
      if (res.ok) setFedData(await res.json());

      const cRes = await fetch(`${API}/api/memory/conflicts`);
      if (cRes.ok) {
        const cData = await cRes.json();
        setConflicts(cData.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadFederation();
  }, []);

  const triggerSync = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/memory/sync/process`, { method: 'POST' });
      await loadFederation();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const resolveConflict = async (conflictId: number, resolution: string) => {
    try {
      await fetch(`${API}/api/memory/conflicts/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conflict_id: conflictId, resolution, resolved_by: 'user' })
      });
      await loadFederation();
      onRefresh();
    } catch {}
  };

  const replicas = fedData?.replicas || {
    local: { enabled: true, writable: true, encrypted: true },
    remote: { enabled: false, writable: false, encrypted: true },
    cloud: { enabled: false, writable: false, encrypted: true }
  };

  return (
    <div className="memory-federation-page">
      <div className="grid3">
        {Object.entries(replicas).map(([name, rep]: [string, any]) => (
          <div className="card" key={name} style={{ borderTop: rep.enabled ? '3px solid #10b981' : '3px solid #64748b' }}>
            <div className="title">
              <h2>{name.toUpperCase()} REPLICA</h2>
              <span className="tag" style={{ background: rep.enabled ? '#064e3b' : '#1e293b', color: rep.enabled ? '#34d399' : '#94a3b8' }}>
                {rep.enabled ? 'CONNECTED' : 'DISABLED'}
              </span>
            </div>
            <div className="kv"><span>Writable:</span> <b>{rep.writable ? 'YES' : 'NO'}</b></div>
            <div className="kv"><span>Encrypted:</span> <b>{rep.encrypted ? 'AES-256' : 'NO'}</b></div>
            <div className="kv"><span>Endpoint:</span> <b>{rep.endpoint || 'Local Path'}</b></div>
          </div>
        ))}
      </div>

      <div className="section card">
        <div className="title">
          <h2>Federated Replication Policy & Sync Queue</h2>
          <button className="btn primary" onClick={triggerSync} disabled={loading}>
            <Play size={14} /> Process Sync Queue Now
          </button>
        </div>
        <div className="kv"><span>Replication Policy:</span> <b>{fedData?.replication_policy || 'LOCAL_ONLY'}</b></div>
        <div className="kv"><span>Conflict Strategy:</span> <b>{fedData?.conflict_resolution_strategy || 'NEWEST'}</b></div>
        <div className="kv"><span>Pending Items in Queue:</span> <b>{fedData?.sync_queue?.pending ?? 0}</b></div>
        <div className="kv"><span>Unresolved Conflicts:</span> <b>{fedData?.conflicts?.unresolved ?? conflicts.length}</b></div>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Conflict Resolution Center</h2>
          <button className="btn" onClick={loadFederation}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="list">
          {conflicts.map(c => (
            <div className="row" key={c.id}>
              <div className="rowTop">
                <b>Conflict #{c.id} · Memory ID {c.memory_id}</b>
                <span className="tag">{c.resolution_status}</span>
              </div>
              <p className="muted">Type: {c.conflict_type} · Node: {c.node_id}</p>
              {c.resolution_status === 'unresolved' && (
                <div className="actions" style={{ marginTop: 8 }}>
                  <button className="btn primary" onClick={() => resolveConflict(c.id, 'local_wins')}>Local Wins</button>
                  <button className="btn" onClick={() => resolveConflict(c.id, 'remote_wins')}>Remote Wins</button>
                  <button className="btn" onClick={() => resolveConflict(c.id, 'merge')}>Merge Both</button>
                </div>
              )}
            </div>
          ))}
          {conflicts.length === 0 && <div className="empty">No memory conflicts detected across federated nodes.</div>}
        </div>
      </div>
    </div>
  );
}
