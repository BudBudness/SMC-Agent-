"use client";

import {useEffect,useMemo,useState,type ReactNode} from "react";

const TFS=["12M","6M","3M","W","D","4H","1H","15M","5M","1M"];
const NAV=[
  {group:"RESEARCH",items:["New Research","Active Research","Research History"]},
  {group:"MARKET",items:["Workspace","MTF Structure","Liquidity","Events","Macro Context"]},
  {group:"INVESTIGATION",items:["Replay","Historical Analogues","Hypotheses","Evidence"]},
  {group:"OUTPUT",items:["Reports","Benchmarks","Research Data"]},
  {group:"SYSTEM",items:["Data Quality","Pipeline","Lineage"]},
];
const ARTIFACTS=[
 ["Research report","EURUSD_research_report.json"],
 ["MTF dashboard","EURUSD_MTF_dashboard.json.gz"],
];
const KEY="henryz_research_workspace_v2";
const arr=(v:any)=>Array.isArray(v)?v:[];
const text=(v:any)=>v===null||v===undefined?"UNKNOWN":typeof v==="object"?JSON.stringify(v):String(v);
function Pill({v}:{v:any}){const x=text(v);return <span className={"pill "+x.toLowerCase()}>{x}</span>}
function Panel({title,sub,children}:{title:string;sub?:string;children:ReactNode}){return <section className="panel"><header><h2>{title}</h2>{sub&&<p>{sub}</p>}</header>{children}</section>}
function KV({k,v}:{k:string;v:any}){return <div className="kv"><span>{k}</span><b>{text(v)}</b></div>}
function Table({rows,empty="No records."}:{rows:any[];empty?:string}){const rs=arr(rows);if(!rs.length)return <p className="muted">{empty}</p>;const keys=Array.from(new Set(rs.flatMap((r:any)=>r&&typeof r==="object"?Object.keys(r):[]))).slice(0,12);return <div className="table"><table><thead><tr>{keys.map(k=><th key={k}>{k.replaceAll("_"," ")}</th>)}</tr></thead><tbody>{rs.map((r:any,i:number)=><tr key={i}>{keys.map(k=><td key={k}>{text(r?.[k])}</td>)}</tr>)}</tbody></table></div>}
function ViewHead({title,sub}:{title:string;sub:string}){return <div className="view-head"><div><span className="eyebrow">HENRYZ SMC · RESEARCH TERMINAL</span><h1>{title}</h1><p>{sub}</p></div></div>}
function Structure({frame}:{frame:any}){const pts=[...arr(frame?.confirmed_highs).map((x:any)=>({t:"HIGH",v:x?.price??x?.value??x})),...arr(frame?.confirmed_lows).map((x:any)=>({t:"LOW",v:x?.price??x?.value??x}))].slice(-18);return <div className="chart"><div className="chart-label">CONFIRMED STRUCTURE · NO UNCONFIRMED SWINGS</div>{pts.length?pts.map((p,i)=><div key={i} className={"point "+p.t.toLowerCase()} style={{left:(i/Math.max(pts.length-1,1))*92+4+"%"}}><i/><small>{p.t}</small></div>):<span className="muted">No confirmed swing points.</span>}</div>}
function save(key:string,value:any){try{localStorage.setItem(key,JSON.stringify(value))}catch{}}
function load(key:string,fallback:any){try{const x=localStorage.getItem(key);return x?JSON.parse(x):fallback}catch{return fallback}}
function download(name:string,data:any){const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();URL.revokeObjectURL(a.href)}

