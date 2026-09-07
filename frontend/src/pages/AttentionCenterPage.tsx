import React, { useState, useEffect } from 'react';
import { ArrowUp, ArrowDown, Pin, RefreshCw } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function AttentionCenterPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [attentionData, setAttentionData] = useState<any>(null);

  const loadAttention = async () => {
    try {
      const res = await fetch(`${API}/api/attention`);
      if (res.ok) {
        const data = await res.json();
        setAttentionData(data);
      }
    } catch {}
  };

  useEffect(() => {
    loadAttention();
  }, []);

  const items = attentionData?.items || state.global_workspace_v2?.active_candidates || [
    { id: '1', title: 'Current user query', weight: 0.98, urgency: 0.9, relevance: 0.95 },
    { id: '2', title: 'Active high-priority goal', weight: 0.91, urgency: 0.85, relevance: 0.90 },
    { id: '3', title: 'Relevant episodic memory', weight: 0.87, urgency: 0.6, relevance: 0.88 },
    { id: '4', title: 'Prediction uncertainty', weight: 0.72, urgency: 0.7, relevance: 0.75 }
  ];

  return (
    <div className="attention-center-page">
      <div className="grid">
        <div className="card metric">
          <span>Top Attention Focus</span>
          <strong style={{ fontSize: 18 }}>{attentionData?.focus || items[0]?.title || 'User Request'}</strong>
        </div>
        <div className="card metric">
          <span>Attention Load</span>
          <strong>{Math.round((state.state?.attention_load ?? 0.45) * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Uncertainty Weight</span>
          <strong>{Math.round((state.state?.uncertainty ?? 0.5) * 100)}%</strong>
        </div>
        <div className="card metric">
          <span>Ranked Items</span>
          <strong>{items.length}</strong>
        </div>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Attention Ranking & Allocation Engine</h2>
          <button className="btn" onClick={loadAttention}><RefreshCw size={14} /> Refresh</button>
        </div>

        <div className="list">
          {items.map((item: any, index: number) => {
            const score = Math.round((item.weight || item.salience || 0.8) * 100);
            return (
              <div className="row" key={item.id || index} style={{ borderLeft: index === 0 ? '4px solid #38bdf8' : '1px solid #1e293b' }}>
                <div className="rowTop">
                  <b>#{index + 1} {item.title || item.content}</b>
                  <span className="tag" style={{ background: index === 0 ? '#0284c7' : '#0f172a', color: '#fff' }}>
                    Score: {score}%
                  </span>
                </div>
                <div className="bar" style={{ margin: '8px 0' }}>
                  <i style={{ width: `${score}%`, background: index === 0 ? '#38bdf8' : '#64748b' }} />
                </div>
                <div className="actions">
                  <button className="btn" title="Boost Attention"><ArrowUp size={13} /> Boost</button>
                  <button className="btn" title="Suppress"><ArrowDown size={13} /> Suppress</button>
                  <button className="btn" title="Pin Attention"><Pin size={13} /> Pin Focus</button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
