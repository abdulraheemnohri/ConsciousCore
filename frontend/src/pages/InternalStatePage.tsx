import React from 'react';
import { Layers, Shield } from 'lucide-react';
import { AppState } from '../types';

export function InternalStatePage({ state }: { state: AppState }) {
  const is = state.state || {};

  return (
    <div className="internal-state-page">
      <div className="notice" style={{ marginBottom: 16 }}>
        <Shield size={18} style={{ color: '#38bdf8' }} />
        <span><b>Neutral Computational Terminology:</b> Energy, uncertainty, confidence, workload, attention load, and task pressure are functional computational variables, not biological emotions or feelings.</span>
      </div>

      <div className="grid3">
        <div className="card metric">
          <span>Energy Level</span>
          <strong>{Math.round((is.energy ?? 0.8) * 100)}%</strong>
          <small>computational capacity</small>
        </div>
        <div className="card metric">
          <span>Uncertainty</span>
          <strong>{Math.round((is.uncertainty ?? 0.2) * 100)}%</strong>
          <small>epistemic state</small>
        </div>
        <div className="card metric">
          <span>Confidence</span>
          <strong>{Math.round((is.confidence ?? 0.85) * 100)}%</strong>
          <small>evaluative variable</small>
        </div>
        <div className="card metric">
          <span>Workload</span>
          <strong>{Math.round((is.workload ?? 0.1) * 100)}%</strong>
          <small>active tasks</small>
        </div>
        <div className="card metric">
          <span>Attention Load</span>
          <strong>{Math.round((is.attention_load ?? 0.3) * 100)}%</strong>
          <small>surface allocation</small>
        </div>
        <div className="card metric">
          <span>Task Pressure</span>
          <strong>{Math.round((is.task_pressure ?? 0.15) * 100)}%</strong>
          <small>deadline proximity</small>
        </div>
      </div>
    </div>
  );
}
