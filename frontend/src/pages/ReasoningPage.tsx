import React from 'react';
import { Brain, CheckCircle2, Shield, AlertTriangle } from 'lucide-react';
import { AppState } from '../types';

export function ReasoningPage({ state }: { state: AppState }) {
  const reasoningSummary = {
    decision: 'Local Cognitive Execution',
    evidence_used: ['User query input', 'Retrieved persistent memories', 'Global Workspace broadcast focus'],
    confidence: state.state?.confidence ?? 0.85,
    uncertainty: state.state?.uncertainty ?? 0.15,
    safety_constraints: ['No secret extraction', 'Approval-gated execution', 'Local privacy boundary'],
    rationale_summary: 'Target route selected based on privacy classification (PRIVATE/LOCAL) and user autonomy settings.'
  };

  return (
    <div className="reasoning-page">
      <div className="notice" style={{ marginBottom: 16 }}>
        <Shield size={18} style={{ color: '#38bdf8' }} />
        <span><b>Safe Decision Summary:</b> Private hidden chain-of-thought is not exposed. Only safe, explainable decision summaries and evidence references are presented.</span>
      </div>

      <div className="grid2">
        <div className="card">
          <div className="title"><h2>Decision & Rationale Summary</h2></div>
          <div className="kv"><span>Decision:</span> <b>{reasoningSummary.decision}</b></div>
          <div className="kv"><span>Confidence:</span> <b>{Math.round(reasoningSummary.confidence * 100)}%</b></div>
          <div className="kv"><span>Uncertainty:</span> <b>{Math.round(reasoningSummary.uncertainty * 100)}%</b></div>
          <div style={{ marginTop: 12 }}>
            <b style={{ color: '#f8fafc', fontSize: 13 }}>Rationale Summary:</b>
            <p className="muted" style={{ margin: '4px 0 0' }}>{reasoningSummary.rationale_summary}</p>
          </div>
        </div>

        <div className="card">
          <div className="title"><h2>Evidence & Memory Grounding</h2></div>
          <div className="list">
            {reasoningSummary.evidence_used.map((ev, i) => (
              <div key={i} className="row">
                <b>Evidence #{i + 1}: {ev}</b>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="section card">
        <div className="title"><h2>Safety & Policy Constraints Evaluated</h2></div>
        <div className="list">
          {reasoningSummary.safety_constraints.map((sc, i) => (
            <div key={i} className="row" style={{ borderLeft: '3px solid #10b981' }}>
              <b><CheckCircle2 size={14} color="#10b981" /> {sc}</b>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
