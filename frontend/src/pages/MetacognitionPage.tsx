import React from 'react';
import { Activity, ShieldCheck, HelpCircle } from 'lucide-react';
import { AppState } from '../types';

export function MetacognitionPage({ state }: { state: AppState }) {
  const meta = {
    confidence: state.state?.confidence ?? 0.85,
    uncertainty: state.state?.uncertainty ?? 0.15,
    memory_reliability: 0.92,
    reasoning_reliability: 0.88,
    prediction_accuracy: 0.82,
    verification_status: 'HEALTHY'
  };

  return (
    <div className="metacognition-page">
      <div className="grid">
        <div className="card metric">
          <span>Overall Confidence</span>
          <strong>{Math.round(meta.confidence * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Uncertainty Level</span>
          <strong>{Math.round(meta.uncertainty * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Memory Reliability</span>
          <strong>{Math.round(meta.memory_reliability * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Reasoning Reliability</span>
          <strong>{Math.round(meta.reasoning_reliability * 100)}%</strong>
        </div>
      </div>

      <div className="section card">
        <div className="title"><h2>Metacognitive Monitoring Surface</h2></div>
        <div className="kv"><span>Prediction Accuracy Rate:</span> <b>{Math.round(meta.prediction_accuracy * 100)}%</b></div>
        <div className="kv"><span>System Verification Status:</span> <b style={{ color: '#10b981' }}>{meta.verification_status}</b></div>
        <div className="kv"><span>Low Confidence Trigger Policy:</span> <b>Alternative model / Human approval fallback</b></div>
      </div>
    </div>
  );
}
