"use client";
import {useEffect,useMemo,useState} from "react";

const TFS=["12M","6M","3M","W","D","4H","1H","15M","5M","1M"];
const NAV=[["RESEARCH",["New Research","Active Research","Research History"]],["MARKET",["Workspace","MTF Structure","Liquidity","Events","Macro Context"]],["INVESTIGATION",["Replay","Historical Analogues","Hypotheses","Evidence"]],["OUTPUT",["Reports","Benchmarks","Research Data"]],["SYSTEM",["Data Quality","Pipeline","Lineage"]]];
const ARTIFACTS=[["Research report","EURUSD_research_report.json"],["MTF dashboard","EURUSD_MTF_dashboard.json.gz"],["M1 replay dataset","EURUSD_M1_dashboard.csv.gz"],["Labelled benchmark","labelled-eurusd.json"]];

const arr=(v:any)=>Array.isArray(v)?v:[];
const txt=(v:any)=>v===null||v===undefined?"UNKNOWN":typeof v==="object"?JSON.stringify(v):String(v);
function Panel({title,sub,children}:{title:string;sub?:string;children:any}){return <section className="panel"><header><h2>{title}</h2>{sub&&<p>{sub}</p>}</header>{children}</section>}
function KV({k,v}:{k:string;v:any}){return <div className="kv"><span>{k}</span><b>{txt(v)}</b></div>}
function Table({rows,empty="No records."}:{rows:any[];empty?:string}){if(!rows.length)return <p className="muted">{empty}</p>;const keys=Array.from(new Set(rows.flatMap(r=>r&&typeof r==="object"?Object.keys(r):[]))).slice(0,12);return <div className="table"><table><thead><tr>{keys.map(k=><th key={k}>{k.replaceAll("_"," ")}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{keys.map(k=><td key={k}>{txt(r?.[k])}</td>)}</tr>)}</tbody></table></div>}
function Head({title,sub}:{title:string;sub:string}){return <div className="view-head"><div><span className="eyebrow">HENRYZ SMC · RESEARCH TERMINAL</span><h1>{title}</h1><p>{sub}</p></div></div>}
function download(name:string,data:any){const a=document.createElement("a");a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:"application/json"}));a.download=name;a.click()}

