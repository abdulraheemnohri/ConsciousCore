import React from 'react';
import { Shield, Lock, EyeOff, AlertOctagon, Key } from 'lucide-react';

export function SecurityPage() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Security Governor & Privacy Zones</h1>
          <p className="text-slate-400 text-sm">Least-Privilege Enforcement, Vault Protection & Emergency Lockdown</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-red-600/80 hover:bg-red-600 text-white rounded-lg text-sm font-semibold shadow-lg shadow-red-900/30">
          <AlertOctagon size={16} /> EMERGENCY LOCKDOWN
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="font-semibold text-slate-200 mb-3 flex items-center gap-2">
            <Lock size={18} className="text-blue-400" /> Privacy Zones & Data Routing
          </h3>
          <div className="space-y-2 text-xs">
            <div className="p-2.5 bg-slate-800/40 rounded flex justify-between">
              <span className="text-slate-300">SENSITIVE / SECRET Data</span>
              <span className="text-emerald-400 font-mono">LOCAL_ONLY (Enforced)</span>
            </div>
            <div className="p-2.5 bg-slate-800/40 rounded flex justify-between">
              <span className="text-slate-300">Cloud Model Exfiltration</span>
              <span className="text-red-400 font-mono">DISABLED</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h3 className="font-semibold text-slate-200 mb-3 flex items-center gap-2">
            <Key size={18} className="text-amber-400" /> Secret Vault & Credentials
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Secrets and API tokens are stored in the local encrypted OS vault. Plaintext credentials are redacted from logs and audit trails automatically.
          </p>
        </div>
      </div>
    </div>
  );
}
