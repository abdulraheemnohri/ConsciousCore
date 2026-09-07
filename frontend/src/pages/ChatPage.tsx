import React, { useState } from 'react';
import { Send, RefreshCw, Sliders } from 'lucide-react';
import { AppState } from '../types';

interface ChatPageProps {
  state: AppState;
  onRefresh: () => void;
}

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function ChatPage({ state, onRefresh }: ChatPageProps) {
  const [chat, setChat] = useState<any[]>([]);
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const [runtimeMode, setRuntimeMode] = useState('auto');
  const [allowCloud, setAllowCloud] = useState(false);
  const [allowRemote, setAllowRemote] = useState(false);
  const [privacyClass, setPrivacyClass] = useState('private');

  const send = async () => {
    if (!msg.trim() || busy) return;
    const userMsg = msg;
    setMsg('');
    setBusy(true);

    const userEntry = {
      role: 'user',
      text: userMsg,
      timestamp: new Date().toLocaleTimeString(),
      privacy: privacyClass
    };
    setChat(prev => [...prev, userEntry]);

    try {
      const res = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      const aiEntry = {
        role: 'ai',
        text: data.response || 'No response returned',
        confidence: data.metacognition?.confidence || 0.85,
        cycle: data.cycle?.cycle_id,
        runtime: data.runtime?.mode || 'local',
        timestamp: new Date().toLocaleTimeString()
      };
      setChat(prev => [...prev, aiEntry]);
      onRefresh();
    } catch (err: any) {
      setChat(prev => [
        ...prev,
        {
          role: 'ai',
          text: `[Runtime Error]: ${err.message || String(err)}`,
          error: true,
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="chat-page">
      <div className={`grid2 ${drawerOpen ? '' : 'single-col'}`}>
        <div className="card chat">
          <div className="title">
            <h2>Local Cognitive Chat</h2>
            <div className="actions">
              <span className="tag">Local-First</span>
              <button className="btn" onClick={() => setDrawerOpen(!drawerOpen)}>
                <Sliders size={14} /> {drawerOpen ? 'Hide Drawer' : 'Cognitive Drawer'}
              </button>
            </div>
          </div>

          <div className="messages">
            {chat.length === 0 && (
              <div className="empty">
                Send a message to ConsciousCore. The cognitive engine will run perception, attention, memory retrieval, reasoning, and safety evaluation.
              </div>
            )}
            {chat.map((item, idx) => (
              <div key={idx} className={`bubble ${item.role} ${item.error ? 'error' : ''}`}>
                <div className="bubble-meta">
                  <span>{item.role === 'user' ? 'USER' : 'CONSCIOUSCORE'}</span>
                  <span>{item.timestamp}</span>
                  {item.confidence && <span> · Confidence: {Math.round(item.confidence * 100)}%</span>}
                  {item.cycle && <span> · Cycle #{item.cycle}</span>}
                </div>
                <div>{item.text}</div>
              </div>
            ))}
          </div>

          <div className="composer">
            <input
              value={msg}
              onChange={e => setMsg(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send()}
              placeholder="Message ConsciousCore cognitive system..."
              disabled={busy}
            />
            <button className="btn primary" onClick={send} disabled={busy}>
              {busy ? <RefreshCw className="spin" size={16} /> : <Send size={16} />}
            </button>
          </div>
        </div>

        {drawerOpen && (
          <div className="card drawer-panel">
            <div className="title">
              <h2>Cognitive Parameters</h2>
            </div>
            <div className="form">
              <div className="field">
                <label>Runtime Mode</label>
                <select value={runtimeMode} onChange={e => setRuntimeMode(e.target.value)}>
                  <option value="auto">AUTO (Policy-driven)</option>
                  <option value="local">LOCAL (Device execution)</option>
                  <option value="cloud">CLOUD (Opt-in)</option>
                  <option value="remote">REMOTE (User endpoint)</option>
                  <option value="hybrid">HYBRID (Local state + Remote gen)</option>
                  <option value="parallel">PARALLEL (Multi-model)</option>
                </select>
              </div>

              <div className="field">
                <label>Data Boundary Classification</label>
                <select value={privacyClass} onChange={e => setPrivacyClass(e.target.value)}>
                  <option value="public">PUBLIC (Cloud allowed)</option>
                  <option value="internal">INTERNAL (Policy check)</option>
                  <option value="private">PRIVATE (Local preferred)</option>
                  <option value="sensitive">SENSITIVE (Local only)</option>
                  <option value="secret">SECRET (Strict local blocking)</option>
                </select>
              </div>

              <div className="field" style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <input
                  type="checkbox"
                  id="allowCloud"
                  checked={allowCloud}
                  onChange={e => setAllowCloud(e.target.checked)}
                  style={{ width: 'auto' }}
                />
                <label htmlFor="allowCloud" style={{ margin: 0, cursor: 'pointer' }}>Allow Cloud Fallback</label>
              </div>

              <div className="field" style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                <input
                  type="checkbox"
                  id="allowRemote"
                  checked={allowRemote}
                  onChange={e => setAllowRemote(e.target.checked)}
                  style={{ width: 'auto' }}
                />
                <label htmlFor="allowRemote" style={{ margin: 0, cursor: 'pointer' }}>Allow Remote Generation</label>
              </div>

              <hr style={{ borderColor: '#1e293b', margin: '10px 0' }} />

              <div className="kv">
                <span>Active Model:</span>
                <b>{state.model?.name || 'Fallback'}</b>
              </div>
              <div className="kv">
                <span>Autonomy Level:</span>
                <b>L{state.safety?.autonomy_level ?? 1}</b>
              </div>
              <div className="kv">
                <span>Memory Retrieval:</span>
                <b>ENABLED</b>
              </div>
              <div className="kv">
                <span>Reflection Cycle:</span>
                <b>ENABLED</b>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
