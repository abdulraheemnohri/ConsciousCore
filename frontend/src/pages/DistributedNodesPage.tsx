import React, { useState, useEffect } from 'react';
import { Server, Plus, RefreshCw, Activity } from 'lucide-react';
import { AppState } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export function DistributedNodesPage({ state }: { state: AppState }) {
  const [nodes, setNodes] = useState<any[]>([]);
  const [nodeId, setNodeId] = useState('');
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);

  const loadNodes = async () => {
    try {
      const res = await fetch(`${API}/api/nodes`);
      if (res.ok) {
        const data = await res.json();
        setNodes(data.items || []);
      }
    } catch {}
  };

  useEffect(() => {
    loadNodes();
  }, []);

  const registerNode = async () => {
    if (!nodeId.trim() || !name.trim() || loading) return;
    setLoading(true);
    try {
      await fetch(`${API}/api/nodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          node_id: nodeId,
          name,
          address: address || 'http://127.0.0.1:8000',
          capabilities: ['cognition', 'inference', 'memory_replication']
        })
      });
      setNodeId('');
      setName('');
      setAddress('');
      await loadNodes();
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <div className="distributed-nodes-page">
      <div className="grid">
        <div className="card metric">
          <span>Total Registered Nodes</span>
          <strong>{nodes.length}</strong>
        </div>
        <div className="card metric">
          <span>Coordinator Node</span>
          <strong style={{ color: '#38bdf8' }}>Node-Local (Active)</strong>
        </div>
        <div className="card metric">
          <span>Inference Worker</span>
          <strong style={{ color: '#10b981' }}>ONLINE</strong>
        </div>
        <div className="card metric">
          <span>Memory Workers</span>
          <strong>Replicated</strong>
        </div>
      </div>

      <div className="section grid2">
        <div className="card form">
          <div className="title"><h2>Register Distributed ConsciousCore Node</h2></div>
          <div className="field">
            <label>Node ID (slug)</label>
            <input value={nodeId} onChange={e => setNodeId(e.target.value)} placeholder="e.g. node_gpu_worker_1" />
          </div>
          <div className="field">
            <label>Node Name</label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Remote GPU Inference Worker" />
          </div>
          <div className="field">
            <label>Network Address / Endpoint</label>
            <input value={address} onChange={e => setAddress(e.target.value)} placeholder="e.g. http://192.168.1.100:8000" />
          </div>
          <button className="btn primary" onClick={registerNode} disabled={loading}>
            <Plus size={15} /> Register Node
          </button>
        </div>

        <div className="card">
          <div className="title">
            <h2>Active Nodes Registry</h2>
            <button className="btn" onClick={loadNodes}><RefreshCw size={14} /> Refresh</button>
          </div>
          <div className="list">
            {nodes.map(n => (
              <div className="row" key={n.node_id}>
                <div className="rowTop">
                  <b>{n.name} ({n.node_id})</b>
                  <span className="tag" style={{ background: '#064e3b', color: '#34d399' }}>{n.status || 'ONLINE'}</span>
                </div>
                <small className="muted">Address: {n.address || 'Local'} · Last seen: {n.last_seen || 'Just now'}</small>
              </div>
            ))}
            {nodes.length === 0 && <div className="empty">No distributed external nodes registered yet. Operating as solo local node.</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
