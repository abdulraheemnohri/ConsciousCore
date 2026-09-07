import React, { useState } from 'react';
import { Settings, RefreshCw, Terminal, Play } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function DeveloperConsolePage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [endpoint, setEndpoint] = useState('/api/state');
  const [method, setMethod] = useState('GET');
  const [requestBody, setRequestBody] = useState('');
  const [responseJson, setResponseJson] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const executeApi = async () => {
    setLoading(true);
    try {
      const options: RequestInit = { method };
      if (method !== 'GET' && requestBody.trim()) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = requestBody;
      }
      const res = await fetch(`${API}${endpoint}`, options);
      const data = await res.json();
      setResponseJson(data);
    } catch (e: any) {
      setResponseJson({ error: e.message || String(e) });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="developer-console-page">
      <div className="section card form">
        <div className="title"><h2><Terminal size={16} /> API Inspector & Runtime Tester</h2></div>
        <div className="grid2">
          <div className="field">
            <label>HTTP Method</label>
            <select value={method} onChange={e => setMethod(e.target.value)}>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
          <div className="field">
            <label>Endpoint Path</label>
            <input value={endpoint} onChange={e => setEndpoint(e.target.value)} placeholder="/api/state" />
          </div>
        </div>

        {method !== 'GET' && (
          <div className="field">
            <label>Request JSON Body</label>
            <textarea value={requestBody} onChange={e => setRequestBody(e.target.value)} placeholder="{}" />
          </div>
        )}

        <button className="btn primary" onClick={executeApi} disabled={loading}>
          {loading ? <RefreshCw className="spin" size={15} /> : <Play size={15} />} Dispatch API Request
        </button>
      </div>

      {responseJson && (
        <div className="section card">
          <div className="title"><h2>Response Payload</h2></div>
          <pre className="json">{JSON.stringify(responseJson, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
