import React from 'react';
import { Users, Bot, Shield, CheckCircle, Plus } from 'lucide-react';

export function AgentsPage() {
  const agents = [
    { id: 'ag_01', name: 'Researcher', role: 'Researcher', status: 'READY', tasks_completed: 42, permissions: 'READ_ONLY' },
    { id: 'ag_02', name: 'Architect', role: 'Architect', status: 'READY', tasks_completed: 18, permissions: 'PROPOSE' },
    { id: 'ag_03', name: 'Developer', role: 'Developer', status: 'IDLE', tasks_completed: 29, permissions: 'SANDBOX_EXEC' },
    { id: 'ag_04', name: 'Security Reviewer', role: 'Security Reviewer', status: 'ACTIVE', tasks_completed: 55, permissions: 'AUDIT' }
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Agent Runtime & Roles</h1>
          <p className="text-slate-400 text-sm">Specialized AI Agents, Memory Scopes & Execution Permissions</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium">
          <Plus size={16} /> Create Agent
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {agents.map((ag) => (
          <div key={ag.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="font-semibold text-slate-100 text-base">{ag.name}</h3>
                <p className="text-xs text-slate-500 font-mono">Role: {ag.role}</p>
              </div>
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-mono">
                {ag.status}
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-400 bg-slate-800/40 p-3 rounded-lg my-3">
              <div>Tasks Completed: <b className="text-slate-200">{ag.tasks_completed}</b></div>
              <div>Permissions: <b className="text-blue-400">{ag.permissions}</b></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
