import React, { useState, useEffect } from 'react';
import { RefreshCw, Plus } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function GlobalWorkspacePage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [workspaceData, setWorkspaceData] = useState<any>(null);
  const [candidateContent, setCandidateContent] = useState('');
  const [candidateSource, setCandidateSource] = useState('user');
  const [loading, setLoading] = useState(false);

  const loadWorkspace = async () => {
    try {
      const res = await fetch(`${API}/api/workspace/v2`);
      if (res.ok) {
        const data = await res.json();
        setWorkspaceData(data);
      }
    } catch {}
  };

  useEffect(() => {
    loadWorkspace();
  }, []);

  const submitCandidate = async () => {
    if (!candidateContent.trim() || loading) return;
    setLoading(true);
    try {
      await fetch(`${API}/api/workspace/v2/candidates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source: candidateSource,
          content: candidateContent,
          salience: 0.8,
          confidence: 0.9,
          urgency: 0.7,
          relevance: 0.85
        })
      });
      setCandidateContent('');
      await loadWorkspace();
      onRefresh();
    } catch (e) {
      alert(`Candidate submission error: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const selectWinner = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/workspace/v2/select`, { method: 'POST' });
      await loadWorkspace();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const broadcastCurrent = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/workspace/v2/broadcast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved: true })
      });
      await loadWorkspace();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const interruptWorkspace = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/workspace/v2/interrupt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'Manual high-priority user interrupt' })
      });
      await loadWorkspace();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  const ws = workspaceData || state.global_workspace_v2 || {};

  return (
    <div className="global-workspace-page">
      <div className="grid">
        <div className="card metric">
          <span>Active Candidates</span>
          <strong>{(ws.active_candidates || []).length}</strong>
        </div>
        <div className="card metric">
          <span>Current Broadcast</span>
          <strong>{ws.current_broadcast ? 'ACTIVE' : 'IDLE'}</strong>
        </div>
        <div className="card metric">
          <span>Subscribers</span>
          <strong>{(ws.subscribers || []).length}</strong>
        </div>
        <div className="card metric">
          <span>Total Broadcasts</span>
          <strong>{ws.stats?.total_broadcasts ?? 0}</strong>
        </div>
      </div>

      <div className="section grid2">
        <div className="card">
          <div className="title">
            <h2>Current Active Focus / Broadcast</h2>
            <div className="actions">
              <button className="btn primary" onClick={selectWinner} disabled={loading}>
                Select Winner
              </button>
              <button className="btn" onClick={broadcastCurrent} disabled={loading}>
                Broadcast
              </button>
              <button className="btn danger" onClick={interruptWorkspace} disabled={loading}>
                Interrupt
              </button>
            </div>
          </div>

          {ws.current_broadcast ? (
            <div className="row" style={{ borderColor: '#38bdf8', background: '#032b45' }}>
              <div className="rowTop">
                <b>Source: {ws.current_broadcast.source}</b>
                <span className="tag">Salience: {Math.round((ws.current_broadcast.salience || 0.8) * 100)}%</span>
              </div>
              <p style={{ fontSize: 15, color: '#f8fafc', fontWeight: 500 }}>{ws.current_broadcast.content}</p>
              <small className="muted">Broadcast at: {ws.current_broadcast.timestamp || 'Just now'}</small>
            </div>
          ) : (
            <div className="empty">No active broadcast winner selected in the workspace surface.</div>
          )}
        </div>

        <div className="card form">
          <div className="title">
            <h2>Submit Candidate</h2>
          </div>
          <div className="field">
            <label>Source Module</label>
            <input value={candidateSource} onChange={e => setCandidateSource(e.target.value)} placeholder="user / memory / goal" />
          </div>
          <div className="field">
            <label>Candidate Content</label>
            <textarea value={candidateContent} onChange={e => setCandidateContent(e.target.value)} placeholder="Propose information candidate to compete for broadcast..." />
          </div>
          <button className="btn primary" onClick={submitCandidate} disabled={loading}>
            <Plus size={15} /> Submit Candidate
          </button>
        </div>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Active Competing Candidates Surface</h2>
          <button className="btn" onClick={loadWorkspace}><RefreshCw size={14} /> Refresh</button>
        </div>
        <div className="list">
          {(ws.active_candidates || []).map((cand: any, i: number) => (
            <div className="row" key={cand.id || i}>
              <div className="rowTop">
                <b>#{i + 1} [{cand.source}] - {cand.content}</b>
                <span className="tag">Relevance: {Math.round((cand.relevance || 0.8) * 100)}%</span>
              </div>
              <small className="muted">
                Salience: {Math.round((cand.salience || 0.8) * 100)}% · Urgency: {Math.round((cand.urgency || 0.5) * 100)}% · Confidence: {Math.round((cand.confidence || 0.8) * 100)}%
              </small>
            </div>
          ))}
          {(!ws.active_candidates || ws.active_candidates.length === 0) && (
            <div className="empty">No candidates currently competing in Global Workspace.</div>
          )}
        </div>
      </div>
    </div>
  );
}
