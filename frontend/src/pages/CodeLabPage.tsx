import React from 'react';
import { Code, ShieldCheck, Terminal, AlertTriangle, CheckCircle } from 'lucide-react';

export function CodeLabPage() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Code Lab & Controlled Self-Improvement</h1>
          <p className="text-slate-400 text-sm">Gated Code Proposals, Static Analysis & Sandbox Execution</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3">
          <div>
            <h3 className="font-semibold text-slate-200">Proposal #CP-204: Add Exponential Backoff to Model HTTP Providers</h3>
            <p className="text-xs text-slate-400">Source: AI Developer Agent · Target: backend/app/runtime/providers_http.py</p>
          </div>
          <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2.5 py-1 rounded">
            Awaiting Approval
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-slate-800/40 rounded-lg flex items-center gap-2 text-emerald-400">
            <CheckCircle size={16} /> Syntax & Static Check: PASSED
          </div>
          <div className="p-3 bg-slate-800/40 rounded-lg flex items-center gap-2 text-emerald-400">
            <ShieldCheck size={16} /> Security Scan: ZERO VULNERABILITIES
          </div>
          <div className="p-3 bg-slate-800/40 rounded-lg flex items-center gap-2 text-blue-400">
            <Terminal size={16} /> Sandbox Unit Tests: 4/4 PASSED
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg">
            Reject Proposal
          </button>
          <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg">
            Approve & Deploy to Sandbox
          </button>
        </div>
      </div>
    </div>
  );
}
