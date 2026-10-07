import {NextResponse} from "next/server";
import {gunzipSync} from "node:zlib";

export const maxDuration = 300;

const BASE="https://github.com/BudBudness/SMC-Agent-/releases/download/research-data";
const SUPA="https://prqbeocaycxqsremxvmb.supabase.co";
const KEY="sb_publishable_PVS7tsfzFOSwbRxfsv6plg_eK0nAynL";
const H={apikey:KEY,Authorization:"Bearer "+KEY,"Content-Type":"application/json"};

async function db(path:string,init:RequestInit={}) {
  const r=await fetch(SUPA+"/rest/v1/"+path,{...init,headers:{...H,...((init.headers||{}) as Record<string,string>)},cache:"no-store"});
  const b=await r.text();
  if(!r.ok) throw Error("database "+r.status+": "+b);
  return b?JSON.parse(b):null;
}

async function rel(name:string) {
  const r=await fetch(BASE+"/"+name,{cache:"no-store"});
  if(!r.ok) throw Error("release unavailable: "+name);
  return r;
}

async function canonical() {
  const [a,b]=await Promise.all([rel("EURUSD_research_report.json"),rel("EURUSD_MTF_dashboard.json.gz")]);
  return {report:await a.json(),mtf:JSON.parse(gunzipSync(Buffer.from(await b.arrayBuffer())).toString("utf8"))};
}

async function executeEngine(req:Request, parameters:any) {
  const url=new URL(req.url);
  const r=await fetch(url.origin+"/api/research_engine",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    cache:"no-store",
    body:JSON.stringify(parameters)
  });
  const body=await r.json();
  if(!r.ok || body.status==="FAILED") throw Error(body.error||"research engine failed");
  return body;
}

function normalizeEngine(engine:any) {
  const report=engine.report||{};
  const market=report.market_state||{};
  return {
    run_version:"2.0",
    engine_version:engine.engine_version,
    execution:engine.execution,
    instrument:engine.parameters?.instrument||report.symbol,
    dataset:engine.source||{},
    look_ahead_policy:engine.lineage?.lookahead_policy||"confirmed swing events expose right-side confirmation timestamps",
    mtf:market.timeframes||{},
    market_state:market,
    events:report.events||[],
    evidence:report.evidence||[],
    benchmarks:engine.benchmarks,
    replay:engine.replay||[],
    analogue_research:report.analogue_research||{},
    hypotheses:report.hypotheses||[],
    conclusion:report.conclusion,
    dataset_validation:engine.dataset_validation,
    mtf_validation:engine.mtf_validation,
    lineage:[
      {stage:"source",artifact:engine.source?.artifact||"validated release dataset",rows:engine.source?.rows_after_window},
      {stage:"dataset_validation",status:engine.dataset_validation?.valid?"PASS":"FAIL"},
      {stage:"mtf_reconstruction",status:engine.mtf_validation?.valid?"PASS":"FAIL"},
      {stage:"canonical_engine",status:"EXECUTED",version:engine.engine_version},
    ],
    parameters:engine.parameters,
  };
}

export async function GET(req:Request) {
  try {
    const q=new URL(req.url).searchParams;
    const resource=q.get("resource");
    if(resource==="runs") return NextResponse.json(await db("smc_research_runs?select=*&order=created_at.desc"));
    if(resource==="hypotheses") return NextResponse.json(await db("smc_hypotheses?select=*&order=created_at.desc"));
    if(resource==="evidence") return NextResponse.json(await db("smc_evidence?select=*&order=created_at.desc"));
    const x=await canonical();
    return NextResponse.json({report:x.report,mtf:x.mtf,source:x.report.dataset||{}});
  } catch(e) {
    return NextResponse.json({error:e instanceof Error?e.message:"Research data unavailable"},{status:503});
  }
}

export async function POST(req:Request) {
  try {
    const b=await req.json();

    if(b.action==="run") {
      const p={
        instrument:b.instrument||b.parameters?.instrument||"EURUSD",
        dataset_artifact:b.parameters?.dataset_artifact,
        start:b.parameters?.start||null,
        end:b.parameters?.end||null,
        now:b.parameters?.now||null,
        replay_bars:b.parameters?.replay_bars||2000,
        news_events:b.parameters?.news_events||[],
        historical_episodes:b.parameters?.historical_episodes||[],
      };
      if(!p.dataset_artifact) delete p.dataset_artifact;

      const engine=await executeEngine(req,p);
      const result=normalizeEngine(engine);

      const run=(await db("smc_research_runs",{
        method:"POST",
        headers:{"Prefer":"return=representation"},
        body:JSON.stringify({
          instrument:result.instrument,
          dataset:result.dataset.artifact||"validated release",
          status:"COMPLETED",
          parameters:p,
          result,
          completed_at:new Date().toISOString()
        })
      }))[0];

      await db("smc_reports",{
        method:"POST",
        headers:{"Prefer":"return=representation"},
        body:JSON.stringify({run_id:run.id,report:result})
      });

      return NextResponse.json({run,result});
    }

    if(b.action==="hypothesis")
      return NextResponse.json((await db("smc_hypotheses",{method:"POST",headers:{"Prefer":"return=representation"},body:JSON.stringify(b.data)}))[0]);

    if(b.action==="evidence")
      return NextResponse.json((await db("smc_evidence",{method:"POST",headers:{"Prefer":"return=representation"},body:JSON.stringify(b.data)}))[0]);

    if(b.action==="report")
      return NextResponse.json(await db("smc_reports?select=*&run_id=eq."+encodeURIComponent(b.run_id)));

    return NextResponse.json({error:"Unknown action"},{status:400});
  } catch(e) {
    return NextResponse.json({error:e instanceof Error?e.message:"Research operation failed"},{status:500});
  }
}
