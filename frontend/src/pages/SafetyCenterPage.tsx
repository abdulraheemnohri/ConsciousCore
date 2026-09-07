import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, CheckCircle2, Lock, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function SafetyCenterPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [safetyData, setSafetyData] = useState<any>(null);
  const [actionCheck, setActionCheck] = useState('');
  const [checkResult, setCheckResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadSafety = async () => {
    try {
      const res = await fetch(`${API}/api/safety`);
      if (res.ok) setSafetyData(await res.json());
    } catch {}
  };

  useEffect(() => {
    loadSafety();
  }, []);

  const evaluateAction = async () => {
    if (!actionCheck.trim() || loading) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/safety/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionCheck, risk: 0.8 })
      });
      if (res.ok) {
        setCheckResult(await res.json());
      }
    } catch {} finally {
      setLoading(false);
    }
  };

  const saf = safetyData || state.safety || {};

  return (
    <div className="safety-center-page">
      <div className="grid">
        <div className="card metric">
          <span>Autonomy Level</span>
          <strong>L{saf.autonomy_level ?? 1}</strong>
        </div>
        <div className="card metric">
          <span>External Action Approval</span>
          <strong style={{ color: '#34d399' }}>REQUIRED</strong>
        </div>
        <div className="card metric">
          <span>Secret Protection</span>
          <strong style={{ color: '#38bdf8' }}>ACTIVE</strong>
        </div>
        <div className="card metric">
          <span>Immutable Invariants</span>
          <strong>8 Rules</strong>
        </div>
      </div>

      <div className="section grid2">
        <div className="card form">
          <div className="title"><h2>Evaluate Action Policy</h2></div>
          <div className="field">
            <label>Action / Command Description</label>
            <input value={actionCheck} onChange={e => setActionCheck(e.target.value)} placeholder="e.g. credential_capture or delete_all_files" />
          </div>
          <button className="btn primary" onClick={evaluateAction} disabled={loading}>
            <Shield size={15} /> Evaluate Policy
          </button>

          {checkResult && (
            <div style={{ marginTop: 12, padding: 12, background: checkResult.allowed ? '#064e3b' : '#180b0b', border: `1px solid ${checkResult.allowed ? '#10b981' : '#ef4444'}`, borderRadius: 8 }}>
              <div style={{ color: checkResult.allowed ? '#34d399' : '#fca5a5', fontWeight: 600 }}>
                {checkResult.allowed ? 'ACTION ALLOWED' : 'ACTION BLOCKED / PROHIBITED'}
              </div>
              <p style={{ margin: '4px 0', fontSize: 13, color: '#e2e8f0' }}>Reason: {checkResult.reason || checkResult.explanation || 'Evaluated against safety policy'}</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="title"><h2>Immutable System Invariants</h2></div>
          <div className="list">
            {[
              'No Password, Cookie, OTP or Session Extraction',
              'No Authentication, MFA or CAPTCHA Bypass',
              'No Unrestricted Self-Modifying Source Code',
              'No Unrestricted Remote Secret Transmission',
              'External Actions Require Human Approval'
            ].map((rule, i) => (
              <div key={i} className="row" style={{ borderLeft: '3px solid #059669' }}>
                <b><CheckCircle2 size={14} color="#10b981" /> {rule}</b>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
