import React from 'react';
import { Box, Play, CheckCircle, XCircle, Clock } from 'lucide-react';

export function ExperimentsPage() {
  const experiments = [
    { id: 'exp_01', objective: 'Benchmark FTS5 vs Vector Retrieval Latency', status: 'PASSED', metric: '1.2ms avg retrieval' },
    { id: 'exp_02', objective: 'Test Self-Skill Discovery on repeated task logs', status: 'RUNNING', metric: '2 candidate skills generated' }
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Experiment Lab</h1>
          <p className="text-slate-400 text-sm">Hypothesis Testing, Controlled Benchmarking & Empirical Validation</p>
        </div>
      </div>

      <div className="space-y-4">
        {experiments.map((exp) => (
          <div key={exp.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs text-slate-500">{exp.id}</span>
                <h3 className="font-semibold text-slate-200 text-base">{exp.objective}</h3>
              </div>
              <p className="text-xs text-slate-400">Metric Output: {exp.metric}</p>
            </div>
            <span className={`text-xs px-3 py-1 rounded font-medium ${
              exp.status === 'PASSED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
            }`}>
              {exp.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
