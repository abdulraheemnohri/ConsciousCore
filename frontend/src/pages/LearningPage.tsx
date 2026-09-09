import React from 'react';
import { Brain, Sparkles, AlertCircle, CheckCircle, Flame, ArrowUpRight } from 'lucide-react';

export function LearningPage() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Self Learning Engine</h1>
          <p className="text-slate-400 text-sm">Experience Evaluation, Lesson Extraction & Failure Adaptation</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1.5 rounded-lg font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Auto-Learning Active
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs font-medium">New Facts Learned</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">14</div>
          <div className="text-xs text-emerald-400 mt-1 flex items-center gap-0.5"><ArrowUpRight size={12} /> +3 today</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs font-medium">Discovered Skills</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">6</div>
          <div className="text-xs text-blue-400 mt-1">2 candidates in validation</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs font-medium">Failures Learned From</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">8</div>
          <div className="text-xs text-purple-400 mt-1">Rules updated</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="text-slate-400 text-xs font-medium">Idle Cognition Yield</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">98%</div>
          <div className="text-xs text-emerald-400 mt-1">High confidence</div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        <h3 className="font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <Sparkles size={18} className="text-amber-400" /> Recent Lessons & Skill Proposals
        </h3>
        <div className="space-y-3">
          <div className="p-3 bg-slate-800/40 border border-slate-800 rounded-lg flex items-start gap-3">
            <CheckCircle className="text-emerald-400 shrink-0 mt-0.5" size={18} />
            <div>
              <div className="text-sm font-medium text-slate-200">Fact Extraction from Local Document</div>
              <p className="text-xs text-slate-400 mt-0.5">Lesson: FTS5 BM25 search yields higher relevance than plain keyword search for technical queries.</p>
            </div>
          </div>
          <div className="p-3 bg-slate-800/40 border border-slate-800 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-amber-400 shrink-0 mt-0.5" size={18} />
            <div>
              <div className="text-sm font-medium text-slate-200">Failure Adaptation: High RAM Workload</div>
              <p className="text-xs text-slate-400 mt-0.5">Lesson: Throttle background AI-to-AI sessions when RAM threshold exceeds 85%.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
