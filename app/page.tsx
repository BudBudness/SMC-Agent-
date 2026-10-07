"use client";

import {useEffect,useMemo,useState} from "react";

const TFS=["12M","6M","3M","W","D","4H","1H","15M","5M","1M"];
const NAV=[
  {group:"RESEARCH",items:["New Research","Active Research","Research History"]},
  {group:"MARKET",items:["Workspace","MTF Structure","Liquidity","Events","Macro Context"]},
  {group:"INVESTIGATION",items:["Replay","Historical Analogues","Hypotheses","Evidence"]},
  {group:"OUTPUT",items:["Reports","Benchmarks","Research Data"]},
  {group:"SYSTEM",items:["Data Quality","Pipeline","Lineage"]},
];

function asArray<T=any>(v:any):T[]{return Array.isArray(v)?v:[]}
function displayValue(v:any){if(v===null||v===undefined)return"UNKNOWN";if(typeof v==="object"){if("phase"in v)return String(v.phase??"UNKNOWN");if("state"in v)return String(v.state??"UNKNOWN");try{return JSON.stringify(v)??"UNKNOWN"}catch{return"UNSERIALIZABLE"}}return String(v)}
function Pill({v}:{v:any}){const value=typeof v==="string"&&v?v:"NEUTRAL";return <span className={"pill "+value.toLowerCase()}>{value}</span>}
function Panel({title,sub,children}:{title:string;sub?:string;children:React.ReactNode}){return <section className="panel"><div className="panel-head"><div><h2>{title}</h2>{sub&&<p>{sub}</p>}</div></div>{children}</section>}
function KV({k,v}:{k:string;v:any}){return <div className="kv"><span>{k}</span><b>{displayValue(v)}</b></div>}
function Table({rows,empty="No records available."}:{rows:any[];empty?:string}){const safeRows=asArray(rows);if(!safeRows.length)return <p className="muted">{empty}</p>;const keys=Array.from(new Set(safeRows.flatMap(r=>r&&typeof r==="object"?Object.keys(r):[]))).slice(0,10);return <div className="table-wrap"><table><thead><tr>{keys.map(k=><th key={k}>{k.replaceAll("_"," ")}</th>)}</tr></thead><tbody>{safeRows.map((r,i)=><tr key={i}>{keys.map(k=><td key={k}>{typeof r[k]==="object"?JSON.stringify(r[k]):String(r[k]??"")}</td>)}</tr>)}</tbody></table></div>}
function StructureViz({frame}:{frame:any}){const highs=asArray(frame?.confirmed_highs),lows=asArray(frame?.confirmed_lows);const points=[...highs.map((x:any)=>({type:"HIGH",value:Array.isArray(x)?x.at(-1):x.value??x.price??x})),...lows.map((x:any)=>({type:"LOW",value:Array.isArray(x)?x.at(-1):x.value??x.price??x}))].slice(-16);return <div className="structure-viz"><div className="axis"><span>CONFIRMED STRUCTURE</span><span>{points.length} points</span></div><div className="structure-line">{points.length?points.map((p:any,i:number)=><div key={i} className={"structure-point "+p.type.toLowerCase()} style={{left:(i/Math.max(points.length-1,1))*96+2+"%"}}><i/><small>{p.type}</small></div>):<span className="muted">No confirmed swing points.</span>}</div></div>}
function AppError({message}:{message:string}){return <main className="terminal"><section className="error"><b>Research data unavailable</b><p>{message}</p><span>Check the versioned research release and API runtime.</span></section></main>}

