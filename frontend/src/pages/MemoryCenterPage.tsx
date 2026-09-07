import React, { useState, useEffect } from 'react';
import { Database, Search, Plus, Archive, Clock3 } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function MemoryCenterPage({ state, onRefresh }: { state: AppState; onRefresh: () => void }) {
  const [activeTab, setActiveTab] = useState('all');
  const [memories, setMemories] = useState<any[]>([]);
  const [query, setQuery] = useState('');
  const [content, setContent] = useState('');
  const [kind, setKind] = useState('semantic');
  const [importance, setImportance] = useState(0.7);
  const [confidence, setConfidence] = useState(0.8);
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);

  const loadMemories = async () => {
    try {
      const kindParam = activeTab === 'all' ? '' : `&kind=${activeTab}`;
      const res = await fetch(`${API}/api/memory?q=${encodeURIComponent(query)}&limit=100${kindParam}`);
      if (res.ok) {
        const data = await res.json();
        setMemories(data.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadMemories();
  }, [activeTab, query]);

  const addMemory = async () => {
    if (!content.trim() || loading) return;
    setLoading(true);
    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(Boolean);
      await fetch(`${API}/api/memory`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          kind,
          importance: Number(importance),
          confidence: Number(confidence),
          tags: tagList,
          source: 'user'
        })
      });
      setContent('');
      setTags('');
      await loadMemories();
      onRefresh();
    } catch (e) {
      alert(`Error adding memory: ${e}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteMemory = async (id: number) => {
    try {
      await fetch(`${API}/api/memory/${id}`, { method: 'DELETE' });
      await loadMemories();
      onRefresh();
    } catch {}
  };

  const consolidate = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/memory/consolidate`, { method: 'POST' });
      await loadMemories();
      onRefresh();
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <div className="memory-center-page">
      <div className="tabs">
        {['all', 'working', 'episodic', 'semantic', 'procedural', 'self', 'meta', 'autobiographical'].map(t => (
          <button key={t} className={activeTab === t ? 'on' : ''} onClick={() => setActiveTab(t)}>
            {t.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="section card form">
        <div className="title">
          <h2>Create Persistent Memory Record</h2>
          <button className="btn" onClick={consolidate} disabled={loading}>
            <Clock3 size={14} /> Run Memory Consolidation
          </button>
        </div>
        <div className="grid3">
          <div className="field">
            <label>Memory Kind</label>
            <select value={kind} onChange={e => setKind(e.target.value)}>
              <option value="semantic">Semantic (Facts & Knowledge)</option>
              <option value="episodic">Episodic (Events & History)</option>
              <option value="working">Working (Active Context)</option>
              <option value="procedural">Procedural (Skills & Rules)</option>
              <option value="self">Self (Identity & Bounds)</option>
              <option value="meta">Meta (Uncertainty & Reliability)</option>
            </select>
          </div>
          <div className="field">
            <label>Importance (0.0 - 1.0)</label>
            <input type="number" step="0.1" min="0" max="1" value={importance} onChange={e => setImportance(Number(e.target.value))} />
          </div>
          <div className="field">
            <label>Confidence (0.0 - 1.0)</label>
            <input type="number" step="0.1" min="0" max="1" value={confidence} onChange={e => setConfidence(Number(e.target.value))} />
          </div>
        </div>
        <div className="field">
          <label>Memory Content</label>
          <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Type memory content..." />
        </div>
        <div className="field">
          <label>Tags (comma separated)</label>
          <input value={tags} onChange={e => setTags(e.target.value)} placeholder="ai, core, policy" />
        </div>
        <button className="btn primary" onClick={addMemory} disabled={loading}>
          <Plus size={15} /> Store Memory Record
        </button>
      </div>

      <div className="section card">
        <div className="title">
          <h2>Memory Search & Registry</h2>
          <div className="actions">
            <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search memories..." />
            <button className="btn" onClick={loadMemories}><Search size={14} /> Search</button>
          </div>
        </div>

        <div className="list">
          {memories.map(m => (
            <div className="row" key={m.id}>
              <div className="rowTop">
                <b>#{m.id} · [{m.kind.toUpperCase()}]</b>
                <span className="tag">Confidence: {Math.round((m.confidence || 0.8) * 100)}%</span>
              </div>
              <p style={{ margin: '8px 0', color: '#f8fafc' }}>{m.content}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <small className="muted">Importance: {Math.round((m.importance || 0.5) * 100)}% · Source: {m.source || 'system'}</small>
                <button className="btn danger" onClick={() => deleteMemory(m.id)}>
                  <Archive size={13} /> Delete
                </button>
              </div>
            </div>
          ))}
          {memories.length === 0 && <div className="empty">No memory records found matching query.</div>}
        </div>
      </div>
    </div>
  );
}
