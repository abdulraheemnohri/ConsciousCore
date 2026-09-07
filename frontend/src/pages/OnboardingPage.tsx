import React from 'react';
import { Shield, Database, Cpu, Lock, CheckCircle2 } from 'lucide-react';

export function OnboardingPage() {
  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
            <Cpu size={28} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Welcome to ConsciousCore V1</h1>
            <p className="text-slate-400 text-sm">Local-First Cognitive Operating System Setup</p>
          </div>
        </div>
        <p className="text-slate-300 leading-relaxed mb-6">
          ConsciousCore is built as a local-first cognitive runtime that operates with or without AI models.
          Your data, memory, self-model, and skills remain strictly local and under complete human control.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-6">
          <div className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 font-semibold text-slate-200 mb-2">
              <Shield className="text-emerald-400" size={18} /> Mode: NATIVE_ONLY
            </div>
            <p className="text-xs text-slate-400">Model-free deterministic processing using rules, knowledge lookup, state machines, and FTS search.</p>
          </div>
          <div className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 font-semibold text-slate-200 mb-2">
              <Database className="text-blue-400" size={18} /> Mode: HYBRID (Recommended)
            </div>
            <p className="text-xs text-slate-400">Combines local deterministic cognitive core with local GGUF/llama.cpp inference models.</p>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex justify-between items-center">
          <div className="flex items-center gap-2 text-xs text-emerald-400">
            <CheckCircle2 size={16} /> Local Vault Initialized (SQLite)
          </div>
          <button className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm rounded-lg transition-colors">
            Initialize Workspace
          </button>
        </div>
      </div>
    </div>
  );
}
