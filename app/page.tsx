"use client";

import {useEffect,useState} from "react";

const TFS=["12M","6M","3M","W","D","4H","1H","15M","5M","1M"];
const tabs=["Overview","Structure","Liquidity & Events","Macro Context","Historical Analogues","Hypotheses","Evidence","Research Data"];

function displayValue(v:any){
  if(v===null||v===undefined)return "UNKNOWN";
  if(typeof v==="object"){
    if("phase" in v)return String(v.phase);
    if("state" in v)return String(v.state);
    return JSON.stringify(v);
  }
  return String(v);
}
function Pill({v}:{v:string}){return <span className={"pill "+String(v||"NEUTRAL").toLowerCase()}>{v||"NEUTRAL"}</span>}
function Panel({title,sub,children}:{title:string;sub?:string;children:React.ReactNode}){return <section className="panel"><div className="panel-head"><div><h2>{title}</h2>{sub&&<p>{sub}</p>}</div></div>{children}</section>}
function KV({k,v}:{k:string;v:any}){return <div className="kv"><span>{k}</span><b title={typeof v==="object"?JSON.stringify(v):undefined}>{displayValue(v)}</b></div>}
function Table({rows,empty="No records available."}:{rows:any[];empty?:string}){
  if(!rows?.length)return <p className="muted">{empty}</p>;
  const keys=Array.from(new Set(rows.flatMap(r=>Object.keys(r||{})))).slice(0,10);
  return <div className="table-wrap"><table><thead><tr>{keys.map(k=><th key={k}>{k.replaceAll("_"," ")}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{keys.map(k=><td key={k}>{typeof r[k]==="object"?JSON.stringify(r[k]):String(r[k]??"")}</td>)}</tr>)}</tbody></table></div>;
}
function StructureViz({frame}:{frame:any}){
  const highs=frame?.confirmed_highs||[], lows=frame?.confirmed_lows||[];
  const points=[...highs.map((x:any)=>({type:"HIGH",value:Array.isArray(x)?x.at(-1):x.value??x.price??x})),...lows.map((x:any)=>({type:"LOW",value:Array.isArray(x)?x.at(-1):x.value??x.price??x}))].slice(-16);
  return <div className="structure-viz"><div className="axis"><span>CONFIRMED STRUCTURE</span><span>{points.length} points</span></div><div className="structure-line">{points.length?points.map((p:any,i:number)=><div key={i} className={"structure-point "+p.type.toLowerCase()} style={{left:(i/Math.max(points.length-1,1))*96+2+"%"}}><i/><small>{p.type}</small></div>):<span className="muted">No confirmed swing points in this frame.</span>}</div></div>;
}
function AppError({message}:{message:string}){return <main className="shell"><section className="error"><b>Research data unavailable</b><p>{message}</p><span>Check the versioned research release and API runtime.</span></section></main>}