export default function Home(){
 const[d,setD]=useState<any>(null),[e,setE]=useState(""),[view,setView]=useState("Workspace"),[tf,setTf]=useState("W"),[query,setQuery]=useState("");
 useEffect(()=>{fetch("/api/research",{cache:"no-store"}).then(async r=>{const x=await r.json();if(!r.ok)throw Error(x.error);return x}).then(setD).catch(x=>setE(x.message))},[]);
 if(e)return <AppError message={e}/>;
 if(!d)return <main className="terminal"><div className="loading">Loading validated research system…</div></main>;

 const r=d.report&&typeof d.report==="object"?d.report:{},s=r.market_state&&typeof r.market_state==="object"?r.market_state:{},frames=d.mtf?.timeframes&&typeof d.mtf.timeframes==="object"?d.mtf.timeframes:{},contradictions=asArray(s.contradictions),evidence=asArray(r.evidence),events=asArray(r.events),macro=r.macro&&typeof r.macro==="object"?r.macro:{},analogue=r.analogue_research&&typeof r.analogue_research==="object"?r.analogue_research:{},source=d.source||r.dataset||{},selected=frames[tf]||{};
 const coverage=TFS.map(x=>({timeframe:x,bars:frames[x]?.bars,state:frames[x]?.state,start:frames[x]?.start,end:frames[x]?.end}));
 const runResearch=()=>{setView("Workspace");setQuery("")};

 const workspace=<>
  <div className="workspace-head"><div><span className="eyebrow">ACTIVE RESEARCH · EURUSD</span><h1>Market Workspace</h1><p>Investigate structure, liquidity and evidence across the canonical timeframe hierarchy.</p></div><button className="primary" onClick={runResearch}>RUN RESEARCH</button></div>
  <section className="state-strip">{TFS.map(x=><button key={x} className={"tf-cell "+(tf===x?"selected":"")} onClick={()=>setTf(x)}><small>{x}</small><Pill v={frames[x]?.state}/></button>)}</section>
  <section className="authority-bar"><div><span>WEEKLY AUTHORITY</span><strong><Pill v={s.weekly_bias}/></strong></div><p>Higher-timeframe authority governs interpretation. Lower-timeframe conflict is retained as evidence.</p><span className="research-lock">RESEARCH ONLY</span></section>
  <div className="workspace-grid">
   <div className="main-column">
    <Panel title={"Structure · "+tf} sub="Confirmed swings appear only after right-side confirmation.">
      <div className="structure-card"><div className="state-row"><div><small>SELECTED TIMEFRAME</small><h3>{tf}</h3></div><Pill v={selected.state}/></div><StructureViz frame={selected}/><div className="three"><KV k="Bars" v={selected.bars?.toLocaleString?.()??selected.bars}/><KV k="Start" v={selected.start}/><KV k="End" v={selected.end}/></div></div>
    </Panel>
    <Panel title="Chronological evidence" sub="Observed events remain ordered by confirmation time."><div className="event-list">{events.slice(-8).map((x:any,i:number)=><div className="event" key={i}><div><b>{String(x.name).toUpperCase()}</b><span>{x.timeframe} · {x.kind}</span></div><code>{String(x.time||"")}</code></div>)}</div></Panel>
   </div>
   <aside className="evidence-rail">
    <Panel title="Research state"><KV k="4H AMD" v={s["4H_AMD"]}/><KV k="Daily location" v={s.daily_location}/><KV k="Displacement" v={s.displacement}/><KV k="Contradictions" v={contradictions.length}/></Panel>
    <Panel title="SMC observations"><KV k="15M FVGs" v={s.fvg_count?.toLocaleString?.()??s.fvg_count}/><KV k="15M order blocks" v={s.order_block_count?.toLocaleString?.()??s.order_block_count}/><KV k="Sequenced events" v={events.length}/><KV k="Evidence claims" v={evidence.length}/></Panel>
    <Panel title="Research interpretation"><p className="conclusion">{r.conclusion}</p></Panel>
   </aside>
  </div>
 </>;

 const genericView=()=>{
  if(view==="MTF Structure")return <><ViewHead title="MTF Structure" sub="The canonical hierarchy from regime to execution refinement."/><Panel title="Research hierarchy"><div className="hierarchy">{TFS.map((x,i)=><span key={x} className={i===3?"authority":""}>{x}</span>)}</div><Table rows={coverage}/></Panel><Panel title={"Confirmed structure · "+tf}><StructureViz frame={selected}/><div className="grid2 compact"><Panel title="Confirmed highs"><Table rows={asArray(selected.confirmed_highs).map((x:any)=>typeof x==="object"?x:{value:x})}/></Panel><Panel title="Confirmed lows"><Table rows={asArray(selected.confirmed_lows).map((x:any)=>typeof x==="object"?x:{value:x})}/></Panel></div></Panel></>;
  if(view==="Liquidity"||view==="Events")return <><ViewHead title={view} sub="First-class observations from the canonical research report."/><section className="grid2"><Panel title="Liquidity map"><KV k="External zones" v={r.liquidity?.external_zone_count??0}/><KV k="Internal zones" v={r.liquidity?.internal_zone_count??0}/><Table rows={r.liquidity?.zones||[]} empty="No liquidity zones recorded."/></Panel><Panel title="Sequenced events"><div className="event-list">{events.map((x:any,i:number)=><div className="event" key={i}><div><b>{String(x.name).toUpperCase()}</b><span>{x.timeframe} · {x.kind}</span></div><code>{String(x.time||"")}</code></div>)}</div></Panel></section></>;
  if(view==="Macro Context")return <><ViewHead title="Macro Context" sub="Event context and reaction observations; no directional inference."/><Panel title="Macro events"><Table rows={asArray(macro.events)} empty="No macro events supplied."/></Panel><Panel title="Reaction study"><Table rows={Array.isArray(macro.event_reaction_study)?macro.event_reaction_study:Object.entries(macro.event_reaction_study||{}).map(([k,v])=>({metric:k,value:typeof v==="object"?JSON.stringify(v):v}))}/></Panel></>;
  if(view==="Historical Analogues")return <><ViewHead title="Historical Analogues" sub="Descriptive similarity research, never a forecast."/><section className="grid2"><Panel title="Analogue contract"><KV k="Status" v={analogue.status}/><KV k="Samples" v={analogue.samples}/><KV k="Method" v={analogue.method}/><KV k="Minimum similarity" v={analogue.min_similarity}/><p className="warning">{analogue.warning||"Descriptive only."}</p></Panel><Panel title="Matched episodes"><Table rows={analogue.matches||[]}/></Panel></section></>;
  if(view==="Hypotheses")return <><ViewHead title="Hypotheses" sub="Competing explanations with explicit supporting and contradicting evidence."/>{asArray(r.hypotheses).map((h:any,i:number)=><Panel title={h.name} sub="Research hypothesis — not a recommendation." key={i}><div className="grid3"><div><h3>Supporting</h3><Table rows={asArray(h.evidence).map((x:any)=>({claim_id:x}))}/></div><div><h3>Contradictions</h3><Table rows={asArray(h.contradictions).map((x:any)=>({explanation:x}))}/></div><div><h3>Invalidation</h3><Table rows={asArray(h.invalidation).map((x:any)=>({condition:x}))}/></div></div></Panel>)}</>;
  if(view==="Evidence")return <><ViewHead title="Evidence Ledger" sub="Claim → observation → provenance → qualitative strength."/><Panel title="Canonical evidence"><Table rows={evidence}/></Panel><Panel title="Contradictions"><Table rows={contradictions}/></Panel></>;
  if(view==="Reports")return <><ViewHead title="Research Reports" sub="Canonical outputs generated from validated research artifacts."/><Panel title="Current report"><KV k="Symbol" v={r.symbol}/><KV k="Timestamp" v={r.timestamp}/><KV k="Analogue status" v={analogue.status}/><p className="conclusion">{r.conclusion}</p></Panel></>;
  if(view==="Benchmarks")return <><ViewHead title="Benchmarks" sub="Engine/reference evaluation using the same terminal research frame."/><Panel title="Benchmark boundary"><p className="muted">Benchmarks are methodological research artifacts. They are not profitability or predictive-accuracy claims.</p></Panel></>;
  if(view==="Research Data"||view==="Data Quality"||view==="Pipeline"||view==="Lineage")return <><ViewHead title={view} sub="Research infrastructure, lineage and integrity controls."/><section className="grid2"><Panel title="Dataset lineage"><KV k="Rows" v={source.rows??d.mtf?.source_rows}/><KV k="Start" v={source.start??d.mtf?.source_start}/><KV k="End" v={source.end??d.mtf?.source_end}/><KV k="Frequency" v={d.mtf?.source_frequency}/><KV k="Source" v={source.source??"EUR/USD M1 research release"}/></Panel><Panel title="Integrity"><KV k="Source integrity" v={s.source_integrity?.status||"UNKNOWN"}/><KV k="Duplicate timestamps" v={s.source_integrity?.duplicate_timestamps}/><KV k="Look-ahead control" v={d.mtf?.lookahead_control}/><KV k="Execution semantics" v="Disabled"/></Panel></section><Panel title="MTF coverage"><Table rows={coverage}/></Panel></>;
  if(view==="Replay")return <><ViewHead title="Market Replay" sub="Reconstruct the sequence without turning observations into predictions."/><Panel title="Chronological replay"><div className="replay">{events.map((x:any,i:number)=><div className="replay-row" key={i}><span>{String(x.time||"")}</span><b>{String(x.name||"").toUpperCase()}</b><em>{x.timeframe}</em><code>{JSON.stringify(x.evidence||{})}</code></div>)}</div></Panel></>;
  return workspace;
 };
 function ViewHead({title,sub}:{title:string;sub:string}){return <div className="workspace-head"><div><span className="eyebrow">RESEARCH TERMINAL</span><h1>{title}</h1><p>{sub}</p></div><button className="secondary" onClick={()=>setView("Workspace")}>OPEN WORKSPACE</button></div>}

 return <main className="app-shell">
  <aside className="sidebar"><div className="brand"><span className="brand-mark">H</span><div><b>HENRYZ SMC</b><small>INTELLIGENCE</small></div></div><button className="new-research" onClick={runResearch}>＋ NEW RESEARCH</button><nav>{NAV.map(g=><div className="nav-group" key={g.group}><small>{g.group}</small>{g.items.map(item=><button key={item} className={view===item?"active":""} onClick={()=>setView(item)}>{item}</button>)}</div>)}</nav><div className="sidebar-foot"><span className="status-dot"/>RESEARCH ONLY<div>EURUSD · canonical release</div></div></aside>
  <section className="app-main"><header className="topbar"><div className="crumb">Henryz SMC / {view}</div><div className="top-actions"><input value={query} onChange={x=>setQuery(x.target.value)} placeholder="Search research…" /><span className="data-status">DATA · PASS</span></div></header>{genericView()}<footer>Research application only · no trading, execution, orders, or recommendations.</footer></section>
 </main>
}