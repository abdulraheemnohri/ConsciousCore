import React, { useState, useEffect } from 'react';
import { Search, Brain, Database, Shield, Sliders, Target, Workflow, Network, Layers, Activity, MessageSquare, Zap, BookOpen, UserRound, Clock3, Box, Settings, History, HelpCircle, Server, Radio, Cpu, LineChart, AlertTriangle } from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (page: string) => void;
}

export const commands = [
  { name: 'Dashboard', page: 'Dashboard', icon: Activity, category: 'Main' },
  { name: 'Chat Workspace', page: 'Chat Workspace', icon: MessageSquare, category: 'Main' },
  { name: 'Global Workspace', page: 'Global Workspace', icon: Brain, category: 'Cognition' },
  { name: 'Attention Center', page: 'Attention Center', icon: Zap, category: 'Cognition' },
  { name: 'Memory Center', page: 'Memory', icon: Database, category: 'Memory' },
  { name: 'Memory Federation', page: 'Memory Federation', icon: Network, category: 'Memory' },
  { name: 'Self Model', page: 'Self Model', icon: UserRound, category: 'Cognition' },
  { name: 'World Model', page: 'World Model', icon: Network, category: 'Cognition' },
  { name: 'Goals', page: 'Goals', icon: Target, category: 'Planning' },
  { name: 'Planner', page: 'Planner', icon: Workflow, category: 'Planning' },
  { name: 'Reasoning Center', page: 'Reasoning', icon: Brain, category: 'Cognition' },
  { name: 'Reflection', page: 'Reflection', icon: BookOpen, category: 'Cognition' },
  { name: 'Metacognition', page: 'Metacognition', icon: Activity, category: 'Cognition' },
  { name: 'Prediction', page: 'Prediction', icon: LineChart, category: 'Cognition' },
  { name: 'Imagination / Simulation', page: 'Simulation', icon: Box, category: 'Cognition' },
  { name: 'Internal State', page: 'Internal State', icon: Layers, category: 'Cognition' },
  { name: 'Sleep / Consolidation', page: 'Sleep', icon: Clock3, category: 'Memory' },
  { name: 'Tool Center', page: 'Tools', icon: Box, category: 'System' },
  { name: 'Safety Center', page: 'Safety', icon: Shield, category: 'System' },
  { name: 'Runtime Center', page: 'Runtime Center', icon: Cpu, category: 'Runtime' },
  { name: 'Model Manager', page: 'Models', icon: Sliders, category: 'Runtime' },
  { name: 'Parallel AI', page: 'Parallel AI', icon: Radio, category: 'Runtime' },
  { name: 'Distributed Nodes', page: 'Distributed Nodes', icon: Server, category: 'Runtime' },
  { name: 'Telemetry Center', page: 'Telemetry', icon: LineChart, category: 'System' },
  { name: 'Analytics', page: 'Analytics', icon: Activity, category: 'System' },
  { name: 'Logs', page: 'Logs', icon: History, category: 'System' },
  { name: 'Developer Console', page: 'Developer Console', icon: Settings, category: 'System' },
  { name: 'Settings', page: 'Settings', icon: Settings, category: 'System' }
];

export function CommandPalette({ isOpen, onClose, onNavigate }: CommandPaletteProps) {
  const [query, setQ] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  if (!isOpen) return null;

  const filtered = commands.filter(c =>
    c.name.toLowerCase().includes(query.toLowerCase()) ||
    c.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleSelect = (page: string) => {
    onNavigate(page);
    onClose();
    setQ('');
  };

  const handleKeyDownModal = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev + 1) % (filtered.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev - 1 + filtered.length) % (filtered.length || 1));
    } else if (e.key === 'Enter' && filtered[selectedIndex]) {
      e.preventDefault();
      handleSelect(filtered[selectedIndex].page);
    }
  };

  return (
    <div className="cmd-overlay" onClick={onClose}>
      <div className="cmd-modal" onClick={e => e.stopPropagation()} onKeyDown={handleKeyDownModal}>
        <div className="cmd-header">
          <Search size={18} className="cmd-icon" />
          <input
            autoFocus
            className="cmd-input"
            value={query}
            onChange={e => setQ(e.target.value)}
            placeholder="Type a command or search pages... (Press Esc to close)"
          />
        </div>
        <div className="cmd-list">
          {filtered.length === 0 ? (
            <div className="cmd-empty">No matching commands found.</div>
          ) : (
            filtered.map((cmd, index) => {
              const Icon = cmd.icon;
              return (
                <div
                  key={cmd.name}
                  className={`cmd-item ${index === selectedIndex ? 'selected' : ''}`}
                  onClick={() => handleSelect(cmd.page)}
                  onMouseEnter={() => setSelectedIndex(index)}
                >
                  <Icon size={16} />
                  <span className="cmd-name">{cmd.name}</span>
                  <span className="cmd-category">{cmd.category}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
