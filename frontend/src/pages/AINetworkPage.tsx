import React from 'react';
import { Network, Bot, Users, MessageSquare, Play, Pause, ShieldCheck } from 'lucide-react';

export function AINetworkPage() {
  const agents = [
    { name: 'Researcher', role: 'Information Retrieval & Synthesis', status: 'READY', model: 'Local (Llama-3-8B)' },
    { name: 'Architect', role: 'System & Code Design', status: 'IDLE', model: 'Local (GGUF)' },
    { name: 'Developer', role: 'Code Generation & Refactoring', status: 'READY', model: 'Local (GGUF)' },
    { name: 'Critic', role: 'Logical & Security Critique', status: 'IDLE', model: 'Native Core' },
    { name: 'Tester', role: 'Unit & Integration Test Verification', status: 'READY', model: 'Native Core' }
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">AI Communication Bus & Agent Network</h1>
          <p className="text-slate-400 text-sm">Structured AI-to-AI Collaboration, Debate & Consensus Layer</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium">
          <MessageSquare size={16} /> Start AI Session
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {agents.map((ag) => (
          <div key={ag.name} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                  <Bot size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-100">{ag.name}</h3>
                  <p className="text-xs text-slate-500">{ag.model}</p>
                </div>
              </div>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-mono">
                {ag.status}
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-4">{ag.role}</p>
            <div className="pt-3 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
              <span className="flex items-center gap-1 text-emerald-400">
                <ShieldCheck size={14} /> Gated Sandbox
              </span>
              <button className="hover:text-slate-200">Configure</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
