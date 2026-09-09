import React from 'react';
import { Cpu, HardDrive, Zap, Server, Activity, Thermometer } from 'lucide-react';

export function SystemPage() {
  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">System Diagnostics & Hardware Telemetry</h1>
          <p className="text-slate-400 text-sm">Real-time CPU, RAM, Disk, Temperature & Diagnostic Checks</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>CPU Load</span> <Cpu size={16} className="text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">12%</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>RAM Usage</span> <Server size={16} className="text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">4.2 GB / 16 GB</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>SQLite Database</span> <HardDrive size={16} className="text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">18.4 MB</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Core Temp</span> <Thermometer size={16} className="text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">42°C</div>
        </div>
      </div>
    </div>
  );
}
