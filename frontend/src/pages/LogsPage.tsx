import React, { useState, useEffect } from 'react';
import { History, RefreshCw, Search } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function LogsPage({ state }: { state: AppState }) {
  const [logs, setLogs] = useState<any[]>([]);
  const [filter, setFilter] = useState('');

  const loadLogs = async () => {
    try {
      const res = await fetch(`${API}/api/audit?limit=100`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadLogs();
  }, []);

  const filtered = logs.filter(l =>
    (l.event_type || '').toLowerCase().includes(filter.toLowerCase()) ||
    JSON.stringify(l.payload || {}).toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="logs-page">
      <div className="section card">
        <div className="title">
          <h2><History size={16} /> Audit & System Logs</h2>
          <div className="actions">
            <input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter audit logs..." />
            <button className="btn" onClick={loadLogs}><RefreshCw size={14} /> Refresh</button>
          </div>
        </div>

        <div className="list">
          {filtered.map(l => (
            <div className="row" key={l.id}>
              <div className="rowTop">
                <b>#{l.id} · {l.event_type}</b>
                <span className="tag">{l.created_at}</span>
              </div>
              <pre className="json">{JSON.stringify(JSON.parse(l.payload || '{}'), null, 2)}</pre>
            </div>
          ))}
          {filtered.length === 0 && <div className="empty">No audit log records found.</div>}
        </div>
      </div>
    </div>
  );
}
