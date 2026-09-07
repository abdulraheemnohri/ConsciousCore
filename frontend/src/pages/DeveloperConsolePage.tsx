import React, { useState } from 'react';
import { Terminal, Play, RefreshCw, Cpu, Zap, Moon, BookOpen, Layers, ShieldCheck } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function DeveloperConsolePage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [endpoint, setEndpoint] = useState('/api/state');
  const [method, setMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [responseJson, setResponseJson] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [controlStatus, setControlStatus] = useState<string | null>(null);

  const executeApi = async (overrideMethod?: string, overridePath?: string, overrideBody?: any) => {
    setLoading(true);
    setControlStatus(null);
    const effMethod = overrideMethod || method;
    const effPath = overridePath || endpoint;
    const effBody = overrideBody !== undefined ? JSON.stringify(overrideBody) : requestBody;

    try {
      const options: RequestInit = { method: effMethod };
      if (effMethod !== 'GET' && effBody.trim()) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = effBody;
      }
      const res = await fetch(`${API}${effPath}`, options);
      const data = await res.json();
      setResponseJson(data);
      setControlStatus(`Successfully executed ${effMethod} ${effPath}`);
      onRefresh();
    } catch (e: any) {
      setResponseJson({ error: e.message || String(e) });
      setControlStatus(`Failed: ${e.message || String(e)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="developer-console-page">
      <div className="panel" style={{ marginBottom: 16 }}>
        <div className="panelTitle">
          <h2><Cpu size={16} /> Instant Backend Control Center</h2>
          <span>Direct Operations</span>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: 11, margin: '0 0 14px' }}>
          Execute real backend triggers and state transitions across ConsciousCore cognitive subsystems.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
          <button
            className="secondaryBtn"
            onClick={() => executeApi('POST', '/api/loop/run', { message: 'Run manual cognitive cycle test' })}
          >
            <Zap size={14} /> Run Cognitive Loop
          </button>

          <button
            className="secondaryBtn"
            onClick={() => executeApi('POST', '/api/reflection', {})}
          >
            <BookOpen size={14} /> Trigger Instant Reflection
          </button>

          <button
            className="secondaryBtn"
            onClick={() => executeApi('POST', '/api/memory/consolidate', {})}
          >
            <Layers size={14} /> Consolidate Memory
          </button>

          <button
            className="secondaryBtn"
            onClick={() => executeApi('POST', '/api/sleep', {})}
          >
            <Moon size={14} /> Execute Sleep Cycle
          </button>

          <button
            className="secondaryBtn"
            onClick={() => executeApi('POST', '/api/internal-state/recover', { amount: 0.2 })}
          >
            <ShieldCheck size={14} /> Recover Internal Energy
          </button>

          <button
            className="secondaryBtn"
            onClick={() => executeApi('POST', '/api/workspace/v2/interrupt', { reason: 'Developer console manual interruption' })}
          >
            <Terminal size={14} /> Workspace Interruption
          </button>
        </div>

        {controlStatus && (
          <div style={{ marginTop: 12, padding: '8px 12px', background: '#0a1018', border: '1px solid #1e2a39', borderRadius: 6, fontSize: 11, color: '#3fb950' }}>
            {controlStatus}
          </div>
        )}
      </div>

      <div className="panel">
        <div className="panelTitle">
          <h2><Terminal size={16} /> API Inspector & Runtime Tester</h2>
          <span>REST Explorer</span>
        </div>

        <div className="formRow">
          <div>
            <label>HTTP Method</label>
            <select value={method} onChange={e => setMethod(e.target.value)}>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
          <div>
            <label>Endpoint Path</label>
            <input value={endpoint} onChange={e => setEndpoint(e.target.value)} placeholder="/api/state" />
          </div>
        </div>

        {method !== 'GET' && (
          <div style={{ marginTop: 12 }}>
            <label>Request JSON Body</label>
            <textarea
              style={{ width: '100%', minHeight: 90, background: 'var(--bg-input)', border: '1px solid #263244', color: '#fff', borderRadius: 8, padding: 10, fontFamily: 'var(--font-mono)', fontSize: 11 }}
              value={requestBody}
              onChange={e => setRequestBody(e.target.value)}
              placeholder="{}"
            />
          </div>
        )}

        <button className="primaryBtn" style={{ marginTop: 14 }} onClick={() => executeApi()} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={14} /> : <Play size={14} />} Dispatch API Request
        </button>
      </div>

      {responseJson && (
        <div className="panel dataPanel" style={{ marginTop: 16 }}>
          <div className="panelTitle">
            <h2>Response Payload</h2>
            <span>JSON Output</span>
          </div>
          <pre>{JSON.stringify(responseJson, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