export default function Home(){
  const[d,setD]=useState<any>(null),[e,setE]=useState(""),[tab,setTab]=useState("Overview"),[tf,setTf]=useState("W");
  useEffect(()=>{fetch("/api/research",{cache:"no-store"}).then(async r=>{const x=await r.json();if(!r.ok)throw Error(x.error);return x}).then(setD).catch(x=>setE(x.message))},[]);
  if(e)return <AppError message={e}/>;
  if(!d)return <main className="shell"><div className="loading">Loading validated research workspace…</div></main>;
  const r=d.report||{},s=r.market_state||{},frames=d.mtf?.timeframes||{}, contradictions=s.contradictions||[], evidence=r.evidence||[], events=r.events||[], macro=r.macro||{}, analogue=r.analogue_research||{};
  const selected=frames[tf]||{};
  const macroEvents=macro.events||[];
  const eventStudy=macro.event_reaction_study||{};
  const source=d.source||r.dataset||{};
  const coverage=TFS.map(x=>({timeframe:x,bars:frames[x]?.bars,state:frames[x]?.state,start:frames[x]?.start,end:frames[x]?.end}));

  return <main className="shell">
    <header className="hero">
      <div><div className="eyebrow">MARKET INTELLIGENCE · RESEARCH WORKSPACE</div><h1>Henryz SMC Intelligence</h1><p>Structure, liquidity, events, macro context, historical analogues, hypotheses and evidence.</p></div>
      <div className="badge">RESEARCH ONLY</div>
    </header>

    <section className="mtf-grid">{TFS.map(x=><button className="mtf" key={x} onClick={()=>{setTf(x);setTab("Structure")}}><small>{x}</small><Pill v={frames[x]?.state}/></button>)}</section>

    <section className="metrics">
      <div className="metric"><small>Weekly structure</small><strong><Pill v={s.weekly_bias}/></strong><span>Authoritative timeframe</span></div>
      <div className="metric"><small>Contradictions</small><strong>{contradictions.length}</strong><span>Retained, not suppressed</span></div>
      <div className="metric"><small>Sequenced events</small><strong>{events.length}</strong><span>Canonical report</span></div>
      <div className="metric"><small>Evidence claims</small><strong>{evidence.length}</strong><span>With provenance</span></div>
    </section>

    <nav className="tabs">{tabs.map(x=><button className={tab===x?"active":""} onClick={()=>setTab(x)} key={x}>{x}</button>)}</nav>

    {tab==="Overview"&&<section className="grid2">
      <Panel title="Intelligence conclusion" sub="Research interpretation, not a trading prediction."><p className="conclusion">{r.conclusion}</p></Panel>
      <Panel title="Current context" sub="Canonical market-state fields.">
        <KV k="4H AMD" v={s["4H_AMD"]}/><KV k="Daily location" v={s.daily_location}/><KV k="Displacement" v={s.displacement}/><KV k="15M FVGs detected" v={s.fvg_count?.toLocaleString?.()??s.fvg_count}/><KV k="15M order blocks detected" v={s.order_block_count?.toLocaleString?.()??s.order_block_count}/>
      </Panel>
      <Panel title="Research hierarchy" sub="Authority flows from higher timeframe to lower timeframe refinement.">
        <div className="hierarchy">{TFS.map((x,i)=><span key={x} className={i===3?"authority":""}>{x}</span>)}</div>
        <p className="muted">Weekly structure is authoritative. Lower-timeframe conflict is retained as contradiction and cannot silently override it.</p>
      </Panel>
      <Panel title="Integrity & lineage">
        <KV k="Symbol" v={r.symbol}/><KV k="Report timestamp" v={r.timestamp}/><KV k="Analogue status" v={analogue.status}/><KV k="Look-ahead policy" v={d.mtf?.lookahead_control}/><KV k="Dataset source" v={source.source||"EUR/USD M1 research release"}/>
      </Panel>
      <Panel title="Contradictions" sub="Conflicts are first-class research evidence.">
        <Table rows={contradictions} empty="No cross-timeframe contradictions were recorded."/>
      </Panel>
      <Panel title="Recent sequenced events" sub="Chronological observations from the canonical report.">
        <Table rows={events.slice(-8)}/>
      </Panel>
    </section>}

    {tab==="Structure"&&<section>
      <Panel title="Multi-timeframe structure" sub="Confirmed swings are shown only after right-side confirmation.">
        <div className="select-row">{TFS.map(x=><button className={tf===x?"selected":""} onClick={()=>setTf(x)} key={x}>{x}</button>)}</div>
        <div className="structure-card"><div className="state-row"><h3>{tf}</h3><Pill v={selected.state}/></div><StructureViz frame={selected}/><div className="three"><KV k="Bars" v={selected.bars?.toLocaleString?.()??selected.bars}/><KV k="Start" v={selected.start}/><KV k="End" v={selected.end}/></div></div>
        <div className="grid2 compact"><Panel title="Confirmed highs"><Table rows={(selected.confirmed_highs||[]).map((x:any)=>typeof x==="object"?x:{value:x})} empty="No confirmed highs."/></Panel><Panel title="Confirmed lows"><Table rows={(selected.confirmed_lows||[]).map((x:any)=>typeof x==="object"?x:{value:x})} empty="No confirmed lows."/></Panel></div>
      </Panel>
    </section>}

    {tab==="Liquidity & Events"&&<section className="grid2">
      <Panel title="Liquidity map" sub="External and internal liquidity remain distinct.">
        <div className="stat-grid"><div><small>External zones</small><b>{r.liquidity?.external_zone_count??0}</b></div><div><small>Internal zones</small><b>{r.liquidity?.internal_zone_count??0}</b></div></div>
        <Table rows={r.liquidity?.zones||[]} empty="No liquidity zones recorded."/>
      </Panel>
      <Panel title="Sweep & inducement" sub="A sweep is not automatically a breakout or inducement.">
        <KV k="Sweep" v={r.liquidity?.sweep?.kind||r.liquidity?.sweep?.status||"NONE"}/><KV k="Inducement" v={r.liquidity?.inducement?.kind||r.liquidity?.inducement?.status||"NONE"}/>
        {r.liquidity?.sweep&&<pre>{JSON.stringify(r.liquidity.sweep,null,2)}</pre>}
      </Panel>
      <Panel title="Sequenced SMC events" sub="Chronological event ordering preserves causal context."><div className="event-list">{events.map((x:any,i:number)=><div className="event" key={i}><div><b>{String(x.name).toUpperCase()}</b><span>{x.timeframe} · {x.kind}</span></div><code>{String(x.time||"")}</code></div>)}</div></Panel>
      <Panel title="Delivery context"><KV k="4H AMD" v={s["4H_AMD"]}/><KV k="Displacement" v={s.displacement}/><KV k="FVG count" v={s.fvg_count}/><KV k="Order blocks" v={s.order_block_count}/></Panel>
    </section>}

    {tab==="Macro Context"&&<section>
      <Panel title="Macro event context" sub="Actual vs expected/previous is contextual evidence; surprise is not inherently directional.">
        <Table rows={macroEvents} empty="No macro events supplied for this research report."/>
      </Panel>
      <Panel title="Historical event reaction study" sub="Descriptive event-window observations; not a causal or predictive model.">
        <Table rows={Array.isArray(eventStudy)?eventStudy:Object.entries(eventStudy).map(([k,v])=>({metric:k,value:typeof v==="object"?JSON.stringify(v):v}))}/>
      </Panel>
    </section>}

    {tab==="Historical Analogues"&&<section className="grid2">
      <Panel title="Analogue research contract" sub="Historical similarity is descriptive and does not imply future direction.">
        <KV k="Status" v={analogue.status}/><KV k="Samples" v={analogue.samples}/><KV k="Method" v={analogue.method}/><KV k="Minimum similarity" v={analogue.min_similarity}/>
        <p className="warning">{analogue.warning||"No warning supplied."}</p>
      </Panel>
      <Panel title="Matched historical episodes" sub="Matches are research observations, not forecasts."><Table rows={analogue.matches||[]} empty="No historical episode set was supplied; no analogue inference was made."/></Panel>
      <Panel title="Conditional statistics" sub="Only displayed when supplied by the research engine."><Table rows={Array.isArray(analogue.conditional_stats)?analogue.conditional_stats:Object.entries(analogue.conditional_stats||{}).map(([k,v])=>({metric:k,value:typeof v==="object"?JSON.stringify(v):v}))} empty="No conditional statistics supplied."/></Panel>
    </section>}

    {tab==="Hypotheses"&&<section>{(r.hypotheses||[]).map((h:any,i:number)=><Panel title={h.name} sub="Competing research hypothesis — not a recommendation." key={i}>
      <div className="grid3"><div><h3>Supporting evidence</h3><Table rows={(h.evidence||[]).map((x:any)=>({claim_id:x}))} empty="None recorded."/></div><div><h3>Contradictions</h3><Table rows={(h.contradictions||[]).map((x:any)=>({explanation:x}))} empty="None recorded."/></div><div><h3>Invalidation</h3><Table rows={(h.invalidation||[]).map((x:any)=>({condition:x}))} empty="None recorded."/></div></div>
    </Panel>)}</section>}

    {tab==="Evidence"&&<section>
      <Panel title="Canonical evidence ledger" sub="Claim → observation → provenance → qualitative strength.">
        <Table rows={evidence} empty="No canonical evidence records."/>
      </Panel>
    </section>}

    {tab==="Research Data"&&<section className="grid2">
      <Panel title="Dataset lineage"><KV k="Rows" v={source.rows??d.mtf?.source_rows}/><KV k="Start" v={source.start??d.mtf?.source_start}/><KV k="End" v={source.end??d.mtf?.source_end}/><KV k="Frequency" v={d.mtf?.source_frequency}/><KV k="Source" v={source.source??"EUR/USD M1 research release"}/></Panel>
      <Panel title="MTF coverage"><Table rows={coverage}/></Panel>
      <Panel title="Research controls"><KV k="Look-ahead control" v={d.mtf?.lookahead_control}/><KV k="Release" v="research-data"/><KV k="Execution semantics" v="Disabled"/><KV k="Trading recommendations" v="Disabled"/></Panel>
      <Panel title="Research limitations"><p className="muted">Benchmarks use rule-generated reference labels rather than human ground truth. Historical analogues are descriptive only. No profitability, predictive-accuracy, recommendation, or live-readiness claim is made.</p></Panel>
    </section>}

    <footer>Research interface only · no trading, execution, orders, or recommendations.</footer>
  </main>;
}