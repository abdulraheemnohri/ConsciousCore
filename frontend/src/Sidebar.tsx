import React from 'react';
import {
  Activity, MessageSquare, Brain, Zap, Database, Network, UserRound, Target,
  Workflow, BookOpen, LineChart, Box, Layers, Clock3, Shield, Cpu, Sliders,
  Radio, Server, History, Settings
} from 'lucide-react';

export interface NavSection {
  title: string;
  items: {
    name: string;
    icon: React.ComponentType<{ size?: number }>;
  }[];
}

export const navSections: NavSection[] = [
  {
    title: 'Core Workspace',
    items: [
      { name: 'Dashboard', icon: Activity },
      { name: 'Chat Workspace', icon: MessageSquare },
      { name: 'Global Workspace', icon: Brain },
      { name: 'Attention Center', icon: Zap }
    ]
  },
  {
    title: 'Memory & State',
    items: [
      { name: 'Memory', icon: Database },
      { name: 'Memory Federation', icon: Network },
      { name: 'Self Model', icon: UserRound },
      { name: 'World Model', icon: Network },
      { name: 'Internal State', icon: Layers }
    ]
  },
  {
    title: 'Planning & Reasoning',
    items: [
      { name: 'Goals', icon: Target },
      { name: 'Planner', icon: Workflow },
      { name: 'Reasoning', icon: Brain },
      { name: 'Reflection', icon: BookOpen },
      { name: 'Metacognition', icon: Activity },
      { name: 'Prediction', icon: LineChart },
      { name: 'Simulation', icon: Box },
      { name: 'Sleep', icon: Clock3 }
    ]
  },
  {
    title: 'Runtime & AI Engine',
    items: [
      { name: 'Runtime Center', icon: Cpu },
      { name: 'Models', icon: Sliders },
      { name: 'Parallel AI', icon: Radio },
      { name: 'Distributed Nodes', icon: Server }
    ]
  },
  {
    title: 'System & Control',
    items: [
      { name: 'Tools', icon: Box },
      { name: 'Safety', icon: Shield },
      { name: 'Telemetry', icon: LineChart },
      { name: 'Analytics', icon: Activity },
      { name: 'Logs', icon: History },
      { name: 'Developer Console', icon: Settings },
      { name: 'Settings', icon: Settings }
    ]
  }
];

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  autonomyLevel?: number;
}

export function Sidebar({ currentPage, onNavigate, autonomyLevel = 1 }: SidebarProps) {
  return (
    <aside className="side">
      <div className="brand">
        <span className="brandIcon">
          <Brain size={22} />
        </span>
        <div>
          <b>ConsciousCore</b>
          <small>V2.6.0 · Universal Layer</small>
        </div>
      </div>

      <nav className="nav">
        {navSections.map(section => (
          <div key={section.title} className="nav-group">
            <div className="nav-group-title">{section.title}</div>
            {section.items.map(item => {
              const Icon = item.icon;
              const isActive = currentPage === item.name;
              return (
                <button
                  key={item.name}
                  className={`nav-item ${isActive ? 'on' : ''}`}
                  onClick={() => onNavigate(item.name)}
                >
                  <Icon size={16} />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="sideFoot">
        <div className="foot-status">
          <span className="dot online" /> LOCAL-FIRST RUNTIME
        </div>
        <div>Autonomy Level: <b>L{autonomyLevel}</b> (Approval Gated)</div>
        <div className="muted" style={{ fontSize: '0.7rem', marginTop: 4 }}>
          Ctrl+K for Command Palette
        </div>
      </div>
    </aside>
  );
}
