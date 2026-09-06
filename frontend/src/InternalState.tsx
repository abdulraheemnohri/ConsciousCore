import React,{useEffect,useState}from'react';
import{Activity,RefreshCw,ShieldAlert,Zap}from'lucide-react';

const API=import.meta.env.VITE_API_URL||'http://127.0.0.1:8000';
const fields=[['energy','Energy'],['arousal','Arousal'],['attention_load','Attention Load'],['stress','Stress'],['uncertainty','Uncertainty'],['confidence','Confidence'],['stability','Stability'],['valence','Valence']];

export default function InternalState(){
 const[data,setData]=useState<any>({state:{},status:'unknown'}); const[busy,setBusy]=useState(false);
 const load=()=>fetch(API+'/api/internal-state').then(r=>r.json()).then(setData).catch(()=>{});
 useEffect(()=>{load();const t=setInterval(load,2500);return()=>clearInterval(t)},[]);
 const recover=async()=>{setBusy(true);try{await fetch(API+'/api/internal-state/recover',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:.1})});await load()}finally{setBusy(false)}};
 const s=data.state||{};
 return <div className="statePage">
  <section className="goalHero panel"><div><div className="eyebrow">INTERNAL STATE ENGINE</div><h2>Internal State</h2><p>Inspectable runtime variables used by the cognitive architecture; these values are computational state, not subjective feelings.</p></div><button className="secondaryBtn" onClick={recover} disabled={busy}>{busy?<RefreshCw className="spin" size={14}/>:<Zap size={14}/>} Recover energy</button></section>
  <section className="stateBanner panel"><div><span className="live"/> Current state: <strong>{data.status}</strong></div><small>Persisted locally in SQLite · updates during cognitive cycles</small></section>
  <section className="stateGrid">{fields.map(([key,label])=>{const v=Number(s[key]??0);const display=key==='valence'?Math.round(v*100)+'%':Math.round(v*100)+'%';return <div className="stateMetric panel" key={key}><div className="stateMetricHead"><span>{label}</span><strong>{display}</strong></div><div className="progress"><i style={{width:(key==='valence'?(v+1)/2:v)*100+'%'}}/></div><small>{key.replace('_',' ')}</small></div>})}</section>
  <section className="dashboardGrid"><div className="panel"><div className="panelTitle"><h2>State Interpretation</h2><Activity size={15}/></div><div className="stateRows"><div><span>Stability</span><b>{Math.round((s.stability??0)*100)}%</b></div><div><span>Cognitive load</span><b>{Math.round((s.attention_load??0)*100)}%</b></div><div><span>Stress</span><b>{Math.round((s.stress??0)*100)}%</b></div><div><span>Confidence</span><b>{Math.round((s.confidence??0)*100)}%</b></div></div></div><div className="panel"><div className="panelTitle"><h2>Safety Boundary</h2><ShieldAlert size={15}/></div><p className="safetyNote">Internal-state transitions do not grant external authority. System, browser, credential, authentication and destructive actions remain subject to the existing safety and approval layer.</p></div></section>
 </div>
}
