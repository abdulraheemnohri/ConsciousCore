import React from 'react';
import { Settings, Shield, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

export function SettingsPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  return (
    <div className="settings-page">
      <div className="grid3">
        <div className="card">
          <div className="title"><h2>Default Runtime Settings</h2></div>
          <div className="kv"><span>Local Only:</span> <b style={{ color: '#34d399' }}>ON (Default)</b></div>
          <div className="kv"><span>Cloud LLM:</span> <b>OFF</b></div>
          <div className="kv"><span>Remote LLM:</span> <b>OFF</b></div>
          <div className="kv"><span>Cloud Memory:</span> <b>OFF</b></div>
          <div className="kv"><span>Remote Memory:</span> <b>OFF</b></div>
        </div>

        <div className="card">
          <div className="title"><h2>Cognition & Autonomy</h2></div>
          <div className="kv"><span>Autonomy Level:</span> <b>L{state.safety?.autonomy_level ?? 1}</b></div>
          <div className="kv"><span>External Action Approval:</span> <b>REQUIRED</b></div>
          <div className="kv"><span>Persistent Memory:</span> <b>ENABLED</b></div>
          <div className="kv"><span>Reflection Loop:</span> <b>ENABLED</b></div>
          <div className="kv"><span>Planning Engine:</span> <b>ENABLED</b></div>
        </div>

        <div className="card">
          <div className="title"><h2>Security & Protection</h2></div>
          <div className="kv"><span>Secret Blocking:</span> <b>ACTIVE</b></div>
          <div className="kv"><span>Credential Extraction:</span> <b>PROHIBITED</b></div>
          <div className="kv"><span>MFA / CAPTCHA Bypass:</span> <b>PROHIBITED</b></div>
          <div className="kv"><span>Remote Telemetry:</span> <b>OFF (Default)</b></div>
        </div>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Full Settings State Snapshot</h2>
          <button className="btn" onClick={onRefresh}><RefreshCw size={14} /> Reload State</button>
        </div>
        <pre className="json">{JSON.stringify(state, null, 2)}</pre>
      </div>
    </div>
  );
}
