import { useEffect, useState } from 'react'
import './global-workspace-v2.css'

type Candidate = { id:string; source:string; content:string; salience:number; confidence:number; urgency:number; novelty:number; relevance:number; score:number; selected:boolean }
type Snapshot = { cycle_id:string; current:Candidate|null; candidates:Candidate[]; subscribers:string[]; interrupted:boolean; history:any[]; weights:Record<string,number>; scientific_note:string }

const API = import.meta.env.VITE_API_URL || ''
const pct=(v:number)=>`${Math.round(v*100)}%`
const Metric=({label,value}:{label:string,value:number})=><div className="gw-metric"><div><span>{label}</span><b>{pct(value)}</b></div><div className="gw-bar"><i style={{width:pct(value)}} /></div></div>

export default function GlobalWorkspaceV2(){
  const [data,setData]=useState<Snapshot|null>(null); const [loading,setLoading]=useState(true); const [error,setError]=useState(''); const [source,setSource]=useState('user'); const [content,setContent]=useState('')
  const load=async()=>{try{setLoading(true);const r=await fetch(`${API}/api/workspace/v2`);if(!r.ok)throw new Error('Workspace unavailable');setData(await r.json());setError('')}catch(e:any){setError(e.message)}finally{setLoading(false)}}
  useEffect(()=>{load();const id=setInterval(load,2000);return()=>clearInterval(id)},[])
  const submit=async()=>{if(!content.trim())return;await fetch(`${API}/api/workspace/v2/candidates`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source,content})});setContent('');load()}
  if(loading&&!data)return <section className="gw-shell"><div className="gw-loading">Loading Global Workspace V2…</div></section>
  return <section className="gw-shell">
    <header className="gw-header"><div><span className="gw-kicker">CONSCIOUSCORE V6</span><h2>Global Workspace</h2><p>Computational attention competition and global broadcast coordination.</p></div><button onClick={load}>↻ Refresh</button></header>
    {error&&<div className="gw-error">{error}</div>}
    <div className="gw-grid">
      <article className="gw-hero"><span>GLOBAL BROADCAST</span>{data?.current?<><h3>{data.current.content}</h3><p>{data.current.source} · score {pct(data.current.score)}</p><div className="gw-metrics"><Metric label="Salience" value={data.current.salience}/><Metric label="Confidence" value={data.current.confidence}/><Metric label="Urgency" value={data.current.urgency}/><Metric label="Novelty" value={data.current.novelty}/><Metric label="Relevance" value={data.current.relevance}/></div></>:<h3>No winner selected</h3>}</article>
      <article className="gw-panel"><div className="gw-panel-title"><h3>Submit candidate</h3><span>attention competition</span></div><input value={source} onChange={e=>setSource(e.target.value)} placeholder="source/module"/><textarea value={content} onChange={e=>setContent(e.target.value)} placeholder="Information competing for workspace access…"/><button className="gw-primary" onClick={submit}>Submit to workspace</button></article>
    </div>
    <div className="gw-grid lower"><article className="gw-panel"><div className="gw-panel-title"><h3>Candidate competition</h3><span>{data?.candidates.length||0} active</span></div>{data?.candidates.map(c=><div className={`gw-candidate ${c.selected?'selected':''}`} key={c.id}><div className="gw-candidate-top"><b>{c.source}</b><strong>{pct(c.score)}</strong></div><p>{c.content}</p><div className="gw-mini"><span>S {pct(c.salience)}</span><span>U {pct(c.urgency)}</span><span>N {pct(c.novelty)}</span><span>R {pct(c.relevance)}</span></div></div>)}</article>
      <article className="gw-panel"><div className="gw-panel-title"><h3>Subscribers</h3><span>{data?.subscribers.length||0} modules</span></div><div className="gw-subs">{data?.subscribers.map(s=><span key={s}>{s}</span>)}{!data?.subscribers.length&&<em>No module subscriptions</em>}</div><div className={`gw-interrupt ${data?.interrupted?'active':''}`}>⚡ Interruption: {data?.interrupted?'ACTIVE':'clear'}</div><h3 className="gw-history-title">Broadcast history</h3>{data?.history.slice(0,8).map((h:any)=><div className="gw-history" key={h.id}><span>{new Date(h.created_at*1000).toLocaleTimeString()}</span><b>{h.candidate_id}</b></div>)}</article>
    </div>
    <footer className="gw-note">{data?.scientific_note||'This is a computational coordination mechanism, not evidence of subjective consciousness.'}</footer>
  </section>
}
