import React, { useState } from 'react';
import { Cpu, Play, Plus, RefreshCw, CheckCircle, ShieldAlert, Award } from 'lucide-react';

export function SkillsPage() {
  const [skills] = useState([
    {
      id: 'skill_001',
      name: 'System Diagnostic Check',
      category: 'system',
      version: '1.0.0',
      state: 'ACTIVE',
      success_rate: 1.0,
      confidence: 0.98,
      last_used: 'Just now'
    },
    {
      id: 'skill_002',
      name: 'FTS Memory Retrieval',
      category: 'knowledge',
      version: '1.2.0',
      state: 'ACTIVE',
      success_rate: 0.95,
      confidence: 0.94,
      last_used: '5 mins ago'
    },
    {
      id: 'skill_003',
      name: 'Candidate Procedure Synthesizer',
      category: 'learned',
      version: '0.9.0',
      state: 'OPTIMIZED',
      success_rate: 0.91,
      confidence: 0.89,
      last_used: '1 hour ago'
    }
  ]);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Self Skill Engine</h1>
          <p className="text-slate-400 text-sm">Autonomous Skill Registry, Procedure Execution & Lifecycle Management</p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium">
            <Plus size={16} /> Discover Skill
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {skills.map((skill) => (
          <div key={skill.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors">
            <div className="flex justify-between items-start mb-3">
              <span className="text-xs font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded">
                {skill.category.toUpperCase()}
              </span>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                skill.state === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
              }`}>
                {skill.state}
              </span>
            </div>

            <h3 className="font-semibold text-slate-100 text-base mb-1">{skill.name}</h3>
            <p className="text-xs text-slate-500 font-mono mb-4">ID: {skill.id} · v{skill.version}</p>

            <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 bg-slate-800/40 p-3 rounded-lg mb-4">
              <div>Success Rate: <b className="text-slate-200">{(skill.success_rate * 100).toFixed(0)}%</b></div>
              <div>Confidence: <b className="text-slate-200">{(skill.confidence * 100).toFixed(0)}%</b></div>
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-800">
              <span>Last: {skill.last_used}</span>
              <button className="flex items-center gap-1 text-blue-400 hover:text-blue-300 font-medium">
                <Play size={12} /> Execute
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