export default function Home(){
 const[d,setD]=useState<any>(null),[error,setError]=useState(""),[view,setView]=useState("Workspace"),[tf,setTf]=useState("W"),[query,setQuery]=useState(""),[runs,setRuns]=useState<any[]>([]),[run,setRun]=useState<any>(null),[hyp,setHyp]=useState<any[]>([]),[evidence,setEvidence]=useState<any[]>([]);
 const load=async()=>{try{const urls=["/api/research","/api/research?resource=runs","/api/research?resource=hypotheses","/api/research?resource=evidence"];const [a,b,c,e]=await Promise.all(urls.map(u=>fetch(u,{cache:"no-store"}).then(async r=>{const x=await r.json();if(!r.ok)throw Error(x.error);return x})));setD(a);setRuns(b||[]);setHyp(c||[]);setEvidence(e||[])}catch(e){setError(e instanceof Error?e.message:"Research data unavailable")}};
 useEffect(()=>{load()},[]);
 if(error)return <main className="terminal error"><b>Research system unavailable</b><p>{error}</p></main>;
 if(!d)return <main className="terminal loading">Loading validated research system…</main>;
 const r=d.report||{},s=r.market_state||{},frames=d.mtf?.timeframes||{},source=d.source||r.dataset||{},events=arr(r.events),contradictions=arr(s.contradictions),analogue=r.analogue_research||{},selected=frames[tf]||{};
 const filtered=events.filter(x=>!query||JSON.stringify(x).toLowerCase().includes(query.toLowerCase()));
 const execute=async(parameters:any={})=>{ 
  setRun({status:"RUNNING"});
  try{
    const response=await fetch("/api/research",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"run",instrument:r.symbol||"EURUSD",parameters})});
    const result=await response.json();
    if(!response.ok) throw Error(result.error||"Research run failed");
    setRun(result);
    setRuns(v=>[result.run,...v]);
    setView("Active Research");
  }catch(e){
    setRun({status:"FAILED",error:e instanceof Error?e.message:"Run failed"});
  }
 };
 const addHyp=async()=>{
  const title=prompt("Hypothesis title");
  if(!title)return;
  const response=await fetch("/api/research",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"hypothesis",data:{title:title,statement:title,status:"OPEN"}})});
  if(response.ok){const item=await response.json();setHyp(v=>[item,...v]);}
 };
 const addEvidence=async()=>{
  const claim=prompt("Evidence claim");
  if(!claim)return;
  const response=await fetch("/api/research",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"evidence",data:{claim:claim,evidence_type:"UNCLASSIFIED",provenance:{source:"researcher"}}})});
  if(response.ok){const item=await response.json();setEvidence(v=>[item,...v]);}
 };
 const active=run?.result;
 const workspace=<><div className="hero"><div><span className="eyebrow">ACTIVE RESEARCH · {r.symbol||"EURUSD"}</span><h1>Market Workspace</h1><p>Research execution, MTF structure, evidence and historical reconstruction. No trading execution.</p></div><button className="primary" onClick={execute}>RUN ANALYSIS</button></div><div className="tf-strip">{TFS.map(x=><button key={x} className={tf===x?"sel":""} onClick={()=>setTf(x)}><small>{x}</small><b>{txt(frames[x]?.state)}</b></button>)}</div><div className="authority"><b>WEEKLY AUTHORITY · {txt(s.weekly_bias)}</b><span>Weekly structure remains authoritative; lower timeframes are retained as evidence.</span><em>RESEARCH ONLY</em></div><div className="columns"><div><Panel title={"Structure · "+tf} sub="Canonical validated MTF state."><div className="chart"><b>{txt(selected.state)}</b><span>{selected.bars||0} bars · {selected.start||""} → {selected.end||""}</span></div><Table rows={[...arr(selected.confirmed_highs).map(x=>({type:"HIGH",value:x?.price??x?.value??x})),...arr(selected.confirmed_lows).map(x=>({type:"LOW",value:x?.price??x?.value??x}))].slice(-20)}/></Panel><Panel title="Chronological events" sub="Canonical research events from the validated report."><input className="search-wide" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Filter events…"/><Table rows={filtered}/></Panel></div><aside><Panel title="Research state"><KV k="4H AMD" v={s["4H_AMD"]}/><KV k="Daily location" v={s.daily_location}/><KV k="Displacement" v={s.displacement}/><KV k="Contradictions" v={contradictions.length}/></Panel><Panel title="Data quality"><KV k="Source" v={source.source}/><KV k="Rows" v={source.rows}/><KV k="Integrity" v={s.source_integrity?.status}/></Panel></aside></div></>;

 const benchmarkRows=active?.benchmarks?Object.entries(active.benchmarks.results||{}).map(([metric,result])=>({metric:metric,result:result,definition:active.benchmarks.definitions?.[metric]||""})):[];
 const limitationRows=(active?.benchmarks?.limitations||["Execute a research run to calculate persisted benchmarks."]).map((x:any)=>({limitation:x}));
 const pipelineRows=active?.lineage||[{stage:"Research run",status:run?.run?.status||"NOT EXECUTED"}];
 let content:any=workspace;
 if(view==="New Research")content=<><Head title="New Research" sub="Execute the canonical parameterized research pipeline and persist its result."/><Panel title="Research configuration"><div className="form"><label>Instrument<select><option>EURUSD</option></select></label><label>Start (UTC)<input id="research-start" type="datetime-local" defaultValue="2026-09-01T00:00"/></label><label>End (UTC)<input id="research-end" type="datetime-local" defaultValue="2026-10-02T16:58"/></label><label>Replay bars<input id="research-replay" type="number" min="100" max="10000" defaultValue="2000"/></label><label>Hierarchy<select><option>12M → 1M</option></select></label></div><button className="primary" onClick={()=>{const s=(document.getElementById("research-start") as HTMLInputElement)?.value;const e=(document.getElementById("research-end") as HTMLInputElement)?.value;const n=Number((document.getElementById("research-replay") as HTMLInputElement)?.value||2000);execute({start:s?new Date(s).toISOString():null,end:e?new Date(e).toISOString():null,replay_bars:n})}}>START RESEARCH RUN</button></Panel></>;
 if(view==="Active Research")content=<><Head title="Active Research" sub="Persisted canonical research-engine execution result."/><Panel title="Run"><KV k="Run ID" v={run?.run?.id}/><KV k="Status" v={run?.run?.status||run?.status}/><KV k="Execution" v={active?.execution}/><KV k="Engine" v={active?.engine_version}/><KV k="Dataset" v={active?.dataset?.artifact}/><KV k="Window" v={active?.parameters?.start+" → "+active?.parameters?.end}/><KV k="Replay bars" v={active?.replay?.length}/><KV k="Events" v={active?.events?.length}/></Panel><Panel title="Executed benchmarks"><Table rows={active?.benchmarks?Object.entries(active.benchmarks.results||{}).map(([metric,result])=>({metric,result})):[]}/></Panel></>;
 if(view==="Research History")content=<><Head title="Research History" sub="Persisted research runs in Supabase."/><Panel title="Runs"><Table rows={runs}/></Panel></>;
 if(view==="MTF Structure")content=<><Head title="MTF Structure" sub="12M regime → 6M context → 3M structure → Weekly authority → lower timeframe evidence."/><Panel title="Timeframe hierarchy"><Table rows={TFS.map(x=>({timeframe:x,bars:frames[x]?.bars,state:frames[x]?.state,start:frames[x]?.start,end:frames[x]?.end}))}/></Panel><Panel title={"Confirmed structure · "+tf}><Table rows={[...arr(selected.confirmed_highs).map(x=>({type:"HIGH",value:x?.price??x?.value??x})),...arr(selected.confirmed_lows).map(x=>({type:"LOW",value:x?.price??x?.value??x}))]}/></Panel></>;
 if(view==="Liquidity")content=<><Head title="Liquidity" sub="Observed liquidity formations and sweeps."/><Panel title="Liquidity observations"><Table rows={events.filter(x=>/liquidity|sweep/i.test(String(x.name||x.type)))}/></Panel></>;
 if(view==="Events")content=<><Head title="Events" sub="Searchable chronological event ledger."/><Panel title="Events"><input className="search-wide" value={query} onChange={e=>setQuery(e.target.value)} placeholder="Filter…"/><Table rows={filtered}/></Panel></>;
 if(view==="Macro Context")content=<><Head title="Macro Context" sub="Macro observations retained as contextual evidence."/><Panel title="Macro"><Table rows={arr(r.macro?.events||r.macro)}/></Panel></>;
 if(view==="Replay")content=<Replay bars={active?.replay||[]}/>;
 if(view==="Historical Analogues")content=<><Head title="Historical Analogues" sub="Actual descriptive similarity output from the validated research engine."/><Panel title="Analogue research"><KV k="Status" v={analogue.status}/><KV k="Method" v={analogue.method}/><KV k="Samples" v={analogue.samples}/><Table rows={arr(analogue.matches||analogue.results)}/></Panel></>;
 if(view==="Hypotheses")content=<><Head title="Hypotheses" sub="Persistent research questions."/><Panel title="Hypotheses"><button className="secondary" onClick={addHyp}>+ ADD HYPOTHESIS</button><Table rows={hyp}/></Panel></>;
 if(view==="Evidence")content=<><Head title="Evidence" sub="Persistent claims and provenance."/><Panel title="Evidence ledger"><button className="secondary" onClick={addEvidence}>+ ADD EVIDENCE</button><Table rows={[...arr(r.evidence),...evidence]}/></Panel><Panel title="Contradictions"><Table rows={contradictions}/></Panel></>;
 if(view==="Reports")content=<><Head title="Reports" sub="Persisted report artifact generated from an executed run."/><Panel title="Report"><button className="primary" disabled={!active} onClick={()=>download("henryz-research-report.json",active)}>EXPORT REPORT</button><Table rows={[{run:run?.run?.id||"NOT EXECUTED",dataset:source.source,authority:s.weekly_bias,events:active?.events?.length||events.length,replay_bars:active?.replay?.length||0}]}/></Panel></>;
 if(view==="Benchmarks")content=<><Head title="Benchmarks" sub="Measured results, definitions and limitations."/><Panel title="Benchmark results"><Table rows={benchmarkRows}/></Panel><Panel title="Limitations"><Table rows={limitationRows}/></Panel></>;
 if(view==="Research Data")content=<><Head title="Research Data" sub="Published machine-readable artifacts."/><Panel title="Artifacts">{ARTIFACTS.map(a=><div className="artifact" key={a[1]}><b>{a[0]}</b><small>{a[1]}</small><a href={"https://github.com/BudBudness/SMC-Agent-/releases/download/research-data/"+a[1]}>OPEN</a></div>)}</Panel></>;
 if(view==="Data Quality")content=<><Head title="Data Quality" sub="Validated source and contamination controls."/><Panel title="Validation"><KV k="Integrity" v={s.source_integrity?.status}/><KV k="Rows" v={source.rows}/><KV k="Duplicates" v={source.duplicate_timestamps}/><KV k="Look-ahead" v={r.look_ahead_policy}/></Panel></>;
 if(view==="Pipeline")content=<><Head title="Pipeline" sub="Actual execution state; no fabricated PASS states."/><Panel title="Run pipeline"><Table rows={pipelineRows}/></Panel></>;
 if(view==="Lineage")content=<><Head title="Lineage" sub="Source → validated artifacts → replay → persisted research result."/><Panel title="Lineage"><Table rows={active?.lineage||[{stage:"Release",artifact:"EURUSD_research_report.json"},{stage:"MTF",artifact:"EURUSD_MTF_dashboard.json.gz"},{stage:"Replay",artifact:"EURUSD_M1_dashboard.csv.gz"}]}/></Panel></>;

 return <div className="app"><aside className="side"><div className="brand"><strong>HENRYZ SMC</strong><small>RESEARCH TERMINAL</small></div><button className="new" onClick={()=>setView("New Research")}>＋ NEW RESEARCH</button><nav>{NAV.map(([group,items]:any)=><div className="nav-group" key={group}><small>{group}</small>{items.map((item:string)=><button key={item} className={view===item?"active":""} onClick={()=>setView(item)}>{item}</button>)}</div>)}</nav><footer><span className="dot"/> DATA RELEASE ONLINE<br/>RESEARCH ONLY · NO EXECUTION</footer></aside><main className="main"><div className="top"><span>{view} / {r.symbol||"EURUSD"}</span><div><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search…"/><b>VALIDATED RELEASE</b></div></div><div className="body">{content}</div><footer className="page-foot">Henryz SMC Intelligence · research application only · no trading, execution, orders or recommendations.</footer></main></div>
}

function Replay({bars}:{bars:any[]}){const[i,setI]=useState(0);const b=bars[i]||{};return <><Head title="Replay" sub="Bar-level historical reconstruction from the published M1 dashboard dataset."/><Panel title="Replay"><div className="replay-controls"><button className="secondary" disabled={!bars.length} onClick={()=>setI(Math.max(0,i-1))}>PREVIOUS</button><b>{bars.length?i+1:0} / {bars.length}</b><button className="secondary" disabled={!bars.length} onClick={()=>setI(Math.min(bars.length-1,i+1))}>NEXT</button></div><Table rows={bars.length?[b]:[]}/></Panel><Panel title="Timeline"><div className="timeline">{bars.slice(Math.max(0,i-20),i+21).map((x,n)=>{const idx=Math.max(0,i-20)+n;return <button key={idx} className={idx===i?"active":""} onClick={()=>setI(idx)}>{idx+1} · {x.timestamp} · C {x.close}</button>})}</div></Panel></>}
