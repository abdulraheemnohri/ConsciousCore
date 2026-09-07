import React, { useState, useEffect } from 'react';
import { LineChart, Shield, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function TelemetryPage({ state }: { state: AppState }) {
  const [telem, setTelem] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);

  const loadTelem = async () => {
    try {
      const res = await fetch(`${API}/api/telemetry`);
      if (res.ok) setTelem(await res.json());

      const evRes = await fetch(`${API}/api/telemetry/events?limit=50`);
      if (evRes.ok) {
        const evData = await evRes.json();
        setEvents(evData.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadTelem();
  }, []);

  const setMode = async (mode: string) => {
    try {
      await fetch(`${API}/api/telemetry/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });
      await loadTelem();
    } catch {}
  };

  const t = telem || {};

  return (
    <div className="telemetry-page">
      <div className="notice" style={{ marginBottom: 16 }}>
        <Shield size={18} style={{ color: '#38bdf8' }} />
        <span><b>Privacy Boundary:</b> Remote telemetry is OFF by default. Local diagnostics run on-device. Telemetry NEVER records or transmits passwords, private memory, API keys, or secret tokens.</span>
      </div>

      <div className="grid">
        <div className="card metric">
          <span>Telemetry Mode</span>
          <strong style={{ color: t.mode === 'off' ? '#ef4444' : '#38bdf8' }}>{(t.mode || 'local').toUpperCase()}</strong>
        </div>
        <div className="card metric">
          <span>Local Diagnostics</span>
          <strong style={{ color: '#34d399' }}>{t.enabled !== false ? 'ENABLED' : 'DISABLED'}</strong>
        </div>
        <div className="card metric">
          <span>Remote Telemetry</span>
          <strong style={{ color: t.remote_enabled ? '#38bdf8' : '#94a3b8' }}>{t.remote_enabled ? 'ON' : 'OFF (Default)'}</strong>
        </div>
        <div className="card metric">
          <span>Total Logged Requests</span>
          <strong>{t.latency?.total_requests ?? 0}</strong>
        </div>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Privacy Mode Selector</h2>
          <button className="btn" onClick={loadTelem}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="actions">
          <button className={`btn ${t.mode === 'off' ? 'primary' : ''}`} onClick={() => setMode('off')}>OFF (No telemetry)</button>
          <button className={`btn ${t.mode === 'local' ? 'primary' : ''}`} onClick={() => setMode('local')}>LOCAL (On-device diagnostics only)</button>
          <button className={`btn ${t.mode === 'anonymous' ? 'primary' : ''}`} onClick={() => setMode('anonymous')}>ANONYMOUS (Anonymized stats)</button>
          <button className={`btn ${t.mode === 'full' ? 'primary' : ''}`} onClick={() => setMode('full')}>FULL (Opt-in full telemetry)</button>
        </div>
      </div>

      <div className="section card">
        <div className="title"><h2>Recent Local Telemetry Events</h2></div>
        <div className="list">
          {events.map(ev => (
            <div className="row" key={ev.id}>
              <div className="rowTop">
                <b>[{ev.event_type?.toUpperCase()}]</b>
                <span className="tag">{ev.timestamp}</span>
              </div>
              <pre className="json">{JSON.stringify(ev.payload || {}, null, 2)}</pre>
            </div>
          ))}
          {events.length === 0 && <div className="empty">No telemetry events recorded.</div>}
        </div>
      </div>
    </div>
  );
}
