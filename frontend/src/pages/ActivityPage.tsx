import React from 'react';
import { Activity, Clock, Shield, Database, Cpu } from 'lucide-react';

export function ActivityPage() {
  const events = [
    { time: '14:22:01', source: 'User', type: 'chat.message', detail: 'Executed query on local memory graph' },
    { time: '14:20:15', source: 'Native Engine', type: 'skill.discovery', detail: 'Pattern detected in repeated FTS retrieval queries' },
    { time: '14:15:00', source: 'Safety Governor', type: 'safety.check', detail: 'Validated local-only constraint for sensitive query' }
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Unified Activity Timeline</h1>
          <p className="text-slate-400 text-sm">System, User, AI Agent & Cognitive Core Event History</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 font-semibold text-slate-200 text-sm flex items-center gap-2">
          <Clock size={16} className="text-blue-400" /> Recent System Events
        </div>
        <div className="divide-y divide-slate-800 font-mono text-xs">
          {events.map((ev, idx) => (
            <div key={idx} className="p-3.5 hover:bg-slate-800/30 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-slate-500">{ev.time}</span>
                <span className="text-blue-400 font-semibold">{ev.source}</span>
                <span className="text-slate-300">[{ev.type}]</span>
                <span className="text-slate-400">{ev.detail}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
