import React from 'react';
import { Search, Shield, Cpu, Database, Activity, RefreshCw, AlertOctagon } from 'lucide-react';
import { AppState } from './types';

interface HeaderProps {
  currentPage: string;
  state: AppState;
  onOpenCommandPalette: () => void;
  onRefresh: () => void;
}

export function Header({ currentPage, state, onOpenCommandPalette, onRefresh }: HeaderProps) {
  const modelName = state.model?.name || state.model?.model_id || 'Deterministic Fallback';
  const memoryCount = state.memory_count ?? 0;
  const autonomyLevel = state.safety?.autonomy_level ?? 1;

  const handleEmergencyStop = async () => {
    try {
      const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      await fetch(`${API}/api/v1/emergency-stop`, { method: 'POST' });
      alert("EMERGENCY STOP TRIGGERED: All autonomous activity halted.");
      onRefresh();
    } catch (err) {
      alert("Failed to trigger emergency stop.");
    }
  };

  return (
    <header className="head">
      <div className="head-left">
        <div className="eyebrow">CONSCIOUSCORE V1 · COGNITIVE CONTROL CENTER</div>
        <h1>{currentPage}</h1>
        <div className="muted subtitle">
          Consciousness-inspired functional continuity layer — not subjective experience.
        </div>
      </div>

      <div className="head-center">
        <button className="cmd-trigger-btn" onClick={onOpenCommandPalette}>
          <Search size={14} />
          <span>Quick search or command...</span>
          <kbd>Ctrl+K</kbd>
        </button>
      </div>

      <div className="head-right">
        <div className="status-badges">
          <div className="badge runtime" title="Universal Runtime Mode">
            <Cpu size={13} />
            <span>Mode: <b>Hybrid</b></span>
          </div>
          <div className="badge model" title="Active Intelligence Model">
            <Activity size={13} />
            <span>Model: <b>{modelName}</b></span>
          </div>
          <div className="badge memory" title="Active Memory Items">
            <Database size={13} />
            <span>Memories: <b>{memoryCount}</b></span>
          </div>
          <div className="badge safety" title="Safety & Autonomy Policy">
            <Shield size={13} />
            <span>Level: <b>L{autonomyLevel}</b></span>
          </div>
        </div>

        <button className="btn refresh-btn" onClick={onRefresh} title="Refresh System State">
          <RefreshCw size={14} />
        </button>

        <button
          className="px-2.5 py-1.5 bg-red-600/80 hover:bg-red-600 text-white font-semibold text-xs rounded-lg flex items-center gap-1 shadow transition-colors"
          onClick={handleEmergencyStop}
          title="STOP ALL AUTONOMOUS ACTIVITY"
        >
          <AlertOctagon size={13} /> STOP
        </button>
      </div>
    </header>
  );
}
