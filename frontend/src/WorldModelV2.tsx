import React,{useEffect,useState}from'react';
import './world-model-v2.css';

type World={entities:any[];relations:any[];events:any[];beliefs:any[];contradictions:any[];uncertainty:number};
const API=import.meta.env.VITE_API_URL||'http://127.0.0.1:8000';
export default function WorldModelV2(){
 const[w,setW]=useState<World>({entities:[],relations:[],events:[],beliefs:[],contradictions:[],uncertainty:0}); const[q,setQ]=useState(''); const[loading,setLoading]=useState(true);
 const load=async()=>{setLoading(true);try{const r=await fetch(`${API}/api/world`);setW(await r.json())}finally{setLoading(false)}};
 useEffect(()=>{load()},[]);
 const query=async()=>{if(!q.trim())return load();const r=await fetch(`${API}/api/world/query?q=${encodeURIComponent(q)}`);const x=await r.json();setW({...w,...x})};
 return <section className="wm2">
  <header className="wm2-head"><div><span className="eyebrow">WORLD MODEL V2</span><h1>World representation</h1><p>Entities, relationships, events and uncertain beliefs in a persistent local model.</p></div><button onClick={load}>↻ Refresh</button></header>
  <div className="wm2-stats"><div><b>{w.entities.length}</b><span>Entities</span></div><div><b>{w.relations.length}</b><span>Relations</span></div><div><b>{w.events.length}</b><span>Events</span></div><div><b>{w.beliefs.length}</b><span>Beliefs</span></div><div><b>{w.contradictions.length}</b><span>Conflicts</span></div></div>
  <div className="wm2-search"><input value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==='Enter'&&query()} placeholder="Search entities, relations, beliefs…"/><button onClick={query}>Search</button></div>
  <div className="wm2-grid">
   <article><h2>Entity graph</h2><div className="graph">{w.entities.length===0?<div className="empty">No world entities yet.</div>:w.entities.map((e,i)=><div className="node" key={e.id} style={{left:`${12+(i*23)%76}%`,top:`${20+(i*31)%58}%`}}><strong>{e.label}</strong><small>{e.kind} · {(e.confidence*100).toFixed(0)}%</small></div>)}</div></article>
   <article><h2>Relationships</h2><div className="list">{w.relations.slice(0,12).map((r:any)=><div className="row" key={r.id}><span>{r.source}</span><b>→ {r.relation} →</b><span>{r.target}</span><em>{(r.confidence*100).toFixed(0)}%</em></div>)}{!w.relations.length&&<div className="empty">No relationships yet.</div>}</div></article>
   <article><h2>Beliefs & uncertainty</h2><div className="list">{w.beliefs.slice(0,10).map((b:any)=><div className="belief" key={b.id}><div><strong>{b.statement}</strong><small>{b.status}</small></div><span>{(b.confidence*100).toFixed(0)}%</span></div>)}{!w.beliefs.length&&<div className="empty">No beliefs recorded.</div>}</div><div className="uncertainty">Aggregate confidence signal: <b>{(w.uncertainty*100).toFixed(0)}%</b></div></article>
   <article><h2>Contradictions</h2><div className="list">{w.contradictions.slice(0,10).map((c:any,i)=><div className="conflict" key={i}><b>{c.type}</b><span>{c.left.relation} ↔ {c.right.relation}</span><small>uncertainty {(c.uncertainty*100).toFixed(0)}%</small></div>)}{!w.contradictions.length&&<div className="empty">No detected relation conflicts.</div>}</div></article>
  </div>
  <footer>World Model V2 stores computational representations; confidence is epistemic metadata, not objective truth or evidence of consciousness.{loading?' Loading…':''}</footer>
 </section>
}
