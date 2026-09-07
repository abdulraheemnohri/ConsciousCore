import React, { useState } from 'react';
import { BookOpen, Search, Plus, GitConflict, CheckCircle, Database } from 'lucide-react';

export function KnowledgePage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [facts] = useState([
    { id: 'fact_001', subject: 'Python', predicate: 'type', object: 'programming_language', confidence: 0.99, verified: true },
    { id: 'fact_002', subject: 'ConsciousCore', predicate: 'architecture', object: 'local_first_cognitive_runtime', confidence: 0.98, verified: true },
    { id: 'fact_003', subject: 'SQLite', predicate: 'storage_mode', object: 'embedded_relational_database', confidence: 0.99, verified: true }
  ]);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Knowledge Engine</h1>
          <p className="text-slate-400 text-sm">Structured Knowledge, Fact Network & Contradiction Resolution</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium">
          <Plus size={16} /> Add Fact
        </button>
      </div>

      <div className="flex gap-4 items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 text-slate-500" size={18} />
          <input
            type="text"
            placeholder="Search knowledge graph (FTS / BM25 / Exact match)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
          <h3 className="font-semibold text-slate-200 flex items-center gap-2 text-sm">
            <BookOpen size={18} className="text-blue-400" /> Fact Triples & Verification
          </h3>
          <span className="text-xs text-slate-400">Total Facts: {facts.length}</span>
        </div>
        <div className="divide-y divide-slate-800">
          {facts.map((fact) => (
            <div key={fact.id} className="p-4 hover:bg-slate-800/30 flex items-center justify-between">
              <div>
                <div className="font-mono text-sm text-slate-200">
                  <span className="text-blue-400 font-semibold">{fact.subject}</span> →{' '}
                  <span className="text-purple-400">{fact.predicate}</span> →{' '}
                  <span className="text-emerald-400 font-semibold">{fact.object}</span>
                </div>
                <div className="text-xs text-slate-500 mt-1">ID: {fact.id} · Source: local://knowledge.json</div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs bg-slate-800 px-2.5 py-1 rounded text-slate-300">
                  Confidence: {(fact.confidence * 100).toFixed(0)}%
                </span>
                {fact.verified && (
                  <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded">
                    <CheckCircle size={14} /> Verified
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