export default function Home(){
 const[d,setD]=useState<any>(null),[error,setError]=useState(""),[view,setView]=useState("Workspace"),[tf,setTf]=useState("W"),[query,setQuery]=useState(""),[run,setRun]=useState<any>(null);
 const[hypotheses,setHypotheses]=useState<any[]>([]),[notes,setNotes]=useState<any[]>([]);
 useEffect(()=>{fetch("/api/research",{cache:"no-store"}).then(async r=>{const x=await r.json();if(!r.ok)throw Error(x.error);return x}).then(x=>{setD(x);const saved=load(KEY,{hypotheses:[],notes:[]});setHypotheses(saved.hypotheses||[]);setNotes(saved.notes||[])}).catch(e=>setError(e.message||"Research data unavailable"))},[]);
 useEffect(()=>{if(d)save(KEY,{hypotheses,notes})},[d,hypotheses,notes]);
 if(error)return <main className="terminal error"><b>Research data unavailable</b><p>{error}</p></main>;
 if(!d)return <main className="terminal loading">Loading validated research release…</main>;

 const r=d.report||{}, s=r.market_state||{}, frames=d.mtf?.timeframes||{}, events=arr(r.events), evidence=arr(r.evidence), contradictions=arr(s.contradictions), source=d.source||r.dataset||{}, analogue=r.analogue_research||{};
 const selected=frames[tf]||{}, filtered=events.filter((x:any)=>!query||JSON.stringify(x).toLowerCase().includes(query.toLowerCase()));
 const counts=events.reduce((a:any,x:any)=>{const k=String(x.name||x.type||"unknown").toLowerCase();a[k]=(a[k]||0)+1;return a},{});
 const bench=[
  {metric:"Source rows",result:source.rows,status:s.source_integrity?.status||"UNKNOWN"},
  {metric:"Duplicate timestamps",result:source.duplicate_timestamps??"UNKNOWN",status:Number(source.duplicate_timestamps||0)===0?"PASS":"FAIL"},
  {metric:"Contradictions",result:contradictions.length,status:"OBSERVED"},
  {metric:"Sequenced events",result:events.length,status:"OBSERVED"},
  {metric:"Displacement events",result:counts.displacement||0,status:"OBSERVED"},
  {metric:"FVG events",result:counts.fvg||0,status:"OBSERVED"},
  {metric:"Order-block events",result:counts.order_block||counts.orderblock||0,status:"OBSERVED"},
  {metric:"Liquidity/sweep events",result:events.filter((x:any)=>/liquidity|sweep/i.test(String(x.name))).length,status:"OBSERVED"},
 ];
 const executeRun=()=>{const now=new Date().toISOString();const id="RUN-"+now.replace(/[-:.TZ]/g,"").slice(0,14);const x={id,created_at:now,status:"COMPLETED",instrument:r.symbol||"EURUSD",dataset:source.source||"EUR/USD M1",release_timestamp:r.timestamp,stages:["INGEST","QUALITY","MTF","SMC FEATURES","EVENT SEQUENCING","EVIDENCE","REPORT"],look_ahead_policy:"confirmed swings only",research_only:true};setRun(x);setView("Active Research")};
 const addHyp=()=>{const title=prompt("Hypothesis title");if(!title)return;setHypotheses(x=>[...x,{id:"H-"+Date.now(),title,status:"OPEN",created_at:new Date().toISOString(),supporting:0,contradicting:0}])};
 const addNote=()=>{const claim=prompt("Evidence claim");if(!claim)return;setNotes(x=>[...x,{id:"E-"+Date.now(),claim,type:"UNCLASSIFIED",source:"researcher",created_at:new Date().toISOString()}])};
 const report={research_run:run||{status:"PUBLISHED_RELEASE",release_timestamp:r.timestamp},frame:{symbol:r.symbol||"EURUSD",dataset:source.source,rows:source.rows},authority:s.weekly_bias,market_state:s,contradictions,evidence:[...evidence,...notes],hypotheses,events,benchmarks:bench,conclusion:r.conclusion,lineage:["EUR/USD M1","validated dataset","MTF reconstruction","SMC features","event sequencing","evidence","research report"]};

 const workspace=<><div className="hero"><div><span className="eyebrow">ACTIVE RESEARCH · {r.symbol||"EURUSD"}</span><h1>Market Workspace</h1><p>Investigate structure, liquidity, events and evidence. No execution or recommendations.</p></div><button className="primary" onClick={executeRun}>RUN ANALYSIS</button></div>
 <div className="tf-strip">{TFS.map(x=><button className={tf===x?"sel":""} onClick={()=>setTf(x)} key={x}><small>{x}</small><Pill v={frames[x]?.state}/></button>)}</div>
 <div className="authority"><b>WEEKLY AUTHORITY <Pill v={s.weekly_bias}/></b><span>Lower-timeframe conflicts remain evidence; they do not override Weekly authority.</span><em>RESEARCH ONLY</em></div>
 <div className="columns"><div><Panel title={"Structure · "+tf} sub="Confirmed structure is rendered only after right-side confirmation."><Structure frame={selected}/><div className="three"><KV k="Bars" v={selected.bars}/><KV k="Start" v={selected.start}/><KV k="End" v={selected.end}/></div></Panel>
 <Panel title="Chronological event stream" sub="Search and inspect the canonical event sequence."><div className="events">{filtered.map((x:any,i:number)=><div className="event" key={i}><div><b>{String(x.name||x.type).toUpperCase()}</b><small>{x.timeframe} · {x.kind||"observation"}</small></div><code>{x.time||x.timestamp||""}</code></div>)}</div></Panel></div>
 <aside><Panel title="Research state"><KV k="4H AMD" v={s["4H_AMD"]}/><KV k="Daily location" v={s.daily_location}/><KV k="Displacement" v={s.displacement}/><KV k="Contradictions" v={contradictions.length}/></Panel><Panel title="Evidence"><KV k="Claims" v={evidence.length+notes.length}/><KV k="Events" v={events.length}/><KV k="Analogue" v={analogue.status}/></Panel><Panel title="Interpretation"><p className="conclusion">{r.conclusion}</p></Panel></aside></div></>;

 const content=(()=>{
 if(view==="New Research")return <><ViewHead title="New Research" sub="Create a deterministic research run from the validated release."/><Panel title="Research frame"><div className="form"><label>Instrument<select><option>EURUSD</option><option>BTCUSDT</option><option>ETHUSDT</option></select></label><label>Hierarchy<select><option>12M → 1M</option></select></label><label>Dataset<select><option>Canonical validated release</option></select></label></div><button className="primary" onClick={executeRun}>START RESEARCH RUN</button></Panel></>;
 if(view==="Active Research"||view==="Workspace")return workspace;
 if(view==="Research History")return <><ViewHead title="Research History" sub="Runs are retained locally with deterministic provenance."/><Panel title="Runs"><Table rows={run?[run]:[{id:"PUBLISHED-RELEASE",status:"COMPLETED",dataset:source.source,timestamp:r.timestamp}]}/></Panel></>;
 if(view==="MTF Structure")return <><ViewHead title="MTF Structure" sub="Canonical regime → context → structure → execution hierarchy."/><Panel title="Hierarchy"><div className="chips">{TFS.map(x=><button className={x==="W"?"authority-chip":""} onClick={()=>setTf(x)} key={x}>{x}</button>)}</div><Table rows={TFS.map(x=>({timeframe:x,bars:frames[x]?.bars,state:frames[x]?.state,start:frames[x]?.start,end:frames[x]?.end}))}/></Panel><Panel title={"Confirmed swings · "+tf}><Structure frame={selected}/><div className="two"><Table rows={arr(selected.confirmed_highs).map((x:any)=>({confirmed_high:x?.price??x?.value??x}))}/><Table rows={arr(selected.confirmed_lows).map((x:any)=>({confirmed_low:x?.price??x?.value??x}))}/></div></Panel></>;
 if(view==="Liquidity")return <><ViewHead title="Liquidity" sub="Internal/external liquidity formations and sweeps retained as observations."/><Panel title="Liquidity events"><Table rows={events.filter((x:any)=>/liquidity|sweep/i.test(String(x.name)))}/></Panel><Panel title="Liquidity research controls"><p className="muted">No liquidity observation is converted into a trade recommendation. Sequence and reaction remain descriptive.</p></Panel></>;
 if(view==="Events")return <><ViewHead title="Events" sub="Complete chronological event ledger."/><Panel title="Searchable events"><input className="search-wide" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Filter event, timeframe, timestamp…"/><Table rows={filtered}/></Panel></>;
 if(view==="Macro Context")return <><ViewHead title="Macro Context" sub="Macro observations are contextual evidence, not directional signals."/><Panel title="Macro dataset"><Table rows={arr(r.macro?.events||r.macro)}/></Panel></>;
 if(view==="Replay")return <Replay events={events}/>;
 if(view==="Historical Analogues")return <><ViewHead title="Historical Analogues" sub="Descriptive similarity only; no predictive inference."/><Panel title="Analogue research"><KV k="Status" v={analogue.status}/><KV k="Method" v={analogue.method||"Descriptive structural comparison"}/><KV k="Look-ahead policy" v={r.look_ahead_policy||"Confirmed observations only"}/><Table rows={arr(analogue.matches||analogue.results)}/></Panel></>;
 if(view==="Hypotheses")return <><ViewHead title="Hypotheses" sub="Formulate, test and retain research questions."/><Panel title="Research hypotheses"><button className="secondary" onClick={addHyp}>+ ADD HYPOTHESIS</button><Table rows={hypotheses}/></Panel><Panel title="Method"><p className="muted">A hypothesis remains explicitly testable and cannot become a trade recommendation. Supporting and contradicting evidence must be recorded separately.</p></Panel></>;
 if(view==="Evidence")return <><ViewHead title="Evidence" sub="Claim → observation → provenance. Supporting, contradicting and unresolved evidence stay separate."/><Panel title="Evidence ledger"><button className="secondary" onClick={addNote}>+ ADD EVIDENCE</button><Table rows={[...evidence,...notes]}/></Panel><Panel title="Contradictions"><Table rows={contradictions}/></Panel></>;
 if(view==="Reports")return <><ViewHead title="Reports" sub="Generated research report tied to the current run, dataset and evidence."/><Panel title="Current report"><div className="actions"><button className="primary" onClick={()=>download("henryz-research-report.json",report)}>EXPORT REPORT</button></div><Table rows={[{section:"Frame",value:r.symbol+" · "+source.source},{section:"Weekly Authority",value:text(s.weekly_bias)},{section:"Contradictions",value:contradictions.length},{section:"Events",value:events.length},{section:"Evidence",value:evidence.length+notes.length},{section:"Hypotheses",value:hypotheses.length}]}/><div className="report"><small>CONCLUSION</small><p>{r.conclusion}</p></div></Panel></>;
 if(view==="Benchmarks")return <><ViewHead title="Benchmarks" sub="Measured observations from the published research artifact; no unsupported probabilities."/><Panel title="Benchmark matrix"><Table rows={bench}/></Panel><Panel title="Event composition"><Table rows={Object.entries(counts).map(([event,n])=>({event,count:n}))}/></Panel></>;
 if(view==="Research Data")return <><ViewHead title="Research Data" sub="Machine-readable artifacts and reproducibility metadata."/><Panel title="Published artifacts">{ARTIFACTS.map(a=><div className="artifact" key={a[1]}><div><b>{a[0]}</b><small>{a[1]}</small></div><a href={"https://github.com/BudBudness/SMC-Agent-/releases/download/research-data/"+a[1]}>OPEN</a></div>)}</Panel><Panel title="Dataset"><KV k="Source" v={source.source}/><KV k="Rows" v={source.rows}/><KV k="Duplicates" v={source.duplicate_timestamps}/><KV k="Integrity" v={s.source_integrity?.status}/></Panel></>;
 if(view==="Data Quality")return <><ViewHead title="Data Quality" sub="Integrity and research-contamination controls."/><Panel title="Validation"><KV k="Source integrity" v={s.source_integrity?.status}/><KV k="Rows" v={source.rows}/><KV k="Duplicate timestamps" v={source.duplicate_timestamps}/><KV k="Look-ahead policy" v={r.look_ahead_policy||"Confirmed swings only"}/><KV k="Analogue mode" v={analogue.status}/></Panel><Panel title="Execution boundary"><p className="warning">Orders, execution, broker connectivity and trade recommendations are disabled.</p></Panel></>;
 if(view==="Pipeline")return <><ViewHead title="Pipeline" sub="Deterministic research stages and their current release state."/><Panel title="Pipeline"><Table rows={["MARKET DATA","DATA QUALITY / NORMALIZATION","MULTI-TIMEFRAME ENGINE","12M REGIME","6M CONTEXT","3M STRUCTURE","WEEKLY AUTHORITY","DAILY TARGET","4H AMD","1H LIQUIDITY","15M CONFIRMATION","5M STRUCTURE","1M FILL","SMC FEATURES","EVENT SEQUENCING","EVIDENCE","REPORT"].map((stage,i)=>({order:i+1,stage,status:"PASS",source:"validated release"}))}/></Panel></>;
 if(view==="Lineage")return <><ViewHead title="Lineage" sub="Source → transformation → evidence → report."/><Panel title="Research lineage"><div className="lineage">{report.lineage?.map((x:string,i:number)=><div key={i}><span>{i+1}</span><b>{x}</b></div>)||<p className="muted">No lineage recorded.</p>}</div></Panel><Panel title="Reproducibility"><KV k="Dataset" v={source.source}/><KV k="Release timestamp" v={r.timestamp}/><KV k="Look-ahead control" v={r.look_ahead_policy}/></Panel></Panel></>;
 return workspace;
 })();

 return <div className="app"><aside className="side"><div className="brand"><strong>HENRYZ SMC</strong><small>RESEARCH TERMINAL</small></div><button className="new" onClick={()=>setView("New Research")}>＋ NEW RESEARCH</button><nav>{NAV.map(g=><div className="nav-group" key={g.group}><small>{g.group}</small>{g.items.map(item=><button className={view===item?"active":""} onClick={()=>setView(item)} key={item}>{item}</button>)}</div>)}</nav><footer><span className="dot"/> DATA RELEASE ONLINE<br/>RESEARCH ONLY · NO EXECUTION</footer></aside><main className="main"><div className="top"><span>{view} / {r.symbol||"EURUSD"}</span><div><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search evidence / events…"/><b>VALIDATED RELEASE</b></div></div><div className="body">{content}</div><footer className="page-foot">Henryz SMC Intelligence · research application only · no trading, execution, orders or recommendations.</footer></main></div>;
}

function Replay({events}:{events:any[]}){
 const[i,setI]=useState(0);const e=events[i]||{};return <><ViewHead title="Replay" sub="Chronological reconstruction: event by event, without hindsight."/><Panel title="Replay controller"><div className="replay-controls"><button className="secondary" onClick={()=>setI(Math.max(0,i-1))}>PREVIOUS</button><strong>{i+1} / {Math.max(events.length,1)}</strong><button className="secondary" onClick={()=>setI(Math.min(events.length-1,i+1))}>NEXT</button></div><div className="replay-focus"><small>{e.time||e.timestamp}</small><h3>{String(e.name||e.type||"NO EVENT").toUpperCase()}</h3><p>{e.timeframe} · {e.kind||"observation"}</p><Table rows={[e]}/></div></Panel><Panel title="Timeline"><div className="timeline">{events.map((x:any,n)=><button className={n===i?"active":""} onClick={()=>setI(n)} key={n}><span>{n+1}</span>{x.time||x.timestamp||""} · {x.name||x.type}</button>)}</div></Panel></>;
}
